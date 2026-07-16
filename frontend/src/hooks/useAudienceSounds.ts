/** Hook crowd reactions (clap / cheer) to debate playback lifecycle. */

'use client';

import { useEffect, useRef } from 'react';

import {
  playApplause,
  playCheer,
  playCrowdMurmur,
  unlockAudienceAudio,
} from '@/lib/audienceSounds';
import { useDebateStore } from '@/store/debateStore';
import type { AgentRole } from '@/types/debate';

/**
 * Plays audience sounds as agents finish speaking, rounds change, and the show ends.
 * Call `prime()` from a user gesture (Start Debate) so browsers allow audio.
 */
export function useAudienceSounds(speakingRole: AgentRole | null) {
  const streaming = useDebateStore((s) => s.streaming);
  const loading = useDebateStore((s) => s.loading);
  const debateId = useDebateStore((s) => s.debateId);
  const audioQueueLength = useDebateStore((s) => s.audioQueue.length);
  const transcriptLength = useDebateStore((s) => s.transcript.length);

  const prevSpeakingRef = useRef<AgentRole | null>(null);
  const cheeredOpenRef = useRef(false);
  const finalCheerRef = useRef(false);
  const primedRef = useRef(false);

  useEffect(() => {
    const prev = prevSpeakingRef.current;
    // Someone just finished speaking → clap
    if (prev && !speakingRole) {
      void playApplause('soft');
    }
    // Host starts → light cheer (except the very first open, handled below)
    if (speakingRole === 'host' && prev && prev !== 'host') {
      void playCheer('soft');
    }
    prevSpeakingRef.current = speakingRole;
  }, [speakingRole]);

  // Opening cheer once the debate goes live
  useEffect(() => {
    if (!debateId || cheeredOpenRef.current) return;
    if (loading || streaming || audioQueueLength > 0 || transcriptLength > 0) {
      cheeredOpenRef.current = true;
      void playCheer('soft');
      void playCrowdMurmur(0.9);
    }
  }, [debateId, loading, streaming, audioQueueLength, transcriptLength]);

  // Closing ovation when stream is done and nothing left to play
  useEffect(() => {
    if (!debateId || finalCheerRef.current) return;
    if (!streaming && !loading && audioQueueLength === 0 && !speakingRole && transcriptLength > 0) {
      finalCheerRef.current = true;
      void playApplause('full');
      void playCheer('full');
    }
  }, [debateId, streaming, loading, audioQueueLength, speakingRole, transcriptLength]);

  // Reset flags when the user starts a fresh debate
  useEffect(() => {
    if (!debateId) {
      cheeredOpenRef.current = false;
      finalCheerRef.current = false;
      prevSpeakingRef.current = null;
    }
  }, [debateId]);

  return {
    prime: async () => {
      if (primedRef.current) return;
      primedRef.current = true;
      await unlockAudienceAudio();
    },
  };
}
