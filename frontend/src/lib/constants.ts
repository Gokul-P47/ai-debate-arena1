/** Application-wide constants. */

import type { DebateMood } from '@/types/debate';

export const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000';

export const APP_NAME = 'AI Debate Arena';

export const APP_TAGLINE =
  'Watch two AI agents debate opposite sides of any topic.';

export const DEBATE_MOODS: { value: DebateMood; label: string }[] = [
  { value: 'SERIOUS', label: 'Serious' },
  { value: 'FUN', label: 'Fun' },
  { value: 'MIXED', label: 'Mixed' },
];

export const DEFAULT_ROUNDS = 3;
export const MIN_ROUNDS = 1;
export const MAX_ROUNDS = 10;

export const PLACEHOLDER_MESSAGE =
  'Debate generation will be implemented in the next phase.';

export const AGENTS = {
  support: {
    id: 'agent-a',
    name: 'Agent A',
    role: 'support' as const,
    label: 'Support Agent',
  },
  opposition: {
    id: 'agent-b',
    name: 'Agent B',
    role: 'opposition' as const,
    label: 'Opposition Agent',
  },
};
