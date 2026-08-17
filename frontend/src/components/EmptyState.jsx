import { Box, Button, Typography } from '@mui/material';

export default function EmptyState({ title, description, actionLabel, onAction }) {
  return (
    <Box sx={{ py: 6, px: 3, textAlign: 'center' }}>
      <Typography variant="subtitle1" fontWeight={650}>
        {title}
      </Typography>
      {description ? (
        <Typography
          variant="body2"
          color="text.secondary"
          sx={{ mt: 1, mb: actionLabel ? 2.5 : 0, maxWidth: 360, mx: 'auto' }}
        >
          {description}
        </Typography>
      ) : null}
      {actionLabel && onAction ? (
        <Button variant="contained" size="small" onClick={onAction}>
          {actionLabel}
        </Button>
      ) : null}
    </Box>
  );
}
