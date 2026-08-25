import AccountBalanceWalletOutlinedIcon from '@mui/icons-material/AccountBalanceWalletOutlined';
import {
  Alert,
  Button,
  Chip,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  FormControl,
  IconButton,
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
  Tooltip,
  Typography,
} from '@mui/material';
import { useCallback, useEffect, useState } from 'react';
import EmptyState from '../../components/EmptyState';
import LoadingBlock from '../../components/LoadingBlock';
import PageShell from '../../components/PageShell';
import PaginationBar from '../../components/PaginationBar';
import TableCard from '../../components/TableCard';
import TruncateText from '../../components/TruncateText';
import { useModuleGate } from '../../context/ModulesContext';
import {
  fetchGroceryCredit,
  fetchGroceryOutstanding,
  payGroceryCredit,
} from '../../services/groceryService';
import { PAYMENT_CASH, PAYMENT_ONLINE } from '../../utils/paymentMethod';

const PAGE_SIZE = 25;

function money(value) {
  if (value === null || value === undefined || value === '') return '—';
  return `₹${Number(value).toFixed(2)}`;
}

export default function GroceryCreditPage() {
  const moduleEnabled = useModuleGate('customer_credit');
  const [rows, setRows] = useState([]);
  const [meta, setMeta] = useState({ page: 1, per_page: PAGE_SIZE, total: 0 });
  const [page, setPage] = useState(1);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [ledgerCustomer, setLedgerCustomer] = useState(null);
  const [ledgerData, setLedgerData] = useState(null);
  const [ledgerLoading, setLedgerLoading] = useState(false);
  const [payCustomer, setPayCustomer] = useState(null);
  const [payAmount, setPayAmount] = useState('');
  const [payMethod, setPayMethod] = useState(PAYMENT_CASH);
  const [payNotes, setPayNotes] = useState('');
  const [saving, setSaving] = useState(false);
  const [confirmPay, setConfirmPay] = useState(false);

  const load = useCallback(async (nextPage = 1) => {
    setLoading(true);
    setError('');
    try {
      const res = await fetchGroceryOutstanding({ page: nextPage, per_page: PAGE_SIZE });
      setRows(res.data || []);
      setMeta(res.meta || { page: nextPage, per_page: PAGE_SIZE, total: 0 });
      setPage(res.meta?.page || nextPage);
    } catch (err) {
      setError(err.response?.data?.error?.message || 'Unable to load outstanding credit.');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    if (!moduleEnabled) return;
    load(1);
  }, [moduleEnabled, load]);

  const openLedger = async (customer) => {
    setLedgerCustomer(customer);
    setLedgerLoading(true);
    setError('');
    try {
      const res = await fetchGroceryCredit(customer.id, { per_page: 50 });
      setLedgerData(res.data);
    } catch (err) {
      setError(err.response?.data?.error?.message || 'Unable to load payment history.');
    } finally {
      setLedgerLoading(false);
    }
  };

  const onCollectPayment = async () => {
    if (!payCustomer || !payAmount || Number(payAmount) <= 0) {
      setError('Enter a valid payment amount.');
      return;
    }
    setSaving(true);
    setError('');
    setSuccess('');
    try {
      await payGroceryCredit(payCustomer.id, {
        amount: payAmount,
        collection_method: payMethod,
        notes: payNotes.trim() || null,
      });
      setSuccess(`Payment recorded for ${payCustomer.name}.`);
      setPayCustomer(null);
      setConfirmPay(false);
      await load(page);
    } catch (err) {
      setError(err.response?.data?.error?.message || 'Failed to record payment.');
    } finally {
      setSaving(false);
    }
  };

  if (!moduleEnabled) {
    return (
      <PageShell>
        <Alert severity="info">Customer credit / udhari is not enabled for this business type.</Alert>
      </PageShell>
    );
  }

  return (
    <PageShell>
      <Stack spacing={2}>
        {error ? <Alert severity="error">{error}</Alert> : null}
        {success ? <Alert severity="success">{success}</Alert> : null}

        <TableCard>
          {loading ? (
            <LoadingBlock />
          ) : (
            <Table size="small" sx={{ minWidth: 720 }}>
              <TableHead>
                <TableRow>
                  <TableCell>Customer</TableCell>
                  <TableCell>Phone</TableCell>
                  <TableCell align="right">Limit</TableCell>
                  <TableCell align="right">Outstanding</TableCell>
                  <TableCell align="right">Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {rows.map((customer) => (
                  <TableRow key={customer.id} hover>
                    <TableCell>
                      <TruncateText value={customer.name} maxWidth={200} />
                    </TableCell>
                    <TableCell>{customer.phone_masked || '—'}</TableCell>
                    <TableCell align="right">{money(customer.credit_limit)}</TableCell>
                    <TableCell align="right">
                      <Chip size="small" color="warning" label={money(customer.balance)} />
                    </TableCell>
                    <TableCell align="right">
                      <Stack direction="row" spacing={0.5} justifyContent="flex-end">
                        <Tooltip title="Payment history">
                          <IconButton
                            size="small"
                            aria-label={`History for ${customer.name}`}
                            onClick={() => openLedger(customer)}
                          >
                            <AccountBalanceWalletOutlinedIcon fontSize="small" />
                          </IconButton>
                        </Tooltip>
                        <Button
                          size="small"
                          variant="contained"
                          onClick={() => {
                            setPayCustomer(customer);
                            setPayAmount('');
                            setPayMethod(PAYMENT_CASH);
                            setPayNotes('');
                            setConfirmPay(false);
                          }}
                        >
                          Collect
                        </Button>
                      </Stack>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
          {!loading && !rows.length ? (
            <EmptyState
              title="No outstanding udhari"
              description="Credit sales from Grocery POS appear here until they are collected."
            />
          ) : null}
        </TableCard>

        {!loading && rows.length ? (
          <PaginationBar
            page={page}
            total={meta.total}
            pageSize={PAGE_SIZE}
            onPageChange={(next) => load(next)}
          />
        ) : null}
      </Stack>

      <Dialog
        open={Boolean(ledgerCustomer)}
        onClose={() => setLedgerCustomer(null)}
        fullWidth
        maxWidth="md"
      >
        <DialogTitle>Payment history — {ledgerCustomer?.name}</DialogTitle>
        <DialogContent>
          {ledgerLoading ? (
            <LoadingBlock />
          ) : (
            <Stack spacing={2} sx={{ mt: 1 }}>
              <Typography variant="body2">
                Outstanding: <strong>{money(ledgerData?.balance)}</strong>
                {ledgerData?.credit_limit != null ? <> · Limit: {money(ledgerData.credit_limit)}</> : null}
              </Typography>
              <Table size="small">
                <TableHead>
                  <TableRow>
                    <TableCell>Date</TableCell>
                    <TableCell>Type</TableCell>
                    <TableCell align="right">Amount</TableCell>
                    <TableCell align="right">Balance</TableCell>
                    <TableCell>Notes</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {(ledgerData?.entries || []).map((entry) => (
                    <TableRow key={entry.id}>
                      <TableCell>
                        {entry.created_at ? new Date(entry.created_at).toLocaleString() : '—'}
                      </TableCell>
                      <TableCell>{entry.entry_type}</TableCell>
                      <TableCell align="right">{money(entry.amount)}</TableCell>
                      <TableCell align="right">{money(entry.balance_after)}</TableCell>
                      <TableCell>
                        <TruncateText value={entry.notes || '—'} maxWidth={220} />
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </Stack>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setLedgerCustomer(null)}>Close</Button>
        </DialogActions>
      </Dialog>

      <Dialog open={Boolean(payCustomer)} onClose={() => setPayCustomer(null)} fullWidth maxWidth="xs">
        <DialogTitle>Collect udhari — {payCustomer?.name}</DialogTitle>
        <DialogContent>
          <Stack spacing={2.5} sx={{ mt: 1 }}>
            <Alert severity="warning">
              Outstanding {money(payCustomer?.balance)}. Confirm the amount before recording.
            </Alert>
            <TextField
              label="Amount"
              type="number"
              value={payAmount}
              onChange={(e) => setPayAmount(e.target.value)}
              fullWidth
              inputProps={{ min: 0.01, step: '0.01' }}
              required
            />
            <FormControl fullWidth>
              <InputLabel id="grocery-collect-method">Collection method</InputLabel>
              <Select
                labelId="grocery-collect-method"
                label="Collection method"
                value={payMethod}
                onChange={(e) => setPayMethod(e.target.value)}
              >
                <MenuItem value={PAYMENT_CASH}>Cash</MenuItem>
                <MenuItem value={PAYMENT_ONLINE}>Online</MenuItem>
              </Select>
            </FormControl>
            <TextField
              label="Notes (optional)"
              value={payNotes}
              onChange={(e) => setPayNotes(e.target.value)}
              fullWidth
              multiline
              minRows={2}
            />
          </Stack>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setPayCustomer(null)}>Cancel</Button>
          {!confirmPay ? (
            <Button
              variant="contained"
              onClick={() => {
                if (!payAmount || Number(payAmount) <= 0) {
                  setError('Enter a valid payment amount.');
                  return;
                }
                setConfirmPay(true);
              }}
            >
              Review
            </Button>
          ) : (
            <Button variant="contained" color="warning" onClick={onCollectPayment} disabled={saving}>
              {saving ? 'Saving…' : `Confirm ${money(payAmount)}`}
            </Button>
          )}
        </DialogActions>
      </Dialog>
    </PageShell>
  );
}
