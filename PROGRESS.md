# AI Debate Arena — Project Progress

Living document tracking what has been implemented in this repository. Updated after each development session or code change.

**Last updated:** 2026-07-17

---

## Current Phase

**Phase 4 — Frontend Integration** (TV talk-show UI wired to live API)

Goal: Next.js UI runs a friendly Host + 2–4 guest talk show with soft contradictions.

---

## Completed

### Monorepo Structure

| Item | Status | Notes |
| ---- | ------ | ----- |
| `backend/` | Done | Python + FastAPI backend |
| `frontend/` | Done | Next.js + TypeScript + Tailwind CSS |
| Root `README.md` | Done | Monorepo overview and quick links |

### Backend — Application Core

| Item | Status | Location |
| ---- | ------ | -------- |
| FastAPI app entry point | Done | `backend/app/main.py` |
| CORS for local frontend | Done | `localhost:3000` / `127.0.0.1:3000` |
| App title & version | Done | `AI Debate Arena API` v1.0.0 |
| Root endpoint `GET /` | Done | Returns welcome message, title, version |
| Environment loading | Done | `python-dotenv` in `main.py` |

### Backend — API Routes

| Endpoint | Status | Response |
| -------- | ------ | -------- |
| `GET /api/v1/health` | Done | `{"status": "UP", "service": "AI Debate Arena API"}` |
| `POST /api/v1/debates` | Done | Full `DebateResponse` with transcript, turns, summary, metadata |
| `POST /api/v1/debates/stream` | Done | SSE: tokens + `audio_ready` (ElevenLabs), overlapped TTS pipeline |
| `GET /api/v1/audio/{id}` | Done | Serves cached TTS mp3 clips |

### Backend — Layered Architecture

| Layer | Status | Files |
| ----- | ------ | ----- |
| Routes | Done | `health.py`, `debate.py`, `audio.py` |
| Services | Done | `debate_service` (N-guest loop + TTS‖LLM overlap), claim memory, `tts_service`, `audio_cache` |
| Agents | Done | `host_agent`, `guest_agent` (+ legacy support/opposition wrappers) |
| Providers | Done | `app/providers/` — OpenAI, Grok, Gemini + `get_provider()` factory |
| Schemas | Done | `debate_request` (`participantCount` 2–4), `debate_response`, roles |
| Core | Done | `config.py`, `participants.py` roster, `prompt_templates.py` |
| Utils | Done | `app/utils/logger.py` |

### Backend — Configuration

| Item | Status | Notes |
| ---- | ------ | ----- |
| Pydantic settings | Done | LLM keys, ElevenLabs TTS voices (host + 4 guests), memory tuning |
| `.env.example` | Done | Template for OpenAI, Grok, Gemini, ElevenLabs, and active provider |

### Backend — Schemas

| Model | Status | Fields |
| ----- | ------ | ------ |
| `DebateRequest` | Done | `topic`, `rounds`, `mood`, `language`, `turnSeconds`, `participantCount` (2–4) |
| `DebateMessage` | Done | `speaker`, `role` (`host`/`support`/`opposition`/`guest3`/`guest4`), … |
| `DebateTurn` | Done | `roundNumber`, `messages[]` (+ legacy support/opposition) |
| `DebateSummary` | Done | `text`, `supportPoints`, `oppositionPoints`, `participants[]` |
| `DebateMetadata` | Done | `provider`, `model`, `totalRounds`, timestamps |
| `DebateResponse` | Done | transcript + `claimMemory` (`DebateState` with per-guest claims) |
| Claim models | Done | `DebateClaim`, `ClaimStatus`, `AgentClaimMemory`, `DebateState.guestMemories` |

### Backend — Multi-guest talk show

| Item | Status | Notes |
| ---- | ------ | ----- |
| Guest roster | Done | Advocate, Friendly Critic, Pragmatist, Wild Card |
| N-guest round loop | Done | Host → each guest once per segment → Host close; peers may contradict |
| Per-guest claim memory | Done | `MemoryService` keyed by guest role; peer contradiction ingest |
| SSE `debate_started` | Done | Emits `participantCount` + `participants` |

### Backend — Tests & Tooling

| Item | Status | Notes |
| ---- | ------ | ----- |
| Health / providers / debate / TTS tests | Done | Including 4-guest stream turn-order test |
| `requirements.txt` | Done | fastapi, uvicorn, openai, google-genai, … |
| `backend/README.md` | Done | Setup, run, test, and roadmap docs |

### Frontend — Application Core

| Item | Status | Location |
| ---- | ------ | -------- |
| Next.js App Router setup | Done | `frontend/src/app/` |
| Root layout with Navbar & Footer | Done | `frontend/src/app/layout.tsx` |
| Home page (hero + form + arena) | Done | `frontend/src/app/page.tsx` |
| Dark AI-themed global styles | Done | `frontend/src/app/globals.css` |
| React Query provider | Done | `frontend/src/app/providers.tsx` |

