/** Agent panel displaying debate messages for one speaker. */

import { DebateMessage } from '@/components/debate/DebateMessage';
import type { AgentInfo, AgentRole, DebateMessage as DebateMessageType } from '@/types/debate';

interface AgentPanelProps {
  agent: AgentInfo;
  messages?: DebateMessageType[];
  placeholder?: string;
  speaking?: boolean;
  streaming?: boolean;
  latestKey?: string | null;
  compact?: boolean;
}

const roleStyles: Record<
  AgentRole,
  {
    header: string;
    badge: string;
    glow: string;
    variant: AgentRole;
  }
> = {
  host: {
    header: 'from-amber-500/20 to-amber-800/10 border-amber-400/30',
    badge: 'bg-amber-500/20 text-amber-100',
    glow: 'shadow-[0_0_40px_-12px_rgba(251,191,36,0.45)]',
    variant: 'host',
  },
  support: {
    header: 'from-teal-500/20 to-teal-800/10 border-teal-400/30',
    badge: 'bg-teal-500/20 text-teal-100',
    glow: 'shadow-[0_0_40px_-12px_rgba(45,212,191,0.45)]',
    variant: 'support',
  },
  opposition: {
    header: 'from-rose-500/20 to-rose-900/10 border-rose-400/30',
    badge: 'bg-rose-500/20 text-rose-100',
    glow: 'shadow-[0_0_40px_-12px_rgba(251,113,133,0.4)]',
    variant: 'opposition',
  },
  guest3: {
    header: 'from-sky-500/20 to-sky-900/10 border-sky-400/30',
    badge: 'bg-sky-500/20 text-sky-100',
    glow: 'shadow-[0_0_40px_-12px_rgba(56,189,248,0.45)]',
    variant: 'guest3',
  },
  guest4: {
    header: 'from-violet-500/20 to-violet-900/10 border-violet-400/30',
    badge: 'bg-violet-500/20 text-violet-100',
    glow: 'shadow-[0_0_40px_-12px_rgba(167,139,250,0.45)]',
    variant: 'guest4',
  },
};

export function AgentPanel({
  agent,
  messages = [],
  placeholder = 'Waiting for the opening statement…',
  speaking = false,
  streaming = false,
  latestKey = null,
  compact = false,
}: AgentPanelProps) {
  const styles = roleStyles[agent.role];

  return (
    <div
      className={[
        'flex flex-col overflow-hidden rounded-xl border border-gray-800 bg-gray-900/70 transition-shadow duration-500',
        compact ? 'min-h-[160px]' : 'h-full min-h-[280px]',
        speaking ? styles.glow : '',
      ].join(' ')}
    >
      <div className={['border-b bg-gradient-to-r px-5 py-4', styles.header].join(' ')}>
        <div className="flex items-center justify-between gap-3">
          <div className="flex items-center gap-3">
            <span className="text-lg font-bold text-white">{agent.name}</span>
            <span
              className={['rounded-full px-2.5 py-0.5 text-xs font-medium', styles.badge].join(' ')}
            >
              {agent.label}
            </span>
          </div>
          {speaking && (
            <span className="flex items-center gap-1.5 text-xs font-semibold uppercase tracking-wider text-emerald-300">
              <span className="debate-live-dot h-2 w-2 rounded-full bg-emerald-400" />
              Speaking
            </span>
          )}
        </div>
      </div>

      <div className="flex flex-1 flex-col gap-3 overflow-y-auto p-4">
        {messages.length === 0 ? (
          <p className="flex flex-1 items-center justify-center text-sm italic text-gray-500">
            {placeholder}
          </p>
        ) : (
          messages.map((message, index) => {
            const key = `${message.role}-${message.roundNumber}-${index}`;
            const isLatest = key === latestKey;
            return (
              <DebateMessage
                key={key}
                message={message}
                variant={styles.variant}
                isLatest={isLatest}
                showCursor={Boolean(streaming && isLatest)}
              />
            );
          })
        )}
      </div>
    </div>
  );
}
