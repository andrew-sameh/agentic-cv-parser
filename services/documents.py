import os
import shutil
from typing import List

import structlog
from fastapi import HTTPException, UploadFile
from langchain_community.document_loaders import Docx2txtLoader, PyPDFLoader
from langchain_core.documents import Document
from langchain_core.prompts import (
    ChatPromptTemplate,
    MessagesPlaceholder,
    PromptTemplate,
)
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_unstructured import UnstructuredLoader

from core.config import settings
from schema.candidates import CandidateExtraction
from schema.certificates import CertificationList
from schema.education import EducationList
from schema.experience import ExperienceList
from schema.projects import ProjectList
from schema.skills import SkillList

logger = structlog.stdlib.get_logger()


class DocumentProcessor:
    def __init__(self):
        self.index_name = settings.PINECONE_INDEX_NAME
        self.pinecone_api_key = settings.PINECONE_API_KEY
        self.openai_api_key = settings.OPENAI_API_KEY
        self.top_k = settings.EMBEDDING_TOPK
        self.llm = ChatOpenAI(api_key=self.openai_api_key, model=settings.LLM_MODEL)
        self.embeddings = OpenAIEmbeddings(
            api_key=self.openai_api_key, model=settings.EMBEDDINGS_MODEL
        )
        self.base_namespace = "resume_documents"
        self.vectorstore = PineconeVectorStore(
            index_name=self.index_name,
            embedding=self.embeddings,
            pinecone_api_key=self.pinecone_api_key,
        )
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=25000, chunk_overlap=200, add_start_index=True
        )
        self.candidate_tool = self.llm.with_structured_output(
            schema=CandidateExtraction
        )
        self.cert_tool = self.llm.with_structured_output(schema=CertificationList)
        self.edu_tool = self.llm.with_structured_output(schema=EducationList)
        self.exp_tool = self.llm.with_structured_output(schema=ExperienceList)
        self.skill_tool = self.llm.with_structured_output(schema=SkillList)
        self.project_tool = self.llm.with_structured_output(schema=ProjectList)
        self.base_prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "You are an expert extraction algorithm specialized in parsing and extracting structured information from resumes. "
                    "You will extract the following key information: Personal Information, Education, Experience, Certifications, Skills, and Projects. "
                    "For each section, accurately identify and return the requested attributes. "
                    "If a value is not provided or cannot be determined, return 'null' for that attribute. "
                    "Adhere strictly to the predefined schema for each attribute. "
                    "Output should be well-structured and in accordance with the schema to facilitate downstream processing.",
                ),
                # Include a placeholder for examples to improve performance
                # MessagesPlaceholder('examples'),
                ("human", "{text}"),
            ]
        )

    async def load_and_split_document(self, file_path: str) -> List[Document]:
        if file_path.endswith(".pdf"):
            loader = PyPDFLoader(file_path)
        elif file_path.endswith(".docx"):
            loader = Docx2txtLoader(file_path)
        else:
            raise ValueError(f"Unsupported file type: {file_path}")

        documents = await loader.aload()
        await logger.info(f"1st Loaded {len(documents)} documents from {file_path}")
        # check if the pdf is empty
        if (
            file_path.endswith(".pdf")
            and len(documents) == 1
            and documents[0].page_content == ""
        ):
            await logger.info(f"Empty PDF file: {file_path}")
            loader = UnstructuredLoader(
                api_key=settings.UNSTRUCTURED_API_KEY,
                url="https://api.unstructured.io/general/v0/general",
                file_path=file_path,
                strategy="hi_res",  # "fast" or "hi_res"
                partition_via_api=True,
                coordinates=True,
            )
            documents = await loader.aload()
            return documents

        if len(documents) == 0:
            raise ValueError(f"Empty document: {file_path}")
        return documents

    def serialize_docs(self, docs: List[Document]) -> str:
        return "\n\n".join(
            (f"Source: {doc.metadata}\nContent: {doc.page_content}") for doc in docs
        )

    def combine_docs(self, docs: List[Document], namespace: str) -> Document:
        content = "\n\n".join((f"{doc.page_content}") for doc in docs)
        return Document(page_content=content, metadata={"id": namespace})

    def retrieve_docs(self, query: str) -> List[Document]:
        results = self.vectorstore.similarity_search(
            query, k=self.top_k, namespace=self.base_namespace
        )
        return results
    
    def retrieve_docs_serialized(self,query: str) -> str:
        results = self.vectorstore.similarity_search(
            query, k=self.top_k, namespace=self.base_namespace
        )
        if not results:
            return "No results found"
        serialized = self.serialize_docs(results)
        return serialized

    async def process_file_upload(self, file: UploadFile, namespace: str):
        temp_file_path = f"temp_{file.filename}"

        try:
            # Save the uploaded file to a temporary file
            with open(temp_file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            await logger.info(f"Saved file to {temp_file_path}")
            # Load and split the document
            loaded_docs = await self.load_and_split_document(temp_file_path)
            single_doc = self.combine_docs(loaded_docs, namespace)
            documents = self.text_splitter.split_documents([single_doc])
            await logger.info(f"Loaded and split {len(documents)} documents")
            ids = await self.vectorstore.aadd_documents(documents, namespace=self.base_namespace)
            await logger.info(
                f"Indexed {len(ids)} documents and added to pinecone with the namespace {namespace}"
            )
            content = self.serialize_docs(documents)
            (
                candidate,
                certs,
                edu,
                exp,
                skills,
                projects,
            ) = await self.extract_candidate_info(content)
            await logger.info(f"Extracted candidate info: {candidate}")

            return candidate, certs, edu, exp, skills, projects, content

        finally:
            if os.path.exists(temp_file_path):
                await logger.info(f"Removing temporary file {temp_file_path}")
                os.remove(temp_file_path)

    async def use_candidate_tool(self, text: str) -> CandidateExtraction:
        prompt = await self.base_prompt.ainvoke({"text": text})
        candidate = await self.candidate_tool.ainvoke(prompt)
        return candidate

    async def use_cert_tool(self, text: str) -> CertificationList:
        prompt = await self.base_prompt.ainvoke({"text": text})
        certs = await self.cert_tool.ainvoke(prompt)
        return certs

    async def use_edu_tool(self, text: str) -> EducationList:
        prompt = await self.base_prompt.ainvoke({"text": text})
        edu = await self.edu_tool.ainvoke(prompt)
        return edu

    async def use_exp_tool(self, text: str) -> ExperienceList:
        prompt = await self.base_prompt.ainvoke({"text": text})
        exp = await self.exp_tool.ainvoke(prompt)
        return exp

    async def use_skill_tool(self, text: str) -> SkillList:
        prompt = await self.base_prompt.ainvoke({"text": text})
        skills = await self.skill_tool.ainvoke(prompt)
        return skills

    async def use_project_tool(self, text: str) -> ProjectList:
        prompt = await self.base_prompt.ainvoke({"text": text})
        projects = await self.project_tool.ainvoke(prompt)
        return projects

    async def extract_candidate_info(self, text: str):
        candidate = await self.use_candidate_tool(text)
        certs = await self.use_cert_tool(text)
        edu = await self.use_edu_tool(text)
        exp = await self.use_exp_tool(text)
        skills = await self.use_skill_tool(text)
        projects = await self.use_project_tool(text)
        return candidate, certs, edu, exp, skills, projects


document_processor = DocumentProcessor()
