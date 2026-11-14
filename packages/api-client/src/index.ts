import createClient, { type Client } from 'openapi-fetch';

import type { components, paths } from './schema';

export type { components, paths };

/** All request/response models from the contract, e.g. `Schemas['Report']`. */
export type Schemas = components['schemas'];

export type ApiClient = Client<paths>;

export type CreateApiClientOptions = {
  /**
   * Value of API_BASE_URL. Switches between mock and real API:
   *   mock: http://<host>:4010
   *   real: http://<host>:8000/api/v1
   */
  baseUrl: string;
  /** Returns the current access token, if the user is logged in. */
  getToken?: () => string | null | undefined | Promise<string | null | undefined>;
};

/**
 * Create a typed client:
 *
 *   const api = createApiClient({ baseUrl: API_BASE_URL, getToken });
 *   const { data, error } = await api.GET('/reports/mine');
 */
export function createApiClient({ baseUrl, getToken }: CreateApiClientOptions): ApiClient {
  const client = createClient<paths>({ baseUrl: baseUrl.replace(/\/+$/, '') });

  if (getToken) {
    client.use({
      async onRequest({ request }) {
        const token = await getToken();
        if (token) {
          request.headers.set('Authorization', `Bearer ${token}`);
        }
        return request;
      },
    });
  }

  return client;
}
