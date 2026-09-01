import { Box, Stack, Typography } from '@mui/material';

/** Section title + optional description/actions above a content block. */
export default function Section({ title, description, actions = null, children, sx = {} }) {
  return (
    <Box sx={sx}>
      {title || actions ? (
        <Stack
          direction={{ xs: 'column', sm: 'row' }}
          justifyContent="space-between"
          alignItems={{ xs: 'stretch', sm: 'flex-start' }}
          spacing={1.5}
          sx={{ mb: 2 }}
        >
          <Box sx={{ minWidth: 0 }}>
            {title ? (
              <Typography
                variant="h6"
                component="h2"
                sx={{ fontWeight: 650, letterSpacing: '-0.01em', lineHeight: 1.3 }}
              >
                {title}
              </Typography>
            ) : null}
            {description ? (
              <Typography
                variant="body2"
                color="text.secondary"
                sx={{ mt: 0.5, maxWidth: 640, lineHeight: 1.5 }}
              >
                {description}
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
                width: { xs: '100%', sm: 'auto' },
                '& > *': { flexGrow: { xs: 1, sm: 0 } },
              }}
            >
              {actions}
            </Stack>
          ) : null}
        </Stack>
      ) : null}
      {children}
    </Box>
  );
}
