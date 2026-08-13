import { Box, Stack, Typography } from '@mui/material';

/** Section title + optional description/actions above a content block. */
export default function Section({ title, description, actions = null, children, sx = {} }) {
  return (
    <Box sx={sx}>
      {(title || actions) ? (
        <Stack
          direction={{ xs: 'column', sm: 'row' }}
          justifyContent="space-between"
          alignItems={{ xs: 'stretch', sm: 'flex-start' }}
          spacing={1.5}
          sx={{ mb: 2 }}
        >
          <Box sx={{ minWidth: 0 }}>
            {title ? (
              <Typography variant="h6" component="h2">
                {title}
              </Typography>
            ) : null}
            {description ? (
              <Typography variant="body2" color="text.secondary" sx={{ mt: 0.5 }}>
                {description}
              </Typography>
            ) : null}
          </Box>
          {actions}
        </Stack>
      ) : null}
      {children}
    </Box>
  );
}
