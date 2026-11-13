import { ApiError } from '@/api/api-error';
import type { ErrorResponse } from '@/api/types';
import { API_BASE_URL, API_PREFIX } from '@/config/env';

type RequestOptions = {
  method?: 'GET' | 'POST' | 'PATCH' | 'PUT' | 'DELETE';
  body?: unknown;
  accessToken?: string;
};

/**
 * Sends a JSON request to the API and returns the parsed JSON answer.
 * Throws an ApiError when the server answers with an error or cannot be reached.
 *
 * Example: request<AuthResponse>('/auth/login', { method: 'POST', body: { email, password } })
 */
export async function request<T>(path: string, options: RequestOptions = {}): Promise<T> {
  const headers: Record<string, string> = { Accept: 'application/json' };
  if (options.body !== undefined) {
    headers['Content-Type'] = 'application/json';
  }
  if (options.accessToken) {
    headers.Authorization = `Bearer ${options.accessToken}`;
  }

  let response: Response;
  try {
    response = await fetch(`${API_BASE_URL}${API_PREFIX}${path}`, {
      method: options.method ?? 'GET',
      headers,
      body: options.body === undefined ? undefined : JSON.stringify(options.body),
    });
  } catch {
    throw new ApiError(0, 'NETWORK_ERROR', `Cannot reach the server at ${API_BASE_URL}.`);
  }

  const data: unknown = await response.json().catch(() => null);

  if (!response.ok) {
    const error = (data as ErrorResponse | null)?.error;
    throw new ApiError(
      response.status,
      error?.code ?? 'HTTP_ERROR',
      error?.message ?? `The server answered with status ${response.status}.`
    );
  }

  return data as T;
}
