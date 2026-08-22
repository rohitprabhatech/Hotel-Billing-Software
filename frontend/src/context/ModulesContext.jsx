import { createContext, useCallback, useContext, useEffect, useMemo, useState } from 'react';
import { useAuth } from './AuthContext';
import { fetchMyModules } from '../services/tenantService';

const ModulesContext = createContext(null);

export function ModulesProvider({ children }) {
  const { token, user, sessionReady } = useAuth();
  const [enabledModules, setEnabledModules] = useState(() => {
    const fromUser = user?.tenant?.enabled_modules;
    return Array.isArray(fromUser) ? fromUser : [];
  });
  const [modulesDetail, setModulesDetail] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const refresh = useCallback(async () => {
    if (!token || user?.role === 'MASTER_ADMIN') {
      setEnabledModules([]);
      setModulesDetail([]);
      return;
    }
    setLoading(true);
    setError('');
    try {
      const payload = await fetchMyModules();
      const data = payload?.data || {};
      setEnabledModules(Array.isArray(data.enabled_modules) ? data.enabled_modules : []);
      setModulesDetail(Array.isArray(data.modules) ? data.modules : []);
    } catch (err) {
      setError(err?.response?.data?.error?.message || err.message || 'Failed to load modules');
      const fallback = user?.tenant?.enabled_modules;
      setEnabledModules(Array.isArray(fallback) ? fallback : []);
    } finally {
      setLoading(false);
    }
  }, [token, user]);

  useEffect(() => {
    if (!sessionReady) return undefined;
    refresh();
    return undefined;
  }, [sessionReady, refresh]);

  useEffect(() => {
    const fromUser = user?.tenant?.enabled_modules;
    if (Array.isArray(fromUser) && fromUser.length && enabledModules.length === 0) {
      setEnabledModules(fromUser);
    }
  }, [user, enabledModules.length]);

  const value = useMemo(() => {
    const enabledSet = new Set(enabledModules);
    return {
      enabledModules,
      modulesDetail,
      loading,
      error,
      refresh,
      isModuleEnabled: (code) => enabledSet.has(code),
      filterByModule: (items) =>
        (items || []).filter((item) => !item.module || enabledSet.has(item.module)),
    };
  }, [enabledModules, modulesDetail, loading, error, refresh]);

  return <ModulesContext.Provider value={value}>{children}</ModulesContext.Provider>;
}

export function useModules() {
  const ctx = useContext(ModulesContext);
  if (!ctx) {
    throw new Error('useModules must be used within ModulesProvider');
  }
  return ctx;
}

/** Soft gate — returns false when provider missing or module off. */
export function useModuleGate(moduleCode) {
  const ctx = useContext(ModulesContext);
  if (!ctx || !moduleCode) return true;
  return ctx.isModuleEnabled(moduleCode);
}
