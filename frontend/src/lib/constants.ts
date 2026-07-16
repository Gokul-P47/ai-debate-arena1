/** Application-wide constants. */

import type { AgentRole, DebateMood } from '@/types/debate';

export const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000';

export const APP_NAME = 'AI Talk Show';

export const APP_TAGLINE =
  'A hilarious TV-style talk show — Host plus 2–4 guests sharing views, banter, and witty jokes.';

export const DEBATE_MOODS: { value: DebateMood; label: string }[] = [
  { value: 'MIXED', label: 'Friendly' },
  { value: 'FUN', label: 'Playful' },
  { value: 'SERIOUS', label: 'Thoughtful' },
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

/** Guest participants on the couch (Host is always extra). */
export const DEFAULT_PARTICIPANT_COUNT = 2;
export const MIN_PARTICIPANT_COUNT = 2;
export const MAX_PARTICIPANT_COUNT = 4;

/** Target spoken length for one guest turn (seconds). */
export const DEFAULT_TURN_SECONDS = 45;
export const MIN_TURN_SECONDS = 15;
export const MAX_TURN_SECONDS = 120;

export type GuestTheme = 'teal' | 'rose' | 'sky' | 'violet' | 'amber';

export interface ParticipantInfo {
  role: AgentRole;
  name: string;
  label: string;
  stance?: string;
  theme: GuestTheme;
}

export const AGENTS = {
  host: {
    id: 'agent-host',
    name: 'Host',
    role: 'host' as const,
    label: 'Show host',
    theme: 'amber' as const,
  },
  support: {
    id: 'agent-a',
    name: 'Dave',
    role: 'support' as const,
    label: 'Dave',
    theme: 'teal' as const,
  },
  opposition: {
    id: 'agent-b',
    name: 'Sarah',
    role: 'opposition' as const,
    label: 'Sarah',
    theme: 'rose' as const,
  },
  guest3: {
    id: 'agent-c',
    name: 'Winston',
    role: 'guest3' as const,
    label: 'Winston',
    theme: 'sky' as const,
  },
  guest4: {
    id: 'agent-d',
    name: 'Chloe',
    role: 'guest4' as const,
    label: 'Chloe',
    theme: 'violet' as const,
  },
};

/** Default couch lineup by count (Host not included). */
export const GUEST_ROSTER: ParticipantInfo[] = [
  AGENTS.support,
  AGENTS.opposition,
  AGENTS.guest3,
  AGENTS.guest4,
];

export function guestsForCount(count: number): ParticipantInfo[] {
  const n = Math.min(MAX_PARTICIPANT_COUNT, Math.max(MIN_PARTICIPANT_COUNT, count));
  return GUEST_ROSTER.slice(0, n);
}
