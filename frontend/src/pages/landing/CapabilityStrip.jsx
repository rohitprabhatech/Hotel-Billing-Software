import { Box, Stack, Typography } from '@mui/material';
import { CAPABILITIES, CONTENT_MAX, DISPLAY_FONT } from './constants';

/** Quiet proof line under the hero — not a KPI dashboard strip. */
export default function CapabilityStrip() {
  return (
    <Box
      component="section"
      aria-label="Product highlights"
      sx={{
        borderBottom: '1px solid',
        borderColor: 'divider',
        bgcolor: (t) => (t.palette.mode === 'dark' ? 'rgba(255,255,255,0.02)' : '#FFFFFF'),
        px: { xs: 2.5, sm: 3.5, md: 5 },
        py: { xs: 3.5, md: 4.25 },
      }}
    >
      <Box
        sx={{
          maxWidth: CONTENT_MAX,
          mx: 'auto',
          display: 'grid',
          gap: { xs: 3, md: 0 },
          gridTemplateColumns: { xs: '1fr 1fr', md: 'repeat(4, 1fr)' },
        }}
      >
        {CAPABILITIES.map((item, idx) => (
          <Stack
            key={item.title}
            spacing={0.6}
            sx={{
              px: { md: 2.5 },
              borderLeft: {
                xs: 'none',
                md: idx === 0 ? 'none' : '1px solid',
              },
              borderColor: 'divider',
              pl: { md: idx === 0 ? 0 : 2.5 },
            }}
          >
            <Typography
              sx={{
                fontFamily: DISPLAY_FONT,
                fontWeight: 700,
                fontSize: { xs: '1.05rem', md: '1.15rem' },
                letterSpacing: '-0.025em',
                color: 'text.primary',
              }}
            >
              {item.title}
            </Typography>
            <Typography
              variant="body2"
              color="text.secondary"
              sx={{ lineHeight: 1.5, fontSize: '0.86rem', maxWidth: 220 }}
            >
              {item.body}
            </Typography>
          </Stack>
        ))}
      </Box>
    </Box>
  );
}
