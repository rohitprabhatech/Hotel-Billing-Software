import { createContext, useContext, useMemo, useState } from 'react';

const AuthContext = createContext(null);

function readStoredUser() {
  try {
    const raw = localStorage.getItem('auth_user');
    return raw ? JSON.parse(raw) : null;
  } catch {
    return null;
  }
}

export function AuthProvider({ children }) {
  const [token, setToken] = useState(() => localStorage.getItem('access_token'));
  const [user, setUser] = useState(() => readStoredUser());

  const value = useMemo(
    () => ({
      token,
      user,
      isAuthenticated: Boolean(token),
      role: user?.role || null,
      login: (accessToken, nextUser) => {
        localStorage.setItem('access_token', accessToken);
        localStorage.setItem('auth_user', JSON.stringify(nextUser));
        setToken(accessToken);
        setUser(nextUser);
      },
      logout: () => {
        localStorage.removeItem('access_token');
        localStorage.removeItem('auth_user');
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