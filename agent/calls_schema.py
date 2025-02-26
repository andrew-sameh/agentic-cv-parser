from pydantic import BaseModel, Field
from typing import Optional



class DecisionMakingOutput(BaseModel):
    """Output object of the decision making node."""

    requires_db_query: bool = Field(
        description="Whether the user query requires a db query or not."
    )
    answer: Optional[str] = Field(
        default=None,
        description="The answer to the user query. It should be None if the user query requires checking the database, otherwise it should be a direct answer to the user query.",
    )


class JudgeOutput(BaseModel):
    """Output object of the judge node."""

    is_good_answer: bool = Field(description="Whether the answer is good or not.")
    feedback: Optional[str] = Field(
        default=None,
        description="Detailed feedback about why the answer is not good. It should be None if the answer is good.",
    )
