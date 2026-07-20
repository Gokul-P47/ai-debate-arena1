/** Show recap after the talk show completes. */

'use client';

import { FileText } from 'lucide-react';

import { Card } from '@/components/common/Card';
import { AGENTS } from '@/lib/constants';
import { useDebateStore } from '@/store/debateStore';
import type { AgentRole } from '@/types/debate';

const roleAccent: Record<AgentRole, string> = {
  host: 'text-amber-300',
  support: 'text-teal-300',
  opposition: 'text-rose-300',
  guest3: 'text-sky-300',
  guest4: 'text-violet-300',
};

interface ClaimDetail {
  id: string;
  claim: string;
  status: string;
  category: string;
  importance: number;
  confidence: number;
  challenged?: string;
  defended?: string;
}

interface ParticipantClaims {
  speaker: string;
  claims: ClaimDetail[];
}

function parseClaimsText(text: string): ParticipantClaims[] {
  const lines = text.split('\n');
  const participants: ParticipantClaims[] = [];
  let currentParticipant: ParticipantClaims | null = null;

  for (const line of lines) {
    const trimmed = line.trim();
    if (!trimmed) continue;

    // Check if it's a participant header (e.g. "Dave claims:" or "Sarah claims:")
    if (trimmed.endsWith('claims:')) {
      const speakerName = trimmed.replace('claims:', '').trim();
      currentParticipant = { speaker: speakerName, claims: [] };
      participants.push(currentParticipant);
      continue;
    }

    // Check if it's a claim line (starts with "- [")
    if (trimmed.startsWith('- [') && currentParticipant) {
      const claimRegex =
        /^-\s*\[([^\]]+)\]\s*(.*?)\s*\(([^,]+),\s*([^,]+),\s*importance=([^,)]+),\s*confidence=([^)]+)\)(?:\s*\|\s*(.*))?$/;
      const match = trimmed.match(claimRegex);
      if (match) {
        const [, id, claimText, status, category, importance, confidence, extrasStr] = match;

        let challenged: string | undefined;
        let defended: string | undefined;

        if (extrasStr) {
          const challengedMatch = extrasStr.match(/challenged=['"]([^'"]+)['"]/);
          if (challengedMatch) {
            challenged = challengedMatch[1];
          }
          const defendedMatch = extrasStr.match(/defended=['"]([^'"]+)['"]/);
          if (defendedMatch) {
            defended = defendedMatch[1];
          }
        }

        currentParticipant.claims.push({
          id,
          claim: claimText.trim(),
          status: status.trim(),
          category: category.trim(),
          importance: parseFloat(importance),
          confidence: parseFloat(confidence),
          challenged,
          defended,
        });
      } else {
        currentParticipant.claims.push({
          id: '',
          claim: trimmed.replace(/^-\s*/, ''),
          status: 'ACTIVE',
          category: '',
          importance: 0,
          confidence: 0,
        });
      }
    }
  }

  return participants;
}

export function DebateSummary() {
  const summary = useDebateStore((state) => state.summary);
  const streaming = useDebateStore((state) => state.streaming);
  const loading = useDebateStore((state) => state.loading);
  const transcript = useDebateStore((state) => state.transcript);

  const show = !!summary && !loading && !streaming && transcript.length > 0;

  if (!show || !summary) {
    return null;
  }

  const parsedParticipants = parseClaimsText(summary.text || '');

  const participantBlocks =
    summary.participants && summary.participants.length > 0
      ? summary.participants
      : [
          {
            role: 'support' as const,
            name: AGENTS.support.name,
            points: summary.supportPoints,
          },
          {
            role: 'opposition' as const,
            name: AGENTS.opposition.name,
            points: summary.oppositionPoints,
          },
        ];

  return (
    <section aria-label="Debate Summary" className="w-full">
      <Card variant="gradient-border" padding="lg">
        <div className="flex items-start gap-4">
          <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-amber-500/20">
            <FileText className="h-5 w-5 text-amber-300" aria-hidden="true" />
          </div>
          <div className="min-w-0 flex-1">
            <h2 className="font-display text-lg font-semibold text-[#f8f1e3]">Show recap</h2>

            {parsedParticipants.length > 0 ? (
              <div className="mt-4 space-y-5">
                {parsedParticipants.map((p) => (
                  <div
                    key={p.speaker}
                    className="rounded-xl border border-slate-800/60 bg-slate-900/25 p-4 shadow-sm"
                  >
                    <div className="flex items-center gap-2 border-b border-slate-800/40 pb-2 mb-3">
                      <span className="text-xs font-bold uppercase tracking-wider text-amber-200/90">
                        {p.speaker}
                      </span>
                      <span className="text-[10px] uppercase tracking-widest text-slate-500 font-semibold">
                        Stances & Memory
                      </span>
                    </div>
                    <div className="space-y-2.5">
                      {p.claims.map((c) => (
                        <div key={c.id || c.claim} className="text-sm">
                          <p className="text-slate-200 font-medium leading-relaxed pl-4 relative">
                            <span className="absolute left-0 text-amber-400 select-none">•</span>
                            {c.claim}
                          </p>
                        </div>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              summary.text && (
                <p className="mt-2 whitespace-pre-wrap text-sm leading-relaxed text-slate-300">
                  {summary.text}
                </p>
              )
            )}

            <div
              className={[
                'mt-5 grid gap-4',
                participantBlocks.length <= 2
                  ? 'sm:grid-cols-2'
                  : participantBlocks.length === 3
                    ? 'sm:grid-cols-2 lg:grid-cols-3'
                    : 'sm:grid-cols-2 lg:grid-cols-4',
              ].join(' ')}
            >
              {participantBlocks.map((block) => (
                <div key={block.role}>
                  <h3
                    className={[
                      'text-xs font-semibold uppercase tracking-wide',
                      roleAccent[block.role] ?? 'text-slate-300',
                    ].join(' ')}
                  >
                    {block.name} highlights
                  </h3>
                  <ul className="mt-2 list-disc space-y-1 pl-4 text-sm text-slate-300">
                    {block.points.map((point) => (
                      <li key={point}>{point}</li>
                    ))}
                  </ul>
                </div>
              ))}
            </div>
          </div>
        </div>
      </Card>
    </section>
  );
}
