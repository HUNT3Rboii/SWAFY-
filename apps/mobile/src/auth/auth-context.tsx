import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useRef,
  useState,
  type ReactNode,
} from 'react';

import * as authApi from '@/api/auth';
import {
  setAccessToken,
  type AuthResponse,
  type LoginRequest,
  type RegisterRequest,
  type User,
} from '@/api/client';
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
  signIn: (body: LoginRequest) => Promise<void>;
  signUp: (body: RegisterRequest) => Promise<void>;
  signOut: () => Promise<void>;
};

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [status, setStatus] = useState<AuthStatus>('loading');
  const [user, setUser] = useState<User | null>(null);
  // Kept outside React state: only needed to log out, never shown on screen.
  const refreshTokenRef = useRef<string | null>(null);

  // When the app starts, restore the session saved in SecureStore (if any).
  useEffect(() => {
    let cancelled = false;
    loadSession()
      .then((session) => {
        if (cancelled) return;
        if (session) {
          setAccessToken(session.accessToken);
          refreshTokenRef.current = session.refreshToken;
          setUser(session.user);
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

  const startSession = useCallback(async (result: AuthResponse) => {
    await saveSession(result.user, result.tokens);
    setAccessToken(result.tokens.access_token);
    refreshTokenRef.current = result.tokens.refresh_token;
    setUser(result.user);
    setStatus('signedIn');
  }, []);

  const signIn = useCallback(
    async (body: LoginRequest) => startSession(await authApi.login(body)),
    [startSession]
  );

  const signUp = useCallback(
    async (body: RegisterRequest) => startSession(await authApi.register(body)),
    [startSession]
  );

  const signOut = useCallback(async () => {
    const refreshToken = refreshTokenRef.current;
    if (refreshToken) {
      try {
        // Ask the server to revoke the refresh token (POST /auth/logout).
        await authApi.logout(refreshToken);
      } catch {
        // No network or server error: still log out on the phone.
      }
    }
    await clearSession();
    setAccessToken(null);
    refreshTokenRef.current = null;
    setUser(null);
    setStatus('signedOut');
  }, []);

  const value = useMemo(
    () => ({ status, user, signIn, signUp, signOut }),
    [status, user, signIn, signUp, signOut]
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
