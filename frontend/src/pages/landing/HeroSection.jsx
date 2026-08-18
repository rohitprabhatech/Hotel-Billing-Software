import ArrowForwardOutlinedIcon from '@mui/icons-material/ArrowForwardOutlined';
import { Box, Button, Stack, Typography } from '@mui/material';
import { Link as RouterLink } from 'react-router-dom';
import { COMPANY } from '../../constants/company';
import { PATHS } from '../../routes/paths';
import BillingDashboardMock from './BillingDashboardMock';
import { CONTENT_MAX, DISPLAY_FONT } from './constants';

function planHeadline(plans) {
  const first = plans?.[0];
  if (!first) return COMPANY.planPriceLabel;
  const period = first.billing_cycle === 'YEARLY' ? 'year' : 'month';
  return `₹${Number(first.price).toLocaleString('en-IN')} / ${period}`;
}

export default function HeroSection({ isDark, scrollToHash, plans = [] }) {
  return (
    <Box
      component="section"
      sx={{
        position: 'relative',
        overflow: 'hidden',
        minHeight: { xs: 'auto', lg: 'calc(100vh - 64px)' },
        display: 'flex',
        alignItems: 'center',
        borderBottom: '1px solid',
        borderColor: 'divider',
        background: isDark
          ? `
            radial-gradient(1200px 560px at 78% 12%, rgba(110,180,200,0.2), transparent 55%),
            radial-gradient(800px 480px at 8% 88%, rgba(224,138,90,0.07), transparent 50%),
            linear-gradient(155deg, #0A1016 0%, #121C24 48%, #152430 100%)
          `
          : `
            radial-gradient(1100px 520px at 85% -10%, rgba(31,78,95,0.14), transparent 52%),
            radial-gradient(720px 420px at -5% 110%, rgba(196,92,38,0.07), transparent 48%),
            linear-gradient(165deg, #F7FAFB 0%, #EEF3F6 42%, #E8EFF3 100%)
          `,
        '&::before': {
          content: '""',
          position: 'absolute',
          inset: 0,
          opacity: isDark ? 0.22 : 0.35,
          backgroundImage: `url("data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.85' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)' opacity='0.45'/%3E%3C/svg%3E")`,
          backgroundSize: '180px 180px',
          pointerEvents: 'none',
          mixBlendMode: isDark ? 'soft-light' : 'multiply',
        },
        '@keyframes heroRise': {
          from: { opacity: 0, transform: 'translateY(18px)' },
          to: { opacity: 1, transform: 'translateY(0)' },
        },
        '@keyframes heroFloat': {
          '0%, 100%': { transform: 'translateY(0)' },
          '50%': { transform: 'translateY(-8px)' },
        },
      }}
    >
      <Box
        sx={{
          position: 'relative',
          zIndex: 1,
          width: '100%',
          maxWidth: CONTENT_MAX,
          mx: 'auto',
          px: { xs: 2.5, sm: 3.5, md: 5 },
          py: { xs: 6, md: 8, lg: 7 },
          display: 'grid',
          gap: { xs: 5, lg: 6 },
          gridTemplateColumns: { xs: '1fr', lg: 'minmax(0, 0.95fr) minmax(0, 1.05fr)' },
          alignItems: 'center',
        }}
      >
        <Box sx={{ maxWidth: 560, animation: 'heroRise 0.75s ease-out both' }}>
          <Typography
            component="p"
            sx={{
              mb: 1.5,
              fontFamily: DISPLAY_FONT,
              fontWeight: 600,
              fontSize: '0.8rem',
              letterSpacing: '0.12em',
              textTransform: 'uppercase',
              color: 'secondary.main',
            }}
          >
            by Prabha Technology
          </Typography>

          <Typography
            component="h1"
            sx={{
              fontFamily: DISPLAY_FONT,
              fontWeight: 700,
              fontSize: { xs: '2.65rem', sm: '3.35rem', md: '3.85rem' },
              lineHeight: 0.98,
              letterSpacing: '-0.045em',
              mb: 2,
              color: 'text.primary',
            }}
          >
            {COMPANY.productName}
          </Typography>

          <Typography
            component="p"
            sx={{
              fontFamily: DISPLAY_FONT,
              fontWeight: 600,
              fontSize: { xs: '1.2rem', md: '1.35rem' },
              lineHeight: 1.35,
              letterSpacing: '-0.02em',
              color: 'text.primary',
              mb: 1.5,
              maxWidth: 440,
            }}
          >
            Billing, stock, and sales — one calm system for the counter.
          </Typography>

          <Typography
            sx={{
              fontSize: { xs: '0.98rem', md: '1.05rem' },
              lineHeight: 1.65,
              color: 'text.secondary',
              mb: 3.25,
              maxWidth: 460,
            }}
          >
            Built for restaurants, kirana, grocery, clothing, and retail teams who need GST-ready
            bills without juggling spreadsheets.
          </Typography>

          <Stack
            direction={{ xs: 'column', sm: 'row' }}
            spacing={1.25}
            sx={{ mb: 2, '& > *': { width: { xs: '100%', sm: 'auto' } } }}
          >
            <Button
              component={RouterLink}
              to={PATHS.register}
              variant="contained"
              size="large"
              endIcon={<ArrowForwardOutlinedIcon />}
              sx={{
                px: 2.75,
                py: 1.3,
                borderRadius: 1.5,
                fontSize: '0.95rem',
                boxShadow: isDark ? 'none' : '0 12px 32px rgba(31,78,95,0.28)',
              }}
            >
              Register Your Business
            </Button>
            <Button
              variant="outlined"
              size="large"
              onClick={() => scrollToHash('#features')}
              sx={{
                px: 2.75,
                py: 1.3,
                borderRadius: 1.5,
                fontSize: '0.95rem',
                borderColor: 'divider',
                bgcolor: isDark ? 'rgba(255,255,255,0.03)' : 'rgba(255,255,255,0.55)',
                backdropFilter: 'blur(8px)',
              }}
            >
              See what&apos;s included
            </Button>
          </Stack>

          <Typography variant="body2" color="text.secondary" sx={{ letterSpacing: '0.01em' }}>
            {planHeadline(plans)}
            <Box component="span" sx={{ mx: 1, opacity: 0.45 }}>
              ·
            </Box>
            Contact to activate
          </Typography>
        </Box>

        <Box
          sx={{
            minWidth: 0,
            display: 'flex',
            justifyContent: { xs: 'center', lg: 'flex-end' },
            animation: 'heroRise 0.9s ease-out 0.12s both, heroFloat 7s ease-in-out 1.1s infinite',
            '@media (prefers-reduced-motion: reduce)': {
              animation: 'heroRise 0.01s both',
            },
          }}
        >
          <BillingDashboardMock />
        </Box>
      </Box>
    </Box>
  );
}
