# AI Debate Arena

A monorepo for an AI-powered debate platform where language models argue opposing sides of a topic in structured rounds.

## Project Overview

**AI Debate Arena** orchestrates multi-agent debates using large language models. Two agents — Support and Opposition — take turns presenting arguments on a user-defined topic. This repository is organized as a monorepo with separate backend and frontend packages.

| Package    | Status        | Description                                      |
| ---------- | ------------- | ------------------------------------------------ |
| `backend/` | Active        | Python + FastAPI API with clean layered architecture |
| `frontend/`| Not started   | Reserved for future UI development               |

The current phase establishes the backend foundation: routing, configuration, schemas, provider interfaces, agent stubs, and tests. Debate generation logic will be implemented in a subsequent phase.

## Folder Structure

```
ai-debate-arena/
├── backend/
│   ├── app/
│   │   ├── main.py                 # FastAPI application entry point
│   │   ├── api/
│   │   │   └── routes/             # HTTP route handlers
│   │   │       ├── health.py       # Health check endpoint
│   │   │       └── debate.py       # Debate endpoint (placeholder)
│   │   ├── services/               # Business logic layer
│   │   │   └── debate_service.py
│   │   ├── agents/                 # Debate agent definitions
│   │   │   ├── support_agent.py
│   │   │   └── opposition_agent.py
│   │   ├── providers/              # LLM provider abstractions
│   │   │   ├── base_provider.py
│   │   │   └── openai_provider.py
│   │   ├── schemas/                # Pydantic request/response models
│   │   │   ├── debate_request.py
│   │   │   └── debate_response.py
│   │   ├── core/                   # Configuration and prompts
│   │   │   ├── config.py
│   │   │   └── prompts.py
│   │   └── utils/
│   │       └── logger.py
│   ├── tests/
│   │   └── test_health.py
│   ├── .env.example
│   ├── .gitignore
│   ├── requirements.txt
│   └── README.md
└── frontend/                       # Reserved for future development
```

## Setup Instructions

### Prerequisites

- Python 3.12 or later
- pip

### Installation

1. Clone the repository and navigate to the backend directory:

   ```bash
   cd backend
   ```

2. Create and activate a virtual environment:

   ```bash
   python -m venv .venv

   # Windows
   .venv\Scripts\activate

   # macOS / Linux
   source .venv/bin/activate
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Configure environment variables:

   ```bash
   cp .env.example .env
   ```

   Edit `.env` and set your values:

   ```env
   OPENAI_API_KEY=your-api-key-here
   OPENAI_MODEL=gpt-5
   ```

## Running the Application

From the `backend/` directory with your virtual environment activated:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at [http://localhost:8000](http://localhost:8000).

Interactive API documentation:

- Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs)
- ReDoc: [http://localhost:8000/redoc](http://localhost:8000/redoc)

### Available Endpoints

| Method | Path              | Description                          |
| ------ | ----------------- | ------------------------------------ |
| GET    | `/`               | Root — API welcome and version       |
| GET    | `/api/v1/health`  | Health check                         |
| POST   | `/api/v1/debates` | Create debate (placeholder response) |

## Running Tests

From the `backend/` directory:

```bash
pytest
```

Run with verbose output:

```bash
pytest -v
```

## Future Roadmap

- **Phase 2 — Debate Engine**: Implement OpenAI provider, agent logic, and multi-round debate orchestration
- **Phase 3 — Streaming**: Add real-time streaming of debate turns via Server-Sent Events or WebSockets
- **Phase 4 — Frontend**: Build a React/Next.js UI in `frontend/` for topic input, live debate viewing, and history
- **Phase 5 — Persistence**: Add database storage for debate sessions and replay
- **Phase 6 — Multi-Provider**: Support additional LLM providers (Anthropic, Google, local models)

## License

Private — all rights reserved.
