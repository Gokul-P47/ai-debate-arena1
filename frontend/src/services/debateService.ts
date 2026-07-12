/** Debate API service — placeholder methods for future backend integration. */

import { api } from '@/lib/api';
import type { DebateRequest, DebateResponse } from '@/types/debate';

/**
 * Start a new AI debate session.
 * @param _request - Debate configuration payload.
 * @returns Debate response with messages and optional summary.
 */
export async function startDebate(request: DebateRequest): Promise<DebateResponse> {
  // Placeholder — will call POST /api/v1/debates in the next phase
  void request;
  void api;
  throw new Error('startDebate() is not implemented yet');
}

/**
 * Retrieve an existing debate session by ID.
 * @param id - Unique debate session identifier.
 * @returns Debate response with messages and optional summary.
 */
export async function getDebate(id: string): Promise<DebateResponse> {
  // Placeholder — will call GET /api/v1/debates/:id in the next phase
  void id;
  void api;
  throw new Error('getDebate() is not implemented yet');
}
