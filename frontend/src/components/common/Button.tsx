/** Reusable button component with variant support. */

import { type ButtonHTMLAttributes, forwardRef } from 'react';

type ButtonVariant = 'primary' | 'secondary' | 'ghost' | 'outline';
type ButtonSize = 'sm' | 'md' | 'lg';

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: ButtonVariant;
  size?: ButtonSize;
  isLoading?: boolean;
}

const variantClasses: Record<ButtonVariant, string> = {
  primary:
    'bg-gradient-to-r from-amber-400 to-teal-400 text-[#0b1218] hover:from-amber-300 hover:to-teal-300 shadow-lg shadow-amber-500/20 font-semibold',
  secondary:
    'bg-slate-800 text-slate-100 border border-slate-700 hover:bg-slate-700 hover:border-slate-600',
  ghost: 'bg-transparent text-slate-300 hover:bg-slate-800/60 hover:text-white',
  outline:
    'bg-transparent text-amber-200 border border-amber-500/40 hover:bg-amber-500/10 hover:border-amber-500/60',
};

const sizeClasses: Record<ButtonSize, string> = {
  sm: 'px-3 py-1.5 text-sm',
  md: 'px-4 py-2 text-sm',
  lg: 'px-6 py-3 text-base',
};

export const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  (
    {
      variant = 'primary',
      size = 'md',
      isLoading = false,
      className = '',
      disabled,
      children,
      ...props
    },
    ref,
  ) => {
    return (
      <button
        ref={ref}
        disabled={disabled || isLoading}
        className={[
          'inline-flex items-center justify-center gap-2 rounded-lg font-medium',
          'transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-blue-500/50',
          'disabled:cursor-not-allowed disabled:opacity-50',
          variantClasses[variant],
          sizeClasses[size],
          className,
        ].join(' ')}
        {...props}
      >
        {isLoading ? (
          <>
            <span className="h-4 w-4 animate-spin rounded-full border-2 border-white/30 border-t-white" />
            Loading...
          </>
        ) : (
          children
        )}
      </button>
    );
  },
);

Button.displayName = 'Button';
