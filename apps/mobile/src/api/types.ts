/**
 * Types for the API, copied by hand from docs/contracts/openapi.yaml (BE-1).
 *
 * TEMPORARY: issue #11 asks for the generated api-client (OPS-2). When it exists,
 * delete this file and import the generated types instead.
 */

export type UserRole = 'citizen' | 'municipal_admin';

export type User = {
  id: string;
  display_name: string;
  email: string;
  role: UserRole;
};

export type AuthTokens = {
  access_token: string;
  refresh_token: string;
  token_type: 'Bearer';
  /** Access-token lifetime in seconds. */
  expires_in: number;
};

export type AuthResponse = {
  user: User;
  tokens: AuthTokens;
};

export type RegisterRequest = {
  display_name: string;
  email: string;
  password: string;
};

export type LoginRequest = {
  email: string;
  password: string;
};

/** Error body returned by the API: { "error": { "code": ..., "message": ... } } */
export type ErrorResponse = {
  error: {
    code: string;
    message: string;
    details?: Record<string, unknown> | null;
    request_id: string;
  };
};
