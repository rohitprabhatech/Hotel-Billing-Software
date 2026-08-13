import PointOfSaleOutlinedIcon from '@mui/icons-material/PointOfSaleOutlined';
import ReceiptLongOutlinedIcon from '@mui/icons-material/ReceiptLongOutlined';
import {
  Alert,
  Box,
  Button,
  Card,
  CardContent,
  Stack,
  Typography,
} from '@mui/material';
import { useEffect, useState } from 'react';
import { Link as RouterLink } from 'react-router-dom';
import KpiCard from '../../components/KpiCard';
import { useAuth } from '../../context/AuthContext';
import { fetchTodaySummary, listBills } from '../../services/billService';
import { PATHS } from '../../routes/paths';

export default function BillingHomePage() {
  const { role } = useAuth();
  const [summary, setSummary] = useState({ total_sales: 0, bill_count: 0 });
  const [recent, setRecent] = useState([]);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
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
      })
      .finally(() => setLoading(false));
  }, []);

  return (
    <>
      {role === 'OWNER' ? (
        <Alert severity="info" sx={{ mb: 2 }}>
          You are in the Billing workspace. Use <strong>Owner Dashboard</strong> in the sidebar,
          header, or breadcrumb to return to the main Owner console.
        </Alert>
      ) : null}
      {error ? <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert> : null}

      <Box
        sx={{
          display: 'grid',
          gap: 2,
          gridTemplateColumns: { xs: '1fr', sm: '1fr 1fr', md: 'repeat(4, 1fr)' },
          mb: 3,
        }}
      >
        <Card sx={{ height: '100%' }}>
          <CardContent>
            <Typography variant="body2" color="text.secondary">
              Quick action
            </Typography>
            <Typography variant="h6" sx={{ mt: 0.5, mb: 1.5 }}>
              Start a new bill
            </Typography>
            <Button
              component={RouterLink}
              to={PATHS.billingNew}
              variant="contained"
              startIcon={<PointOfSaleOutlinedIcon />}
            >
              New Bill
            </Button>
          </CardContent>
        </Card>
        <KpiCard
          title="Today's Bills"
          value={loading ? '—' : summary.bill_count}
          icon={<ReceiptLongOutlinedIcon fontSize="small" />}
        />
        <KpiCard
          title="Today's Sales"
          value={
            loading
              ? '—'
              : `₹${Number(summary.total_sales || 0).toLocaleString('en-IN', {
                  minimumFractionDigits: 2,
                  maximumFractionDigits: 2,
                })}`
          }
          icon={<PointOfSaleOutlinedIcon fontSize="small" />}
        />
        <KpiCard
          title="Cash"
          value={
            loading
              ? '—'
              : `₹${Number(summary.cash_sales || 0).toLocaleString('en-IN', {
                  minimumFractionDigits: 2,
                  maximumFractionDigits: 2,
                })}`
          }
          hint="Today's cash sales"
        />
        <KpiCard
          title="Online"
          value={
            loading
              ? '—'
              : `₹${Number(summary.online_sales || 0).toLocaleString('en-IN', {
                  minimumFractionDigits: 2,
                  maximumFractionDigits: 2,
                })}`
          }
          hint="Today's online sales"
        />
      </Box>

      <Stack direction="row" justifyContent="space-between" alignItems="center" mb={1.5}>
        <Typography variant="h6">Recent Bills</Typography>
        <Button component={RouterLink} to={PATHS.billingBills} size="small">
          View all
        </Button>
      </Stack>

      <Card>
        <CardContent sx={{ p: 0, '&:last-child': { pb: 0 } }}>
          {recent.map((bill) => (
            <Box
              key={bill.id}
              sx={{
                px: 2,
                py: 1.5,
                display: 'flex',
                justifyContent: 'space-between',
                gap: 2,
                borderBottom: '1px solid',
                borderColor: 'divider',
                '&:last-child': { borderBottom: 0 },
              }}
            >
              <Box sx={{ minWidth: 0 }}>
                <Typography fontWeight={600}>#{bill.bill_number}</Typography>
                <Typography variant="caption" color="text.secondary">
                  {bill.payment_method_label
                    || (bill.payment_method === 'online' ? 'Online' : 'Cash')}
                  {' · '}
                  {bill.status}
                </Typography>
              </Box>
              <Typography fontVariantNumeric="tabular-nums" fontWeight={650}>
                ₹{Number(bill.grand_total).toFixed(2)}
              </Typography>
            </Box>
          ))}
          {!loading && !recent.length ? (
            <Box sx={{ p: 3 }}>
              <Typography color="text.secondary">No bills yet today.</Typography>
            </Box>
          ) : null}
        </CardContent>
      </Card>
    </>
  );
}
