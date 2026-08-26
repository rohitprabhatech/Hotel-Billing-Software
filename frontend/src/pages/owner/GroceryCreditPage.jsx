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
  Tab,
  Tabs,
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
import {
  fetchSupplierLedger,
  fetchSupplierOutstanding,
  paySupplierCredit,
} from '../../services/tradeCreditService';
import { PAYMENT_CASH, PAYMENT_ONLINE } from '../../utils/paymentMethod';

const PAGE_SIZE = 25;

function money(value) {
  if (value === null || value === undefined || value === '') return '—';
  return `₹${Number(value).toFixed(2)}`;
}

export default function GroceryCreditPage() {
  const moduleEnabled = useModuleGate('customer_credit');
  const [partyTab, setPartyTab] = useState('customer');
  const [rows, setRows] = useState([]);
  const [meta, setMeta] = useState({ page: 1, per_page: PAGE_SIZE, total: 0 });
  const [page, setPage] = useState(1);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [ledgerParty, setLedgerParty] = useState(null);
  const [ledgerData, setLedgerData] = useState(null);
  const [ledgerLoading, setLedgerLoading] = useState(false);
  const [payParty, setPayParty] = useState(null);
  const [payAmount, setPayAmount] = useState('');
  const [payMethod, setPayMethod] = useState(PAYMENT_CASH);
  const [payNotes, setPayNotes] = useState('');
  const [saving, setSaving] = useState(false);
  const [confirmPay, setConfirmPay] = useState(false);

  const isSupplier = partyTab === 'supplier';

  const load = useCallback(
    async (nextPage = 1) => {
      setLoading(true);
      setError('');
      try {
        const res = isSupplier
          ? await fetchSupplierOutstanding({ page: nextPage, per_page: PAGE_SIZE })
          : await fetchGroceryOutstanding({ page: nextPage, per_page: PAGE_SIZE });
        setRows(res.data || []);
        setMeta(res.meta || { page: nextPage, per_page: PAGE_SIZE, total: 0 });
        setPage(res.meta?.page || nextPage);
      } catch (err) {
        setError(err.response?.data?.error?.message || 'Unable to load outstanding credit.');
      } finally {
        setLoading(false);
      }
    },
    [isSupplier],
  );

  useEffect(() => {
    if (!moduleEnabled) return;
    load(1);
  }, [moduleEnabled, load]);

  const openLedger = async (party) => {
    setLedgerParty(party);
    setLedgerLoading(true);
    setError('');
    try {
      const res = isSupplier
        ? await fetchSupplierLedger(party.id, { per_page: 50 })
        : await fetchGroceryCredit(party.id, { per_page: 50 });
      setLedgerData(res.data);
    } catch (err) {
      setError(err.response?.data?.error?.message || 'Unable to load payment history.');
    } finally {
      setLedgerLoading(false);
    }
  };

  const onCollectPayment = async () => {
    if (!payParty || !payAmount || Number(payAmount) <= 0) {
      setError('Enter a valid payment amount.');
      return;
    }
    setSaving(true);
    setError('');
    setSuccess('');
    try {
      const payload = {
        amount: payAmount,
        collection_method: payMethod,
        notes: payNotes.trim() || null,
      };
      if (isSupplier) {
        await paySupplierCredit(payParty.id, payload);
      } else {
        await payGroceryCredit(payParty.id, payload);
      }
      setSuccess(`Payment recorded for ${payParty.name}.`);
      setPayParty(null);
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

        <Tabs
          value={partyTab}
          onChange={(_, value) => {
            setPartyTab(value);
            setRows([]);
          }}
        >
          <Tab value="customer" label="Customers" />
          <Tab value="supplier" label="Suppliers" />
        </Tabs>

        <TableCard>
          {loading ? (
            <LoadingBlock />
          ) : (
            <Table size="small" sx={{ minWidth: 720 }}>
              <TableHead>
                <TableRow>
                  <TableCell>{isSupplier ? 'Supplier' : 'Customer'}</TableCell>
                  <TableCell>Phone</TableCell>
                  <TableCell align="right">Limit</TableCell>
                  <TableCell align="right">Outstanding</TableCell>
                  <TableCell align="right">Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {rows.map((party) => (
                  <TableRow key={party.id} hover>
                    <TableCell>
                      <TruncateText value={party.name} maxWidth={200} />
                    </TableCell>
                    <TableCell>{party.phone_masked || '—'}</TableCell>
                    <TableCell align="right">{money(party.credit_limit)}</TableCell>
                    <TableCell align="right">
                      <Chip size="small" color="warning" label={money(party.balance)} />
                    </TableCell>
                    <TableCell align="right">
                      <Stack direction="row" spacing={0.5} justifyContent="flex-end">
                        <Tooltip title="Ledger history">
                          <IconButton
                            size="small"
                            aria-label={`History for ${party.name}`}
                            onClick={() => openLedger(party)}
                          >
                            <AccountBalanceWalletOutlinedIcon fontSize="small" />
                          </IconButton>
                        </Tooltip>
                        <Button
                          size="small"
                          variant="contained"
                          onClick={() => {
                            setPayParty(party);
                            setPayAmount('');
                            setPayMethod(PAYMENT_CASH);
                            setPayNotes('');
                            setConfirmPay(false);
                          }}
                        >
                          {isSupplier ? 'Pay' : 'Collect'}
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
              title={isSupplier ? 'No supplier outstanding' : 'No outstanding udhari'}
              description={
                isSupplier
                  ? 'Credit purchases appear here until they are paid.'
                  : 'Credit sales appear here until they are collected.'
              }
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

      <Dialog open={Boolean(ledgerParty)} onClose={() => setLedgerParty(null)} fullWidth maxWidth="md">
        <DialogTitle>
          {isSupplier ? 'Supplier ledger' : 'Payment history'} — {ledgerParty?.name}
        </DialogTitle>
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
          <Button onClick={() => setLedgerParty(null)}>Close</Button>
        </DialogActions>
      </Dialog>

      <Dialog open={Boolean(payParty)} onClose={() => setPayParty(null)} fullWidth maxWidth="xs">
        <DialogTitle>
          {isSupplier ? 'Pay supplier' : 'Collect udhari'} — {payParty?.name}
        </DialogTitle>
        <DialogContent>
          <Stack spacing={2.5} sx={{ mt: 1 }}>
            <Alert severity="warning">
              Outstanding {money(payParty?.balance)}. Confirm the amount before recording.
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
              <InputLabel id="trade-collect-method">Method</InputLabel>
              <Select
                labelId="trade-collect-method"
                label="Method"
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
          <Button onClick={() => setPayParty(null)}>Cancel</Button>
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
