/** Single debate message bubble. */

import type { DebateMessage as DebateMessageType } from '@/types/debate';

interface DebateMessageProps {
  message: DebateMessageType;
  variant?: 'support' | 'opposition';
  isLatest?: boolean;
  showCursor?: boolean;
}

const variantStyles = {
  support: 'border-blue-500/30 bg-blue-500/10',
  opposition: 'border-purple-500/30 bg-purple-500/10',
};

export function DebateMessage({
  message,
  variant = 'support',
  isLatest = false,
  showCursor = false,
}: DebateMessageProps) {
  return (
    <article
      className={[
        'rounded-lg border px-4 py-3 text-sm leading-relaxed text-gray-200',
        !showCursor ? 'debate-message-enter' : '',
        variantStyles[variant],
        isLatest ? 'ring-1 ring-white/20' : '',
      ].join(' ')}
    >
      <div className="mb-2 flex items-center justify-between gap-2">
        <span className="text-xs font-semibold uppercase tracking-wide text-gray-400">
          {message.speaker}
        </span>
        <span className="text-xs text-gray-500">Round {message.roundNumber}</span>
      </div>
      <p className="whitespace-pre-wrap">
        {message.content}
        {showCursor && <span className="debate-stream-cursor ml-0.5 inline-block">▍</span>}
      </p>
    </article>
  );
}
