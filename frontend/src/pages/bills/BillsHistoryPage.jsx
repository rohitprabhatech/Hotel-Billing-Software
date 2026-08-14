import {
  Alert,
  Box,
  Button,
  Chip,
  CircularProgress,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  FormControl,
  InputLabel,
  MenuItem,
  Select,
  Stack,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
  TextField,
} from '@mui/material';
import { useEffect, useState } from 'react';
import EmptyState from '../../components/EmptyState';
import FilterBar from '../../components/FilterBar';
import PageShell from '../../components/PageShell';
import TableCard from '../../components/TableCard';
import { filterControlSx } from '../../layouts/shell';
import {
  cancelBill,
  getBill,
  listBills,
  openBillPrint,
} from '../../services/billService';
import BillPreview from '../../print/BillPreview';
import { PAYMENT_CASH, PAYMENT_ONLINE, paymentMethodLabel } from '../../utils/paymentMethod';

export default function BillsHistoryPage({ todayDefault = false }) {
  const [bills, setBills] = useState([]);
  const [q, setQ] = useState('');
  const [status, setStatus] = useState('');
  const [paymentMethod, setPaymentMethod] = useState('');
  const [todayOnly, setTodayOnly] = useState(todayDefault);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [selected, setSelected] = useState(null);
  const [cancelOpen, setCancelOpen] = useState(false);
  const [cancelReason, setCancelReason] = useState('');
  const [saving, setSaving] = useState(false);
  const [loading, setLoading] = useState(true);

  const load = async () => {
    setError('');
    setLoading(true);
    try {
      const res = await listBills({
        q: q || undefined,
        status: status || undefined,
        payment_method: paymentMethod || undefined,
        today: todayOnly || undefined,
        per_page: 100,
      });
      setBills(res.data || []);
    } catch (err) {
      setError(err.response?.data?.error?.message || 'Failed to load bills');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [status, todayOnly, paymentMethod]);

  const openDetails = async (bill) => {
    setError('');
    try {
      const res = await getBill(bill.id);
      setSelected(res.data);
    } catch (err) {
      setError(err.response?.data?.error?.message || 'Failed to load bill details');
    }
  };

  const onCancel = async () => {
    if (!selected) return;
    setSaving(true);
    setError('');
    setSuccess('');
    try {
      const res = await cancelBill(selected.id, cancelReason);
      setSelected(res.data);
      setCancelOpen(false);
      setCancelReason('');
      setSuccess(`Bill #${res.data.bill_number} cancelled`);
      await load();
    } catch (err) {
      setError(err.response?.data?.error?.message || 'Failed to cancel bill');
    } finally {
      setSaving(false);
    }
  };

  return (
    <PageShell>
      <FilterBar
        actions={
          <Button variant="outlined" onClick={load} disabled={loading}>
            Search
          </Button>
        }
      >
        <TextField
          label="Search bill / reference"
          value={q}
          onChange={(e) => setQ(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === 'Enter') load();
          }}
          sx={{ flex: 1, minWidth: { xs: '100%', sm: 200 } }}
        />
        <FormControl sx={filterControlSx}>
          <InputLabel>Status</InputLabel>
          <Select
            label="Status"
            value={status}
            onChange={(e) => setStatus(e.target.value)}
          >
            <MenuItem value="">All</MenuItem>
            <MenuItem value="FINALIZED">Finalized</MenuItem>
            <MenuItem value="CANCELLED">Cancelled</MenuItem>
          </Select>
        </FormControl>
        <FormControl sx={filterControlSx}>
          <InputLabel>Payment Method</InputLabel>
          <Select
            label="Payment Method"
            value={paymentMethod}
            onChange={(e) => setPaymentMethod(e.target.value)}
          >
            <MenuItem value="">All</MenuItem>
            <MenuItem value={PAYMENT_CASH}>Cash</MenuItem>
            <MenuItem value={PAYMENT_ONLINE}>Online</MenuItem>
          </Select>
        </FormControl>
        <FormControl sx={filterControlSx}>
          <InputLabel>Period</InputLabel>
          <Select
            label="Period"
            value={todayOnly ? 'today' : 'all'}
            onChange={(e) => setTodayOnly(e.target.value === 'today')}
          >
            <MenuItem value="all">All</MenuItem>
            <MenuItem value="today">Today</MenuItem>
          </Select>
        </FormControl>
      </FilterBar>

      {error ? <Alert severity="error">{error}</Alert> : null}
      {success ? <Alert severity="success">{success}</Alert> : null}

      <TableCard>
        {loading ? (
          <Box sx={{ py: 8, display: 'grid', placeItems: 'center' }}>
            <CircularProgress size={28} />
          </Box>
        ) : (
          <Table size="small" sx={{ minWidth: 960 }}>
            <TableHead>
              <TableRow>
                <TableCell>Bill No</TableCell>
                <TableCell>Reference</TableCell>
                <TableCell>Status</TableCell>
                <TableCell>Payment Method</TableCell>
                <TableCell align="right">Total</TableCell>
                <TableCell>Prints</TableCell>
                <TableCell>Created By</TableCell>
                <TableCell>Time</TableCell>
                <TableCell align="right">Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {bills.map((bill) => (
                <TableRow key={bill.id} hover>
                  <TableCell sx={{ fontVariantNumeric: 'tabular-nums', fontWeight: 600 }}>
                    {bill.bill_number}
                  </TableCell>
                  <TableCell>{bill.reference || bill.table_number || '—'}</TableCell>
                  <TableCell>
                    <Chip
                      size="small"
                      label={bill.status === 'CANCELLED' ? 'Cancelled' : 'Finalized'}
                      color={bill.status === 'CANCELLED' ? 'warning' : 'success'}
                      variant={bill.status === 'CANCELLED' ? 'filled' : 'outlined'}
                    />
                  </TableCell>
                  <TableCell>{paymentMethodLabel(bill.payment_method)}</TableCell>
                  <TableCell align="right">₹{Number(bill.grand_total).toFixed(2)}</TableCell>
                  <TableCell>{bill.printed_count}</TableCell>
                  <TableCell>{bill.created_by_name || '—'}</TableCell>
                  <TableCell>
                    {bill.created_at ? new Date(bill.created_at).toLocaleString() : '—'}
                  </TableCell>
                  <TableCell align="right">
                    <Stack direction="row" spacing={0.5} justifyContent="flex-end" useFlexGap flexWrap="wrap">
                      <Button size="small" onClick={() => openDetails(bill)}>
                        View
                      </Button>
                      <Button size="small" onClick={() => openBillPrint(bill.id)}>
                        Print
                      </Button>
                    </Stack>
                  </TableCell>
                </TableRow>
              ))}
              {!bills.length ? (
                <TableRow>
                  <TableCell colSpan={9} sx={{ p: 0, border: 0 }}>
                    <EmptyState
                      title="No bills found"
                      description="Try another search, status, payment method, or period."
                    />
                  </TableCell>
                </TableRow>
              ) : null}
            </TableBody>
          </Table>
        )}
      </TableCard>

      <Dialog
        open={Boolean(selected)}
        onClose={() => setSelected(null)}
        fullWidth
        maxWidth="md"
      >
        <DialogTitle>
          Bill #{selected?.bill_number}{' '}
          {selected?.status === 'CANCELLED' ? '(Cancelled)' : ''}
        </DialogTitle>
        <DialogContent>
          {selected ? (
            <Stack spacing={2.5} sx={{ pt: 1 }}>
              {selected.status === 'CANCELLED' ? (
                <Alert severity="warning">
                  Reason: {selected.cancellation_reason || '—'}
                  {selected.cancelled_at
                    ? ` · ${new Date(selected.cancelled_at).toLocaleString()}`
                    : ''}
                </Alert>
              ) : null}
              <BillPreview
                bill={selected}
                onPrint={() => openBillPrint(selected.id, { auto: true })}
              />
            </Stack>
          ) : null}
        </DialogContent>
        <DialogActions>
          {selected?.status === 'FINALIZED' ? (
            <Button color="error" onClick={() => setCancelOpen(true)}>
              Cancel Bill
            </Button>
          ) : null}
          <Button onClick={() => setSelected(null)}>Close</Button>
        </DialogActions>
      </Dialog>

      <Dialog open={cancelOpen} onClose={() => setCancelOpen(false)} fullWidth maxWidth="sm">
        <DialogTitle>Cancel Bill #{selected?.bill_number}</DialogTitle>
        <DialogContent>
          <Stack spacing={2.5} sx={{ pt: 1 }}>
            <TextField
              label="Cancellation reason"
              value={cancelReason}
              onChange={(e) => setCancelReason(e.target.value)}
              fullWidth
              required
              multiline
              minRows={3}
            />
          </Stack>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setCancelOpen(false)}>Back</Button>
          <Button
            color="error"
            variant="contained"
            disabled={saving || !cancelReason.trim()}
            onClick={onCancel}
          >
            Confirm Cancel
          </Button>
        </DialogActions>
      </Dialog>
    </PageShell>
  );
}
