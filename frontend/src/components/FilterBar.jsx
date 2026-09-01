import { Card, CardContent, Stack } from '@mui/material';

/**
 * Consistent filter/search strip used above tables.
 * Children are laid out in a responsive row/grid.
 */
export default function FilterBar({ children, actions = null }) {
  return (
    <Card
      sx={{
        bgcolor: (theme) =>
          theme.palette.mode === 'dark' ? 'background.paper' : 'rgba(255,255,255,0.9)',
      }}
    >
      <CardContent
        sx={{
          p: { xs: 2, sm: 2.25 },
          '&:last-child': { pb: { xs: 2, sm: 2.25 } },
        }}
      >
        <Stack spacing={1.5}>
          <Stack
            direction={{ xs: 'column', sm: 'row' }}
            spacing={1.5}
            useFlexGap
            flexWrap="wrap"
            sx={{ alignItems: { sm: 'flex-end' } }}
          >
            {children}
          </Stack>
          {actions ? (
            <Stack direction="row" spacing={1} useFlexGap flexWrap="wrap" justifyContent="flex-end">
              {actions}
            </Stack>
          ) : null}
        </Stack>
      </CardContent>
    </Card>
  );
}
