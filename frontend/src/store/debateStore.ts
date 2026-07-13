/** Zustand store for debate session state (supports live token streaming). */

import { create } from 'zustand';

import { DEFAULT_LANGUAGE, DEFAULT_ROUNDS } from '@/lib/constants';
import type {
  AgentRole,
  DebateMessage,
  DebateMetadata,
  DebateMood,
  DebateSummaryData,
} from '@/types/debate';

interface DebateState {
  topic: string;
  mood: DebateMood;
  rounds: number;
  language: string;
  debateId: string | null;
  transcript: DebateMessage[];
  summary: DebateSummaryData | null;
  metadata: DebateMetadata | null;
  loading: boolean;
  streaming: boolean;
  statusMessage: string | null;
  error: string | null;
  /** Live draft while the current agent is still generating tokens. */
  streamingDraft: {
    role: AgentRole;
    speaker: string;
    roundNumber: number;
    content: string;
  } | null;
  setTopic: (topic: string) => void;
  setMood: (mood: DebateMood) => void;
  setRounds: (rounds: number) => void;
  setLanguage: (language: string) => void;
  setLoading: (loading: boolean) => void;
  setStreaming: (streaming: boolean) => void;
  setStatusMessage: (message: string | null) => void;
  setError: (error: string | null) => void;
  startStreamingSession: (payload: {
    debateId: string;
    topic: string;
    mood: string;
    language?: string;
    totalRounds: number;
    provider?: string;
    model?: string;
  }) => void;
  beginTurn: (payload: {
    role: AgentRole;
    speaker: string;
    roundNumber: number;
  }) => void;
  appendToken: (delta: string) => void;
  completeMessage: (message: DebateMessage) => void;
  completeDebate: (payload: {
    summary: DebateSummaryData | null;
    metadata: DebateMetadata;
    transcript?: DebateMessage[];
  }) => void;
  reset: () => void;
}

const initialState = {
  topic: '',
  mood: 'SERIOUS' as DebateMood,
  rounds: DEFAULT_ROUNDS,
  language: DEFAULT_LANGUAGE,
  debateId: null as string | null,
  transcript: [] as DebateMessage[],
  summary: null as DebateSummaryData | null,
  metadata: null as DebateMetadata | null,
  loading: false,
  streaming: false,
  statusMessage: null as string | null,
  error: null as string | null,
  streamingDraft: null as DebateState['streamingDraft'],
};

export const useDebateStore = create<DebateState>((set, get) => ({
  ...initialState,
  setTopic: (topic) => set({ topic }),
  setMood: (mood) => set({ mood }),
  setRounds: (rounds) => set({ rounds }),
  setLanguage: (language) => set({ language }),
  setLoading: (loading) => set({ loading }),
  setStreaming: (streaming) => set({ streaming }),
  setStatusMessage: (statusMessage) => set({ statusMessage }),
  setError: (error) => set({ error }),
  startStreamingSession: ({
    debateId,
    topic,
    mood,
    language,
    totalRounds,
    provider,
    model,
  }) =>
    set({
      debateId,
      topic,
      mood: mood as DebateMood,
      language: language ?? DEFAULT_LANGUAGE,
      transcript: [],
      summary: null,
      streamingDraft: null,
      streaming: true,
      loading: false,
      error: null,
      statusMessage: 'Debate is live…',
      metadata: {
        provider: provider ?? 'unknown',
        model: model ?? 'unknown',
        totalRounds,
        createdAt: new Date().toISOString(),
      },
    }),
  beginTurn: ({ role, speaker, roundNumber }) =>
    set({
      streamingDraft: { role, speaker, roundNumber, content: '' },
      streaming: true,
      statusMessage: `${speaker} is speaking…`,
    }),
  appendToken: (delta) => {
    const draft = get().streamingDraft;
    if (!draft) return;
    set({
      streamingDraft: { ...draft, content: draft.content + delta },
    });
  },
  completeMessage: (message) =>
    set((state) => ({
      transcript: [...state.transcript, message],
      streamingDraft: null,
      statusMessage: null,
    })),
  completeDebate: ({ summary, metadata, transcript }) =>
    set((state) => ({
      summary,
      metadata,
      transcript: transcript ?? state.transcript,
      streamingDraft: null,
      streaming: false,
      loading: false,
      statusMessage: null,
    })),
  reset: () => set(initialState),
}));
