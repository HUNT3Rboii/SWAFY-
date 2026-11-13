/**
 * App configuration read from environment variables.
 *
 * Expo only exposes variables whose name starts with EXPO_PUBLIC_.
 * Set them in apps/mobile/.env.local (not committed); see .env.example.
 */

const DEFAULT_API_BASE_URL = 'http://localhost:8000';

function readApiBaseUrl(): string {
  const value = process.env.EXPO_PUBLIC_API_BASE_URL?.trim();

  if (!value) {
    if (__DEV__) {
      console.warn(
        `EXPO_PUBLIC_API_BASE_URL is not set, using ${DEFAULT_API_BASE_URL}. ` +
          'Copy .env.example to .env.local and set your API address.'
      );
    }
    return DEFAULT_API_BASE_URL;
  }

  // Remove a trailing slash so paths can always be written as `${API_BASE_URL}/reports`.
  return value.replace(/\/+$/, '');
}

export const API_BASE_URL = readApiBaseUrl();
