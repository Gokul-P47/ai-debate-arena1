/** Site footer. */

import { APP_NAME } from '@/lib/constants';

export function Footer() {
  const year = new Date().getFullYear();

  return (
    <footer className="mt-auto border-t border-white/10 bg-[#0b1218]/70">
      <div className="mx-auto flex max-w-7xl flex-col items-center gap-2 px-4 py-6 text-center sm:flex-row sm:justify-between sm:text-left">
        <p className="text-sm text-slate-500">Built for Hackathon · Team of 2</p>
        <p className="text-sm text-slate-600">
          &copy; {year} {APP_NAME}. All rights reserved.
        </p>
      </div>
    </footer>
  );
}
