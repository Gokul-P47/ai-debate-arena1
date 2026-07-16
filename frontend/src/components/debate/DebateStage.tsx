/** TV talk-show stage: Host + 2–4 couch guests. */

'use client';

import { DebateCharacter, type CharacterPose } from '@/components/debate/DebateCharacter';
import { AGENTS, guestsForCount } from '@/lib/constants';
import { getCurrentSubtitle } from '@/lib/subtitleReveal';
import { useDebateStore } from '@/store/debateStore';
import type { AgentRole } from '@/types/debate';

interface DebateStageProps {
  speakingRole: AgentRole | null;
  isLive: boolean;
}

function poseFor(role: AgentRole, speakingRole: AgentRole | null): CharacterPose {
  if (speakingRole === role) return 'speaking';
  if (speakingRole && speakingRole !== role) return 'listening';
  return 'idle';
}

/** Host sits in the middle of the couch lineup. */
function stageLineup(guestRoles: AgentRole[]) {
  const mid = Math.floor(guestRoles.length / 2);
  return [
    ...guestRoles.slice(0, mid).map((role) => AGENTS[role]),
    AGENTS.host,
    ...guestRoles.slice(mid).map((role) => AGENTS[role]),
  ];
}

export function DebateStage({ speakingRole, isLive }: DebateStageProps) {
  const participantCount = useDebateStore((s) => s.participantCount);
  const participants = useDebateStore((s) => s.participants);
  const activeSubtitleMessageId = useDebateStore((s) => s.activeSubtitleMessageId);
  const transcript = useDebateStore((s) => s.transcript);
  const streamingDraft = useDebateStore((s) => s.streamingDraft);
  const ttsEnabled = useDebateStore((s) => s.ttsEnabled);
  const paused = useDebateStore((s) => s.paused);

  const getSubtitleFor = (role: AgentRole): string => {
    if (speakingRole !== role) return '';

    if (ttsEnabled) {
      if (!activeSubtitleMessageId) return '';
      const msg = transcript.find((m) => m.id === activeSubtitleMessageId);
      if (!msg || msg.role !== role) return '';
      return getCurrentSubtitle(msg.content, msg.revealRatio ?? 0);
    } else {
      if (!streamingDraft || streamingDraft.role !== role) return '';
      return getCurrentSubtitle(streamingDraft.content, 1);
    }
  };

  const guestRoles =
    participants.length > 0
      ? participants.map((p) => p.role)
      : guestsForCount(participantCount).map((g) => g.role);

  const lineup = stageLineup(guestRoles);
  const colClass =
    lineup.length <= 3 ? 'grid-cols-3' : lineup.length === 4 ? 'grid-cols-4' : 'grid-cols-5';

  return (
    <div
      className={[
        'debate-stage debate-stage-tv relative mb-6 overflow-hidden',
        paused ? 'debate-stage--paused' : '',
      ].join(' ')}
      aria-label="Live talk-show studio"
    >
      <div className="pointer-events-none absolute inset-0 debate-stage-bg" aria-hidden />
      <div className="pointer-events-none absolute inset-0 debate-stage-curtains" aria-hidden />
      <div
        className="pointer-events-none absolute inset-x-0 bottom-0 h-24 debate-stage-floor"
        aria-hidden
      />
      <div
        className="pointer-events-none absolute left-1/2 top-0 h-40 w-[70%] -translate-x-1/2 debate-stage-spot"
        aria-hidden
      />

      <div
        className="pointer-events-none absolute inset-x-[8%] bottom-8 h-10 rounded-[2rem] bg-gradient-to-b from-slate-700/40 to-slate-900/70 sm:bottom-10"
        aria-hidden
      />

      <div
        className="pointer-events-none absolute inset-x-0 bottom-0 flex h-10 items-end justify-center gap-1 px-4 opacity-35"
        aria-hidden
      >
        {Array.from({ length: 18 }).map((_, i) => (
          <span
            key={i}
            className="debate-audience-head inline-block rounded-t-full bg-slate-800"
            style={{
              width: `${10 + (i % 3) * 3}px`,
              height: `${16 + (i % 4) * 4}px`,
              animationDelay: `${(i % 7) * 0.15}s`,
            }}
          />
        ))}
      </div>

      <div
        className={[
          'relative z-10 grid items-end gap-1 px-2 pb-54 pt-10 sm:gap-4 sm:px-6 sm:pb-40 sm:pt-12',
          colClass,
        ].join(' ')}
      >
        {lineup.map((agent) => (
          <DebateCharacter
            key={agent.role}
            role={agent.role}
            name={agent.name}
            label={agent.label}
            pose={poseFor(agent.role, speakingRole)}
            listenToward={speakingRole}
            lineupRoles={lineup.map((a) => a.role)}
            subtitle={getSubtitleFor(agent.role)}
          />
        ))}
      </div>

      <div className="pointer-events-none absolute left-3 top-3 flex items-center gap-2 sm:left-4 sm:top-4">
        {isLive ? (
          <span className="inline-flex items-center gap-1.5 rounded-sm bg-red-600 px-2 py-0.5 text-[10px] font-bold uppercase tracking-[0.2em] text-white shadow">
            <span className="debate-live-dot h-1.5 w-1.5 rounded-full bg-white" />
            On air
          </span>
        ) : (
          <span className="rounded-sm border border-white/15 bg-black/40 px-2 py-0.5 text-[10px] font-semibold uppercase tracking-[0.18em] text-slate-300">
            Studio
          </span>
        )}
      </div>
    </div>
  );
}
