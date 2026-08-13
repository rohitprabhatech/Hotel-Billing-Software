import { Alert, Box, Button, Card, CardContent, Typography } from '@mui/material';
import { useEffect, useState } from 'react';
import { Link as RouterLink } from 'react-router-dom';
import { fetchTodaySummary, listBills } from '../../services/billService';

export default function BillingHomePage() {
  const [summary, setSummary] = useState({ total_sales: 0, bill_count: 0 });
  const [recent, setRecent] = useState([]);
  const [error, setError] = useState('');

  useEffect(() => {
    Promise.all([
      fetchTodaySummary(),
      listBills({ today: true, per_page: 5 }),
    ])
      .then(([summaryRes, billsRes]) => {
        setSummary(summaryRes.data || { total_sales: 0, bill_count: 0 });
        setRecent(billsRes.data || []);
      })
      .catch((err) => {
        setError(err.response?.data?.error?.message || 'Failed to load billing dashboard');
      });
  }, []);

  return (
    <>
      <Typography variant="h5" gutterBottom>
        Billing Dashboard
      </Typography>
      {error ? <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert> : null}

      <Box
        sx={{
          display: 'grid',
          gap: 2,
          gridTemplateColumns: { xs: '1fr', sm: '1fr 1fr', md: 'repeat(4, 1fr)' },
          mb: 3,
        }}
      >
        <Card>
          <CardContent>
            <Typography variant="body2" color="text.secondary">New Bill</Typography>
            <Button component={RouterLink} to="/billing/new" variant="contained" sx={{ mt: 1.5 }}>
              Start
            </Button>
          </CardContent>
        </Card>
        <Card>
          <CardContent>
            <Typography variant="body2" color="text.secondary">Today&apos;s Bills</Typography>
            <Typography variant="h5" sx={{ mt: 1 }}>{summary.bill_count}</Typography>
          </CardContent>
        </Card>
        <Card>
          <CardContent>
            <Typography variant="body2" color="text.secondary">Today&apos;s Total Sales</Typography>
            <Typography variant="h5" sx={{ mt: 1 }}>
              ₹{Number(summary.total_sales || 0).toFixed(2)}
            </Typography>
          </CardContent>
        </Card>
        <Card>
          <CardContent>
            <Typography variant="body2" color="text.secondary">Recent Bills</Typography>
            <Typography variant="h5" sx={{ mt: 1 }}>{recent.length}</Typography>
          </CardContent>
        </Card>
      </Box>

      <Typography variant="h6" gutterBottom>Recent Bills</Typography>
      {recent.map((bill) => (
        <Box
          key={bill.id}
          sx={{
            bgcolor: 'background.paper',
            borderRadius: 2,
            p: 2,
            mb: 1,
            display: 'flex',
            justifyContent: 'space-between',
          }}
        >
          <Typography>#{bill.bill_number}</Typography>
          <Typography>₹{Number(bill.grand_total).toFixed(2)}</Typography>
          <Typography color="text.secondary">{bill.status}</Typography>
        </Box>
      ))}
      {!recent.length ? (
        <Typography color="text.secondary">No bills yet today.</Typography>
      ) : null}
    </>
  );
}