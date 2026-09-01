import { Box, Card, CardContent, Typography } from '@mui/material';

export default function KpiCard({ title, value, hint, icon = null, tone = 'default' }) {
  const accent =
    tone === 'warning'
      ? 'warning.main'
      : tone === 'success'
        ? 'success.main'
        : 'primary.main';

  return (
    <Card
      sx={{
        height: '100%',
        transition: 'box-shadow 0.15s ease, border-color 0.15s ease',
        '&:hover': {
          boxShadow: (theme) =>
            theme.palette.mode === 'dark'
              ? '0 4px 20px rgba(0,0,0,0.35)'
              : '0 4px 16px rgba(26, 35, 48, 0.08)',
        },
      }}
    >
      <CardContent
        sx={{
          height: '100%',
          display: 'flex',
          gap: 2,
          alignItems: 'flex-start',
          p: { xs: 2, sm: 2.5 },
          '&:last-child': { pb: { xs: 2, sm: 2.5 } },
        }}
      >
        {icon ? (
          <Box
            sx={{
              width: 40,
              height: 40,
              borderRadius: 2,
              bgcolor: (theme) =>
                theme.palette.mode === 'dark' ? 'rgba(110,180,200,0.14)' : 'rgba(31, 78, 95, 0.1)',
              color: accent,
              display: 'grid',
              placeItems: 'center',
              flexShrink: 0,
            }}
          >
            {icon}
          </Box>
        ) : null}
        <Box sx={{ minWidth: 0, width: '100%' }}>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 0.75, fontWeight: 500 }}>
            {title}
          </Typography>
          <Typography
            variant="h5"
            sx={{
              fontVariantNumeric: 'tabular-nums',
              fontSize: { xs: '1.35rem', md: '1.5rem' },
              lineHeight: 1.25,
              fontWeight: 700,
            }}
          >
            {value}
          </Typography>
          {hint ? (
            <Typography
              variant="caption"
              color="text.secondary"
              display="block"
              sx={{ mt: 0.75, lineHeight: 1.4 }}
            >
              {hint}
            </Typography>
          ) : null}
        </Box>
      </CardContent>
    </Card>
  );
}
