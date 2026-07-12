/** Agent panel displaying debate messages for one side. */

import { DebateMessage } from '@/components/debate/DebateMessage';
import type { AgentInfo, DebateMessage as DebateMessageType } from '@/types/debate';

interface AgentPanelProps {
  agent: AgentInfo;
  messages?: DebateMessageType[];
  placeholder?: string;
}

const roleStyles = {
  support: {
    header: 'from-blue-500/20 to-blue-600/10 border-blue-500/30',
    badge: 'bg-blue-500/20 text-blue-300',
    variant: 'support' as const,
  },
  opposition: {
    header: 'from-purple-500/20 to-purple-600/10 border-purple-500/30',
    badge: 'bg-purple-500/20 text-purple-300',
    variant: 'opposition' as const,
  },
};

export function AgentPanel({
  agent,
  messages = [],
  placeholder = 'Waiting for debate to start...',
}: AgentPanelProps) {
  const styles = roleStyles[agent.role];

  return (
    <div className="flex h-full flex-col overflow-hidden rounded-xl border border-gray-800 bg-gray-900/60">
      <div
        className={[
          'border-b bg-gradient-to-r px-5 py-4',
          styles.header,
        ].join(' ')}
      >
        <div className="flex items-center gap-3">
          <span className="text-lg font-bold text-white">{agent.name}</span>
          <span
            className={[
              'rounded-full px-2.5 py-0.5 text-xs font-medium',
              styles.badge,
            ].join(' ')}
          >
            {agent.label}
          </span>
        </div>
      </div>

      <div className="flex flex-1 flex-col gap-3 overflow-y-auto p-4">
        {messages.length === 0 ? (
          <p className="flex flex-1 items-center justify-center text-sm italic text-gray-500">
            {placeholder}
          </p>
        ) : (
          messages.map((message, index) => (
            <DebateMessage
              key={`${message.agent}-${message.round}-${index}`}
              message={message}
              variant={styles.variant}
            />
          ))
        )}
      </div>
    </div>
  );
}
