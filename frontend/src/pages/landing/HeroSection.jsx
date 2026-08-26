import ArrowForwardOutlinedIcon from '@mui/icons-material/ArrowForwardOutlined';
import { Box, Button, Stack, Typography } from '@mui/material';
import { Link as RouterLink } from 'react-router-dom';
import { COMPANY } from '../../constants/company';
import { PATHS } from '../../routes/paths';
import { CONTENT_MAX, DISPLAY_FONT } from './constants';

function planHeadline(plans) {
  const first = plans?.[0];
  if (!first) return COMPANY.planPriceLabel;
  const period = first.billing_cycle === 'YEARLY' ? 'year' : 'month';
  return `₹${Number(first.price).toLocaleString('en-IN')} / ${period}`;
}

/** Full-bleed first viewport — brand, one headline, one line, CTAs. No cards. */
export default function HeroSection({ isDark, scrollToHash, plans = [] }) {
  return (
    <Box
      component="section"
      sx={{
        position: 'relative',
        overflow: 'hidden',
        minHeight: { xs: 'calc(100vh - 64px)', md: 'min(92vh, 820px)' },
        display: 'flex',
        alignItems: 'flex-end',
        color: '#F4F8FA',
        background: isDark
          ? `
            linear-gradient(180deg, rgba(8,14,20,0.35) 0%, rgba(8,14,20,0.78) 55%, #0A1016 100%),
            radial-gradient(1200px 640px at 70% 20%, rgba(110,180,200,0.28), transparent 58%),
            linear-gradient(135deg, #0A1218 0%, #152430 55%, #1A3544 100%)
          `
          : `
            linear-gradient(180deg, rgba(12,40,52,0.25) 0%, rgba(18,58,72,0.72) 48%, #123A48 100%),
            radial-gradient(1100px 620px at 78% 8%, rgba(158,210,224,0.35), transparent 55%),
            linear-gradient(145deg, #1F4E5F 0%, #163A47 42%, #0F2C36 100%)
          `,
        '&::before': {
          content: '""',
          position: 'absolute',
          inset: 0,
          backgroundImage: `
            linear-gradient(90deg, rgba(255,255,255,0.04) 1px, transparent 1px),
            linear-gradient(rgba(255,255,255,0.04) 1px, transparent 1px)
          `,
          backgroundSize: '72px 72px',
          maskImage: 'linear-gradient(180deg, rgba(0,0,0,0.55), transparent 85%)',
          pointerEvents: 'none',
        },
        '&::after': {
          content: '""',
          position: 'absolute',
          right: { xs: '-20%', md: '0%' },
          top: { xs: '8%', md: '0%' },
          width: { xs: '90%', md: '48%' },
          height: { xs: '55%', md: '100%' },
          background: `
            radial-gradient(ellipse at 60% 40%, rgba(255,255,255,0.12), transparent 62%),
            linear-gradient(160deg, rgba(255,255,255,0.08), transparent 70%)
          `,
          pointerEvents: 'none',
        },
        '@keyframes heroRise': {
          from: { opacity: 0, transform: 'translateY(20px)' },
          to: { opacity: 1, transform: 'translateY(0)' },
        },
        '@keyframes heroSheen': {
          '0%, 100%': { opacity: 0.55 },
          '50%': { opacity: 0.85 },
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
          pt: { xs: 8, md: 10 },
          pb: { xs: 7, md: 9 },
          animation: 'heroRise 0.8s ease-out both',
        }}
      >
        <Typography
          component="p"
          sx={{
            mb: 2,
            fontFamily: DISPLAY_FONT,
            fontWeight: 600,
            fontSize: '0.78rem',
            letterSpacing: '0.16em',
            textTransform: 'uppercase',
            color: 'rgba(244,248,250,0.72)',
          }}
        >
          {COMPANY.legalName}
        </Typography>

        <Typography
          component="h1"
          sx={{
            fontFamily: DISPLAY_FONT,
            fontWeight: 700,
            fontSize: { xs: '2.75rem', sm: '3.6rem', md: '4.35rem' },
            lineHeight: 0.96,
            letterSpacing: '-0.045em',
            mb: 2,
            maxWidth: 720,
            textShadow: '0 12px 40px rgba(0,0,0,0.25)',
          }}
        >
          {COMPANY.productName}
        </Typography>

        <Typography
          component="p"
          sx={{
            fontFamily: DISPLAY_FONT,
            fontWeight: 600,
            fontSize: { xs: '1.15rem', md: '1.35rem' },
            lineHeight: 1.4,
            letterSpacing: '-0.02em',
            color: 'rgba(244,248,250,0.9)',
            mb: 3.5,
            maxWidth: 480,
          }}
        >
          Billing for the counter — stock-safe, GST-ready, multi-business.
        </Typography>

        <Stack
          direction={{ xs: 'column', sm: 'row' }}
          spacing={1.25}
          sx={{ mb: 2.5, '& > *': { width: { xs: '100%', sm: 'auto' } } }}
        >
          <Button
            component={RouterLink}
            to={PATHS.register}
            variant="contained"
            size="large"
            endIcon={<ArrowForwardOutlinedIcon />}
            sx={{
              px: 2.75,
              py: 1.35,
              borderRadius: 1.25,
              fontSize: '0.95rem',
              bgcolor: '#F4F8FA',
              color: '#123A48',
              boxShadow: 'none',
              '&:hover': { bgcolor: '#FFFFFF', boxShadow: 'none' },
            }}
          >
            Register Your Business
          </Button>
          <Button
            component={RouterLink}
            to={PATHS.login}
            variant="outlined"
            size="large"
            sx={{
              px: 2.75,
              py: 1.35,
              borderRadius: 1.25,
              fontSize: '0.95rem',
              borderColor: 'rgba(244,248,250,0.45)',
              color: '#F4F8FA',
              '&:hover': {
                borderColor: '#F4F8FA',
                bgcolor: 'rgba(255,255,255,0.08)',
              },
            }}
          >
            Login
          </Button>
          <Button
            variant="text"
            size="large"
            onClick={() => scrollToHash('#features')}
            sx={{
              px: 1.5,
              py: 1.35,
              color: 'rgba(244,248,250,0.82)',
              textDecoration: 'underline',
              textUnderlineOffset: 4,
              '&:hover': { bgcolor: 'transparent', color: '#FFFFFF' },
            }}
          >
            See features
          </Button>
        </Stack>

        <Typography
          variant="body2"
          sx={{
            letterSpacing: '0.02em',
            color: 'rgba(244,248,250,0.62)',
            animation: 'heroSheen 6s ease-in-out infinite',
          }}
        >
          From {planHeadline(plans)} · Contact to activate
        </Typography>
      </Box>
    </Box>
  );
}
