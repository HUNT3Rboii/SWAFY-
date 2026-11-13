import { ApiError } from '@/api/api-error';
import type { AuthResponse, LoginRequest, RegisterRequest } from '@/api/types';

/**
 * FAKE API answers, used while the backend is not running (EXPO_PUBLIC_USE_MOCK_API=true).
 *
 * To test the error messages:
 * - log in with the password "wrongpass" -> "wrong email or password"
 * - register with the email "taken@example.com" -> "account already exists"
 */

const wait = (ms: number) => new Promise((resolve) => setTimeout(resolve, ms));

function fakeAuthResponse(displayName: string, email: string): AuthResponse {
  return {
    user: {
      id: '00000000-0000-4000-8000-000000000001',
      display_name: displayName,
      email,
      role: 'citizen',
    },
    tokens: {
      access_token: `mock-access-${Date.now()}`,
      refresh_token: `mock-refresh-${Date.now()}`,
      token_type: 'Bearer',
      expires_in: 900,
    },
  };
}

export async function mockRegister(body: RegisterRequest): Promise<AuthResponse> {
  await wait(600);
  if (body.email.toLowerCase() === 'taken@example.com') {
    throw new ApiError(409, 'CONFLICT', 'An account with this email already exists');
  }
  return fakeAuthResponse(body.display_name, body.email);
}

export async function mockLogin(body: LoginRequest): Promise<AuthResponse> {
  await wait(600);
  if (body.password === 'wrongpass') {
    throw new ApiError(401, 'UNAUTHORIZED', 'Invalid email or password');
  }
  const nameFromEmail = body.email.split('@')[0] || 'Citizen';
  return fakeAuthResponse(nameFromEmail, body.email);
}
