import structlog
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import StreamingResponse

from agent.workflow import CandidatesAgent 
from schema.agent import ChatMessage, StreamInput, UserInput, sse_response_example
from schema.responses import ResponseBase, create_response
from utils.helpers import langchain_to_chat_message, parse_input

logger = structlog.stdlib.get_logger()

router = APIRouter()
# agent = CandidatesAgent()


@router.post("/query", response_model=ResponseBase[ChatMessage], status_code=200)
async def research_query(
    request: Request, body: UserInput
) -> ResponseBase[ChatMessage]:
    kwargs, run_id = parse_input(body)
    graph: CandidatesAgent= request.app.state.graph
    response = await graph.compiled_agent.ainvoke(**kwargs)
    output = langchain_to_chat_message(response["messages"][-1])
    output.run_id = str(run_id)
    return create_response(output)


@router.post(
    "/stream", response_class=StreamingResponse, responses=sse_response_example()
)
async def stream(request: Request, body: StreamInput) -> StreamingResponse:
    """
    Stream an agent's response to a user input, including intermediate messages and tokens.

    Use thread_id to persist and continue a multi-turn conversation. run_id kwarg
    is also attached to all messages for recording feedback.
    """
    graph: CandidatesAgent= request.app.state.graph
    return StreamingResponse(
        graph.message_generator(body),
        media_type="text/event-stream",
    )

