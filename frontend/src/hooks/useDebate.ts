/** Custom hook for debate session state and actions. */

'use client';

import { useCallback } from 'react';

import { PLACEHOLDER_MESSAGE } from '@/lib/constants';
import { useDebateStore } from '@/store/debateStore';

/**
 * Provides access to debate store state and placeholder actions.
 * Business logic will be implemented in the next phase.
 */
export function useDebate() {
  const store = useDebateStore();

  const startDebate = useCallback(() => {
    store.setLoading(true);
    // Placeholder — no backend call yet
    store.setLoading(false);
    return PLACEHOLDER_MESSAGE;
  }, [store]);

  return {
    topic: store.topic,
    mood: store.mood,
    rounds: store.rounds,
    messages: store.messages,
    summary: store.summary,
    loading: store.loading,
    setTopic: store.setTopic,
    setMood: store.setMood,
    setRounds: store.setRounds,
    setMessages: store.setMessages,
    setSummary: store.setSummary,
    reset: store.reset,
    startDebate,
  };
}
