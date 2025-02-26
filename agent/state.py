from langchain_core.messages import BaseMessage 
from langgraph.graph.message import add_messages
from typing import Annotated, Sequence, TypedDict

class AgentState(TypedDict):
    """The state of the agent during the candidates analysis process."""
    requires_db_query: bool = False
    num_feedback_requests: int = 0
    is_good_answer: bool = False
    messages: Annotated[Sequence[BaseMessage], add_messages]