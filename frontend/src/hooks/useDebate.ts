/** Custom hook for debate session state and live SSE streaming. */

'use client';

import { useCallback } from 'react';

import { unlockAudienceAudio } from '@/lib/audienceSounds';
import * as debateService from '@/services/debateService';
import { useDebateStore } from '@/store/debateStore';
import type {
  AgentRole,
  DebateMessage,
  DebateMetadata,
  DebateMood,
  DebateSummaryData,
  ShowParticipant,
} from '@/types/debate';

/**
 * Shared across every `useDebate()` caller (Form starts, Arena stops).
 * Per-instance refs caused Stop to abort a different controller than Start.
 */
let activeAbort: AbortController | null = null;
let activeSession = 0;

function beginStreamSession(): { controller: AbortController; session: number } {
  activeAbort?.abort();
  const controller = new AbortController();
  activeAbort = controller;
  activeSession += 1;
  return { controller, session: activeSession };
}

function stopStreamSession(): void {
  activeSession += 1;
  activeAbort?.abort();
  activeAbort = null;
}

function isLiveSession(session: number, controller: AbortController): boolean {
  return session === activeSession && !controller.signal.aborted;
}

/**
 * Provides debate form state and starts a live streamed debate show.
 */
export function useDebate() {
  const topic = useDebateStore((s) => s.topic);
  const mood = useDebateStore((s) => s.mood);
  const rounds = useDebateStore((s) => s.rounds);
  const language = useDebateStore((s) => s.language);
  const turnSeconds = useDebateStore((s) => s.turnSeconds);
  const participantCount = useDebateStore((s) => s.participantCount);
  const participants = useDebateStore((s) => s.participants);
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
  const setTurnSeconds = useDebateStore((s) => s.setTurnSeconds);
  const setParticipantCount = useDebateStore((s) => s.setParticipantCount);
  const reset = useDebateStore((s) => s.reset);
  const paused = useDebateStore((s) => s.paused);
  const setPaused = useDebateStore((s) => s.setPaused);
  const stopDebateStore = useDebateStore((s) => s.stopDebate);

  const startDebate = useCallback(async () => {
    const state = useDebateStore.getState();
    const nextTopic = state.topic.trim();
    if (!nextTopic) {
      state.setError('Please enter a debate topic.');
      return;
    }

    const { controller, session } = beginStreamSession();

    state.clearAudio();
    state.setPaused(false);
    state.setError(null);
    state.setLoading(true);
    state.setStreaming(false);
    state.setStatusMessage('Connecting to debate stream…');

    // Browser autoplay policies require a gesture before Web Audio / TTS.
    void unlockAudienceAudio();

    try {
      await debateService.streamDebate(
        {
          topic: nextTopic,
          mood: state.mood,
          rounds: state.rounds,
          language: state.language,
          turnSeconds: state.turnSeconds,
          participantCount: state.participantCount,
        },
        {
          onEvent: (event, data) => {
            if (!isLiveSession(session, controller)) return;
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
                  participantCount: Number(data.participantCount ?? state.participantCount),
                  participants: Array.isArray(data.participants)
                    ? (data.participants as ShowParticipant[])
                    : undefined,
                  ttsEnabled: Boolean(data.ttsEnabled),
                  newsArticles: Array.isArray(data.newsArticles) ? data.newsArticles : undefined,
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

              case 'audio_ready': {
                const audioId = typeof data.audioId === 'string' ? data.audioId : '';
                const audioUrl = typeof data.audioUrl === 'string' ? data.audioUrl : '';
                if (audioId && audioUrl) {
                  store.enqueueAudio({
                    role: data.role as AgentRole,
                    speaker: String(data.speaker ?? 'Agent'),
                    roundNumber: Number(data.roundNumber ?? 1),
                    audioId,
                    audioUrl,
                    mimeType: typeof data.mimeType === 'string' ? data.mimeType : 'audio/mpeg',
                  });
                }
                break;
              }

              case 'status': {
                const statusText = typeof data.message === 'string' ? data.message : null;
                store.setStatusMessage(statusText);
                if (statusText && /tts skipped/i.test(statusText)) {
                  store.revealOrphanMessage();
                }
                break;
              }

              case 'debate_completed':
                store.completeDebate({
                  summary: (data.summary as DebateSummaryData) ?? null,
                  metadata: data.metadata as DebateMetadata,
                  transcript: data.transcript as DebateMessage[] | undefined,
                });
                break;

              case 'error':
                store.setError(
                  typeof data.message === 'string' ? data.message : 'Debate stream failed',
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

      if (isLiveSession(session, controller)) {
        const store = useDebateStore.getState();
        if (store.streaming) {
          store.setStreaming(false);
          store.setLoading(false);
        }
      }
    } catch (err) {
      if (!isLiveSession(session, controller)) return;
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
    turnSeconds,
    participantCount,
    participants,
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
    setTurnSeconds,
    setParticipantCount,
    reset,
    startDebate,
    paused,
    setPaused,
    stopDebate: useCallback(() => {
      stopStreamSession();
      stopDebateStore();
    }, [stopDebateStore]),
  };
}
