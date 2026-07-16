/** Axios instance configured for the AI Debate Arena backend API. */

import axios from 'axios';

import { API_BASE_URL } from '@/lib/constants';

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  // Multi-round LLM debates can take well over 30s
  timeout: 180_000,
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    const detail = error.response?.data?.detail;
    let message: string;

    if (typeof detail === 'string') {
      message = detail;
    } else if (Array.isArray(detail)) {
      message = detail
        .map((item: { msg?: string }) => item.msg)
        .filter(Boolean)
        .join('; ');
    } else {
      message = error.response?.data?.message ?? error.message ?? 'An unexpected error occurred';
    }

    return Promise.reject(new Error(message || 'An unexpected error occurred'));
  },
);
