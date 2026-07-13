/** Debate summary after the show completes. */

'use client';

import { FileText } from 'lucide-react';

import { Card } from '@/components/common/Card';
import { useDebateStore } from '@/store/debateStore';

export function DebateSummary() {
  const summary = useDebateStore((state) => state.summary);
  const streaming = useDebateStore((state) => state.streaming);
  const loading = useDebateStore((state) => state.loading);
  const transcript = useDebateStore((state) => state.transcript);

  const show = !!summary && !loading && !streaming && transcript.length > 0;

  if (!show || !summary) {
    return null;
  }

  return (
    <section aria-label="Debate Summary" className="w-full">
      <Card variant="gradient-border" padding="lg">
        <div className="flex items-start gap-4">
          <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-purple-500/20">
            <FileText className="h-5 w-5 text-purple-400" aria-hidden="true" />
          </div>
          <div className="min-w-0 flex-1">
            <h2 className="text-lg font-semibold text-white">Debate Summary</h2>
            {summary.text && (
              <p className="mt-2 whitespace-pre-wrap text-sm leading-relaxed text-gray-300">
                {summary.text}
              </p>
            )}

            <div className="mt-5 grid gap-4 sm:grid-cols-2">
              <div>
                <h3 className="text-xs font-semibold uppercase tracking-wide text-blue-300">
                  Support points
                </h3>
                <ul className="mt-2 list-disc space-y-1 pl-4 text-sm text-gray-300">
                  {summary.supportPoints.map((point) => (
                    <li key={point}>{point}</li>
                  ))}
                </ul>
              </div>
              <div>
                <h3 className="text-xs font-semibold uppercase tracking-wide text-purple-300">
                  Opposition points
                </h3>
                <ul className="mt-2 list-disc space-y-1 pl-4 text-sm text-gray-300">
                  {summary.oppositionPoints.map((point) => (
                    <li key={point}>{point}</li>
                  ))}
                </ul>
              </div>
            </div>
          </div>
        </div>
      </Card>
    </section>
  );
}
