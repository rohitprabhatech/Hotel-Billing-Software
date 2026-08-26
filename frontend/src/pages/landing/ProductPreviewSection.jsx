import { Box, Typography } from '@mui/material';
import BillingDashboardMock from './BillingDashboardMock';
import { CONTENT_MAX, DISPLAY_FONT } from './constants';

/** Product visual after the hero — interactive mock is allowed outside first viewport. */
export default function ProductPreviewSection() {
  return (
    <Box
      component="section"
      aria-label="Product preview"
      sx={{
        borderBottom: '1px solid',
        borderColor: 'divider',
        bgcolor: (t) => (t.palette.mode === 'dark' ? 'background.default' : '#F7FAFB'),
        px: { xs: 2.5, sm: 3.5, md: 5 },
        py: { xs: 5, md: 7 },
      }}
    >
      <Box sx={{ maxWidth: CONTENT_MAX, mx: 'auto' }}>
        <Typography
          component="h2"
          sx={{
            fontFamily: DISPLAY_FONT,
            fontWeight: 700,
            fontSize: { xs: '1.45rem', md: '1.75rem' },
            letterSpacing: '-0.03em',
            mb: 1,
            textAlign: 'center',
          }}
        >
          Built for the busy counter
        </Typography>
        <Typography
          color="text.secondary"
          sx={{
            textAlign: 'center',
            maxWidth: 520,
            mx: 'auto',
            mb: { xs: 3.5, md: 4.5 },
            lineHeight: 1.55,
          }}
        >
          Fast bills, live stock awareness, and owner clarity — without spreadsheet chaos.
        </Typography>
        <Box sx={{ display: 'flex', justifyContent: 'center' }}>
          <BillingDashboardMock />
        </Box>
      </Box>
    </Box>
  );
}
