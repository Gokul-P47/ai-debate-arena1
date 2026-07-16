/** Premium cartoon-style talk-show character with speaking / listening / idle animations. */

'use client';

import type { AgentRole } from '@/types/debate';

export type CharacterPose = 'idle' | 'speaking' | 'listening';

interface DebateCharacterProps {
  role: AgentRole;
  name: string;
  label: string;
  pose: CharacterPose;
  /** Who they lean toward while listening. */
  listenToward?: AgentRole | null;
  /** Full left-to-right stage order (for lean direction). */
  lineupRoles?: AgentRole[];
  /** Subtitle to show below the active speaker. */
  subtitle?: string;
}

const roleTheme: Record<AgentRole, { accent: string; suit: string; badge: string }> = {
  host: {
    accent: '#fbbf24',
    suit: '#1e293b',
    badge: 'text-amber-100 bg-amber-500/15 border-amber-400/30',
  },
  support: {
    accent: '#2dd4bf',
    suit: '#134e4a',
    badge: 'text-teal-100 bg-teal-500/15 border-teal-400/30',
  },
  opposition: {
    accent: '#fb7185',
    suit: '#4c0519',
    badge: 'text-rose-100 bg-rose-500/15 border-rose-400/30',
  },
  guest3: {
    accent: '#38bdf8',
    suit: '#0c4a6e',
    badge: 'text-sky-100 bg-sky-500/15 border-sky-400/30',
  },
  guest4: {
    accent: '#a78bfa',
    suit: '#2e1065',
    badge: 'text-violet-100 bg-violet-500/15 border-violet-400/30',
  },
};

function leanClass(
  pose: CharacterPose,
  role: AgentRole,
  listenToward: AgentRole | null,
  lineupRoles: AgentRole[],
): string {
  if (pose === 'speaking') return 'debate-char--speaking';
  if (pose !== 'listening' || !listenToward) return 'debate-char--idle';

  const selfIdx = lineupRoles.indexOf(role);
  const towardIdx = lineupRoles.indexOf(listenToward);
  if (selfIdx < 0 || towardIdx < 0) return 'debate-char--idle';
  if (listenToward === 'host' && role !== 'host') return 'debate-char--listen-up';
  if (towardIdx < selfIdx) return 'debate-char--listen-left';
  if (towardIdx > selfIdx) return 'debate-char--listen-right';
  return 'debate-char--idle';
}

