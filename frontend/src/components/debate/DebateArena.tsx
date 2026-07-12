/** Debate arena with side-by-side agent panels. */

'use client';

import { AgentPanel } from '@/components/debate/AgentPanel';
import { AGENTS } from '@/lib/constants';
import { useDebateStore } from '@/store/debateStore';

export function DebateArena() {
  const messages = useDebateStore((state) => state.messages);

  const supportMessages = messages.filter((m) => m.agent.toLowerCase().includes('support'));
  const oppositionMessages = messages.filter((m) =>
    m.agent.toLowerCase().includes('opposition'),
  );

  return (
    <section aria-label="Debate Arena" className="w-full">
      <div className="mb-6 text-center">
        <h2 className="text-2xl font-bold text-white">Debate Arena</h2>
        <p className="mt-1 text-sm text-gray-400">
          Two AI agents will face off here once the debate begins
        </p>
      </div>

      <div className="grid min-h-[320px] grid-cols-1 gap-4 lg:grid-cols-2 lg:gap-6">
        <AgentPanel agent={AGENTS.support} messages={supportMessages} />
        <AgentPanel agent={AGENTS.opposition} messages={oppositionMessages} />
      </div>
    </section>
  );
}
