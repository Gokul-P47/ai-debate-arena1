# AI Debate Arena

A monorepo for an AI-powered debate platform where language models argue opposing sides of a topic in structured rounds.

## Project Overview

**AI Debate Arena** (product UI: **AI Talk Show**) orchestrates a hosted multi-agent chat using large language models. A Host keeps the show moving while Advocate and Friendly Critic guests share friendly, soft-opposition views on a topic.

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
│   │   │   ├── factory.py          # Selects provider via LLM_PROVIDER
│   │   │   ├── openai_provider.py
│   │   │   ├── grok_provider.py
│   │   │   └── gemini_provider.py
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

   Edit `.env` and set your provider keys. Choose which backend to use with
   `LLM_PROVIDER` (`openai`, `grok`, or `gemini`):

   ```env
   LLM_PROVIDER=openai

   OPENAI_API_KEY=your-openai-key
   OPENAI_MODEL=gpt-4o

   GROK_API_KEY=your-xai-key
   GROK_MODEL=grok-3

   GEMINI_API_KEY=your-gemini-key
   GEMINI_MODEL=gemini-3.1-flash-lite
   ```

   Only the active provider’s API key is required. Switch providers by changing
   `LLM_PROVIDER` and restarting the API.

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
| POST   | `/api/v1/debates` | Run multi-round debate; returns transcript |

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

- **Phase 3 — Streaming**: Add real-time streaming of debate turns via Server-Sent Events or WebSockets
- **Phase 4 — Frontend integration**: Connect Next.js UI to `POST /api/v1/debates`
- **Phase 5 — Persistence**: Add database storage for debate sessions and replay
- **Phase 6 — More providers**: Optional Anthropic / local models beyond OpenAI, Grok, and Gemini

## License

Private — all rights reserved.