export function DebateCharacter({
  role,
  name,
  label,
  pose,
  listenToward = null,
  lineupRoles = [],
  subtitle,
}: DebateCharacterProps) {
  const theme = roleTheme[role];
  const speaking = pose === 'speaking';

  return (
    <div
      className={[
        'debate-char relative flex flex-col items-center',
        leanClass(pose, role, listenToward, lineupRoles),
        speaking ? 'debate-char-z' : '',
      ].join(' ')}
      data-role={role}
      data-pose={pose}
      aria-label={`${name} is ${pose}`}
    >
      {speaking && (
        <div
          className="pointer-events-none absolute -top-1 left-1/2 flex -translate-x-1/2 gap-1"
          aria-hidden
        >
          <span className="debate-sound-bar" style={{ animationDelay: '0ms' }} />
          <span className="debate-sound-bar" style={{ animationDelay: '120ms' }} />
          <span className="debate-sound-bar" style={{ animationDelay: '240ms' }} />
        </div>
      )}

      <div
        className={['debate-char-figure relative', speaking ? 'debate-char-figure--hot' : ''].join(
          ' ',
        )}
        style={{ ['--char-accent' as string]: theme.accent }}
      >
        <svg viewBox="0 0 120 160" className="h-32 w-24 sm:h-44 sm:w-32" aria-hidden>
          <defs>
            {/* Skin Gradient */}
            <radialGradient id="skinGrad" cx="50%" cy="30%" r="70%">
              <stop offset="0%" stopColor="#ffebd3" />
              <stop offset="70%" stopColor="#f7d0a8" />
              <stop offset="100%" stopColor="#e5ba95" />
            </radialGradient>

            {/* Suit/Clothes Gradients */}
            <linearGradient id="hostSuit" x1="0%" y1="0%" x2="0%" y2="100%">
              <stop offset="0%" stopColor="#2e3a4e" />
              <stop offset="100%" stopColor="#18202c" />
            </linearGradient>
            <linearGradient id="daveSuit" x1="0%" y1="0%" x2="0%" y2="100%">
              <stop offset="0%" stopColor="#14b8a6" />
              <stop offset="100%" stopColor="#0f766e" />
            </linearGradient>
            <linearGradient id="sarahSuit" x1="0%" y1="0%" x2="0%" y2="100%">
              <stop offset="0%" stopColor="#f43f5e" />
              <stop offset="100%" stopColor="#be123c" />
            </linearGradient>
            <linearGradient id="winstonSuit" x1="0%" y1="0%" x2="0%" y2="100%">
              <stop offset="0%" stopColor="#0ea5e9" />
              <stop offset="100%" stopColor="#0369a1" />
            </linearGradient>
            <linearGradient id="chloeSuit" x1="0%" y1="0%" x2="0%" y2="100%">
              <stop offset="0%" stopColor="#8b5cf6" />
              <stop offset="100%" stopColor="#5b21b6" />
            </linearGradient>

            {/* Hair Gradients */}
            <linearGradient id="hairHost" x1="0%" y1="0%" x2="0%" y2="100%">
              <stop offset="0%" stopColor="#3f3730" />
              <stop offset="100%" stopColor="#1c1917" />
            </linearGradient>
            <linearGradient id="hairDave" x1="0%" y1="0%" x2="0%" y2="100%">
              <stop offset="0%" stopColor="#582f0e" />
              <stop offset="100%" stopColor="#292524" />
            </linearGradient>
            <linearGradient id="hairSarah" x1="0%" y1="0%" x2="0%" y2="100%">
              <stop offset="0%" stopColor="#fbbf24" />
              <stop offset="100%" stopColor="#d97706" />
            </linearGradient>
            <linearGradient id="hairWinston" x1="0%" y1="0%" x2="0%" y2="100%">
              <stop offset="0%" stopColor="#52525b" />
              <stop offset="100%" stopColor="#1e293b" />
            </linearGradient>
            <linearGradient id="hairChloe" x1="0%" y1="0%" x2="0%" y2="100%">
              <stop offset="0%" stopColor="#ec4899" />
              <stop offset="100%" stopColor="#9d174d" />
            </linearGradient>
          </defs>

          {/* Character Floor Shadow */}
          <ellipse cx="60" cy="152" rx="30" ry="5" fill="rgba(0,0,0,0.3)" />

          {/* Clothes (Body) Rendering per Persona */}
          {role === 'host' && (
            <g>
              <path
                d="M38 78 C38 58, 82 58, 82 78 L88 130 C88 138, 32 138, 32 130 Z"
                fill="url(#hostSuit)"
              />
              <path d="M48 74 L60 82 L72 74 L68 70 L60 76 L52 70 Z" fill="#ffffff" />
              <path d="M57 78 L60 115 L63 78 Z" fill="#fbbf24" />
              <circle cx="52" cy="95" r="1.8" fill="#fbbf24" />
              <circle cx="68" cy="95" r="1.8" fill="#fbbf24" />
              <circle cx="52" cy="107" r="1.8" fill="#fbbf24" />
              <circle cx="68" cy="107" r="1.8" fill="#fbbf24" />
            </g>
          )}

          {role === 'support' && (
            <g>
              <path
                d="M38 78 C38 58, 82 58, 82 78 L88 130 C88 138, 32 138, 32 130 Z"
                fill="url(#daveSuit)"
              />
              <path
                d="M46 72 Q60 86 74 72"
                stroke="#115e59"
                strokeWidth="4"
                fill="none"
                strokeLinecap="round"
              />
              <path d="M52 74 L60 82 L68 74 Z" fill="#f4f4f5" />
              <path
                d="M55 80 C55 90, 53 96, 53 98"
                stroke="#f4f4f5"
                strokeWidth="1.5"
                fill="none"
                strokeLinecap="round"
              />
              <path
                d="M65 80 C65 90, 67 96, 67 98"
                stroke="#f4f4f5"
                strokeWidth="1.5"
                fill="none"
                strokeLinecap="round"
              />
              <path
                d="M60 82 L60 130"
                stroke="#115e59"
                strokeWidth="2.5"
                strokeDasharray="3 2"
                fill="none"
              />
            </g>
          )}

          {role === 'opposition' && (
            <g>
              <path
                d="M38 78 C38 58, 82 58, 82 78 L88 130 C88 138, 32 138, 32 130 Z"
                fill="url(#sarahSuit)"
              />
              <path d="M46 72 C46 72, 60 92, 74 72 Z" fill="#1e1b4b" />
              <path d="M46 72 L54 78 L48 70 Z" fill="#ffffff" />
              <path d="M74 72 L66 78 L72 70 Z" fill="#ffffff" />
              <path d="M50 78 Q60 88 70 78" stroke="#fbbf24" strokeWidth="1.5" fill="none" />
              <circle cx="60" cy="85" r="2.5" fill="#fbbf24" />
            </g>
          )}

          {role === 'guest3' && (
            <g>
              <path
                d="M38 78 C38 58, 82 58, 82 78 L88 130 C88 138, 32 138, 32 130 Z"
                fill="url(#winstonSuit)"
              />
              <ellipse cx="60" cy="74" rx="14" ry="4" fill="#075985" />
              <path d="M50 71 L60 76 L70 71 L68 67 L60 71 L52 67 Z" fill="#ffffff" />
              <path
                d="M36 94 Q60 96 84 94"
                stroke="#075985"
                strokeWidth="2.5"
                fill="none"
                opacity="0.5"
              />
              <path
                d="M34 110 Q60 112 86 110"
                stroke="#075985"
                strokeWidth="2.5"
                fill="none"
                opacity="0.5"
              />
            </g>
          )}

          {role === 'guest4' && (
            <g>
              <path
                d="M38 78 C38 58, 82 58, 82 78 L88 130 C88 138, 32 138, 32 130 Z"
                fill="url(#chloeSuit)"
              />
              <ellipse cx="60" cy="74" rx="12" ry="3" fill="#4c1d95" />
              <polygon
                points="60,86 63,94 72,94 65,99 68,107 60,102 52,107 55,99 48,94 57,94"
                fill="#fde047"
              />
              <circle cx="44" cy="94" r="1.5" fill="#a78bfa" />
              <circle cx="76" cy="106" r="1.5" fill="#a78bfa" />
              <circle cx="46" cy="116" r="2" fill="#fde047" />
            </g>
          )}

          {/* Left Arm with Sleeve Cuff */}
          <g className="debate-char-arm debate-char-arm--left">
            <path
              d="M38 82 C28 90, 22 108, 26 122"
              stroke={
                role === 'host'
                  ? 'url(#hostSuit)'
                  : role === 'support'
                    ? 'url(#daveSuit)'
                    : role === 'opposition'
                      ? 'url(#sarahSuit)'
                      : role === 'guest3'
                        ? 'url(#winstonSuit)'
                        : 'url(#chloeSuit)'
              }
              strokeWidth="10"
              strokeLinecap="round"
              fill="none"
            />
            <path d="M23 118 L29 122" stroke="#ffffff" strokeWidth="12" strokeLinecap="round" />
            <circle cx="26" cy="124" r="6" fill="#fce3c7" />
          </g>

          {/* Right Arm with Sleeve Cuff */}
          <g className="debate-char-arm debate-char-arm--right">
            <path
              d="M82 82 C92 90, 98 108, 94 122"
              stroke={
                role === 'host'
                  ? 'url(#hostSuit)'
                  : role === 'support'
                    ? 'url(#daveSuit)'
                    : role === 'opposition'
                      ? 'url(#sarahSuit)'
                      : role === 'guest3'
                        ? 'url(#winstonSuit)'
                        : 'url(#chloeSuit)'
              }
              strokeWidth="10"
              strokeLinecap="round"
              fill="none"
            />
            <path d="M97 118 L91 122" stroke="#ffffff" strokeWidth="12" strokeLinecap="round" />
            <circle cx="94" cy="124" r="6" fill="#fce3c7" />
          </g>

          {/* Head & Persona Specific Features */}
          <g className="debate-char-head">
            {/* Base Skin Face */}
            <circle cx="60" cy="42" r="22" fill="url(#skinGrad)" />

            {/* Host Details */}
            {role === 'host' && (
              <g>
                <path
                  d="M38 40 C38 20, 82 20, 82 40 C75 30, 45 30, 38 40 Z"
                  fill="url(#hairHost)"
                />
                <path
                  d="M38 40 Q55 24 75 34 C65 32, 50 34, 38 40 Z"
                  fill="#312e81"
                  opacity="0.15"
                />
                <path
                  d="M46 33 Q52 31 58 33"
                  stroke="#120f0c"
                  strokeWidth="1.8"
                  fill="none"
                  strokeLinecap="round"
                />
                <path
                  d="M62 33 Q68 31 74 33"
                  stroke="#120f0c"
                  strokeWidth="1.8"
                  fill="none"
                  strokeLinecap="round"
                />
                <circle cx="52" cy="39" r="2.5" fill="#1e293b" />
                <circle cx="68" cy="39" r="2.5" fill="#1e293b" />
                <rect
                  x="42"
                  y="33"
                  width="16"
                  height="12"
                  rx="3"
                  stroke="#fbbf24"
                  strokeWidth="1.8"
                  fill="none"
                />
                <rect
                  x="62"
                  y="33"
                  width="16"
                  height="12"
                  rx="3"
                  stroke="#fbbf24"
                  strokeWidth="1.8"
                  fill="none"
                />
                <line x1="58" y1="39" x2="62" y2="39" stroke="#fbbf24" strokeWidth="2" />
              </g>
            )}

            {/* Dave (Support) Details */}
            {role === 'support' && (
              <g>
                <path
                  d="M36 44 C34 26, 86 26, 84 44 C72 32, 48 32, 36 44 Z"
                  fill="url(#hairDave)"
                />
                <path
                  d="M42 28 L46 20 L50 27 L54 18 L60 26 L66 18 L70 27 L74 20 L78 28 Z"
                  fill="url(#hairDave)"
                />
                <path
                  d="M45 32 Q51 28 57 32"
                  stroke="#292524"
                  strokeWidth="2"
                  fill="none"
                  strokeLinecap="round"
                />
                <path
                  d="M63 32 Q69 28 75 32"
                  stroke="#292524"
                  strokeWidth="2"
                  fill="none"
                  strokeLinecap="round"
                />
                <circle cx="52" cy="39" r="3.2" fill="#1e293b" />
                <circle cx="53.5" cy="37.5" r="1" fill="#ffffff" />
                <circle cx="68" cy="39" r="3.2" fill="#1e293b" />
                <circle cx="69.5" cy="37.5" r="1" fill="#ffffff" />
              </g>
            )}

            {/* Sarah (Opposition) Details */}
            {role === 'opposition' && (
              <g>
                <path
                  d="M36 44 C34 20, 86 20, 84 44 L86 58 C86 58, 80 50, 78 52 C74 42, 46 42, 42 52 C40 50, 34 58, 34 58 Z"
                  fill="url(#hairSarah)"
                />
                <path d="M37 38 Q50 28 65 36 C55 32, 45 32, 37 38 Z" fill="#ca8a04" />
                <path
                  d="M45 33 Q51 31 57 34"
                  stroke="#713f12"
                  strokeWidth="1.8"
                  fill="none"
                  strokeLinecap="round"
                />
                <path
                  d="M63 29 Q69 26 75 28"
                  stroke="#713f12"
                  strokeWidth="1.8"
                  fill="none"
                  strokeLinecap="round"
                />
                <circle cx="52" cy="39" r="2.8" fill="#0f172a" />
                <circle cx="68" cy="39" r="2.8" fill="#0f172a" />
                <circle cx="52" cy="39" r="8" stroke="#fda4af" strokeWidth="1.5" fill="none" />
                <circle cx="68" cy="39" r="8" stroke="#fda4af" strokeWidth="1.5" fill="none" />
                <line x1="60" y1="39" x2="60" y2="39" stroke="#fda4af" strokeWidth="2" />
              </g>
            )}

            {/* Winston (Guest 3) Details */}
            {role === 'guest3' && (
              <g>
                <path
                  d="M39 42 C39 58, 81 58, 81 42 C81 58, 39 58, 39 42 Z"
                  fill="#3f3f46"
                  opacity="0.3"
                />
                <path
                  d="M52 50 Q60 52 68 50"
                  stroke="#27272a"
                  strokeWidth="1.8"
                  fill="none"
                  opacity="0.4"
                />
                <path
                  d="M37 40 C35 22, 85 22, 83 40 C75 32, 45 32, 37 40 Z"
                  fill="url(#hairWinston)"
                />
                <path d="M38 38 L38 46 L42 42 Z" fill="url(#hairWinston)" />
                <path d="M82 38 L82 46 L78 42 Z" fill="url(#hairWinston)" />
                <path
                  d="M44 34 Q51 34 56 32"
                  stroke="#1e293b"
                  strokeWidth="1.8"
                  fill="none"
                  strokeLinecap="round"
                />
                <path
                  d="M64 32 Q69 34 76 34"
                  stroke="#1e293b"
                  strokeWidth="1.8"
                  fill="none"
                  strokeLinecap="round"
                />
                <circle cx="52" cy="39" r="2.5" fill="#1e293b" />
                <circle cx="68" cy="39" r="2.5" fill="#1e293b" />
                <path
                  d="M48 44 Q52 46 56 44"
                  stroke="#71717a"
                  strokeWidth="1"
                  fill="none"
                  opacity="0.4"
                />
                <path
                  d="M64 44 Q68 46 72 44"
                  stroke="#71717a"
                  strokeWidth="1"
                  fill="none"
                  opacity="0.4"
                />
              </g>
            )}

            {/* Chloe (Guest 4) Details */}
            {role === 'guest4' && (
              <g>
                <circle cx="36" cy="20" r="10" fill="url(#hairChloe)" />
                <circle cx="84" cy="20" r="10" fill="url(#hairChloe)" />
                <path
                  d="M38 42 C36 24, 84 24, 82 42 C72 32, 48 32, 38 42 Z"
                  fill="url(#hairChloe)"
                />
                <path
                  d="M42 42 C44 32, 54 36, 60 40 C66 36, 76 32, 78 42 Z"
                  fill="url(#hairChloe)"
                />
                <path
                  d="M46 32 Q52 29 58 33"
                  stroke="#831843"
                  strokeWidth="1.8"
                  fill="none"
                  strokeLinecap="round"
                />
                <path
                  d="M62 33 Q68 29 74 32"
                  stroke="#831843"
                  strokeWidth="1.8"
                  fill="none"
                  strokeLinecap="round"
                />
                <circle cx="52" cy="39" r="3.2" fill="#4c1d95" />
                <circle cx="53.5" cy="37.2" r="1" fill="#ffffff" />
                <circle cx="50.8" cy="40.8" r="0.6" fill="#ffffff" />
                <circle cx="68" cy="39" r="3.2" fill="#4c1d95" />
                <circle cx="69.5" cy="37.2" r="1" fill="#ffffff" />
                <circle cx="66.8" cy="40.8" r="0.6" fill="#ffffff" />
              </g>
            )}

            {/* Expressive Mouths */}
            <ellipse
              className="debate-char-mouth"
              cx="60"
              cy="53"
              rx={speaking ? 4.5 : 3.5}
              ry={speaking ? 3.5 : 1}
              fill={speaking ? '#850000' : '#8c593b'}
            />
          </g>

          {/* Vintage Microphone for Active Speakers */}
          {(role === 'host' || speaking) && (
            <g className="debate-char-mic">
              <rect x="88" y="72" width="2" height="28" rx="0.5" fill="#64748b" />
              <rect
                x="84"
                y="62"
                width="10"
                height="12"
                rx="3"
                fill="#475569"
                stroke="#94a3b8"
                strokeWidth="1"
              />
              <line x1="89" y1="62" x2="89" y2="74" stroke="#cbd5e1" strokeWidth="1" />
              <line x1="86" y1="66" x2="92" y2="66" stroke="#cbd5e1" strokeWidth="1" />
              <line x1="86" y1="70" x2="92" y2="70" stroke="#cbd5e1" strokeWidth="1" />
              <circle cx="89" cy="72" r="2" fill="#1e293b" />
            </g>
          )}
        </svg>
      </div>

      <div className="mt-2 text-center">
        <p className="text-sm font-semibold text-white sm:text-base">{name}</p>
        <span
          className={[
            'mt-1 inline-block rounded-full border px-2.5 py-0.5 text-[10px] font-semibold uppercase tracking-wider shadow-sm',
            theme.badge,
          ].join(' ')}
        >
          {pose === 'speaking' ? '🟢 Speaking' : pose === 'listening' ? '👂 Listening' : label}
        </span>
      </div>

      {/* Floating Movie-style Subtitle Overlay */}
      {subtitle && (
        <div className="absolute top-[100%] left-1/2 -translate-x-1/2 mt-2 w-max max-w-[140px] sm:max-w-[180px] z-20 pointer-events-none debate-subtitle-animation">
          <p className="text-xs sm:text-sm font-medium text-slate-100 leading-snug bg-black/85 backdrop-blur-md border border-white/10 rounded-lg px-2.5 py-1.5 shadow-xl text-center">
            {subtitle}
          </p>
        </div>
      )}
    </div>
  );
}
