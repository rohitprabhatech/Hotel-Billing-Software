import { Box, Stack, Typography } from '@mui/material';
import { COMPANY } from '../constants/company';

/**
 * Prabha Technology brand mark — logo from prabhatechnology.com with optional wordmark.
 */
export default function BrandLogo({
  size = 40,
  showText = true,
  title = COMPANY.shortName,
  subtitle = null,
  textColor = 'inherit',
  mutedColor = 'text.secondary',
  href = COMPANY.website,
}) {
  const logo = (
    <Box
      component="img"
      src={COMPANY.logoPath}
      alt={COMPANY.legalName}
      sx={{
        width: size,
        height: size,
        objectFit: 'contain',
        flexShrink: 0,
        display: 'block',
      }}
    />
  );

  const content = (
    <Stack direction="row" spacing={1.5} alignItems="center" sx={{ minWidth: 0 }}>
      {href ? (
        <Box
          component="a"
          href={href}
          target="_blank"
          rel="noopener noreferrer"
          sx={{ lineHeight: 0, flexShrink: 0 }}
          aria-label={`${COMPANY.legalName} website`}
        >
          {logo}
        </Box>
      ) : (
        logo
      )}
      {showText ? (
        <Box sx={{ minWidth: 0 }}>
          <Typography
            variant="subtitle1"
            fontWeight={700}
            noWrap
            sx={{ color: textColor, lineHeight: 1.25 }}
          >
            {title}
          </Typography>
          {subtitle ? (
            <Typography variant="caption" noWrap sx={{ color: mutedColor, display: 'block' }}>
              {subtitle}
            </Typography>
          ) : null}
        </Box>
      ) : null}
    </Stack>
  );

  return content;
}
