import { Card, CardContent, Stack, Typography } from '@mui/material';

/**
 * Shared card section for Profile / Settings / Change Password style forms.
 * Not for dashboard KPI chrome — only interactive form groupings.
 */
export default function FormSection({ title, description, actions, children }) {
  return (
    <Card>
      <CardContent sx={{ p: { xs: 2.5, sm: 3 }, '&:last-child': { pb: { xs: 2.5, sm: 3 } } }}>
        <Stack
          direction={{ xs: 'column', sm: 'row' }}
          justifyContent="space-between"
          alignItems={{ xs: 'flex-start', sm: 'flex-start' }}
          spacing={1.5}
          sx={{ mb: 3 }}
        >
          <Stack spacing={0.75}>
            {title ? (
              <Typography variant="h6" component="h2">
                {title}
              </Typography>
            ) : null}
            {description ? (
              <Typography variant="body2" color="text.secondary" sx={{ maxWidth: 560 }}>
                {description}
              </Typography>
            ) : null}
          </Stack>
          {actions || null}
        </Stack>
        {children}
      </CardContent>
    </Card>
  );
}
