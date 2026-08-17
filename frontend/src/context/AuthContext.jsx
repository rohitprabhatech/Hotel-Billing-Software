import { createContext, useContext, useMemo, useState } from 'react';
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

  const value = useMemo(
    () => ({
      token,
      user,
      isAuthenticated: Boolean(token && user && isValidRole(user.role)),
      role: isValidRole(user?.role) ? user.role : null,
      login: (accessToken, nextUser) => {
        if (!accessToken || !nextUser || !isValidRole(nextUser.role)) {
          clearStoredSession();
          setToken(null);
          setUser(null);
          return;
        }
        localStorage.setItem('access_token', accessToken);
        localStorage.setItem('auth_user', JSON.stringify(nextUser));
        setToken(accessToken);
        setUser(nextUser);
      },
      logout: () => {
        clearStoredSession();
        setToken(null);
        setUser(null);
      },
    }),
    [token, user],
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
