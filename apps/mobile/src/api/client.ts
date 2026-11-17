import { createApiClient, type Schemas } from '@swafy/api-client';

import { API_BASE_URL } from '@/config/env';

/**
 * The one API client used by the whole app, generated from
 * docs/contracts/openapi.yaml (packages/api-client).
 *
 * Example: const { data, error } = await api.GET('/reports/mine');
 */

// The access token of the logged-in user. Set by src/auth/auth-context.tsx.
let accessToken: string | null = null;

export function setAccessToken(token: string | null): void {
  accessToken = token;
}

export const api = createApiClient({
  baseUrl: API_BASE_URL,
  getToken: () => accessToken,
});

// Types from the contract, re-exported so screens import them from one place.
export type User = Schemas['User'];
export type AuthTokens = Schemas['AuthTokens'];
export type AuthResponse = Schemas['AuthResponse'];
export type RegisterRequest = Schemas['RegisterRequest'];
export type LoginRequest = Schemas['LoginRequest'];
