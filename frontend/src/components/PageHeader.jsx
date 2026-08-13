import { Box, Breadcrumbs, Link, Stack, Typography } from '@mui/material';
import { Link as RouterLink } from 'react-router-dom';

/**
 * Single page header: title + description (left), primary actions (right).
 * Spacing below header: 24px before first content section.
 */
export default function PageHeader({ title, subtitle, crumbs = [], actions = null }) {
  return (
    <Stack
      direction={{ xs: 'column', sm: 'row' }}
      justifyContent="space-between"
      alignItems={{ xs: 'stretch', sm: 'flex-start' }}
      spacing={2}
      sx={{ mb: 3 }}
    >
      <Box sx={{ minWidth: 0, flex: 1, pr: { sm: 2 } }}>
        {crumbs.length ? (
          <Breadcrumbs sx={{ mb: 1 }} aria-label="breadcrumb">
            {crumbs.map((crumb, index) => {
              const last = index === crumbs.length - 1;
              if (last || !crumb.to) {
                return (
                  <Typography key={`${crumb.label}-${index}`} color="text.primary" variant="body2">
                    {crumb.label}
                  </Typography>
                );
              }
              return (
                <Link
                  key={`${crumb.label}-${index}`}
                  component={RouterLink}
                  to={crumb.to}
                  underline="hover"
                  color="inherit"
                  variant="body2"
                >
                  {crumb.label}
                </Link>
              );
            })}
          </Breadcrumbs>
        ) : null}
        <Typography
          variant="h5"
          component="h1"
          sx={{
            lineHeight: 1.3,
            fontSize: { xs: '1.35rem', md: '1.5rem' },
            fontWeight: 650,
          }}
        >
          {title}
        </Typography>
        {subtitle ? (
          <Typography
            variant="body2"
            color="text.secondary"
            sx={{ mt: 0.75, maxWidth: 640, lineHeight: 1.5 }}
          >
            {subtitle}
          </Typography>
        ) : null}
      </Box>
      {actions ? (
        <Stack
          direction="row"
          spacing={1}
          useFlexGap
          flexWrap="wrap"
          sx={{
            flexShrink: 0,
            pt: { sm: crumbs.length ? 3.5 : 0.25 },
          }}
        >
          {actions}
        </Stack>
      ) : null}
    </Stack>
  );
}
