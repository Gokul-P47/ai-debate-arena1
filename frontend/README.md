# AI Debate Arena — Frontend

Modern, scalable frontend for the AI Debate Arena platform. Built with Next.js App Router, TypeScript, and Tailwind CSS.

## Project Overview

The frontend allows users to configure and watch AI-powered debates between two agents — Support and Opposition. This phase establishes the UI foundation, component library, routing, state management structure, and API layer scaffolding. Debate functionality and backend integration will be implemented in the next phase.

### Planned Features (Future Phases)

- Enter debate topics via text or voice
- Select debate mood and number of rounds
- Start AI debates with real-time streaming
- Watch two AI agents debate side-by-side
- View final debate summaries

## Tech Stack

| Technology | Purpose |
| ---------- | ------- |
| Next.js 16 (App Router) | React framework with file-based routing |
| TypeScript | Type-safe development |
| Tailwind CSS v4 | Utility-first styling |
| Zustand | Client-side state management |
| TanStack Query | Server state and API caching |
| Axios | HTTP client for backend API |
| Lucide React | Icon library |
| ESLint + Prettier | Code quality and formatting |

## Folder Structure

```
frontend/
├── src/
│   ├── app/
│   │   ├── layout.tsx          # Root layout with Navbar & Footer
│   │   ├── page.tsx            # Home page (hero + form + arena)
│   │   ├── globals.css         # Global styles & dark theme
│   │   └── providers.tsx       # React Query provider
│   │
│   ├── components/
│   │   ├── common/             # Reusable UI primitives
│   │   │   ├── Button.tsx
│   │   │   ├── Input.tsx
│   │   │   ├── Select.tsx
│   │   │   ├── Card.tsx
│   │   │   └── Loading.tsx
│   │   ├── debate/             # Debate-specific components
│   │   │   ├── DebateForm.tsx
│   │   │   ├── DebateArena.tsx
│   │   │   ├── DebateMessage.tsx
│   │   │   ├── AgentPanel.tsx
│   │   │   └── DebateSummary.tsx
│   │   └── layout/
│   │       ├── Navbar.tsx
│   │       └── Footer.tsx
│   │
│   ├── hooks/
│   │   └── useDebate.ts        # Debate state hook
│   │
│   ├── lib/
│   │   ├── api.ts              # Axios instance
│   │   └── constants.ts        # App constants
│   │
│   ├── services/
│   │   └── debateService.ts    # API service (placeholder)
│   │
│   ├── store/
│   │   └── debateStore.ts      # Zustand store
│   │
│   ├── types/
│   │   ├── debate.ts           # Debate domain types
│   │   └── api.ts              # API response types
│   │
│   └── styles/
│       └── theme.ts            # Design tokens
│
├── public/
├── .env.local.example
├── .prettierrc
├── package.json
└── README.md
```

## Installation

### Prerequisites

- Node.js 18+
- npm

### Setup

1. Navigate to the frontend directory:

   ```bash
   cd frontend
   ```

2. Install dependencies:

   ```bash
   npm install
   ```

3. Configure environment variables:

   ```bash
   cp .env.local.example .env.local
   ```

   Default configuration:

   ```env
   NEXT_PUBLIC_API_URL=http://localhost:8000
   ```

## Development

Start the development server:

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

### Other Commands

| Command | Description |
| ------- | ----------- |
| `npm run build` | Production build |
| `npm run start` | Start production server |
| `npm run lint` | Run ESLint |
| `npm run format` | Format code with Prettier |

## Backend Integration

The frontend is configured to connect to the FastAPI backend at `NEXT_PUBLIC_API_URL`. Ensure the backend is running before integrating API calls in the next phase:

```bash
# In backend/
uvicorn app.main:app --reload --port 8000
```

## Future Features

- **Phase 2** — Connect `debateService` to backend API endpoints
- **Phase 3** — Real-time debate streaming via SSE or WebSockets
- **Phase 4** — Voice input integration for topic entry
- **Phase 5** — Debate history and session replay
- **Phase 6** — Responsive mobile optimizations and animations

## License

Private — all rights reserved.
