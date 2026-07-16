/** Zustand store for debate session state (supports live token streaming + TTS subtitles). */

import { create } from 'zustand';

import {
  DEFAULT_LANGUAGE,
  DEFAULT_PARTICIPANT_COUNT,
  DEFAULT_ROUNDS,
  DEFAULT_TURN_SECONDS,
  guestsForCount,
} from '@/lib/constants';
import type {
  AgentRole,
  AudioClip,
  DebateMessage,
  DebateMetadata,
  DebateMood,
  DebateSummaryData,
  ShowParticipant,
} from '@/types/debate';

let messageSeq = 0;

function nextMessageId(): string {
  messageSeq += 1;
  return `msg-${messageSeq}`;
}

interface DebateState {
  topic: string;
  mood: DebateMood;
  rounds: number;
  language: string;
  turnSeconds: number;
  participantCount: number;
  /** Active guests for the current show (from server or form default). */
  participants: ShowParticipant[];
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
  /** Ordered TTS clips waiting to play (FIFO). */
  audioQueue: AudioClip[];
  /** Role whose audio is currently playing (drives speaking glow). */
  playingRole: AgentRole | null;
  /** Message currently being subtitled with audio. */
  activeSubtitleMessageId: string | null;
  ttsEnabled: boolean;
  paused: boolean;
  playbackSpeed: number;
  newsArticles: Array<{ title: string; link: string; pub_date: string; source: string }>;
  setTopic: (topic: string) => void;
  setMood: (mood: DebateMood) => void;
  setRounds: (rounds: number) => void;
  setLanguage: (language: string) => void;
  setTurnSeconds: (seconds: number) => void;
  setParticipantCount: (count: number) => void;
  setLoading: (loading: boolean) => void;
  setStreaming: (streaming: boolean) => void;
  setStatusMessage: (message: string | null) => void;
  setError: (error: string | null) => void;
  setPlayingRole: (role: AgentRole | null) => void;
  enqueueAudio: (clip: Omit<AudioClip, 'messageId'> & { messageId?: string }) => void;
  advanceAudioQueue: () => void;
  beginSubtitle: (audioId: string) => void;
  updateSubtitleProgress: (ratio: number) => void;
  finishSubtitle: () => void;
  revealAllPending: () => void;
  revealOrphanMessage: () => void;
  clearAudio: () => void;
  startStreamingSession: (payload: {
    debateId: string;
    topic: string;
    mood: string;
    language?: string;
    totalRounds: number;
    provider?: string;
    model?: string;
    turnSeconds?: number;
    participantCount?: number;
    participants?: ShowParticipant[];
    ttsEnabled?: boolean;
    newsArticles?: Array<{ title: string; link: string; pub_date: string; source: string }>;
  }) => void;
  beginTurn: (payload: { role: AgentRole; speaker: string; roundNumber: number }) => void;
  appendToken: (delta: string) => void;
  completeMessage: (message: DebateMessage) => void;
  completeDebate: (payload: {
    summary: DebateSummaryData | null;
    metadata: DebateMetadata;
    transcript?: DebateMessage[];
  }) => void;
  setPaused: (paused: boolean) => void;
  setPlaybackSpeed: (speed: number) => void;
  stopDebate: () => void;
  reset: () => void;
}

const initialState = {
  topic: '',
  mood: 'MIXED' as DebateMood,
  rounds: DEFAULT_ROUNDS,
  language: DEFAULT_LANGUAGE,
  turnSeconds: DEFAULT_TURN_SECONDS,
  participantCount: DEFAULT_PARTICIPANT_COUNT,
  participants: guestsForCount(DEFAULT_PARTICIPANT_COUNT),
  debateId: null as string | null,
  transcript: [] as DebateMessage[],
  summary: null as DebateSummaryData | null,
  metadata: null as DebateMetadata | null,
  loading: false,
  streaming: false,
  statusMessage: null as string | null,
  error: null as string | null,
  streamingDraft: null as DebateState['streamingDraft'],
  audioQueue: [] as AudioClip[],
  playingRole: null as AgentRole | null,
  activeSubtitleMessageId: null as string | null,
  ttsEnabled: false,
  paused: false,
  playbackSpeed: 1,
  newsArticles: [] as Array<{ title: string; link: string; pub_date: string; source: string }>,
};

