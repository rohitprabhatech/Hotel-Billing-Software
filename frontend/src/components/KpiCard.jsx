import { Box, Card, CardContent, Typography } from '@mui/material';

export default function KpiCard({ title, value, hint, icon = null }) {
  return (
    <Card sx={{ height: '100%' }}>
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
              bgcolor: 'primary.main',
              color: 'primary.contrastText',
              display: 'grid',
              placeItems: 'center',
              flexShrink: 0,
            }}
          >
            {icon}
          </Box>
        ) : null}
        <Box sx={{ minWidth: 0, width: '100%' }}>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
            {title}
          </Typography>
          <Typography
            variant="h5"
            sx={{
              fontVariantNumeric: 'tabular-nums',
              fontSize: { xs: '1.35rem', md: '1.5rem' },
              lineHeight: 1.25,
            }}
          >
            {value}
          </Typography>
          {hint ? (
            <Typography
              variant="caption"
              color="text.secondary"
              display="block"
              sx={{ mt: 1, lineHeight: 1.4 }}
            >
              {hint}
            </Typography>
          ) : null}
        </Box>
      </CardContent>
    </Card>
  );
}
