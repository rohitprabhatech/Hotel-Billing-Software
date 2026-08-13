import { Alert, Typography } from '@mui/material';

export default function NewBillPage() {
  return (
    <>
      <Typography variant="h5" gutterBottom>
        New Bill
      </Typography>
      <Alert severity="info">
        Item search, cart, discount, and finalize arrive in Sprint 5.
      </Alert>
    </>
  );
}