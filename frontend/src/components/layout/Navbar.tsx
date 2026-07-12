'use client';

/** Top navigation bar. */

import { Code2, Swords } from 'lucide-react';

import { Button } from '@/components/common/Button';
import { APP_NAME } from '@/lib/constants';

export function Navbar() {
  return (
    <header className="sticky top-0 z-50 border-b border-gray-800/80 bg-gray-950/80 backdrop-blur-md">
      <nav className="mx-auto flex max-w-7xl items-center justify-between px-4 py-4 sm:px-6 lg:px-8">
        <div className="flex items-center gap-3">
          <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-gradient-to-br from-blue-500 to-purple-600 shadow-lg shadow-blue-500/20">
            <Swords className="h-5 w-5 text-white" aria-hidden="true" />
          </div>
          <span className="bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-lg font-bold text-transparent sm:text-xl">
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
