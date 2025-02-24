import json
from collections.abc import AsyncGenerator

import structlog
from langchain_core.messages import AIMessage, SystemMessage, ToolMessage
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, StateGraph
from langgraph.graph.state import CompiledStateGraph
from langgraph.store.memory import InMemoryStore
from langgraph.types import Command

from agent.calls_schema import DecisionMakingOutput, JudgeOutput
from agent.prompts import (
    agent_prompt,
    decision_making_prompt,
    judge_prompt,
    planning_prompt,
)
from agent.state import AgentState
from agent.tools import ask_human_feedback, download_paper, search_papers
from core.config import settings
from schema.research import StreamInput
from utils.helpers import (
    convert_message_content_to_string,
    format_tools_description,
    langchain_to_chat_message,
    parse_input,
    remove_tool_calls,
)

logger = structlog.get_logger(__name__)


class ResearchAgent:
    """Encapsulates LangGraph agent logic."""

    def __init__(self):
        self.base_llm = ChatOpenAI(
            model="gpt-4o-mini", temperature=0.0, api_key=settings.OPENAI_API_KEY,streaming=True
        )
        self.tools = [search_papers, download_paper, ask_human_feedback]
        self.tools_dict = {tool.name: tool for tool in self.tools}
        self.decision_making_llm = self.base_llm.with_structured_output(
            DecisionMakingOutput
        )
        self.agent_llm = self.base_llm.bind_tools(self.tools)
        self.judge_llm = self.base_llm.with_structured_output(JudgeOutput)
        self.workflow = self._build_workflow()
        self.compiled_agent = self.workflow.compile(
            checkpointer=InMemorySaver(), store=InMemoryStore()
        )

    def _build_workflow(self):
        """Creates and configures the LangGraph workflow."""
        workflow = StateGraph(AgentState)

        workflow.add_node("decision_making", self.decision_making_node)
        workflow.add_node("planning", self.planning_node)
        workflow.add_node("tools", self.tools_node)
        workflow.add_node("agent", self.agent_node)
        workflow.add_node("judge", self.judge_node)

        workflow.set_entry_point("decision_making")
        workflow.add_conditional_edges(
            "decision_making", self.router, {"planning": "planning", "end": END}
        )
        workflow.add_edge("planning", "agent")
        workflow.add_edge("tools", "agent")
        workflow.add_conditional_edges(
            "agent", self.should_continue, {"continue": "tools", "end": "judge"}
        )
        workflow.add_conditional_edges(
            "judge", self.final_answer_router, {"planning": "planning", "end": END}
        )

        return workflow

    # Decision making node
    def decision_making_node(self, state: AgentState):
        """Entry point of the workflow. Based on the user query, the model can either respond directly or perform a full research, routing the workflow to the planning node"""
        system_prompt = SystemMessage(content=decision_making_prompt)
        response: DecisionMakingOutput = self.decision_making_llm.invoke(
            [system_prompt] + state["messages"]
        )
        output = {"requires_research": response.requires_research}
        if response.answer:
            output["messages"] = [AIMessage(content=response.answer)]
        return output

    # Task router function
    def router(self, state: AgentState):
        """Router directing the user query to the appropriate branch of the workflow."""
        return "planning" if state["requires_research"] else "end"

    # Planning node
    def planning_node(self, state: AgentState):
        """Planning node that creates a step by step plan to answer the user query."""
        system_prompt = SystemMessage(
            content=planning_prompt.format(tools=format_tools_description(self.tools))
        )
        response = self.base_llm.invoke([system_prompt] + state["messages"])
        return {"messages": [response]}

    # Tool call node
    def tools_node(self, state: AgentState):
        """Tool call node that executes the tools based on the plan."""
        outputs = []
        for tool_call in state["messages"][-1].tool_calls:
            tool_result = self.tools_dict[tool_call["name"]].invoke(tool_call["args"])
            outputs.append(
                ToolMessage(
                    content=json.dumps(tool_result),
                    name=tool_call["name"],
                    tool_call_id=tool_call["id"],
                )
            )
        return {"messages": outputs}

    # Agent call node
    def agent_node(self, state: AgentState):
        """Agent call node that uses the LLM with tools to answer the user query."""
        system_prompt = SystemMessage(content=agent_prompt)
        response = self.agent_llm.invoke([system_prompt] + state["messages"])
        return {"messages": [response]}

    # Should continue function
    def should_continue(self, state: AgentState):
        """Check if the agent should continue or end."""
        return "continue" if state["messages"][-1].tool_calls else "end"

    # Judge node
    def judge_node(self, state: AgentState):
        """Node to let the LLM judge the quality of its own final answer."""
        # End execution if the LLM failed to provide a good answer twice.
        num_feedback_requests = state.get("num_feedback_requests", 0)
        if num_feedback_requests >= 2:
            return {"is_good_answer": True}
        system_prompt = SystemMessage(content=judge_prompt)
        response: JudgeOutput = self.judge_llm.invoke(
            [system_prompt] + state["messages"]
        )
        output = {
            "is_good_answer": response.is_good_answer,
            "num_feedback_requests": num_feedback_requests + 1,
        }
        if response.feedback:
            output["messages"] = [AIMessage(content=response.feedback)]
        return output

    # Final answer router function
    def final_answer_router(self, state: AgentState):
        """Router to end the workflow or improve the answer."""
        return "end" if state["is_good_answer"] else "planning"

    async def message_generator(
        self,
        user_input: StreamInput,
    ) -> AsyncGenerator[str, None]:
        """
        Generate a stream of messages from the agent.

        This is the workhorse method for the /stream endpoint.
        """
        agent: CompiledStateGraph = self.compiled_agent
        kwargs, run_id = parse_input(user_input)

        # Process streamed events from the graph and yield messages over the SSE stream.
        async for event in agent.astream_events(**kwargs, version="v2"):
            if not event:
                continue

            new_messages = []
            # Yield messages written to the graph state after node execution finishes.
            if (
                event["event"] == "on_chain_end"
                # on_chain_end gets called a bunch of times in a graph execution
                # This filters out everything except for "graph node finished"
                and any(t.startswith("graph:step:") for t in event.get("tags", []))
            ):
                if isinstance(event["data"]["output"], Command):
                    new_messages = event["data"]["output"].update.get("messages", [])
                elif "messages" in event["data"]["output"]:
                    new_messages = event["data"]["output"]["messages"]

            # Also yield intermediate messages from agents.utils.CustomData.adispatch().
            if event[
                "event"
            ] == "on_custom_event" and "custom_data_dispatch" in event.get("tags", []):
                new_messages = [event["data"]]

            for message in new_messages:
                try:
                    chat_message = langchain_to_chat_message(message)
                    chat_message.run_id = str(run_id)
                except Exception as e:
                    logger.error(f"Error parsing message: {e}")
                    yield f"data: {json.dumps({'event_name':event['name'], 'type': 'error', 'content': 'Unexpected error'})}\n\n"
                    continue
                # LangGraph re-sends the input message, which feels weird, so drop it
                if (
                    chat_message.type == "human"
                    and chat_message.content == user_input.message
                ):
                    continue
                yield f"data: {json.dumps({'event_name':event['name'], 'type': 'message', 'content': chat_message.model_dump()})}\n\n"

            # Yield tokens streamed from LLMs.
            if (
                event["event"] == "on_chat_model_stream"
                and user_input.stream_tokens
                and "llama_guard" not in event.get("tags", [])
            ):
                content = remove_tool_calls(event["data"]["chunk"].content)
                if content:
                    # Empty content in the context of OpenAI usually means
                    # that the model is asking for a tool to be invoked.
                    # So we only print non-empty content.
                    yield f"data: {json.dumps({'event_name':event['name'],'type': 'token', 'content': convert_message_content_to_string(content)})}\n\n"
                continue
            yield f"data: {json.dumps({'event_name':event['name'], 'type': 'info', 'event':event['event'] })}\n\n"
        yield "data: [DONE]\n\n"