export const useDebateStore = create<DebateState>((set, get) => ({
  ...initialState,
  setTopic: (topic) => set({ topic }),
  setMood: (mood) => set({ mood }),
  setRounds: (rounds) => set({ rounds }),
  setLanguage: (language) => set({ language }),
  setTurnSeconds: (turnSeconds) => set({ turnSeconds }),
  setParticipantCount: (participantCount) => {
    const n = Math.min(4, Math.max(2, Math.round(participantCount) || 2));
    set({
      participantCount: n,
      participants: guestsForCount(n),
    });
  },
  setLoading: (loading) => set({ loading }),
  setStreaming: (streaming) => set({ streaming }),
  setStatusMessage: (statusMessage) => set({ statusMessage }),
  setError: (error) => set({ error }),
  setPlayingRole: (playingRole) => set({ playingRole }),
  enqueueAudio: (clip) =>
    set((state) => {
      const matchIndex = state.transcript.findIndex(
        (m) => !m.audioId && m.role === clip.role && m.roundNumber === clip.roundNumber,
      );
      const messageId =
        clip.messageId ?? (matchIndex >= 0 ? state.transcript[matchIndex]?.id : undefined);

      const transcript =
        matchIndex >= 0 && messageId
          ? state.transcript.map((m, i) => (i === matchIndex ? { ...m, audioId: clip.audioId } : m))
          : state.transcript;

      return {
        transcript,
        audioQueue: [
          ...state.audioQueue,
          {
            ...clip,
            messageId,
          },
        ],
      };
    }),
  advanceAudioQueue: () =>
    set((state) => {
      const [, ...rest] = state.audioQueue;
      const done =
        !state.streaming && rest.length === 0
          ? {
              transcript: state.transcript.map((m) =>
                (m.revealRatio ?? 1) < 1 ? { ...m, revealRatio: 1 } : m,
              ),
              activeSubtitleMessageId: null as string | null,
            }
          : {};
      return {
        audioQueue: rest,
        playingRole: rest[0]?.role ?? null,
        ...done,
      };
    }),
  beginSubtitle: (audioId) =>
    set((state) => {
      const clip = state.audioQueue.find((c) => c.audioId === audioId);
      const messageId =
        clip?.messageId ?? state.transcript.find((m) => m.audioId === audioId)?.id ?? null;
      if (!messageId) {
        return {
          playingRole: clip?.role ?? state.playingRole,
          activeSubtitleMessageId: null,
        };
      }
      return {
        playingRole: clip?.role ?? state.playingRole,
        activeSubtitleMessageId: messageId,
        statusMessage: `${clip?.speaker ?? 'Agent'} is speaking…`,
        transcript: state.transcript.map((m) =>
          m.id === messageId ? { ...m, revealRatio: Math.max(m.revealRatio ?? 0, 0.02) } : m,
        ),
      };
    }),
  updateSubtitleProgress: (ratio) =>
    set((state) => {
      const id = state.activeSubtitleMessageId;
      if (!id) return state;
      const clamped = Math.min(1, Math.max(0, ratio));
      return {
        transcript: state.transcript.map((m) => (m.id === id ? { ...m, revealRatio: clamped } : m)),
      };
    }),
  finishSubtitle: () =>
    set((state) => {
      const id = state.activeSubtitleMessageId;
      if (!id) return { activeSubtitleMessageId: null, statusMessage: null };
      return {
        activeSubtitleMessageId: null,
        statusMessage: null,
        transcript: state.transcript.map((m) => (m.id === id ? { ...m, revealRatio: 1 } : m)),
      };
    }),
  revealAllPending: () =>
    set((state) => ({
      activeSubtitleMessageId: null,
      transcript: state.transcript.map((m) =>
        (m.revealRatio ?? 1) < 1 ? { ...m, revealRatio: 1 } : m,
      ),
    })),
  revealOrphanMessage: () =>
    set((state) => {
      const idx = state.transcript.findIndex((m) => (m.revealRatio ?? 1) <= 0 && !m.audioId);
      if (idx < 0) return state;
      return {
        transcript: state.transcript.map((m, i) => (i === idx ? { ...m, revealRatio: 1 } : m)),
      };
    }),
  clearAudio: () =>
    set({
      audioQueue: [],
      playingRole: null,
      activeSubtitleMessageId: null,
    }),
  startStreamingSession: ({
    debateId,
    topic,
    mood,
    language,
    totalRounds,
    provider,
    model,
    participantCount,
    participants,
    ttsEnabled,
    newsArticles,
  }) =>
    set({
      debateId,
      topic,
      mood: mood as DebateMood,
      language: language ?? DEFAULT_LANGUAGE,
      participantCount: participantCount ?? DEFAULT_PARTICIPANT_COUNT,
      participants:
        participants && participants.length > 0
          ? participants
          : guestsForCount(participantCount ?? DEFAULT_PARTICIPANT_COUNT),
      transcript: [],
      summary: null,
      streamingDraft: null,
      audioQueue: [],
      playingRole: null,
      activeSubtitleMessageId: null,
      ttsEnabled: Boolean(ttsEnabled),
      streaming: true,
      loading: false,
      error: null,
      statusMessage: 'Show is live…',
      metadata: {
        provider: provider ?? 'unknown',
        model: model ?? 'unknown',
        totalRounds,
        createdAt: new Date().toISOString(),
      },
      newsArticles: newsArticles ?? [],
    }),
  beginTurn: ({ role, speaker, roundNumber }) =>
    set((state) => ({
      streamingDraft: { role, speaker, roundNumber, content: '' },
      streaming: true,
      statusMessage: state.ttsEnabled ? `${speaker} is preparing…` : `${speaker} is generating…`,
    })),
  appendToken: (delta) => {
    const draft = get().streamingDraft;
    if (!draft) return;
    // Tokens are still collected for the completed message, but with TTS
    // the arena does not display the draft (subtitle sync instead).
    set({
      streamingDraft: { ...draft, content: draft.content + delta },
    });
  },
  completeMessage: (message) =>
    set((state) => {
      const withMeta: DebateMessage = {
        ...message,
        id: message.id ?? nextMessageId(),
        revealRatio: state.ttsEnabled ? 0 : 1,
      };
      return {
        transcript: [...state.transcript, withMeta],
        streamingDraft: null,
        statusMessage: state.ttsEnabled ? 'Cueing speech…' : null,
      };
    }),
  completeDebate: ({ summary, metadata, transcript }) =>
    set((state) => {
      // Keep client transcript (with reveal state) while audio may still play.
      // Only fall back to server transcript when TTS is off.
      const nextTranscript =
        state.ttsEnabled && state.transcript.length > 0
          ? state.transcript
          : (transcript ?? state.transcript).map((m) => ({
              ...m,
              id: m.id ?? nextMessageId(),
              revealRatio: 1,
            }));

      const stillPlaying = state.ttsEnabled && state.audioQueue.length > 0;

      return {
        summary,
        metadata,
        transcript: stillPlaying
          ? nextTranscript
          : nextTranscript.map((m) => ({ ...m, revealRatio: 1 })),
        streamingDraft: null,
        streaming: false,
        loading: false,
        statusMessage: stillPlaying ? state.statusMessage : null,
        activeSubtitleMessageId: stillPlaying ? state.activeSubtitleMessageId : null,
      };
    }),
  setPaused: (paused: boolean) => set({ paused }),
  setPlaybackSpeed: (playbackSpeed) => set({ playbackSpeed }),
  stopDebate: () =>
    set((state) => ({
      audioQueue: [],
      playingRole: null,
      activeSubtitleMessageId: null,
      streaming: false,
      loading: false,
      paused: false,
      statusMessage: 'Show stopped.',
      transcript: state.transcript.map((m) => ({ ...m, revealRatio: 1 })),
    })),
  reset: () =>
    set((state) => ({
      ...initialState,
      playbackSpeed: state.playbackSpeed,
    })),
}));
