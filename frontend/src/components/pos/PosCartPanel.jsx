import { Box, Card, CardContent, Stack, Typography } from '@mui/material';

/**
 * Sticky right-rail cart panel for POS screens.
 * Keeps Generate Bill / totals easy to reach on desktop.
 */
export default function PosCartPanel({
  title = 'Current Bill',
  actions = null,
  empty = null,
  footer = null,
  children,
}) {
  return (
    <Card
      variant="outlined"
      sx={{
        position: { md: 'sticky' },
        top: { md: 80 },
        borderColor: 'divider',
        bgcolor: 'background.paper',
      }}
    >
      <CardContent
        sx={{
          p: { xs: 2, sm: 2.25 },
          '&:last-child': { pb: { xs: 2, sm: 2.25 } },
        }}
      >
        <Stack
          direction="row"
          justifyContent="space-between"
          alignItems="center"
          spacing={1}
          sx={{ mb: 1.5 }}
        >
          <Typography variant="h6" sx={{ fontWeight: 650, fontSize: '1.05rem' }}>
            {title}
          </Typography>
          {actions}
        </Stack>

        {children}

        {empty ? (
          <Box
            sx={{
              py: 2.5,
              px: 1.5,
              textAlign: 'center',
              border: '1px dashed',
              borderColor: 'divider',
              borderRadius: 2,
              bgcolor: (theme) =>
                theme.palette.mode === 'dark' ? 'rgba(255,255,255,0.02)' : 'rgba(31, 78, 95, 0.03)',
            }}
          >
            {typeof empty === 'string' ? (
              <Typography variant="body2" color="text.secondary">
                {empty}
              </Typography>
            ) : (
              empty
            )}
          </Box>
        ) : null}

        {footer ? <Box sx={{ mt: 2 }}>{footer}</Box> : null}
      </CardContent>
    </Card>
  );
}
