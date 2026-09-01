import InboxOutlinedIcon from '@mui/icons-material/InboxOutlined';
import { Box, Button, Typography } from '@mui/material';

export default function EmptyState({ title, description, actionLabel, onAction, icon = null }) {
  return (
    <Box
      sx={{
        py: 6,
        px: 3,
        textAlign: 'center',
        border: '1px dashed',
        borderColor: 'divider',
        borderRadius: 2,
        bgcolor: 'background.paper',
      }}
    >
      <Box
        sx={{
          width: 48,
          height: 48,
          borderRadius: 2,
          mx: 'auto',
          mb: 1.5,
          display: 'grid',
          placeItems: 'center',
          bgcolor: (theme) =>
            theme.palette.mode === 'dark' ? 'rgba(255,255,255,0.04)' : 'rgba(31, 78, 95, 0.06)',
          color: 'text.secondary',
        }}
      >
        {icon || <InboxOutlinedIcon />}
      </Box>
      <Typography variant="subtitle1" fontWeight={650}>
        {title}
      </Typography>
      {description ? (
        <Typography
          variant="body2"
          color="text.secondary"
          sx={{ mt: 1, mb: actionLabel ? 2.5 : 0, maxWidth: 420, mx: 'auto', lineHeight: 1.55 }}
        >
          {description}
        </Typography>
      ) : null}
      {actionLabel && onAction ? (
        <Button variant="contained" onClick={onAction}>
          {actionLabel}
        </Button>
      ) : null}
    </Box>
  );
}
