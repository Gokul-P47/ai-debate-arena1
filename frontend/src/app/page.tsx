import { Radio } from 'lucide-react';

import { DebateArena } from '@/components/debate/DebateArena';
import { DebateForm } from '@/components/debate/DebateForm';
import { DebateSummary } from '@/components/debate/DebateSummary';
import { APP_NAME, APP_TAGLINE } from '@/lib/constants';

export default function HomePage() {
  return (
    <div className="mx-auto max-w-7xl px-4 py-10 sm:px-6 lg:px-8 lg:py-14">
      <section className="relative mb-12 overflow-hidden rounded-[2rem] border border-slate-800/80 bg-[#0c141c]/90 px-6 py-14 text-center sm:px-10 sm:py-16 shadow-2xl shadow-black/55">
        {/* Grid pattern overlay */}
        <div
          className="pointer-events-none absolute inset-0 opacity-15"
          style={{
            backgroundImage:
              'linear-gradient(to right, #80808012 1px, transparent 1px), linear-gradient(to bottom, #80808012 1px, transparent 1px)',
            backgroundSize: '24px 24px',
          }}
          aria-hidden
        />
        {/* Ambient Glows */}
        <div
          className="pointer-events-none absolute inset-0"
          aria-hidden
          style={{
            background:
              'radial-gradient(ellipse 60% 50% at 50% 0%, rgba(251,191,36,0.15), transparent 70%), radial-gradient(circle 350px at 0% 100%, rgba(45,212,191,0.06), transparent), radial-gradient(circle 350px at 100% 100%, rgba(251,113,133,0.06), transparent)',
          }}
        />
        <div className="relative">
          <div className="mb-5 inline-flex items-center gap-2 rounded-full border border-amber-500/20 bg-amber-500/5 px-4 py-1.5 text-xs font-semibold uppercase tracking-wider text-amber-200 shadow-inner">
            <Radio className="h-3.5 w-3.5 text-amber-400" aria-hidden="true" />
            Live TV Talk Show
          </div>

          <h1 className="font-display text-4xl font-extrabold tracking-tight text-[#f8f1e3] sm:text-5xl lg:text-6xl drop-shadow-sm">
            {APP_NAME}
          </h1>

          <p className="mx-auto mt-4 max-w-2xl text-base text-slate-400 sm:text-lg">
            {APP_TAGLINE}
          </p>
        </div>
      </section>

      <section className="mb-14 flex justify-center">
        <DebateForm />
      </section>

      <section className="mb-14">
        <DebateArena />
      </section>

      <DebateSummary />
    </div>
  );
}
