import { Sparkles } from 'lucide-react';

import { DebateArena } from '@/components/debate/DebateArena';
import { DebateForm } from '@/components/debate/DebateForm';
import { DebateSummary } from '@/components/debate/DebateSummary';
import { APP_NAME, APP_TAGLINE } from '@/lib/constants';

export default function HomePage() {
  return (
    <div className="mx-auto max-w-7xl px-4 py-12 sm:px-6 lg:px-8">
      <section className="mb-16 text-center">
        <div className="mb-4 inline-flex items-center gap-2 rounded-full border border-blue-500/20 bg-blue-500/10 px-4 py-1.5 text-sm text-blue-300">
          <Sparkles className="h-4 w-4" aria-hidden="true" />
          Live AI Debate Show
        </div>

        <h1 className="bg-gradient-to-r from-blue-400 via-purple-400 to-blue-400 bg-clip-text text-4xl font-extrabold tracking-tight text-transparent sm:text-5xl lg:text-6xl">
          {APP_NAME}
        </h1>

        <p className="mx-auto mt-4 max-w-2xl text-lg text-gray-400 sm:text-xl">{APP_TAGLINE}</p>
      </section>

      <section className="mb-16 flex justify-center">
        <DebateForm />
      </section>

      <section className="mb-16">
        <DebateArena />
      </section>

      <DebateSummary />
    </div>
  );
}
