# Contract Intelligence Platform Backend

FastAPI backend for Contract Intelligence Platform. It receives lease contract uploads, extracts document text, extracts structured metadata with an LLM, stores operational records in SQLite, indexes contract chunks in ChromaDB, and exposes endpoints for search, chat, and reports.

> This service is for educational and portfolio purposes only. It does not provide legal advice.

## Responsibilities

- Validate uploaded PDF, DOCX, and TXT files.
- Store uploaded source files.
- Convert documents into normalized Markdown.
- Extract lease metadata with the OpenAI Responses API.
- Validate extracted metadata with Pydantic.
- Persist contract records and chunk references in SQLite.
- Build LangChain documents from extracted contract units.
- Split contract text into retrievable chunks.
- Generate OpenAI embeddings.
- Store vectors in a persistent ChromaDB collection.
- Serve semantic search and RAG chat endpoints.

## Tech Stack

- Python 3.13
- FastAPI
- SQLAlchemy
- SQLite
- Pydantic and pydantic-settings
- OpenAI Python SDK
- LangChain
- ChromaDB
- PyMuPDF4LLM for PDFs
- Docling for DOCX files
- uv for dependency management

## Project Structure

```text
backend/
+-- app/
|   +-- api/routes/
|   |   +-- chat.py
|   |   +-- contracts.py
|   |   +-- search.py
|   +-- database/
|   |   +-- models.py
|   |   +-- session.py
|   |   +-- repositories/
|   +-- prompts/
|   |   +-- metadata_extraction_prompt.txt
|   |   +-- rag_answer_prompt.txt
|   +-- schemas/
|   +-- services/
|   |   +-- document_processing/
|   +-- config.py
|   +-- dependencies.py
|   +-- main.py
+-- data/
|   +-- cip.db
|   +-- uploads/
|   +-- chroma/
+-- Dockerfile
+-- pyproject.toml
+-- uv.lock
+-- README.md
```

## Environment Variables

Create a backend `.env` file:

```bash
cp .env.example .env
```

Required:

```env
OPENAI_API_KEY=your_openai_api_key_here
```

Supported variables:

| Variable | Default | Description |
| --- | --- | --- |
| `ENVIRONMENT` | `development` | Runtime environment label returned by `/health`. |
| `OPENAI_API_KEY` | Required | API key used for metadata extraction, chat, and embeddings. |
| `OPENAI_MODEL` | `gpt-4.1-mini` | Model used for metadata extraction and RAG responses. |
| `EMBEDDING_MODEL` | `text-embedding-3-small` | Model used for vector embeddings. |
| `DATABASE_URL` | `sqlite:///./data/cip.db` | SQLAlchemy database URL. |
| `DATA_DIR` | `./data` | Root runtime data directory. |
| `UPLOAD_DIR` | `./data/uploads` | Directory for uploaded source files. |
| `CHROMA_PERSIST_DIR` | `./data/chroma` | Persistent ChromaDB directory. |
| `CHROMA_COLLECTION_NAME` | `contracts` | Chroma collection name. |
| `MAX_UPLOAD_SIZE_MB` | `20` | Maximum upload size in MB. |
| `BACKEND_CORS_ORIGINS` | `http://localhost:8501` | Comma-separated allowed CORS origins. |

## Run Locally

Install dependencies:

```bash
uv sync
```

Start the API:

```bash
uv run uvicorn app.main:app --reload
```

Default URLs:

```text
API:      http://localhost:8000
Docs:     http://localhost:8000/docs
Health:   http://localhost:8000/health
```

## Run with Docker

Build and run from the backend directory:

```bash
docker build -t cip-backend .
docker run --env-file .env -p 8000:8000 -v cip_backend_data:/app/data cip-backend
```

For the full stack, prefer the root `docker-compose.yml`.

## API Endpoints

### Health

```http
GET /
GET /health
```

### Contracts

```http
POST /contracts/upload
GET  /contracts
GET  /contracts/{contract_id}
GET  /contracts/reports/expiring?days=90
```

Upload example:

```bash
curl -X POST http://localhost:8000/contracts/upload \
  -F "file=@sample_lease.pdf"
```

### Semantic Search

```http
POST /search/semantic
```

Request body:

```json
{
  "query": "contracts with early termination penalties",
  "contract_id": null,
  "k": 5
}
```

`contract_id` is optional. When omitted or `null`, the search runs across all indexed contracts.

### Chat

```http
POST /chat/global
POST /chat/contract/{contract_id}
```

Request body:

```json
{
  "question": "What are the tenant's maintenance obligations?",
  "k": 5
}
```

Responses include the generated answer and source references from retrieved chunks.

## Ingestion Flow

`POST /contracts/upload` runs the complete ingestion flow:

```text
UploadFile
  -> file validation
  -> SHA-256 deduplication
  -> file storage
  -> contract row creation
  -> document extraction to Markdown
  -> metadata extraction
  -> SQLite metadata persistence
  -> LangChain document creation
  -> chunking
  -> chunk persistence
  -> embedding generation
  -> ChromaDB indexing
  -> indexed status
```

Supported extraction engines:

| Format | Engine | Location metadata |
| --- | --- | --- |
| PDF | PyMuPDF4LLM | Page number |
| DOCX | Docling | Paragraph index |
| TXT | Native Python reader | Line range |

Scanned PDFs are not supported in the MVP.

## Data Model

Main tables:

- `contracts`: uploaded file metadata, processing status, extracted Markdown, structured lease metadata, and error state.
- `contract_chunks`: chunk content, source location metadata, and Chroma vector ID references.

Contract statuses:

```text
uploaded
text_extracted
metadata_extracted
indexed
failed
```

When ingestion fails, the API stores:

- `failed_step`
- `error_message`

## Runtime Data

Local runtime data lives under:

```text
data/
+-- cip.db
+-- uploads/
+-- chroma/
```

Docker runtime data lives under:

```text
/app/data/
+-- cip.db
+-- uploads/
+-- chroma/
```

This directory must be persistent in deployed environments.

## Development Notes

- Database tables are created automatically on application startup with `Base.metadata.create_all`.
- Upload deduplication is based on the SHA-256 hash of the file bytes.
- Metadata extraction only uses the first 50,000 characters of extracted Markdown.
- Chunking uses a recursive character splitter with `chunk_size=1200` and `chunk_overlap=150`.
- The backend should not be scaled to multiple replicas while it uses SQLite and local ChromaDB storage.

## Related Docs

- [Architecture](../docs/architecture.md)
- [Dataset](../docs/dataset.md)
- [Deployment](../docs/deployment.md)
- [Ingestion Pipeline](../docs/ingestion_pipeline.md)
