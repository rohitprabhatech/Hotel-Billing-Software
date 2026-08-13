import { Alert, Typography } from '@mui/material';

export default function BillingBillsPage() {
  return (
    <>
      <Typography variant="h5" gutterBottom>
        Today&apos;s Bills
      </Typography>
      <Alert severity="info">Bill history and reprint arrive in Sprint 6.</Alert>
    </>
  );
}