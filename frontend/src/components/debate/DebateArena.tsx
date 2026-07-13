/** Debate arena staged as a live debate show with token streaming. */

'use client';

import { AgentPanel } from '@/components/debate/AgentPanel';
import { AGENTS } from '@/lib/constants';
import { useDebateStore } from '@/store/debateStore';
import type { DebateMessage } from '@/types/debate';

export function DebateArena() {
  const topic = useDebateStore((state) => state.topic);
  const transcript = useDebateStore((state) => state.transcript);
  const streamingDraft = useDebateStore((state) => state.streamingDraft);
  const loading = useDebateStore((state) => state.loading);
  const streaming = useDebateStore((state) => state.streaming);
  const statusMessage = useDebateStore((state) => state.statusMessage);
  const metadata = useDebateStore((state) => state.metadata);
  const debateId = useDebateStore((state) => state.debateId);

  const supportMessages = transcript.filter((m) => m.role === 'support');
  const oppositionMessages = transcript.filter((m) => m.role === 'opposition');

  const draftAsMessage = (role: 'support' | 'opposition'): DebateMessage[] => {
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
      },
    ];
  };

  const supportDisplay = [...supportMessages, ...draftAsMessage('support')];
  const oppositionDisplay = [...oppositionMessages, ...draftAsMessage('opposition')];

  const currentRound =
    streamingDraft?.roundNumber ??
    transcript[transcript.length - 1]?.roundNumber ??
    0;
  const totalRounds = metadata?.totalRounds ?? 0;
  const isLive = loading || streaming;
  const speakingRole = streamingDraft?.role ?? null;

  const latestSupportKey =
    speakingRole === 'support'
      ? `support-${streamingDraft?.roundNumber}-${supportDisplay.length - 1}`
      : null;
  const latestOppositionKey =
    speakingRole === 'opposition'
      ? `opposition-${streamingDraft?.roundNumber}-${oppositionDisplay.length - 1}`
      : null;

  return (
    <section id="debate-arena" aria-label="Debate Arena" className="w-full scroll-mt-8">
      <div className="mb-8 text-center">
        <div className="mb-3 flex flex-wrap items-center justify-center gap-3">
          {isLive ? (
            <span className="inline-flex items-center gap-2 rounded-full border border-red-500/30 bg-red-500/10 px-3 py-1 text-xs font-bold uppercase tracking-[0.2em] text-red-300">
              <span className="debate-live-dot h-2 w-2 rounded-full bg-red-400" />
              Live
            </span>
          ) : debateId ? (
            <span className="inline-flex items-center rounded-full border border-emerald-500/30 bg-emerald-500/10 px-3 py-1 text-xs font-bold uppercase tracking-[0.2em] text-emerald-300">
              Complete
            </span>
          ) : null}
          {totalRounds > 0 && (
            <span className="rounded-full border border-gray-700 bg-gray-900/80 px-3 py-1 text-xs text-gray-300">
              Round {Math.max(currentRound, isLive ? currentRound || 1 : currentRound)}/{totalRounds}
            </span>
          )}
        </div>

        <h2 className="text-2xl font-bold text-white sm:text-3xl">Debate Arena</h2>

        {topic ? (
          <p className="mx-auto mt-3 max-w-3xl text-base font-medium text-blue-100/90 sm:text-lg">
            “{topic}”
          </p>
        ) : (
          <p className="mt-2 text-sm text-gray-400">
            Two AI agents will face off here once the debate begins
          </p>
        )}

        {metadata && (
          <p className="mt-2 text-xs text-gray-500">
            Powered by {metadata.provider} · {metadata.model}
          </p>
        )}

        {statusMessage && (
          <p className="mt-3 text-sm text-blue-300/90" role="status">
            {statusMessage}
          </p>
        )}
      </div>

      {loading && transcript.length === 0 && !streamingDraft && (
        <div className="mb-6 rounded-xl border border-blue-500/20 bg-blue-500/5 px-4 py-6 text-center">
          <p className="text-sm font-medium text-blue-200">Connecting to the debate stream…</p>
          <p className="mt-1 text-xs text-gray-400">
            Tokens will appear live as each agent speaks.
          </p>
        </div>
      )}

      <div className="relative grid min-h-[320px] grid-cols-1 gap-4 lg:grid-cols-[1fr_auto_1fr] lg:items-stretch lg:gap-0">
        <AgentPanel
          agent={AGENTS.support}
          messages={supportDisplay}
          speaking={speakingRole === 'support'}
          latestKey={latestSupportKey}
          streaming={speakingRole === 'support'}
          placeholder={
            loading || streaming
              ? 'Waiting for Support to take the floor…'
              : 'Waiting for the opening statement…'
          }
        />

        <div className="flex items-center justify-center lg:px-4">
          <div className="flex h-14 w-14 items-center justify-center rounded-full border border-white/10 bg-gradient-to-br from-blue-500/30 to-purple-500/30 text-sm font-black tracking-widest text-white shadow-lg shadow-black/40">
            VS
          </div>
        </div>

        <AgentPanel
          agent={AGENTS.opposition}
          messages={oppositionDisplay}
          speaking={speakingRole === 'opposition'}
          latestKey={latestOppositionKey}
          streaming={speakingRole === 'opposition'}
          placeholder={
            loading || streaming ? 'Waiting to rebut…' : 'Waiting to rebut…'
          }
        />
      </div>
    </section>
  );
}
