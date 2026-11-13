import { createContext, useCallback, useContext, useEffect, useMemo, useState, type ReactNode } from 'react';

import * as authApi from '@/api/auth';
import type { LoginRequest, RegisterRequest, User } from '@/api/types';
import { clearSession, loadSession, saveSession } from '@/auth/session-storage';

/**
 * Keeps track of who is logged in, for the whole app.
 *
 * status:
 * - 'loading'   : reading the saved session when the app starts
 * - 'signedOut' : nobody is logged in, show the login screen
 * - 'signedIn'  : a user is logged in, show the app
 */
type AuthStatus = 'loading' | 'signedOut' | 'signedIn';

type AuthContextValue = {
  status: AuthStatus;
  user: User | null;
  accessToken: string | null;
  signIn: (body: LoginRequest) => Promise<void>;
  signUp: (body: RegisterRequest) => Promise<void>;
  signOut: () => Promise<void>;
};

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [status, setStatus] = useState<AuthStatus>('loading');
  const [user, setUser] = useState<User | null>(null);
  const [accessToken, setAccessToken] = useState<string | null>(null);

  // When the app starts, restore the session saved in SecureStore (if any).
  useEffect(() => {
    let cancelled = false;
    loadSession()
      .then((session) => {
        if (cancelled) return;
        if (session) {
          setUser(session.user);
          setAccessToken(session.accessToken);
          setStatus('signedIn');
        } else {
          setStatus('signedOut');
        }
      })
      .catch(() => {
        if (!cancelled) setStatus('signedOut');
      });
    return () => {
      cancelled = true;
    };
  }, []);

  const signIn = useCallback(async (body: LoginRequest) => {
    const result = await authApi.login(body);
    await saveSession(result.user, result.tokens);
    setUser(result.user);
    setAccessToken(result.tokens.access_token);
    setStatus('signedIn');
  }, []);

  const signUp = useCallback(async (body: RegisterRequest) => {
    const result = await authApi.register(body);
    await saveSession(result.user, result.tokens);
    setUser(result.user);
    setAccessToken(result.tokens.access_token);
    setStatus('signedIn');
  }, []);

  const signOut = useCallback(async () => {
    await clearSession();
    setUser(null);
    setAccessToken(null);
    setStatus('signedOut');
  }, []);

  const value = useMemo(
    () => ({ status, user, accessToken, signIn, signUp, signOut }),
    [status, user, accessToken, signIn, signUp, signOut]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

/** Use it in any screen: const { user, signOut } = useAuth(); */
export function useAuth(): AuthContextValue {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used inside <AuthProvider>.');
  }
  return context;
}
