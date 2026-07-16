/** FIFO audio playback with subtitle-synced text reveal. */

'use client';

import { useEffect, useRef } from 'react';

import { API_BASE_URL } from '@/lib/constants';
import { useDebateStore } from '@/store/debateStore';
import type { AudioClip } from '@/types/debate';

function resolveAudioUrl(clip: AudioClip): string {
  if (clip.audioUrl.startsWith('http://') || clip.audioUrl.startsWith('https://')) {
    return clip.audioUrl;
  }
  return `${API_BASE_URL}${clip.audioUrl}`;
}

/**
 * Plays queued `audio_ready` clips in order and reveals transcript text
 * in sync with playback (subtitle style).
 */
export function useDebateAudio() {
  const audioQueue = useDebateStore((s) => s.audioQueue);
  const playingRole = useDebateStore((s) => s.playingRole);
  const paused = useDebateStore((s) => s.paused);
  const playbackSpeed = useDebateStore((s) => s.playbackSpeed);
  const audioRef = useRef<HTMLAudioElement | null>(null);
  const playingIdRef = useRef<string | null>(null);

  useEffect(() => {
    const audio = new Audio();
    audioRef.current = audio;

    const onTimeUpdate = () => {
      const duration = audio.duration;
      if (!Number.isFinite(duration) || duration <= 0) return;
      const ratio = Math.min(1, audio.currentTime / duration);
      useDebateStore.getState().updateSubtitleProgress(ratio);
    };

    const onEnded = () => {
      playingIdRef.current = null;
      useDebateStore.getState().finishSubtitle();
      useDebateStore.getState().advanceAudioQueue();
    };

    const onError = () => {
      playingIdRef.current = null;
      useDebateStore.getState().finishSubtitle();
      useDebateStore.getState().advanceAudioQueue();
    };

    audio.addEventListener('timeupdate', onTimeUpdate);
    audio.addEventListener('ended', onEnded);
    audio.addEventListener('error', onError);

    return () => {
      audio.removeEventListener('timeupdate', onTimeUpdate);
      audio.removeEventListener('ended', onEnded);
      audio.removeEventListener('error', onError);
      audio.pause();
      audioRef.current = null;
      playingIdRef.current = null;
    };
  }, []);

  // Update speed of currently playing audio when playbackSpeed changes
  useEffect(() => {
    const audio = audioRef.current;
    if (audio) {
      audio.defaultPlaybackRate = playbackSpeed;
      audio.playbackRate = playbackSpeed;
    }
  }, [playbackSpeed]);

  useEffect(() => {
    const audio = audioRef.current;
    if (!audio) return;

    if (paused) {
      if (!audio.paused) audio.pause();
      return;
    }

    const next = audioQueue[0];
    if (!next) {
      if (!audio.paused) audio.pause();
      playingIdRef.current = null;
      if (playingRole !== null) {
        useDebateStore.getState().setPlayingRole(null);
      }
      // No more audio — show any text that never got a clip
      if (!useDebateStore.getState().streaming) {
        useDebateStore.getState().revealAllPending();
      }
      return;
    }

    if (playingIdRef.current === next.audioId) {
      if (audio.paused) {
        audio.defaultPlaybackRate = playbackSpeed;
        audio.playbackRate = playbackSpeed;
        void audio.play().catch(() => {
          playingIdRef.current = null;
          useDebateStore.getState().finishSubtitle();
          useDebateStore.getState().advanceAudioQueue();
        });
      }
      return;
    }

    playingIdRef.current = next.audioId;
    useDebateStore.getState().beginSubtitle(next.audioId);
    audio.src = resolveAudioUrl(next);
    audio.defaultPlaybackRate = playbackSpeed;
    audio.playbackRate = playbackSpeed;
    void audio.play().catch(() => {
      playingIdRef.current = null;
      useDebateStore.getState().finishSubtitle();
      useDebateStore.getState().advanceAudioQueue();
    });
  }, [audioQueue, playingRole, paused, playbackSpeed]);
}
