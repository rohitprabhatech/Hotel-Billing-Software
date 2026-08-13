import { Alert, Typography } from '@mui/material';

export default function PlaceholderPage({ title, message }) {
  return (
    <>
      <Typography variant="h5" gutterBottom>
        {title}
      </Typography>
      <Alert severity="info">{message}</Alert>
    </>
  );
}