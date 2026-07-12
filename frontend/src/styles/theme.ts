/** Design tokens for the AI Debate Arena UI theme. */

export const theme = {
  colors: {
    primary: {
      blue: '#3b82f6',
      purple: '#8b5cf6',
      darkGray: '#1f2937',
    },
    background: {
      base: '#0f1117',
      elevated: '#161b22',
      card: '#1c2333',
      border: '#2d3748',
    },
    text: {
      primary: '#f1f5f9',
      secondary: '#94a3b8',
      muted: '#64748b',
    },
    accent: {
      blueGlow: 'rgba(59, 130, 246, 0.15)',
      purpleGlow: 'rgba(139, 92, 246, 0.15)',
    },
  },
  gradients: {
    hero: 'linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%)',
    cardBorder: 'linear-gradient(135deg, rgba(59,130,246,0.4), rgba(139,92,246,0.4))',
    background:
      'radial-gradient(ellipse at top, rgba(59,130,246,0.08) 0%, transparent 50%), radial-gradient(ellipse at bottom right, rgba(139,92,246,0.06) 0%, transparent 50%)',
  },
  spacing: {
    section: '4rem',
  },
  borderRadius: {
    card: '1rem',
    button: '0.625rem',
  },
} as const;

export type Theme = typeof theme;
