import { Box } from '@mui/material';
import { createContext, useCallback, useContext, useMemo, useState } from 'react';
import { createPortal } from 'react-dom';

const PageActionsContext = createContext(null);

/** Provides a stable DOM slot for page primary actions in the shared header. */
export function PageActionsProvider({ children }) {
  const [slotEl, setSlotElState] = useState(null);
  const setSlotEl = useCallback((node) => {
    setSlotElState((prev) => (prev === node ? prev : node));
  }, []);
  const value = useMemo(() => ({ slotEl, setSlotEl }), [slotEl, setSlotEl]);
  return (
    <PageActionsContext.Provider value={value}>
      {children}
    </PageActionsContext.Provider>
  );
}

export function usePageActionsSlot() {
  return useContext(PageActionsContext);
}

/** Empty target rendered inside PageHeader for portaled actions. */
export function PageActionsSlot() {
  const ctx = usePageActionsSlot();
  return (
    <Box
      ref={ctx?.setSlotEl}
      sx={{
        display: 'flex',
        flexDirection: 'row',
        flexWrap: 'wrap',
        gap: 1,
        justifyContent: { xs: 'flex-start', sm: 'flex-end' },
        minHeight: 0,
        '&:empty': { display: 'none' },
      }}
    />
  );
}

/** Render inside a page to place buttons in the page header (right side). */
export function PageActions({ children }) {
  const ctx = usePageActionsSlot();
  if (!ctx?.slotEl) return null;
  return createPortal(children, ctx.slotEl);
}
