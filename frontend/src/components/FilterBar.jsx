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
        <Stack
          direction={{ xs: 'column', md: 'row' }}
          spacing={1.5}
          alignItems={{ xs: 'stretch', md: 'flex-end' }}
          useFlexGap
          flexWrap="wrap"
        >
          <Stack
            direction={{ xs: 'column', sm: 'row' }}
            spacing={1.5}
            useFlexGap
            flexWrap="wrap"
            sx={{ flex: 1, minWidth: 0, alignItems: { sm: 'flex-end' } }}
          >
            {children}
          </Stack>
          {actions ? (
            <Stack
              direction="row"
              spacing={1}
              useFlexGap
              flexWrap="wrap"
              sx={{ flexShrink: 0 }}
            >
              {actions}
            </Stack>
          ) : null}
        </Stack>
      </CardContent>
    </Card>
  );
}
