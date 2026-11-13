import type { AuthTokens, User } from '@/api/types';

/**
 * Web version: SecureStore does not exist in browsers, so the session is only
 * kept in memory (lost on page reload). The citizen app targets phones; this
 * file only keeps the web preview from crashing.
 */

export type StoredSession = {
  accessToken: string;
  refreshToken: string;
  user: User;
};

let memorySession: StoredSession | null = null;

export async function saveSession(user: User, tokens: AuthTokens): Promise<void> {
  memorySession = {
    accessToken: tokens.access_token,
    refreshToken: tokens.refresh_token,
    user,
  };
}

export async function loadSession(): Promise<StoredSession | null> {
  return memorySession;
}

export async function clearSession(): Promise<void> {
  memorySession = null;
}
