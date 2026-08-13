import { Alert, Box, Button, Card, CardContent, Typography } from '@mui/material';
import { Link as RouterLink } from 'react-router-dom';

const cards = [
  { title: 'New Bill', value: 'Start', to: '/billing/new' },
  { title: "Today's Bills", value: '—', to: '/billing/bills' },
  { title: "Today's Total Sales", value: '—' },
  { title: 'Recent Bills', value: '—' },
];

export default function BillingHomePage() {
  return (
    <>
      <Typography variant="h5" gutterBottom>
        Billing Dashboard
      </Typography>
      <Alert severity="info" sx={{ mb: 2 }}>
        Fast billing UI will be built in Sprint 5. API foundation is ready.
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
        {cards.map((card) => (
          <Card key={card.title}>
            <CardContent>
              <Typography variant="body2" color="text.secondary">
                {card.title}
              </Typography>
              <Typography variant="h5" sx={{ mt: 1, mb: 1.5 }}>
                {card.value}
              </Typography>
              {card.to ? (
                <Button
                  component={RouterLink}
                  to={card.to}
                  variant="outlined"
                  size="small"
                >
                  Open
                </Button>
              ) : null}
            </CardContent>
          </Card>
        ))}
      </Box>
    </>
  );
}