/** Debate domain types shared across the frontend application. */

export type DebateMood = 'SERIOUS' | 'FUN' | 'MIXED';

export type AgentRole = 'support' | 'opposition';

export interface DebateRequest {
  topic: string;
  mood: DebateMood | string;
  rounds: number;
  language?: string;
}

export interface DebateMessage {
  speaker: string;
  role: AgentRole;
  content: string;
  timestamp: string;
  roundNumber: number;
}

export interface DebateTurn {
  roundNumber: number;
  support: DebateMessage;
  opposition: DebateMessage;
}

export interface DebateSummaryData {
  text: string;
  supportPoints: string[];
  oppositionPoints: string[];
}

export interface DebateMetadata {
  provider: string;
  model: string;
  totalRounds: number;
  createdAt: string;
  completedAt?: string | null;
  extra?: Record<string, unknown>;
}

export interface DebateResponse {
  debateId: string;
  topic: string;
  language: string;
  mood: string;
  currentRound: number;
  transcript: DebateMessage[];
  turns: DebateTurn[];
  summary: DebateSummaryData | null;
  metadata: DebateMetadata;
  claimMemory?: unknown;
}

export interface AgentInfo {
  id: string;
  name: string;
  role: AgentRole;
  label: string;
}

export type DebateStreamEventType =
  | 'debate_started'
  | 'turn_started'
  | 'token'
  | 'message_completed'
  | 'status'
  | 'debate_completed'
  | 'error';

export interface DebateStreamHandlers {
  onEvent: (event: DebateStreamEventType, data: Record<string, unknown>) => void;
}
