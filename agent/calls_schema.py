from pydantic import BaseModel, Field
from typing import Optional


class SearchPapersInput(BaseModel):
    """Input object to search papers with the CORE API."""

    query: str = Field(description="The query to search for on the selected archive.")
    max_papers: int = Field(
        description="The maximum number of papers to return. It's default to 1, but you can increase it up to 10 in case you need to perform a more comprehensive search.",
        default=1,
        ge=1,
        le=10,
    )


class DecisionMakingOutput(BaseModel):
    """Output object of the decision making node."""

    requires_research: bool = Field(
        description="Whether the user query requires research or not."
    )
    answer: Optional[str] = Field(
        default=None,
        description="The answer to the user query. It should be None if the user query requires research, otherwise it should be a direct answer to the user query.",
    )


class JudgeOutput(BaseModel):
    """Output object of the judge node."""

    is_good_answer: bool = Field(description="Whether the answer is good or not.")
    feedback: Optional[str] = Field(
        default=None,
        description="Detailed feedback about why the answer is not good. It should be None if the answer is good.",
    )
