/** Talk-show studio: Host + N guests (2–4) with soft contradictions. */

'use client';

import { useEffect } from 'react';
import { Pause, Play, Square } from 'lucide-react';

import { AgentPanel } from '@/components/debate/AgentPanel';
import { DebateStage } from '@/components/debate/DebateStage';
import { useAudienceSounds } from '@/hooks/useAudienceSounds';
import { useDebate } from '@/hooks/useDebate';
import { useDebateAudio } from '@/hooks/useDebateAudio';
import { AGENTS, guestsForCount } from '@/lib/constants';
import { useDebateStore } from '@/store/debateStore';
import type { AgentRole, DebateMessage } from '@/types/debate';

function isVisibleMessage(message: DebateMessage, ttsEnabled: boolean): boolean {
  if (!ttsEnabled) return true;
  return (message.revealRatio ?? 1) > 0;
}

export function DebateArena() {
  useDebateAudio();
  const { paused, setPaused, stopDebate } = useDebate();

  const topic = useDebateStore((state) => state.topic);
  const transcript = useDebateStore((state) => state.transcript);
  const streamingDraft = useDebateStore((state) => state.streamingDraft);
  const loading = useDebateStore((state) => state.loading);
  const streaming = useDebateStore((state) => state.streaming);
  const statusMessage = useDebateStore((state) => state.statusMessage);
  const metadata = useDebateStore((state) => state.metadata);
  const debateId = useDebateStore((state) => state.debateId);
  const playingRole = useDebateStore((state) => state.playingRole);
  const ttsEnabled = useDebateStore((state) => state.ttsEnabled);
  const audioQueue = useDebateStore((state) => state.audioQueue);
  const participantCount = useDebateStore((state) => state.participantCount);
  const participants = useDebateStore((state) => state.participants);
  const activeSubtitleMessageId = useDebateStore((state) => state.activeSubtitleMessageId);
  const playbackSpeed = useDebateStore((state) => state.playbackSpeed);
  const setPlaybackSpeed = useDebateStore((state) => state.setPlaybackSpeed);

  useEffect(() => {
    if (loading || debateId) {
      const timer = setTimeout(() => {
        document.getElementById('debate-arena')?.scrollIntoView({
          behavior: 'smooth',
          block: 'start',
        });
      }, 100);
      return () => clearTimeout(timer);
    }
  }, [loading, debateId]);

  const speakingRole = ttsEnabled ? playingRole : (streamingDraft?.role ?? playingRole);
  useAudienceSounds(speakingRole);

  const guests = participants.length > 0 ? participants : guestsForCount(participantCount);

  const visibleTranscript = transcript.filter((m) => isVisibleMessage(m, ttsEnabled));

  const draftAsMessage = (role: AgentRole): DebateMessage[] => {
    if (ttsEnabled) return [];
    if (!streamingDraft || streamingDraft.role !== role || !streamingDraft.content) {
      return [];
    }
    return [
      {
        speaker: streamingDraft.speaker,
        role: streamingDraft.role,
        content: streamingDraft.content,
        timestamp: new Date().toISOString(),
        roundNumber: streamingDraft.roundNumber,
        revealRatio: 1,
      },
    ];
  };

  const displayFor = (role: AgentRole) => [
    ...visibleTranscript.filter((m) => m.role === role),
    ...draftAsMessage(role),
  ];

  const hostDisplay = displayFor('host');

  const roundFromAudio = audioQueue[0]?.roundNumber;
  const roundFromSubtitle = transcript.find((m) => m.id === activeSubtitleMessageId)?.roundNumber;
  const displayRound =
    roundFromSubtitle ??
    roundFromAudio ??
    streamingDraft?.roundNumber ??
    transcript[transcript.length - 1]?.roundNumber ??
    0;
  const totalRounds = metadata?.totalRounds ?? 0;
  const isLive = loading || streaming || audioQueue.length > 0 || playingRole !== null;

  const latestKeyFor = (role: AgentRole, display: DebateMessage[]) => {
    if (speakingRole !== role || display.length === 0) return null;
    const active = display[display.length - 1];
    if (!active) return null;
    return `${role}-${active.roundNumber}-${display.length - 1}`;
  };

  const subtitleStreaming = (role: AgentRole) =>
    ttsEnabled
      ? speakingRole === role && Boolean(activeSubtitleMessageId)
      : streamingDraft?.role === role;

  const guestGridClass =
    guests.length <= 2
      ? 'grid-cols-1 lg:grid-cols-2'
      : guests.length === 3
        ? 'grid-cols-1 md:grid-cols-2 lg:grid-cols-3'
        : 'grid-cols-1 md:grid-cols-2 lg:grid-cols-4';

  return (
    <section id="debate-arena" aria-label="Talk Show Studio" className="w-full scroll-mt-8">
      <div className="mb-8 text-center">
        <div className="mb-3 flex flex-wrap items-center justify-center gap-3">
          {isLive ? (
            paused ? (
              <span className="inline-flex items-center gap-2 rounded-full border border-amber-500/30 bg-amber-500/10 px-3 py-1 text-xs font-bold uppercase tracking-[0.2em] text-amber-300 animate-pulse">
                Paused
              </span>
            ) : (
              <span className="inline-flex items-center gap-2 rounded-full border border-red-500/30 bg-red-500/10 px-3 py-1 text-xs font-bold uppercase tracking-[0.2em] text-red-300">
                <span className="debate-live-dot h-2 w-2 rounded-full bg-red-400" />
                On air
              </span>
            )
          ) : debateId ? (
            <span className="inline-flex items-center rounded-full border border-teal-500/30 bg-teal-500/10 px-3 py-1 text-xs font-bold uppercase tracking-[0.2em] text-teal-200">
              Wrap
            </span>
          ) : null}
          {isLive && (
            <div className="flex items-center gap-2">
              <button
                type="button"
                onClick={() => setPaused(!paused)}
                className="flex items-center justify-center gap-1.5 rounded-full border border-amber-500/30 bg-amber-500/10 px-3 py-1 text-xs font-medium text-amber-200 hover:bg-amber-500/25 transition-all focus:outline-none"
                title={paused ? 'Resume Show' : 'Pause Show'}
              >
                {paused ? (
                  <>
                    <Play className="h-3 w-3 fill-current" />
                    <span>Resume</span>
                  </>
                ) : (
                  <>
                    <Pause className="h-3 w-3 fill-current" />
                    <span>Pause</span>
                  </>
                )}
              </button>
              <button
                type="button"
                onClick={stopDebate}
                className="flex items-center justify-center gap-1.5 rounded-full border border-red-500/30 bg-red-500/10 px-3 py-1 text-xs font-medium text-red-300 hover:bg-red-500/25 transition-all focus:outline-none"
                title="Stop Show"
              >
                <Square className="h-2.5 w-2.5 fill-current" />
                <span>Stop</span>
              </button>
            </div>
          )}
          {ttsEnabled && isLive && (
            <div className="flex items-center gap-1.5 rounded-full border border-slate-800 bg-slate-900/60 p-0.5 text-xs shadow-inner">
              <span className="px-2.5 text-slate-400 font-medium select-none">Speed</span>
              <div className="flex items-center gap-1">
                {[1, 1.25, 1.5, 1.75, 2].map((speed) => (
                  <button
                    key={speed}
                    type="button"
                    onClick={() => setPlaybackSpeed(speed)}
                    className={`rounded-full px-2 py-0.5 text-[10px] font-semibold tracking-wider transition-all duration-200 focus:outline-none ${
                      playbackSpeed === speed
                        ? 'bg-amber-500 text-slate-950 font-extrabold shadow-sm shadow-amber-500/30'
                        : 'text-slate-400 hover:bg-slate-800 hover:text-slate-200'
                    }`}
                  >
                    {speed}x
                  </button>
                ))}
              </div>
            </div>
          )}
          {totalRounds > 0 && (
            <span className="rounded-full border border-white/10 bg-black/30 px-3 py-1 text-xs text-slate-300">
              Segment {Math.max(displayRound, isLive ? displayRound || 1 : displayRound)}/
              {totalRounds}
            </span>
          )}
          {ttsEnabled && playingRole && (
            <span className="rounded-full border border-amber-500/30 bg-amber-500/10 px-3 py-1 text-xs text-amber-200">
              Subtitles live
            </span>
          )}
        </div>

        <h2 className="font-display text-2xl font-semibold text-[#f8f1e3] sm:text-3xl">
          Studio Floor
        </h2>

        {topic ? (
          <p className="mx-auto mt-3 max-w-3xl text-base font-medium text-amber-50/90 sm:text-lg">
            “{topic}”
          </p>
        ) : (
          <p className="mt-2 text-sm text-slate-400">
            Hit Start Show — the Host opens, then guests chat
          </p>
        )}

        {metadata && (
          <p className="mt-2 text-xs text-slate-500">
            Powered by {metadata.provider} · {metadata.model}
            {ttsEnabled ? ' · ElevenLabs TTS' : ''}
          </p>
        )}

        {statusMessage && (
          <p className="mt-3 text-sm text-teal-200/90" role="status">
            {statusMessage}
          </p>
        )}
      </div>

      {loading && transcript.length === 0 && !streamingDraft && (
        <div className="mb-6 rounded-xl border border-amber-500/20 bg-amber-500/5 px-4 py-6 text-center">
          <p className="text-sm font-medium text-amber-100">Warming up the studio…</p>
          <p className="mt-1 text-xs text-slate-400">
            Guests take the couch — captions roll with the voice.
          </p>
        </div>
      )}

      <DebateStage speakingRole={speakingRole} isLive={isLive} />

      <div className="mb-4">
        <AgentPanel
          agent={AGENTS.host}
          messages={hostDisplay}
          speaking={speakingRole === 'host'}
          latestKey={latestKeyFor('host', hostDisplay)}
          streaming={subtitleStreaming('host')}
          compact
          placeholder={
            loading || streaming || audioQueue.length > 0
              ? 'Host is welcoming the room…'
              : 'Waiting for the Host to open the show…'
          }
        />
      </div>

      <div className={['relative grid min-h-[280px] gap-4', guestGridClass].join(' ')}>
        {guests.map((guest) => {
          const role = guest.role;
          const agent = AGENTS[role];
          const display = displayFor(role);
          return (
            <AgentPanel
              key={role}
              agent={agent}
              messages={display}
              speaking={speakingRole === role}
              latestKey={latestKeyFor(role, display)}
              streaming={subtitleStreaming(role)}
              placeholder={
                loading || streaming || audioQueue.length > 0
                  ? `${agent.name} is getting ready…`
                  : `Waiting for ${agent.name}…`
              }
            />
          );
        })}
      </div>
    </section>
  );
}
