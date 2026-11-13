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
