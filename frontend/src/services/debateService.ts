/** Debate API service — blocking and SSE streaming. */

import { API_BASE_URL } from '@/lib/constants';
import { api } from '@/lib/api';
import type {
  DebateRequest,
  DebateResponse,
  DebateStreamEventType,
  DebateStreamHandlers,
} from '@/types/debate';

export async function startDebate(request: DebateRequest): Promise<DebateResponse> {
  const { data } = await api.post<DebateResponse>('/api/v1/debates', {
    topic: request.topic,
    mood: request.mood,
    rounds: request.rounds,
    language: request.language ?? 'en',
    turnSeconds: request.turnSeconds ?? 45,
    participantCount: request.participantCount ?? 2,
  });
  return data;
}

/**
 * Start a debate over SSE and invoke handlers as tokens/events arrive.
 */
export async function streamDebate(
  request: DebateRequest,
  handlers: DebateStreamHandlers,
  signal?: AbortSignal,
): Promise<void> {
  const response = await fetch(`${API_BASE_URL}/api/v1/debates/stream`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Accept: 'text/event-stream',
    },
    body: JSON.stringify({
      topic: request.topic,
      mood: request.mood,
      rounds: request.rounds,
      language: request.language ?? 'en',
      turnSeconds: request.turnSeconds ?? 45,
      participantCount: request.participantCount ?? 2,
    }),
    signal,
  });

  if (!response.ok) {
    const text = await response.text();
    throw new Error(text || `Stream failed with status ${response.status}`);
  }

  if (!response.body) {
    throw new Error('Streaming is not supported in this browser.');
  }

  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = '';

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    buffer += decoder.decode(value, { stream: true });
    const parts = buffer.split('\n\n');
    buffer = parts.pop() ?? '';

    for (const part of parts) {
      const lines = part.split('\n');
      let eventName: DebateStreamEventType | '' = '';
      const dataLines: string[] = [];

      for (const line of lines) {
        if (line.startsWith('event:')) {
          eventName = line.slice(6).trim() as DebateStreamEventType;
        } else if (line.startsWith('data:')) {
          dataLines.push(line.slice(5).trim());
        }
      }

      if (!eventName || dataLines.length === 0) continue;

      try {
        const data = JSON.parse(dataLines.join('\n')) as Record<string, unknown>;
        handlers.onEvent(eventName, data);
      } catch {
        // Ignore malformed chunks
      }
    }
  }
}
