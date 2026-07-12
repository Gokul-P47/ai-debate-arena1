/** Loading spinner component. */

interface LoadingProps {
  size?: 'sm' | 'md' | 'lg';
  label?: string;
  className?: string;
}

const sizeClasses = {
  sm: 'h-5 w-5 border-2',
  md: 'h-8 w-8 border-2',
  lg: 'h-12 w-12 border-3',
};

export function Loading({ size = 'md', label, className = '' }: LoadingProps) {
  return (
    <div className={['flex flex-col items-center justify-center gap-3', className].join(' ')}>
      <div
        className={[
          'animate-spin rounded-full border-blue-500/30 border-t-blue-500',
          sizeClasses[size],
        ].join(' ')}
        role="status"
        aria-label={label ?? 'Loading'}
      />
      {label && <p className="text-sm text-gray-400">{label}</p>}
    </div>
  );
}
