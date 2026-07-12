/** Debate configuration form. */

'use client';

import { useState } from 'react';
import { Mic, Play } from 'lucide-react';

import { Button } from '@/components/common/Button';
import { Card } from '@/components/common/Card';
import { Input } from '@/components/common/Input';
import { Select } from '@/components/common/Select';
import { useDebate } from '@/hooks/useDebate';
import {
  DEBATE_MOODS,
  MAX_ROUNDS,
  MIN_ROUNDS,
  PLACEHOLDER_MESSAGE,
} from '@/lib/constants';

export function DebateForm() {
  const { topic, mood, rounds, loading, setTopic, setMood, setRounds, startDebate } = useDebate();
  const [statusMessage, setStatusMessage] = useState<string | null>(null);

  const handleSubmit = (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();

    if (!topic.trim()) {
      setStatusMessage('Please enter a debate topic.');
      return;
    }

    const message = startDebate();
    setStatusMessage(message);
  };

  return (
    <Card variant="gradient-border" padding="lg" className="w-full max-w-2xl">
      <form onSubmit={handleSubmit} className="flex flex-col gap-5">
        <div>
          <h2 className="text-xl font-semibold text-white">Configure Your Debate</h2>
          <p className="mt-1 text-sm text-gray-400">
            Set the topic, mood, and rounds — then let the AI agents battle it out.
          </p>
        </div>

        <Input
          label="Debate Topic"
          placeholder="Enter any debate topic..."
          value={topic}
          onChange={(e) => setTopic(e.target.value)}
          required
        />

        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
          <Select
            label="Mood"
            options={DEBATE_MOODS.map((m) => ({ value: m.value, label: m.label }))}
            value={mood}
            onChange={(e) => setMood(e.target.value)}
          />

          <Input
            label="Number of Rounds"
            type="number"
            min={MIN_ROUNDS}
            max={MAX_ROUNDS}
            value={rounds}
            onChange={(e) => setRounds(Number(e.target.value))}
          />
        </div>

        <Button type="button" variant="outline" className="w-full sm:w-auto">
          <Mic className="h-4 w-4" aria-hidden="true" />
          🎤 Voice Input
        </Button>

        <div className="flex flex-col gap-3 sm:flex-row sm:items-center">
          <Button type="submit" size="lg" isLoading={loading} className="w-full sm:w-auto">
            <Play className="h-4 w-4" aria-hidden="true" />
            Start Debate
          </Button>

          {statusMessage && (
            <p
              role="status"
              className={[
                'text-sm',
                statusMessage === PLACEHOLDER_MESSAGE ? 'text-blue-400' : 'text-amber-400',
              ].join(' ')}
            >
              {statusMessage}
            </p>
          )}
        </div>
      </form>
    </Card>
  );
}
