/** Reusable card container component. */

import { type HTMLAttributes } from 'react';

interface CardProps extends HTMLAttributes<HTMLDivElement> {
  variant?: 'default' | 'gradient-border';
  padding?: 'sm' | 'md' | 'lg';
}

const paddingClasses = {
  sm: 'p-4',
  md: 'p-6',
  lg: 'p-8',
};

export function Card({
  variant = 'default',
  padding = 'md',
  className = '',
  children,
  ...props
}: CardProps) {
  if (variant === 'gradient-border') {
    return (
      <div
        className={[
          'rounded-2xl bg-gradient-to-br from-amber-500/30 via-slate-800/40 to-teal-500/30 p-[1px] shadow-2xl shadow-black/60',
          className,
        ].join(' ')}
        {...props}
      >
        <div
          className={[
            'rounded-[calc(1rem-1px)] bg-[#0d1620]/98 backdrop-blur-md',
            paddingClasses[padding],
          ].join(' ')}
        >
          {children}
        </div>
      </div>
    );
  }

  return (
    <div
      className={[
        'rounded-2xl border border-slate-800/80 bg-[#0c141c]/90 backdrop-blur-md shadow-2xl shadow-black/40',
        paddingClasses[padding],
        className,
      ].join(' ')}
      {...props}
    >
      {children}
    </div>
  );
}
