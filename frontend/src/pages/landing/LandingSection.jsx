import { Box, Typography } from '@mui/material';
import { CONTENT_MAX, DISPLAY_FONT } from './constants';

export function LandingSection({
  id,
  eyebrow,
  title,
  body,
  children,
  tone = 'default',
  align = 'left',
}) {
  const ink = tone === 'ink';
  const muted = tone === 'muted';

  return (
    <Box
      id={id}
      component="section"
      sx={{
        position: 'relative',
        px: { xs: 2.5, sm: 3.5, md: 5 },
        py: { xs: 7, md: 10 },
        bgcolor: ink
          ? 'primary.main'
          : muted
            ? (t) =>
                t.palette.mode === 'dark' ? 'rgba(255,255,255,0.022)' : 'rgba(31,78,95,0.03)'
            : 'transparent',
        color: ink ? 'primary.contrastText' : 'text.primary',
        ...(ink
          ? {
              backgroundImage: `
                radial-gradient(700px 320px at 12% 0%, rgba(255,255,255,0.12), transparent 55%),
                radial-gradient(600px 280px at 90% 100%, rgba(0,0,0,0.12), transparent 50%)
              `,
            }
          : {}),
      }}
    >
      <Box
        sx={{
          maxWidth: CONTENT_MAX,
          mx: 'auto',
          textAlign: align === 'center' ? 'center' : 'left',
        }}
      >
        {eyebrow ? (
          <Typography
            variant="overline"
            sx={{
              letterSpacing: '0.16em',
              fontWeight: 700,
              fontSize: '0.68rem',
              color: ink ? 'rgba(255,255,255,0.68)' : 'secondary.main',
            }}
          >
            {eyebrow}
          </Typography>
        ) : null}
        {title ? (
          <Typography
            variant="h3"
            component="h2"
            sx={{
              mt: eyebrow ? 1 : 0,
              mb: body ? 1.35 : 3.5,
              fontFamily: DISPLAY_FONT,
              fontWeight: 700,
              fontSize: { xs: '1.65rem', md: '2.15rem' },
              letterSpacing: '-0.035em',
              maxWidth: align === 'center' ? 720 : 640,
              mx: align === 'center' ? 'auto' : 0,
              lineHeight: 1.18,
            }}
          >
            {title}
          </Typography>
        ) : null}
        {body ? (
          <Typography
            sx={{
              mb: 4,
              maxWidth: align === 'center' ? 620 : 540,
              mx: align === 'center' ? 'auto' : 0,
              fontSize: '1.02rem',
              lineHeight: 1.65,
              color: ink ? 'rgba(255,255,255,0.84)' : 'text.secondary',
            }}
          >
            {body}
          </Typography>
        ) : null}
        {children}
      </Box>
    </Box>
  );
}
