/** Generic API response and error types. */

export interface ApiError {
  message: string;
  status?: number;
  detail?: string;
}

export interface HealthResponse {
  status: string;
  service: string;
}

export interface PlaceholderDebateResponse {
  message: string;
}
