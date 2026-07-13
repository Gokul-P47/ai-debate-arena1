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

export const DEBATE_LANGUAGES: { value: string; label: string }[] = [
  { value: 'en', label: 'English' },
  { value: 'ta', label: 'Tamil' },
  { value: 'hi', label: 'Hindi' },
  { value: 'te', label: 'Telugu' },
  { value: 'ml', label: 'Malayalam' },
  { value: 'kn', label: 'Kannada' },
];

export const DEFAULT_LANGUAGE = 'en';
export const DEFAULT_ROUNDS = 3;
export const MIN_ROUNDS = 1;
export const MAX_ROUNDS = 10;

export const AGENTS = {
  support: {
    id: 'agent-a',
    name: 'Support',
    role: 'support' as const,
    label: 'For the motion',
  },
  opposition: {
    id: 'agent-b',
    name: 'Opposition',
    role: 'opposition' as const,
    label: 'Against the motion',
  },
};
