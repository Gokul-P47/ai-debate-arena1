/** Debate domain types shared across the frontend application. */

export type DebateMood = 'SERIOUS' | 'FUN' | 'MIXED';

export type AgentRole = 'host' | 'support' | 'opposition' | 'guest3' | 'guest4';

export interface DebateRequest {
  topic: string;
  mood: DebateMood | string;
  rounds: number;
  language?: string;
  /** Target spoken length per guest turn (30–120 seconds). */
  turnSeconds?: number;
  /** Number of guest participants (2–4). Host is always extra. */
  participantCount?: number;
}

export interface DebateMessage {
  speaker: string;
  role: AgentRole;
  content: string;
  timestamp: string;
  roundNumber: number;
  /** Client id used to sync TTS subtitles. */
  id?: string;
  /** Linked ElevenLabs clip when TTS is on. */
  audioId?: string;
  /**
   * How much of `content` to show (0 = hidden, 1 = full).
   * When undefined, treat as fully visible (TTS off / legacy).
   */
  revealRatio?: number;
}

export interface DebateTurn {
  roundNumber: number;
  messages?: DebateMessage[];
  support?: DebateMessage;
  opposition?: DebateMessage;
}

export interface ParticipantSummary {
  role: AgentRole;
  name: string;
  points: string[];
}

export interface DebateSummaryData {
  text: string;
  supportPoints: string[];
  oppositionPoints: string[];
  participants?: ParticipantSummary[];
}

export interface ShowParticipant {
  role: AgentRole;
  name: string;
  label: string;
  stance?: string;
  theme?: string;
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
  | 'audio_ready'
  | 'status'
  | 'debate_completed'
  | 'error';

export interface AudioClip {
  role: AgentRole;
  speaker: string;
  roundNumber: number;
  audioId: string;
  audioUrl: string;
  mimeType?: string;
  /** Transcript message id this clip narrates. */
  messageId?: string;
}

export interface DebateStreamHandlers {
  onEvent: (event: DebateStreamEventType, data: Record<string, unknown>) => void;
}
