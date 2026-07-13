/** Debate configuration form. */

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
  MAX_ROUNDS,
  MIN_ROUNDS,
} from '@/lib/constants';

export function DebateForm() {
  const {
    topic,
    mood,
    rounds,
    language,
    loading,
    revealing,
    streaming,
    error,
    setTopic,
    setMood,
    setRounds,
    setLanguage,
    startDebate,
  } = useDebate();

  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    document.getElementById('debate-arena')?.scrollIntoView({ behavior: 'smooth', block: 'start' });
    await startDebate();
  };

  const busy = loading || revealing || streaming;

  return (
    <Card variant="gradient-border" padding="lg" className="w-full max-w-2xl">
      <form onSubmit={handleSubmit} className="flex flex-col gap-5">
        <div>
          <h2 className="text-xl font-semibold text-white">Configure Your Debate</h2>
          <p className="mt-1 text-sm text-gray-400">
            Set the topic, mood, language, and rounds — then watch the agents take the stage.
          </p>
        </div>

        <Input
          label="Debate Topic"
          placeholder="Enter any debate topic..."
          value={topic}
          onChange={(e) => setTopic(e.target.value)}
          required
          disabled={busy}
        />

        <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
          <Select
            label="Mood"
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

          <Input
            label="Number of Rounds"
            type="number"
            min={MIN_ROUNDS}
            max={MAX_ROUNDS}
            value={rounds}
            onChange={(e) => setRounds(Number(e.target.value))}
            disabled={busy}
          />
        </div>

        <Button type="button" variant="outline" className="w-full sm:w-auto" disabled>
          <Mic className="h-4 w-4" aria-hidden="true" />
          Voice Input (soon)
        </Button>

        <div className="flex flex-col gap-3 sm:flex-row sm:items-center">
          <Button type="submit" size="lg" isLoading={loading} disabled={busy} className="w-full sm:w-auto">
            <Play className="h-4 w-4" aria-hidden="true" />
            {loading ? 'Connecting…' : streaming || revealing ? 'Streaming…' : 'Start Debate'}
          </Button>

          {error && (
            <p role="alert" className="text-sm text-amber-400">
              {error}
            </p>
          )}

          {!error && loading && (
            <p role="status" className="text-sm text-blue-400">
              Agents are preparing their arguments…
            </p>
          )}
        </div>
      </form>
    </Card>
  );
}
