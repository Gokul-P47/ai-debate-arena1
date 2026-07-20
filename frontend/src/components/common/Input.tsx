/** Reusable text input component. */

import { type InputHTMLAttributes, forwardRef } from 'react';

interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
}

export const Input = forwardRef<HTMLInputElement, InputProps>(
  ({ label, error, className = '', id, ...props }, ref) => {
    const inputId = id ?? label?.toLowerCase().replace(/\s+/g, '-');

    return (
      <div className="flex flex-col gap-1.5">
        {label && (
          <label htmlFor={inputId} className="text-sm font-medium text-gray-300">
            {label}
          </label>
        )}
        <input
          ref={ref}
          id={inputId}
          className={[
            'w-full rounded-xl border border-slate-800 bg-[#0f1922] px-4 py-2.5',
            'text-[#f8f1e3] placeholder-slate-500',
            'transition-all duration-200',
            'focus:border-amber-400/80 focus:outline-none focus:ring-4 focus:ring-amber-400/10',
            'disabled:cursor-not-allowed disabled:opacity-50',
            error ? 'border-red-500/60 focus:border-red-500/60 focus:ring-red-500/20' : '',
            className,
          ].join(' ')}
          {...props}
        />
        {error && <p className="text-xs text-red-400">{error}</p>}
      </div>
    );
  },
);

Input.displayName = 'Input';
