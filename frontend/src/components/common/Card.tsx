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
        className={['rounded-xl bg-gradient-to-br from-blue-500/20 to-purple-500/20 p-px', className].join(
          ' ',
        )}
        {...props}
      >
        <div
          className={[
            'rounded-[calc(0.75rem-1px)] bg-gray-900/95 backdrop-blur-sm',
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
        'rounded-xl border border-gray-800 bg-gray-900/80 backdrop-blur-sm',
        paddingClasses[padding],
        className,
      ].join(' ')}
      {...props}
    >
      {children}
    </div>
  );
}
