import { Alert, Box, Card, CardContent, Typography } from '@mui/material';

const placeholders = [
  "Today's Sales",
  "Today's Bills",
  "Today's Discount",
  "Today's GST",
  'Average Bill',
  'Items Sold',
  'Cancelled Bills',
];

export default function OwnerDashboardPage() {
  return (
    <>
      <Typography variant="h5" gutterBottom>
        Business Overview
      </Typography>
      <Alert severity="info" sx={{ mb: 2 }}>
        Dashboard metrics will connect to report APIs in Sprint 7.
      </Alert>
      <Box
        sx={{
          display: 'grid',
          gap: 2,
          gridTemplateColumns: {
            xs: '1fr',
            sm: '1fr 1fr',
            md: 'repeat(4, 1fr)',
          },
        }}
      >
        {placeholders.map((title) => (
          <Card key={title}>
            <CardContent>
              <Typography variant="body2" color="text.secondary">
                {title}
              </Typography>
              <Typography variant="h5" sx={{ mt: 1 }}>
                —
              </Typography>
            </CardContent>
          </Card>
        ))}
      </Box>
    </>
  );
}