### Frontend — Components

| Component | Status | Location |
| --------- | ------ | -------- |
| Button, Input, Select, Card, Loading | Done | `frontend/src/components/common/` |
| Navbar, Footer | Done | `frontend/src/components/layout/` |
| DebateForm (guests 2–4 control) | Done | `frontend/src/components/debate/` |
| DebateArena / DebateStage (N guests) | Done | Dynamic Host + guest lineup |
| AgentPanel / DebateMessage / DebateSummary | Done | Themes for guest3 / guest4 |
| Voice topic input | Done | Web Speech API via `useSpeechInput` (Chrome/Edge) |

### Frontend — State, Services & Types

| Item | Status | Location |
| ---- | ------ | -------- |
| Zustand debate store | Done | `participantCount` + `participants` |
| `useDebate` hook | Done | Sends / applies `participantCount` from SSE |
| Debate service | Done | Stream + sync include `participantCount` |
| TypeScript types | Done | Roles + `ShowParticipant` / summary participants |
| Hosted debate flow | Done | Host + 2–4 guests, soft contradictions |
| ElevenLabs TTS + overlap | Done | Voices for host + 4 guests |
| Stage characters + audience sounds | Done | Dynamic lineup lean / speak poses |

### Frontend — Tooling

| Item | Status | Notes |
| ---- | ------ | ----- |
| TypeScript / Tailwind / ESLint / Prettier | Done | |
| `.env.local.example` | Done | `NEXT_PUBLIC_API_URL=http://localhost:8000` |
| `frontend/README.md` | Done | Setup, dev, and roadmap docs |

### Documentation & Tooling

| Item | Status | Notes |
| ---- | ------ | ----- |
| `PROGRESS.md` | Done | This file — tracks project progress |
| Cursor rule for progress updates | Done | `.cursor/rules/update-progress-readme.mdc` |

---

## Not Yet Implemented

- Database / persistence
- Additional LLM providers beyond OpenAI / Grok / Gemini
- CI/CD pipeline
- Streaming TTS (chunked audio) — currently full-utterance synthesis per turn
- Configurable guest personas (custom names/stances beyond the fixed roster)

---

## Change Log

| Date | Change |
| ---- | ------ |
| 2026-07-12 | Initial monorepo and backend foundation created (Phase 1) |
| 2026-07-12 | Added `PROGRESS.md` and Cursor rule to keep progress doc updated |
| 2026-07-12 | Frontend foundation created — Next.js, components, store, API layer, dark UI theme |
| 2026-07-12 | Configurable LLM providers: OpenAI, Grok (xAI), Gemini via `LLM_PROVIDER` factory |
| 2026-07-12 | Verified Gemini key; default model set to `gemini-3.1-flash-lite` (`gemini-2.5-flash-lite` blocked for new accounts) |
| 2026-07-13 | Debate engine: response models, Support/Opposition agents, provider-wired orchestration, CORS, tests |
| 2026-07-13 | Frontend connected to live debates — sequential debate-show reveal in the arena |
| 2026-07-13 | Conversation memory layer + dynamic Support/Opposition prompt templates |
| 2026-07-13 | Structured claim memory: extract claims, track ACTIVE/CONTRADICTED/DEFENDED, claim-based prompts |
| 2026-07-13 | Added Tamil (`ta`) and other Indic language labels to prompt language map |
| 2026-07-13 | Frontend form now sends mood, rounds, and language (incl. Tamil) to the API |
| 2026-07-13 | Live SSE token streaming for debates (`POST /api/v1/debates/stream`) + frontend live arena |
| 2026-07-13 | Upgraded ContextBuilder prompts, rich claim extraction, LLM contradiction/defense, anti-repetition |
| 2026-07-13 | Added Host Agent (opening / round announce / closing); arena shows Host + Support + Opposition |
| 2026-07-13 | ElevenLabs TTS with overlapped pipeline (TTS A ‖ LLM B) + frontend audio queue |
| 2026-07-13 | Configurable turn length (30–120s) from frontend; prompts sized to spoken word targets |
| 2026-07-13 | Subtitle-synced UI: hide LLM text until TTS plays, reveal words with audio |
| 2026-07-14 | Stage characters (speak/listen animations) + audience clap/cheer Web Audio |
| 2026-07-15 | Reframed as AI Talk Show: friendly TV prompts, soft opposition, studio UI |
| 2026-07-15 | Multi-guest shows: `participantCount` 2–4 (Host + Advoc / Critic / Pragmatist / Wild Card), peer contradictions, stage/arena/form wiring |
| 2026-07-17 | Fixed Stop Show: invalidate SSE session so buffered events can't restart the show; clear draft/audio on stop |
| 2026-07-17 | Voice input for topic: Web Speech API hook + DebateForm mic toggle (matches selected language) |
| 2026-07-17 | Fixed Stop Show for real: shared abort/session across Form+Arena `useDebate` instances; cancel SSE reader |
