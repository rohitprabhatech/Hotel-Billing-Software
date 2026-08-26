import { Stack } from '@mui/material';

/**
 * Standard vertical rhythm for page body sections.
 * Gap = 24px between filters, alerts, tables, charts, etc.
 */
export default function PageShell({ children, spacing = 3, sx = {}, maxWidth }) {
  return (
    <Stack
      spacing={spacing}
      sx={{
        width: '100%',
        maxWidth: maxWidth || '100%',
        minWidth: 0,
        boxSizing: 'border-box',
        ...sx,
      }}
    >
      {children}
    </Stack>
  );
}
