import { createContext, useContext, useEffect, useMemo, useState } from 'react';
import { fetchMe } from '../services/authService';
import { isValidRole } from '../utils/authRouting';

const AuthContext = createContext(null);

function readStoredUser() {
  try {
    const raw = localStorage.getItem('auth_user');
    return raw ? JSON.parse(raw) : null;
  } catch {
    return null;
  }
}

function clearStoredSession() {
  localStorage.removeItem('access_token');
  localStorage.removeItem('auth_user');
}

/** Restore session only when token + user + known role are all present. */
function readValidSession() {
  const token = localStorage.getItem('access_token');
  const user = readStoredUser();
  if (token && user && isValidRole(user.role)) {
    return { token, user };
  }
  if (token || user) {
    clearStoredSession();
  }
  return { token: null, user: null };
}

export function AuthProvider({ children }) {
  const initial = readValidSession();
  const [token, setToken] = useState(() => initial.token);
  const [user, setUser] = useState(() => initial.user);
  const [sessionReady, setSessionReady] = useState(() => !initial.token);

  useEffect(() => {
    let active = true;
    if (!token) {
      setSessionReady(true);
      return () => {
        active = false;
      };
    }
    setSessionReady(false);
    fetchMe()
      .then((payload) => {
        const nextUser = payload?.data;
        if (!active) return;
        if (!nextUser || !isValidRole(nextUser.role)) {
          clearStoredSession();
          setToken(null);
          setUser(null);
          return;
        }
        localStorage.setItem('auth_user', JSON.stringify(nextUser));
        setUser(nextUser);
      })
      .catch(() => {
        if (!active) return;
        clearStoredSession();
        setToken(null);
        setUser(null);
      })
      .finally(() => {
        if (active) setSessionReady(true);
      });
    return () => {
      active = false;
    };
  }, [token]);

  const value = useMemo(
    () => ({
      token,
      user,
      sessionReady,
      isAuthenticated: Boolean(sessionReady && token && user && isValidRole(user.role)),
      role: isValidRole(user?.role) ? user.role : null,
      login: (accessToken, nextUser) => {
        if (!accessToken || !nextUser || !isValidRole(nextUser.role)) {
          clearStoredSession();
          setToken(null);
          setUser(null);
          setSessionReady(true);
          return;
        }
        localStorage.setItem('access_token', accessToken);
        localStorage.setItem('auth_user', JSON.stringify(nextUser));
        setToken(accessToken);
        setUser(nextUser);
        setSessionReady(true);
      },
      updateUser: (nextUser) => {
        if (!nextUser || !isValidRole(nextUser.role)) return;
        localStorage.setItem('auth_user', JSON.stringify(nextUser));
        setUser(nextUser);
      },
      logout: () => {
        clearStoredSession();
        setToken(null);
        setUser(null);
        setSessionReady(true);
      },
    }),
    [sessionReady, token, user],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return ctx;
}
