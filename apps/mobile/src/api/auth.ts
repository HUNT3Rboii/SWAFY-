import { request } from '@/api/http';
import { mockLogin, mockRegister } from '@/api/mock';
import type { AuthResponse, LoginRequest, RegisterRequest } from '@/api/types';
import { USE_MOCK_API } from '@/config/env';

/**
 * Authentication calls, matching docs/contracts/openapi.yaml:
 * POST /auth/register -> 201 AuthResponse (409 if the email is taken)
 * POST /auth/login    -> 200 AuthResponse (401 if wrong email or password)
 *
 * There is no /auth/logout route in the contract: logging out only deletes the
 * tokens saved on the phone (see src/auth/session-storage.ts).
 */

export function register(body: RegisterRequest): Promise<AuthResponse> {
  if (USE_MOCK_API) return mockRegister(body);
  return request<AuthResponse>('/auth/register', { method: 'POST', body });
}

export function login(body: LoginRequest): Promise<AuthResponse> {
  if (USE_MOCK_API) return mockLogin(body);
  return request<AuthResponse>('/auth/login', { method: 'POST', body });
}
