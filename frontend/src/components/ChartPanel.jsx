import { Box, Card, CardContent, Typography } from '@mui/material';

/** Consistent chart container for dashboards and reports. */
export default function ChartPanel({ title, description = null, height = 280, children, actions = null }) {
  return (
    <Card sx={{ height: '100%' }}>
      <CardContent
        sx={{
          p: { xs: 2, sm: 2.5 },
          '&:last-child': { pb: { xs: 2, sm: 2.5 } },
          height: '100%',
          display: 'flex',
          flexDirection: 'column',
        }}
      >
        {(title || actions) && (
          <Box
            sx={{
              display: 'flex',
              alignItems: 'flex-start',
              justifyContent: 'space-between',
              gap: 1.5,
              mb: 1.5,
            }}
          >
            <Box sx={{ minWidth: 0 }}>
              {title ? (
                <Typography variant="subtitle2" fontWeight={650}>
                  {title}
                </Typography>
              ) : null}
              {description ? (
                <Typography variant="caption" color="text.secondary">
                  {description}
                </Typography>
              ) : null}
            </Box>
            {actions}
          </Box>
        )}
        <Box sx={{ width: '100%', height, position: 'relative', flex: 1, minHeight: height }}>
          {children}
        </Box>
      </CardContent>
    </Card>
  );
}
