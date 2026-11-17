import { call } from '@/api/api-error';
import { api, type AuthResponse, type LoginRequest, type RegisterRequest } from '@/api/client';

/**
 * Authentication calls (docs/contracts/openapi.yaml):
 * POST /auth/register -> 201 AuthResponse (409 if the email is taken)
 * POST /auth/login    -> 200 AuthResponse (401 if wrong email or password)
 * POST /auth/logout   -> 204, revokes the refresh token on the server
 */

export function register(body: RegisterRequest): Promise<AuthResponse> {
  return call(api.POST('/auth/register', { body }));
}

export function login(body: LoginRequest): Promise<AuthResponse> {
  return call(api.POST('/auth/login', { body }));
}

export async function logout(refreshToken: string): Promise<void> {
  await call(api.POST('/auth/logout', { body: { refresh_token: refreshToken } }));
}
