/** Talk-show episode setup form. */

'use client';

import { Mic, Play } from 'lucide-react';

import { Button } from '@/components/common/Button';
import { Card } from '@/components/common/Card';
import { Input } from '@/components/common/Input';
import { Select } from '@/components/common/Select';
import { useDebate } from '@/hooks/useDebate';
import {
  DEBATE_LANGUAGES,
  DEBATE_MOODS,
  guestsForCount,
  MAX_PARTICIPANT_COUNT,
  MAX_ROUNDS,
  MAX_TURN_SECONDS,
  MIN_PARTICIPANT_COUNT,
  MIN_ROUNDS,
  MIN_TURN_SECONDS,
} from '@/lib/constants';

export function DebateForm() {
  const {
    topic,
    mood,
    rounds,
    language,
    turnSeconds,
    loading,
    revealing,
    streaming,
    error,
    setTopic,
    setMood,
    setRounds,
    setLanguage,
    setTurnSeconds,
    setParticipantCount,
    participantCount,
    startDebate,
  } = useDebate();

  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    document.getElementById('debate-arena')?.scrollIntoView({ behavior: 'smooth', block: 'start' });
    await startDebate();
  };

  const busy = loading || revealing || streaming;

  return (
    <Card variant="gradient-border" padding="lg" className="w-full max-w-2xl border-amber-500/10">
      <form onSubmit={handleSubmit} className="flex flex-col gap-5">
        <div>
          <h2 className="font-display text-xl font-semibold text-[#f8f1e3]">
            Cue tonight&apos;s show
          </h2>
          <p className="mt-1 text-sm text-slate-400">
            Pick a topic and vibe — guests will chat like a friendly TV panel.
          </p>
        </div>

        <Input
          label="Tonight's topic"
          placeholder="What should the guests talk about?"
          value={topic}
          onChange={(e) => setTopic(e.target.value)}
          required
          disabled={busy}
        />

        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
          <Input
            label="Chat segments"
            type="number"
            min={MIN_ROUNDS}
            max={MAX_ROUNDS}
            value={rounds}
            onChange={(e) => setRounds(Number(e.target.value))}
            disabled={busy}
          />
          <Input
            label="Guests on the couch"
            type="number"
            min={MIN_PARTICIPANT_COUNT}
            max={MAX_PARTICIPANT_COUNT}
            value={participantCount}
            onChange={(e) => setParticipantCount(Number(e.target.value))}
            disabled={busy}
          />
        </div>

        <p className="text-xs text-slate-500">
          Host is always on stage. Guests:{' '}
          {guestsForCount(participantCount)
            .map((g) => g.name)
            .join(' · ')}
          . Views may agree or gently contradict.
        </p>

        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
          <Select
            label="Show vibe"
            options={DEBATE_MOODS.map((m) => ({ value: m.value, label: m.label }))}
            value={mood}
            onChange={(e) => setMood(e.target.value)}
            disabled={busy}
          />

          <Select
            label="Language"
            options={DEBATE_LANGUAGES.map((l) => ({ value: l.value, label: l.label }))}
            value={language}
            onChange={(e) => setLanguage(e.target.value)}
            disabled={busy}
          />
        </div>

        <div className="flex flex-col gap-2">
          <div className="flex items-center justify-between gap-3">
            <label htmlFor="turn-seconds" className="text-sm font-medium text-slate-300">
              Guest turn length
            </label>
            <span className="text-sm tabular-nums text-amber-200/90">{turnSeconds}s</span>
          </div>
          <input
            id="turn-seconds"
            type="range"
            min={MIN_TURN_SECONDS}
            max={MAX_TURN_SECONDS}
            step={5}
            value={turnSeconds}
            onChange={(e) => setTurnSeconds(Number(e.target.value))}
            disabled={busy}
            className="h-2 w-full cursor-pointer appearance-none rounded-full bg-slate-700 accent-amber-400 disabled:cursor-not-allowed disabled:opacity-50"
          />
          <div className="flex justify-between text-xs text-slate-500">
            <span>{MIN_TURN_SECONDS}s</span>
            <span>How long each guest speaks</span>
            <span>{MAX_TURN_SECONDS}s</span>
          </div>
        </div>

        <Button type="button" variant="outline" className="w-full sm:w-auto" disabled>
          <Mic className="h-4 w-4" aria-hidden="true" />
          Voice Input (soon)
        </Button>

        <div className="flex flex-col gap-3 sm:flex-row sm:items-center">
          <Button
            type="submit"
            size="lg"
            isLoading={loading}
            disabled={busy}
            className="w-full sm:w-auto"
          >
            <Play className="h-4 w-4" aria-hidden="true" />
            {loading ? 'Going live…' : streaming || revealing ? 'On air…' : 'Start Show'}
          </Button>

          {error && (
            <p role="alert" className="text-sm text-amber-400">
              {error}
            </p>
          )}

          {!error && loading && (
            <p role="status" className="text-sm text-teal-300/90">
              Guests are settling onto the couch…
            </p>
          )}
        </div>
      </form>
    </Card>
  );
}
