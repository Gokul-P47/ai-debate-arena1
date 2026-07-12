/** Debate summary section — placeholder for future implementation. */

'use client';

import { FileText } from 'lucide-react';

import { Card } from '@/components/common/Card';
import { useDebateStore } from '@/store/debateStore';

export function DebateSummary() {
  const summary = useDebateStore((state) => state.summary);

  if (!summary) {
    return null;
  }

  return (
    <section aria-label="Debate Summary" className="w-full">
      <Card variant="gradient-border" padding="lg">
        <div className="flex items-start gap-4">
          <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-purple-500/20">
            <FileText className="h-5 w-5 text-purple-400" aria-hidden="true" />
          </div>
          <div>
            <h2 className="text-lg font-semibold text-white">Debate Summary</h2>
            <p className="mt-2 text-sm leading-relaxed text-gray-300">{summary}</p>
          </div>
        </div>
      </Card>
    </section>
  );
}
