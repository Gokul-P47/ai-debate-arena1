/** Debate domain types shared across the frontend application. */

export type DebateMood = 'SERIOUS' | 'FUN' | 'MIXED';

export interface DebateRequest {
  topic: string;
  mood: string;
  rounds: number;
}

export interface DebateMessage {
  agent: string;
  content: string;
  round: number;
}

export interface DebateResponse {
  messages: DebateMessage[];
  summary?: string;
}

export type AgentRole = 'support' | 'opposition';

export interface AgentInfo {
  id: string;
  name: string;
  role: AgentRole;
  label: string;
}
