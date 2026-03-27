# Projects-VFree

An internal ChatGPT Projects alternative that lets teams create isolated AI assistants with custom instructions, document-based knowledge, persistent conversation history, and semantic memory — all without a paid subscription.

---

## Overview

Projects-VFree is a full-stack RAG (Retrieval-Augmented Generation) platform built for internal team use. Each project behaves as an independent AI assistant: it has its own system instructions, its own document library, and its own memory of the user. Nothing leaks between projects.

The platform was built as a cost-effective alternative to ChatGPT Projects, covering the three most common internal use cases:

- Writing cover letters and job application responses with specific formatting constraints.
- Answering questions grounded in internal documentation (wikis, runbooks, technical guides).
- Writing, explaining, and debugging code with project-specific context.

---

## Features

- **Multi-project isolation** — each project has its own documents, chat history, and memory stored independently at the database level.
- **Document ingestion** — upload PDF, DOCX, and TXT files; they are automatically chunked, vectorized, and indexed.
- **RAG-powered chat** — responses are grounded in the project's documents, retrieved by semantic similarity at query time.
- **Persistent conversation history** — full chat history is preserved per project across sessions.
- **Semantic memory** — the system automatically extracts and stores key facts from user messages (name, preferences, constraints) and injects them into future responses.
- **Custom instructions** — each project can define system-level behavior rules that the assistant follows in every response.
- **Source attribution** — every response includes the document fragments used to generate it, with similarity scores.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | Streamlit |
| Backend | FastAPI |
| LLM | Groq — Llama 3.3 70B Versatile |
| Embeddings | Google GenAI — `gemini-embedding-001` (3072d) |
| Database | Supabase (PostgreSQL + pgvector) |
| AI Orchestration | LangChain |
| Config management | pydantic-settings v2 |
| Server | Uvicorn |

---

## Project Structure

```
/                                   # Backend root
├── main.py                         # FastAPI app, routers, CORS
├── config.py                       # Typed settings via pydantic-settings
├── requirements.txt
├── .env                            # Environment variables (not committed)
│
├── db/
│   └── client.py                   # Supabase client factory
│
├── routers/
│   ├── projects.py                 # Project CRUD + memory endpoints
│   ├── ingest.py                   # Document upload and indexing
│   ├── query.py                    # Chat endpoint + history management
│   └── documents.py                # Document listing and deletion
│
├── services/
│   ├── ingest_service.py           # Chunking, embeddings, batch insert
│   ├── retrieval_service.py        # Query embedding + vector search
│   ├── llm_service.py              # Prompt construction, Groq completion
│   ├── conversation_service.py     # History persistence and retrieval
│   └── memory_service.py          # Semantic memory extraction and upsert
│
├── utils/
│   ├── loaders.py                  # LangChain document loaders by file type
│   └── splitter.py                 # RecursiveCharacterTextSplitter config
│
└── app/                            # Frontend
    ├── main.py                     # Entry point, sidebar, project selector
    ├── api_client.py               # All HTTP calls to the backend
    └── pages/
        ├── 1_Projects.py           # Project management UI
        ├── 2_Chat.py               # Chat interface with memory panel
        └── 3_Documents.py          # Document upload and listing
```

---

## Getting Started

### Prerequisites

