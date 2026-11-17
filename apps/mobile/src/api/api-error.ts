import { API_BASE_URL } from '@/config/env';

/**
 * Error thrown by every API call, so screens only handle one kind of error.
 *
 * status: the HTTP status (401, 409, 422...), or 0 when the server could not be reached.
 * code: the API error code (UNAUTHORIZED, VALIDATION_ERROR...) or NETWORK_ERROR.
 */
export class ApiError extends Error {
  readonly status: number;
  readonly code: string;

  constructor(status: number, code: string, message: string) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
    this.code = code;
  }
}

type ErrorBody = { error?: { code?: string; message?: string } };

/**
 * Runs one call of the generated client and returns its data,
 * or throws an ApiError when the server answers with an error or cannot be reached.
 *
 * Example: const result = await call(api.POST('/auth/login', { body: { email, password } }));
 */
export async function call<T>(
  request: Promise<{ data?: T; error?: unknown; response: Response }>
): Promise<T> {
  let result: { data?: T; error?: unknown; response: Response };
  try {
    result = await request;
  } catch {
    throw new ApiError(0, 'NETWORK_ERROR', `Cannot reach the server at ${API_BASE_URL}.`);
  }

  const { data, error, response } = result;
  if (!response.ok) {
    const body = (error ?? null) as ErrorBody | null;
    throw new ApiError(
      response.status,
      body?.error?.code ?? 'HTTP_ERROR',
      body?.error?.message ?? `The server answered with status ${response.status}.`
    );
  }

  return data as T;
}
