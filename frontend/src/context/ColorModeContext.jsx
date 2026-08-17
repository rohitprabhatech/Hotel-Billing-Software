import { CssBaseline, ThemeProvider } from '@mui/material';
import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
} from 'react';
import { createAppTheme } from '../theme';

export const COLOR_MODE_STORAGE_KEY = 'bbs-color-mode';

const ColorModeContext = createContext({
  mode: 'light',
  isDark: false,
  setMode: () => {},
  toggleMode: () => {},
});

function readStoredMode() {
  try {
    const stored = localStorage.getItem(COLOR_MODE_STORAGE_KEY);
    if (stored === 'dark' || stored === 'light') return stored;
  } catch {
    // ignore private-mode / blocked storage
  }
  return 'light';
}

function applyDocumentMode(mode) {
  const root = document.documentElement;
  root.setAttribute('data-color-mode', mode);
  root.style.colorScheme = mode;
}

export function ColorModeProvider({ children }) {
  const [mode, setModeState] = useState(() => readStoredMode());

  useEffect(() => {
    applyDocumentMode(mode);
    try {
      localStorage.setItem(COLOR_MODE_STORAGE_KEY, mode);
    } catch {
      // ignore
    }
  }, [mode]);

  const setMode = useCallback((next) => {
    setModeState(next === 'dark' ? 'dark' : 'light');
  }, []);

  const toggleMode = useCallback(() => {
    setModeState((prev) => (prev === 'dark' ? 'light' : 'dark'));
  }, []);

  const theme = useMemo(() => createAppTheme(mode), [mode]);

  const value = useMemo(
    () => ({
      mode,
      isDark: mode === 'dark',
      setMode,
      toggleMode,
    }),
    [mode, setMode, toggleMode],
  );

  return (
    <ColorModeContext.Provider value={value}>
      <ThemeProvider theme={theme}>
        <CssBaseline />
        {children}
      </ThemeProvider>
    </ColorModeContext.Provider>
  );
}

export function useColorMode() {
  return useContext(ColorModeContext);
}
