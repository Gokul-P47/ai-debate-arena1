/** Agent panel displaying debate messages for one side. */

import { DebateMessage } from '@/components/debate/DebateMessage';
import type { AgentInfo, DebateMessage as DebateMessageType } from '@/types/debate';

interface AgentPanelProps {
  agent: AgentInfo;
  messages?: DebateMessageType[];
  placeholder?: string;
  speaking?: boolean;
  streaming?: boolean;
  latestKey?: string | null;
}

const roleStyles = {
  support: {
    header: 'from-blue-500/25 to-blue-600/10 border-blue-500/40',
    badge: 'bg-blue-500/20 text-blue-300',
    glow: 'shadow-[0_0_40px_-12px_rgba(59,130,246,0.55)]',
    variant: 'support' as const,
  },
  opposition: {
    header: 'from-purple-500/25 to-purple-600/10 border-purple-500/40',
    badge: 'bg-purple-500/20 text-purple-300',
    glow: 'shadow-[0_0_40px_-12px_rgba(139,92,246,0.55)]',
    variant: 'opposition' as const,
  },
};

export function AgentPanel({
  agent,
  messages = [],
  placeholder = 'Waiting for the opening statement…',
  speaking = false,
  streaming = false,
  latestKey = null,
}: AgentPanelProps) {
  const styles = roleStyles[agent.role];

  return (
    <div
      className={[
        'flex h-full min-h-[280px] flex-col overflow-hidden rounded-xl border border-gray-800 bg-gray-900/70 transition-shadow duration-500',
        speaking ? styles.glow : '',
      ].join(' ')}
    >
      <div className={['border-b bg-gradient-to-r px-5 py-4', styles.header].join(' ')}>
        <div className="flex items-center justify-between gap-3">
          <div className="flex items-center gap-3">
            <span className="text-lg font-bold text-white">{agent.name}</span>
            <span className={['rounded-full px-2.5 py-0.5 text-xs font-medium', styles.badge].join(' ')}>
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
