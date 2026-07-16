'use client';

/** Top navigation bar. */

import { Code2, Radio } from 'lucide-react';

import { Button } from '@/components/common/Button';
import { APP_NAME } from '@/lib/constants';

export function Navbar() {
  return (
    <header className="sticky top-0 z-50 border-b border-white/10 bg-[#0b1218]/90 backdrop-blur-md">
      <nav className="mx-auto flex max-w-7xl items-center justify-between px-4 py-4 sm:px-6 lg:px-8">
        <div className="flex items-center gap-3">
          <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-gradient-to-br from-amber-400 to-teal-400 shadow-lg shadow-amber-500/20">
            <Radio className="h-5 w-5 text-[#0b1218]" aria-hidden="true" />
          </div>
          <span className="font-display text-lg font-semibold tracking-tight text-[#f8f1e3] sm:text-xl">
            {APP_NAME}
          </span>
        </div>

        <Button
          variant="ghost"
          size="sm"
          aria-label="View on GitHub"
          onClick={() => {
            /* Placeholder — GitHub link will be added later */
          }}
        >
          <Code2 className="h-5 w-5" aria-hidden="true" />
          <span className="hidden sm:inline">GitHub</span>
        </Button>
      </nav>
    </header>
  );
}
