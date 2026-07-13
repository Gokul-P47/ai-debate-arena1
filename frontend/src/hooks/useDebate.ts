/** Custom hook for debate session state and live SSE streaming. */

'use client';

import { useCallback, useRef } from 'react';

import * as debateService from '@/services/debateService';
import { useDebateStore } from '@/store/debateStore';
import type {
  AgentRole,
  DebateMessage,
  DebateMetadata,
  DebateMood,
  DebateSummaryData,
} from '@/types/debate';

/**
 * Provides debate form state and starts a live streamed debate show.
 */
export function useDebate() {
  const topic = useDebateStore((s) => s.topic);
  const mood = useDebateStore((s) => s.mood);
  const rounds = useDebateStore((s) => s.rounds);
  const language = useDebateStore((s) => s.language);
  const transcript = useDebateStore((s) => s.transcript);
  const summary = useDebateStore((s) => s.summary);
  const metadata = useDebateStore((s) => s.metadata);
  const loading = useDebateStore((s) => s.loading);
  const streaming = useDebateStore((s) => s.streaming);
  const statusMessage = useDebateStore((s) => s.statusMessage);
  const error = useDebateStore((s) => s.error);
  const debateId = useDebateStore((s) => s.debateId);
  const streamingDraft = useDebateStore((s) => s.streamingDraft);
  const setTopic = useDebateStore((s) => s.setTopic);
  const setMoodStore = useDebateStore((s) => s.setMood);
  const setRounds = useDebateStore((s) => s.setRounds);
  const setLanguage = useDebateStore((s) => s.setLanguage);
  const reset = useDebateStore((s) => s.reset);

  const abortRef = useRef<AbortController | null>(null);
  const sessionRef = useRef(0);

  const startDebate = useCallback(async () => {
    const state = useDebateStore.getState();
    const nextTopic = state.topic.trim();
    if (!nextTopic) {
      state.setError('Please enter a debate topic.');
      return;
    }

    abortRef.current?.abort();
    const controller = new AbortController();
    abortRef.current = controller;
    sessionRef.current += 1;
    const session = sessionRef.current;

    state.setError(null);
    state.setLoading(true);
    state.setStreaming(false);
    state.setStatusMessage('Connecting to debate stream…');

    try {
      await debateService.streamDebate(
        {
          topic: nextTopic,
          mood: state.mood,
          rounds: state.rounds,
          language: state.language,
        },
        {
          onEvent: (event, data) => {
            if (session !== sessionRef.current) return;
            const store = useDebateStore.getState();

            switch (event) {
              case 'debate_started':
                store.startStreamingSession({
                  debateId: String(data.debateId ?? ''),
                  topic: String(data.topic ?? nextTopic),
                  mood: String(data.mood ?? state.mood),
                  language: String(data.language ?? state.language),
                  totalRounds: Number(data.rounds ?? state.rounds),
                  provider: data.provider ? String(data.provider) : undefined,
                  model: data.model ? String(data.model) : undefined,
                });
                break;

              case 'turn_started':
                store.beginTurn({
                  role: data.role as AgentRole,
                  speaker: String(data.speaker ?? 'Agent'),
                  roundNumber: Number(data.roundNumber ?? 1),
                });
                break;

              case 'token':
                if (typeof data.delta === 'string') {
                  store.appendToken(data.delta);
                }
                break;

              case 'message_completed': {
                const message = data.message as DebateMessage | undefined;
                if (message?.content) {
                  store.completeMessage(message);
                }
                break;
              }

              case 'status':
                store.setStatusMessage(
                  typeof data.message === 'string' ? data.message : null,
                );
                break;

              case 'debate_completed':
                store.completeDebate({
                  summary: (data.summary as DebateSummaryData) ?? null,
                  metadata: data.metadata as DebateMetadata,
                  transcript: data.transcript as DebateMessage[] | undefined,
                });
                break;

              case 'error':
                store.setError(
                  typeof data.message === 'string'
                    ? data.message
                    : 'Debate stream failed',
                );
                store.setStreaming(false);
                store.setLoading(false);
                break;

              default:
                break;
            }
          },
        },
        controller.signal,
      );

      if (session === sessionRef.current) {
        const store = useDebateStore.getState();
        if (store.streaming) {
          store.setStreaming(false);
          store.setLoading(false);
        }
      }
    } catch (err) {
      if (session !== sessionRef.current) return;
      if (controller.signal.aborted) return;
      const message = err instanceof Error ? err.message : 'Failed to start debate';
      const current = useDebateStore.getState();
      current.setError(message);
      current.setLoading(false);
      current.setStreaming(false);
    }
  }, []);

  return {
    topic,
    mood,
    rounds,
    language,
    transcript,
    summary,
    metadata,
    loading,
    streaming,
    revealing: streaming,
    statusMessage,
    error,
    debateId,
    streamingDraft,
    setTopic,
    setMood: (value: string) => setMoodStore(value as DebateMood),
    setRounds,
    setLanguage,
    reset,
    startDebate,
  };
}
