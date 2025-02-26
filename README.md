# Agentic CV Parser API

A robust FastAPI-based backend service for candidate management, CV parsing, and workflow automation.

## Features

- 🚀 High-performance FastAPI backend
- 🤖 AI-powered CV parsing for PDF and Docx (document loaders & Unstructured OCR)
- 🔒 Rate limiting and security middleware
- 📊 PostgreSQL database with SQLAlchemy ORM (Async)
- 🔄 Asynchronous request handling
- 📝 Structured logging system with correlation IDs
- 🌐 CORS support
- 🔍 Request ID tracking
- 🐳 Docker support
- 📄 Pydantic schema validation
- 📚 Database Migrations using Alembic
- 📈 Pinecone vector database integration
- 📦 Poetry dependency management
- 🔑 Redis for rate limiting
- 🤖 LangChain & LangGraph integration for AI workflows
- 📄 Document processing capabilities
- 🔐 AWS S3 integration for file storage (Not enabled)
- 📝 Streaming and None-Streaming chat endpoints

## Project Structure

```
api/
├── agent/              # AI agent implementation
│   ├── workflow.py     # Candidate processing workflow
│   ├── tools.py       # Agent tools
│   └── prompts.py     # Agent prompts
├── api/               # API routes
│   ├── v1/           # API version 1 endpoints
│   ├── deps.py       # Dependencies
│   └── router.py     # Main router
├── core/             # Core configuration
│   └── config.py     # Settings management
├── crud/             # Database operations
│   ├── candidates.py # Candidate CRUD operations
│   └── sections.py   # Section CRUD operations
├── models/           # SQLAlchemy models
│   ├── candidates.py
│   ├── education.py
│   ├── experience.py
│   ├── projects.py
│   └── skills.py
├── schema/           # Pydantic schemas
│   ├── agent.py
│   ├── candidates.py
│   ├── education.py
│   └── responses.py
├── services/         # Business logic
│   └── documents.py  # Document processing
└── utils/           # Utilities
    ├── helpers.py
    ├── logger.py
    ├── s3_client.py
    └── middlewares/
```

## Prerequisites

- Python 3.12+
- Docker and Docker Compose (optional)
- Redis
- PostgreSQL
- OpenAI API key
- Pinecone API key (https://www.pinecone.io/)
- Unstructured API key (https://docs.unstructured.io/api-reference/api-services/free-api)

## Installation

### Using Poetry (Recommended)

1. Clone the repository:

```bash
git clone https://github.com/andrew-sameh/agentic-cv-parser.git
cd agentic-cv-parser
```

2. Install dependencies:

```bash
poetry install
```

3. Set up environment variables:

```bash
cp .env.example .env
# Edit .env with your configuration
```

### Using pip

1. Create a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

### Using Docker Compose

1.Clone the repository

2.Set up environment variables:

```bash
cp .env.example .env
# Edit .env with your configuration
```

3.Start the application:

```bash
docker-compose -p cv-parser up -d
# or
docker compose -p cv-parser up -d
```


## Environment Configuration

The following environment variables need to be configured in your `.env` file:

### Application Settings

- `ENV`: Environment (dev/prod)
- `PROJECT_NAME`: Project name
- `VERSION`: API version
- `DESCRIPTION`: API description
- `LOG_LEVEL`: Logging level
- `LOG_JSON_ENABLE`: Enable JSON logging
- `BACKEND_CORS_ORIGINS`: Allowed CORS origins

### Database Settings

- `DATABASE_USER`: PostgreSQL username
- `DATABASE_PASSWORD`: PostgreSQL password
- `DATABASE_NAME`: Database name
- `DATABASE_HOSTNAME`: Database host
- `DATABASE_PORT`: Database port

### Redis Settings

- `REDIS_HOST`: Redis host
- `REDIS_PORT`: Redis port
- `REDIS_DB`: Redis database number

### AWS S3 Settings (Not enabled)

- `AWS_S3_BUCKET_NAME`: S3 bucket name
- `AWS_S3_ACCESS_KEY_ID`: AWS access key
- `AWS_S3_SECRET_ACCESS_KEY`: AWS secret key
- `AWS_S3_REGION_NAME`: AWS region
- `AWS_S3_BASE_FOLDER`: Base folder in S3

### AI Settings

- `OPENAI_API_KEY`: OpenAI API key
- `LLM_MODEL`: Language model to use
- `EMBEDDING_MODEL`: Embedding model
- `UNSTRUCTURED_API_KEY`: Unstructured API key

### Vector Database Settings

- `PINECONE_API_KEY`: Pinecone API key
- `PINECONE_INDEX_NAME`: Pinecone index name
- `EMBEDDING_SEARCH_TYPE`: Search type
- `EMBEDDING_SCORE_THRESHOLD`: Similarity threshold
- `EMBEDDING_TOPK`: Top K results

## Database Setup

1.Start PostgreSQL and Redis using Docker:

```bash
docker-compose up -d db redis
```

2.Initialize the database:

```bash
alembic upgrade head
```

## API Documentation

Once the application is running, visit:
- Swagger UI: `http://localhost:8000/`
- ReDoc: `http://localhost:8000/redoc`

## Key Components

### Agent System
The agent system (`agent/`) handles chat functionalities.

### API Routes
API endpoints are organized in the `api/` directory with versioning support.

### Database Models
SQLAlchemy models in `models/` define the database schema for:
- Candidates
- Education
- Experience
- Projects
- Skills
- Certifications

### Services
- Document processing (`services/documents.py`) handles document parsing and extraction.

### Utilities
- S3 integration for file storage (not used)
- Structured logging
- Rate limiting
- Request correlation
- Error handling
- Redis integration

## Tests
In progress

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request