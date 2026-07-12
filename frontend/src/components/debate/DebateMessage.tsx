/** Single debate message bubble. */

import type { DebateMessage as DebateMessageType } from '@/types/debate';

interface DebateMessageProps {
  message: DebateMessageType;
  variant?: 'support' | 'opposition';
}

const variantStyles = {
  support: 'border-blue-500/20 bg-blue-500/5',
  opposition: 'border-purple-500/20 bg-purple-500/5',
};

export function DebateMessage({ message, variant = 'support' }: DebateMessageProps) {
  return (
    <div
      className={[
        'rounded-lg border px-4 py-3 text-sm leading-relaxed text-gray-300',
        variantStyles[variant],
      ].join(' ')}
    >
      <div className="mb-1 flex items-center justify-between gap-2">
        <span className="text-xs font-semibold uppercase tracking-wide text-gray-400">
          {message.agent}
        </span>
        <span className="text-xs text-gray-500">Round {message.round}</span>
      </div>
      <p>{message.content}</p>
    </div>
  );
}
