/** Zustand store for debate session state. */

import { create } from 'zustand';

import { DEFAULT_ROUNDS } from '@/lib/constants';
import type { DebateMessage } from '@/types/debate';

interface DebateState {
  topic: string;
  mood: string;
  rounds: number;
  messages: DebateMessage[];
  summary: string | null;
  loading: boolean;
  setTopic: (topic: string) => void;
  setMood: (mood: string) => void;
  setRounds: (rounds: number) => void;
  setMessages: (messages: DebateMessage[]) => void;
  setSummary: (summary: string | null) => void;
  setLoading: (loading: boolean) => void;
  reset: () => void;
}

const initialState = {
  topic: '',
  mood: 'SERIOUS',
  rounds: DEFAULT_ROUNDS,
  messages: [] as DebateMessage[],
  summary: null as string | null,
  loading: false,
};

export const useDebateStore = create<DebateState>((set) => ({
  ...initialState,
  setTopic: (topic) => set({ topic }),
  setMood: (mood) => set({ mood }),
  setRounds: (rounds) => set({ rounds }),
  setMessages: (messages) => set({ messages }),
  setSummary: (summary) => set({ summary }),
  setLoading: (loading) => set({ loading }),
  reset: () => set(initialState),
}));
