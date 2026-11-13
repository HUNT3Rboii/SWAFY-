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

/** Server address, without the /api/v1 prefix. Example: http://192.168.1.20:8000 */
export const API_BASE_URL = readApiBaseUrl();

/** Prefix of every API route, from docs/contracts/openapi.yaml (servers: /api/v1). */
export const API_PREFIX = '/api/v1';

/**
 * When true, the app answers API calls itself with fake data (src/api/mock.ts).
 * Useful while the backend is not running. Set EXPO_PUBLIC_USE_MOCK_API=false to use the real API.
 */
export const USE_MOCK_API = process.env.EXPO_PUBLIC_USE_MOCK_API !== 'false';