- Python 3.10+
- A [Supabase](https://supabase.com) project with the `pgvector` extension enabled
- A [Groq](https://console.groq.com) API key
- A [Google AI Studio](https://aistudio.google.com) API key

### 1. Clone the repository

```bash
git clone https://github.com/your-org/projects-vfree.git
cd projects-vfree
```

### 2. Create and activate a virtual environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file in the project root:

```env
# LLM — Groq
GROQ_API_KEY=your_groq_api_key
GROQ_BASE_URL=https://api.groq.com/openai/v1

# Embeddings — Google GenAI
GEMINI_API_KEY=your_gemini_api_key

# Database — Supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_KEY=your_service_role_key

# RAG parameters
CHUNK_SIZE=800
CHUNK_OVERLAP=200
TOP_K=5
SIMILARITY_THRESHOLD=0.3

# Models
LLM_MODEL=llama-3.3-70b-versatile
EMBEDDING_MODEL=models/gemini-embedding-001
EMBEDDING_DIMENSIONS=3072
```

> **Note:** Use the `service_role` key for `SUPABASE_SERVICE_KEY`, not the `anon` key. The service key bypasses Row Level Security, which is required for server-side operations.

### 5. Set up the database

Run the following SQL blocks in order using the Supabase SQL Editor.

**Enable pgvector and create tables:**

```sql
create extension if not exists vector;

create table projects (
  id           uuid primary key default gen_random_uuid(),
  title        text not null,
  instructions text not null default '',
  created_at   timestamptz default now(),
  updated_at   timestamptz default now()
);

create table documents (
  id          uuid primary key default gen_random_uuid(),
  project_id  uuid not null references projects(id) on delete cascade,
  title       text not null,
  file_name   text not null,
  file_type   text not null,
  file_size   bigint,
  status      text default 'processing',
  created_at  timestamptz default now(),
  updated_at  timestamptz default now()
);
create index on documents(project_id);

create table chunks (
  id           uuid primary key default gen_random_uuid(),
  document_id  uuid not null references documents(id) on delete cascade,
  project_id   uuid not null references projects(id) on delete cascade,
  content      text not null,
  embedding    vector(3072),
  chunk_index  integer,
  section      text,
  token_count  integer,
  metadata     jsonb,
  created_at   timestamptz default now()
);
create index on chunks(project_id);
create index on chunks(document_id);

create table conversations (
  id          uuid primary key default gen_random_uuid(),
  project_id  uuid not null references projects(id) on delete cascade,
  created_at  timestamptz default now()
);

create table messages (
  id               uuid primary key default gen_random_uuid(),
  conversation_id  uuid not null references conversations(id) on delete cascade,
  project_id       uuid not null references projects(id) on delete cascade,
  role             text not null check (role in ('user', 'assistant')),
  content          text not null,
  created_at       timestamptz default now()
);
create index on messages(conversation_id);
create index on messages(project_id);

create table memories (
  id          uuid primary key default gen_random_uuid(),
  project_id  uuid not null references projects(id) on delete cascade,
  key         text not null,
  value       text not null,
  updated_at  timestamptz default now(),
  unique(project_id, key)
);
create index on memories(project_id);
```

**Create the vector search function:**

```sql
create or replace function match_chunks(
  query_embedding  vector(3072),
  match_project_id uuid,
  match_threshold  float default 0.3,
  match_count      int   default 5
)
returns table (
  id          uuid,
  content     text,
  section     text,
  document_id uuid,
  similarity  float
)
language sql stable
as $$
  select
    chunks.id,
    chunks.content,
    chunks.section,
    chunks.document_id,
    1 - (chunks.embedding <=> query_embedding) as similarity
  from chunks
  where
    chunks.project_id = match_project_id
    and 1 - (chunks.embedding <=> query_embedding) > match_threshold
  order by chunks.embedding <=> query_embedding
  limit match_count;
$$;
```

### 6. Run the application

Open two terminals from the project root.

**Terminal 1 — Backend:**

```bash
uvicorn main:app --reload
# API available at http://localhost:8000
# Swagger docs at http://localhost:8000/docs
```

**Terminal 2 — Frontend:**

```bash
cd app
streamlit run main.py
# UI available at http://localhost:8501
```

---

## How It Works

### Document ingestion pipeline

```
File upload → LangChain loader → RecursiveCharacterTextSplitter
    → Gemini embedding per chunk → Batch insert into pgvector (10 chunks/batch)
```

Chunks are inserted in batches of 10 to avoid HTTP timeouts on large documents. Each chunk stores the embedding vector alongside its source `document_id` and `project_id`.

### Chat pipeline

```
User message
    → Embed query (Gemini) → match_chunks() filtered by project_id
    → Load conversation history + semantic memory
    → Build prompt (instructions + memory + chunks + history)
    → Groq LLM completion
    → Save messages → Extract memory facts (async, silent fail)
    → Return answer + sources
```

### Semantic memory

After every user message, a secondary LLM call extracts structured facts (name, preferences, constraints) and stores them as key-value pairs in the `memories` table. Storage uses upsert on `(project_id, key)` — no duplicates, automatic updates. Memory is injected into every future prompt for that project, even after the conversation history is cleared.

---

## API Reference

| Method | Endpoint | Description |
|---|---|---|
| GET | `/projects/` | List all projects |
| POST | `/projects/` | Create a project |
| PATCH | `/projects/{id}` | Update title or instructions |
| DELETE | `/projects/{id}` | Delete project and all associated data |
| GET | `/projects/{id}/memory` | Get semantic memory for a project |
| DELETE | `/projects/{id}/memory` | Clear semantic memory |
| POST | `/ingest/` | Upload and index a document |
| GET | `/documents/` | List documents for a project |
| DELETE | `/documents/{id}` | Delete document and its chunks |
| POST | `/query/` | Send a message, get answer + sources |
| DELETE | `/query/{project_id}/history` | Clear conversation history |
| GET | `/health` | Health check |

Full interactive documentation is available at `http://localhost:8000/docs` when the backend is running.

---

## Known Limitations

**No vector index on chunks**
pgvector on Supabase's free plan limits IVFFlat and HNSW indexes to 2000 dimensions. Since `gemini-embedding-001` generates 3072-dimensional vectors, the `chunks` table operates without a vector index (sequential scan). This is negligible for small document sets but becomes a bottleneck at scale. Migration to Qdrant or Weaviate is planned for future phases.

**No user authentication**
All projects are currently visible to anyone with access to the application URL. User isolation via Supabase Auth and Row Level Security is planned but not yet implemented.

**Conversation history not reloaded on project switch**
Chat history is persisted in Supabase but the frontend reconstructs it from session state. Switching away from a project and returning to it within the same session will show an empty chat, even though the history exists in the database.

---

## Roadmap

- [ ] Reload conversation history from Supabase on project selection
- [ ] Inline document upload from the chat interface
- [ ] Response streaming via SSE
- [ ] User authentication with Supabase Auth and RLS
- [ ] Enriched sources panel with document title and file name
- [ ] Automated test suite (pytest + FastAPI TestClient)
- [ ] Production deployment (Railway/Render + Streamlit Cloud)
- [ ] Migration to a vector store supporting high-dimensional indexes (Qdrant or Weaviate)

---

## Development Notes

- The Groq client is initialized using the OpenAI SDK pointed at Groq's base URL. Switching to OpenAI requires changing two environment variables and one line in `services/llm_service.py`.
- The similarity threshold (`SIMILARITY_THRESHOLD=0.3`) is calibrated for `gemini-embedding-001`, which produces lower cosine similarity scores than models like OpenAI's `text-embedding-3-small`. Do not raise this value without re-calibrating against your document set.
- Memory extraction uses `temperature=0.0` and fails silently — an error in fact extraction never interrupts the main chat flow.

---

## License

Internal use only. Not licensed for public distribution.