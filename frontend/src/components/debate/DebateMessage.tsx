/** Single debate message bubble (supports subtitle-synced reveal). */

import { revealTextByRatio } from '@/lib/subtitleReveal';
import type { AgentRole, DebateMessage as DebateMessageType } from '@/types/debate';

interface DebateMessageProps {
  message: DebateMessageType;
  variant?: AgentRole;
  isLatest?: boolean;
  showCursor?: boolean;
}

const variantStyles: Record<AgentRole, string> = {
  host: 'border-amber-400/30 bg-amber-500/10',
  support: 'border-teal-400/30 bg-teal-500/10',
  opposition: 'border-rose-400/30 bg-rose-500/10',
  guest3: 'border-sky-400/30 bg-sky-500/10',
  guest4: 'border-violet-400/30 bg-violet-500/10',
};

export function DebateMessage({
  message,
  variant = 'support',
  isLatest = false,
  showCursor = false,
}: DebateMessageProps) {
  const ratio = message.revealRatio ?? 1;
  const visible = revealTextByRatio(message.content, ratio);

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
        {visible}
        {showCursor && <span className="debate-stream-cursor ml-0.5 inline-block">▍</span>}
      </p>
    </article>
  );
}
