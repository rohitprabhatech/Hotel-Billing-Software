import {
  Alert,
  Box,
  Button,
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
  Typography,
} from '@mui/material';
import { useEffect, useState } from 'react';
import {
  cancelBill,
  getBill,
  listBills,
  openBillPrint,
} from '../../services/billService';
import BillPreview from '../../print/BillPreview';

export default function BillsHistoryPage({ title = 'Bill History', todayDefault = false }) {
  const [bills, setBills] = useState([]);
  const [q, setQ] = useState('');
  const [status, setStatus] = useState('');
  const [todayOnly, setTodayOnly] = useState(todayDefault);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [selected, setSelected] = useState(null);
  const [cancelOpen, setCancelOpen] = useState(false);
  const [cancelReason, setCancelReason] = useState('');
  const [saving, setSaving] = useState(false);

  const load = async () => {
    setError('');
    try {
      const res = await listBills({
        q: q || undefined,
        status: status || undefined,
        today: todayOnly || undefined,
        per_page: 100,
      });
      setBills(res.data || []);
    } catch (err) {
      setError(err.response?.data?.error?.message || 'Failed to load bills');
    }
  };

  useEffect(() => {
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [status, todayOnly]);

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
    <>
      <Typography variant="h5" gutterBottom>
        {title}
      </Typography>

      <Stack direction={{ xs: 'column', md: 'row' }} spacing={2} mb={2}>
        <TextField
          label="Search bill / table"
          value={q}
          onChange={(e) => setQ(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === 'Enter') load();
          }}
          fullWidth
        />
        <FormControl sx={{ minWidth: 160 }}>
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
        <FormControl sx={{ minWidth: 160 }}>
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
        <Button variant="outlined" onClick={load}>
          Search
        </Button>
      </Stack>

      {error ? <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert> : null}
      {success ? <Alert severity="success" sx={{ mb: 2 }}>{success}</Alert> : null}

      <Box sx={{ bgcolor: 'background.paper', borderRadius: 2, overflow: 'auto' }}>
        <Table size="small">
          <TableHead>
            <TableRow>
              <TableCell>Bill No</TableCell>
              <TableCell>Table</TableCell>
              <TableCell>Status</TableCell>
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
                <TableCell>{bill.bill_number}</TableCell>
                <TableCell>{bill.table_number || '—'}</TableCell>
                <TableCell>{bill.status}</TableCell>
                <TableCell align="right">₹{Number(bill.grand_total).toFixed(2)}</TableCell>
                <TableCell>{bill.printed_count}</TableCell>
                <TableCell>{bill.created_by_name || '—'}</TableCell>
                <TableCell>
                  {bill.created_at ? new Date(bill.created_at).toLocaleString() : '—'}
                </TableCell>
                <TableCell align="right">
                  <Button size="small" onClick={() => openDetails(bill)}>
                    View
                  </Button>
                  <Button size="small" onClick={() => openBillPrint(bill.id)}>
                    Print
                  </Button>
                </TableCell>
              </TableRow>
            ))}
            {!bills.length ? (
              <TableRow>
                <TableCell colSpan={8}>
                  <Typography color="text.secondary">No bills found.</Typography>
                </TableCell>
              </TableRow>
            ) : null}
          </TableBody>
        </Table>
      </Box>

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
            <Stack spacing={2} sx={{ mt: 1 }}>
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
          <TextField
            label="Cancellation reason"
            value={cancelReason}
            onChange={(e) => setCancelReason(e.target.value)}
            fullWidth
            required
            multiline
            minRows={3}
            sx={{ mt: 1 }}
          />
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
    </>
  );
}