# TestCaseCreator

AI-powered manual test case generator using LangGraph, OpenAI, and Pinecone RAG. Ingests requirement docs, retrieves relevant context, generates structured QA test cases via LLM, and supports human-in-the-loop review (approve/edit/reject) before exporting approved test cases to JSON.

## Architecture

```
main.py
  │
  ├── rag_parser/vctore_store_setter.py   # Pinecone index setup & document ingestion
  ├── rag_parser/generator.py             # LLM-based test case generation
  ├── flow/graph.py                       # LangGraph workflow (retrieve → generate → human review → export)
  ├── model/test_models.py                # Pydantic models & state schema
  └── util/exporter.py                    # JSON export of approved test cases
```

## Flow

1. **Retrieve** — Ingests requirements from a `.docx` file into Pinecone, then retrieves relevant context via similarity search.
2. **Generate** — Sends context + query to GPT-4o-mini to produce structured test cases.
3. **Human Review** — Pauses execution and prompts the user to `approve`, `edit`, or `reject` the generated test cases.
4. **Export** — Writes approved test cases to `Approved_Rebalancing_Test_Cases.json`.

## Setup

### Prerequisites

- Python 3.11+
- [uv](https://docs.astral.sh/uv/) package manager
- OpenAI API key
- Pinecone API key

### Installation

```bash
uv sync
```

### Configuration

Create a `.env` file with:

```env
PINECONE_API_KEY=your_pinecone_api_key
INDEX_NAME=manual_test_index
EMBEDDING_MODEL=text-embedding-3-small
VECTOR_DB_DIMENSION=1536
VECTOR_DB_METRIC=cosine
VECTOR_DB_CLOUD=aws
VECTOR_DB_REGION=us-east-1

OPENAI_API_KEY=your_openai_api_key
LANGSMITH_TRACING=true
LANGSMITH_ENDPOINT=https://eu.api.smith.langchain.com
LANGSMITH_API_KEY=your_langsmith_api_key
LANGSMITH_PROJECT=ManualTestCase
```

### Run

```bash
uv run python main.py
```

```power shell
.\.venv\Scripts\python.exe main.py
```


## Tech Stack

- **LangGraph** — Stateful workflow with human-in-the-loop interrupt/resume
- **LangChain + OpenAI** — LLM-based test case generation with structured output parsing
- **Pinecone** — Vector store for RAG-based context retrieval
- **Pydantic** — Data validation and schema enforcement