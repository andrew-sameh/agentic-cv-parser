# import io
# import time

# import pdfplumber
# import urllib3
from langchain_core.tools import tool

# from agent.calls_schema import SearchPapersInput
# from services.core_api_service import CoreAPIWrapper
from langchain_community.utilities import SQLDatabase
from core.config import settings
from services.documents import document_processor
# Initialize the database
db = SQLDatabase.from_uri(settings.SYNC_DATABASE_URI)

@tool("db-query-tool")
def db_query_tool(query: str) -> str:
    """
    Execute a SQL query against the database and get back the result.
    If the query is not correct, an error message will be returned.
    If an error is returned, rewrite the query, check the query, and try again.
    """
    result = db.run_no_throw(query)
    if not result:
        return "Error: Query failed. Please rewrite your query and try again."
    return result

@tool("match-job-description")
def match_job_description(job_description: str) -> str:
    """    
    Match the job description with the resume and return the result.
    Use this tool if the user is asking for a match for a job posting.
    This tool returns the top 4 most relevant resumes, with a unique identifier for each resume.
    """
    return document_processor.retrieve_docs_serialized(job_description)

@tool("ask-human-feedback")
def ask_human_feedback(question: str) -> str:
    """Ask for human feedback. You should call this tool when encountering unexpected errors."""
    return input(question)

