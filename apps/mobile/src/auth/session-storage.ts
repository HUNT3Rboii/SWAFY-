import * as SecureStore from 'expo-secure-store';

import type { AuthTokens, User } from '@/api/types';

/**
 * Saves the logged-in session in SecureStore, the phone's encrypted storage
 * (Android Keystore / iOS Keychain), as issue #11 requires.
 * Each value is stored under its own key to stay small.
 */

const KEYS = {
  accessToken: 'swafy.accessToken',
  refreshToken: 'swafy.refreshToken',
  user: 'swafy.user',
} as const;

export type StoredSession = {
  accessToken: string;
  refreshToken: string;
  user: User;
};

export async function saveSession(user: User, tokens: AuthTokens): Promise<void> {
  await SecureStore.setItemAsync(KEYS.accessToken, tokens.access_token);
  await SecureStore.setItemAsync(KEYS.refreshToken, tokens.refresh_token);
  await SecureStore.setItemAsync(KEYS.user, JSON.stringify(user));
}

export async function loadSession(): Promise<StoredSession | null> {
  const [accessToken, refreshToken, userJson] = await Promise.all([
    SecureStore.getItemAsync(KEYS.accessToken),
    SecureStore.getItemAsync(KEYS.refreshToken),
    SecureStore.getItemAsync(KEYS.user),
  ]);

  if (!accessToken || !refreshToken || !userJson) {
    return null;
  }

  try {
    return { accessToken, refreshToken, user: JSON.parse(userJson) as User };
  } catch {
    return null;
  }
}

export async function clearSession(): Promise<void> {
  await Promise.all([
    SecureStore.deleteItemAsync(KEYS.accessToken),
    SecureStore.deleteItemAsync(KEYS.refreshToken),
    SecureStore.deleteItemAsync(KEYS.user),
  ]);
}
