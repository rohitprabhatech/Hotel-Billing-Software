import PointOfSaleOutlinedIcon from '@mui/icons-material/PointOfSaleOutlined';
import ReceiptLongOutlinedIcon from '@mui/icons-material/ReceiptLongOutlined';
import {
  Alert,
  Box,
  Button,
  CircularProgress,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
} from '@mui/material';
import { useEffect, useState } from 'react';
import { Link as RouterLink, useNavigate } from 'react-router-dom';
import EmptyState from '../../components/EmptyState';
import KpiCard from '../../components/KpiCard';
import PageShell from '../../components/PageShell';
import Section from '../../components/Section';
import TableCard from '../../components/TableCard';
import { PageActions } from '../../context/PageActionsContext';
import { useAuth } from '../../context/AuthContext';
import { fetchTodaySummary, listBills } from '../../services/billService';
import { PATHS } from '../../routes/paths';
import { paymentMethodLabel } from '../../utils/paymentMethod';

export default function BillingHomePage() {
  const { role } = useAuth();
  const navigate = useNavigate();
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
      <PageActions>
        <Button
          component={RouterLink}
          to={PATHS.billingNew}
          variant="contained"
          startIcon={<PointOfSaleOutlinedIcon />}
        >
          New Bill
        </Button>
      </PageActions>

      <PageShell>
        {role === 'OWNER' ? (
          <Alert severity="info">
            You are in the Billing workspace. Use <strong>Owner Dashboard</strong> in the sidebar
            to return to the main Owner console.
          </Alert>
        ) : null}
        {error ? <Alert severity="error">{error}</Alert> : null}

        <Box
          sx={{
            display: 'grid',
            gap: 2,
            gridTemplateColumns: {
              xs: '1fr',
              sm: '1fr 1fr',
              lg: 'repeat(4, 1fr)',
            },
          }}
        >
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

        <Section
          title="Recent Bills"
          description="Latest bills created today."
          actions={
            <Button component={RouterLink} to={PATHS.billingBills} size="small">
              View all
            </Button>
          }
        >
          <TableCard>
            {loading ? (
              <Box sx={{ py: 6, display: 'grid', placeItems: 'center' }}>
                <CircularProgress size={28} />
              </Box>
            ) : (
              <Table size="small" sx={{ minWidth: 480 }}>
                <TableHead>
                  <TableRow>
                    <TableCell>Bill No</TableCell>
                    <TableCell>Payment</TableCell>
                    <TableCell>Status</TableCell>
                    <TableCell align="right">Total</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {recent.map((bill) => (
                    <TableRow key={bill.id} hover>
                      <TableCell sx={{ fontWeight: 600, fontVariantNumeric: 'tabular-nums' }}>
                        #{bill.bill_number}
                      </TableCell>
                      <TableCell>
                        {bill.payment_method_label || paymentMethodLabel(bill.payment_method)}
                      </TableCell>
                      <TableCell>{bill.status}</TableCell>
                      <TableCell align="right" sx={{ fontVariantNumeric: 'tabular-nums', fontWeight: 650 }}>
                        ₹{Number(bill.grand_total).toFixed(2)}
                      </TableCell>
                    </TableRow>
                  ))}
                  {!recent.length ? (
                    <TableRow>
                      <TableCell colSpan={4} sx={{ p: 0, border: 0 }}>
                        <EmptyState
                          title="No bills yet today"
                          description="Create a new bill to see it here."
                          actionLabel="New Bill"
                          onAction={() => navigate(PATHS.billingNew)}
                        />
                      </TableCell>
                    </TableRow>
                  ) : null}
                </TableBody>
              </Table>
            )}
          </TableCard>
        </Section>
      </PageShell>
    </>
  );
}
