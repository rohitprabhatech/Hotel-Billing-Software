import AddOutlinedIcon from '@mui/icons-material/AddOutlined';
import EditOutlinedIcon from '@mui/icons-material/EditOutlined';
import AccountBalanceWalletOutlinedIcon from '@mui/icons-material/AccountBalanceWalletOutlined';
import ReceiptLongOutlinedIcon from '@mui/icons-material/ReceiptLongOutlined';
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
  Switch,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
  TextField,
  Tooltip,
  Typography,
} from '@mui/material';
import { useEffect, useState } from 'react';
import EmptyState from '../../components/EmptyState';
import FilterBar from '../../components/FilterBar';
import LoadingBlock from '../../components/LoadingBlock';
import PageShell from '../../components/PageShell';
import PaginationBar from '../../components/PaginationBar';
import TableCard from '../../components/TableCard';
import TruncateText from '../../components/TruncateText';
import { PageActions } from '../../context/PageActionsContext';
import { useModuleGate } from '../../context/ModulesContext';
import { filterControlWideSx } from '../../layouts/shell';
import {
  createCustomer,
  deactivateCustomer,
  listCustomerBills,
  listCustomerLedger,
  listCustomers,
  listOutstandingCustomers,
  recordCustomerPayment,
  setCustomerStatus,
  updateCustomer,
} from '../../services/customerService';
import { fetchClothingCustomerHistory } from '../../services/clothingService';
import { PAYMENT_CASH, PAYMENT_ONLINE } from '../../utils/paymentMethod';

const emptyForm = {
  name: '',
  phone_country_code: '91',
  phone: '',
  email: '',
  credit_limit: '',
  notes: '',
};

const PAGE_SIZE = 25;

function money(value) {
  if (value === null || value === undefined || value === '') return '—';
  return `₹${Number(value).toFixed(2)}`;
}

export default function CustomersPage() {
  const clothingEnabled = useModuleGate('variants');
  const [customers, setCustomers] = useState([]);
  const [meta, setMeta] = useState({ page: 1, per_page: PAGE_SIZE, total: 0 });
  const [q, setQ] = useState('');
  const [outstandingOnly, setOutstandingOnly] = useState(false);
  const [page, setPage] = useState(1);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [open, setOpen] = useState(false);
  const [editing, setEditing] = useState(null);
  const [form, setForm] = useState(emptyForm);
  const [saving, setSaving] = useState(false);
  const [loading, setLoading] = useState(true);
  const [historyCustomer, setHistoryCustomer] = useState(null);
  const [historyBills, setHistoryBills] = useState([]);
  const [historyLoading, setHistoryLoading] = useState(false);
  const [ledgerCustomer, setLedgerCustomer] = useState(null);
  const [ledgerData, setLedgerData] = useState(null);
  const [ledgerLoading, setLedgerLoading] = useState(false);
  const [payCustomer, setPayCustomer] = useState(null);
  const [payAmount, setPayAmount] = useState('');
  const [payMethod, setPayMethod] = useState(PAYMENT_CASH);
  const [payNotes, setPayNotes] = useState('');

  const load = async (nextPage = page, search = q, onlyOutstanding = outstandingOnly) => {
    setError('');
    setLoading(true);
    try {
      const params = {
        q: search || undefined,
        page: nextPage,
        per_page: PAGE_SIZE,
      };
      const res = onlyOutstanding
        ? await listOutstandingCustomers(params)
        : await listCustomers(params);
      setCustomers(res.data || []);
      setMeta(res.meta || { page: nextPage, per_page: PAGE_SIZE, total: 0 });
      setPage(res.meta?.page || nextPage);
    } catch (err) {
      setError(err.response?.data?.error?.message || 'Unable to load customers.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load(1);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const openCreate = () => {
    setEditing(null);
    setForm(emptyForm);
    setOpen(true);
  };

  const openEdit = (customer) => {
    setEditing(customer);
    setForm({
      name: customer.name || '',
      phone_country_code: customer.phone_country_code || '91',
      phone: customer.phone_national || '',
      email: customer.email || '',
      credit_limit: customer.credit_limit ?? '',
      notes: customer.notes || '',
    });
    setOpen(true);
  };

  const onSave = async () => {
    if (!form.name.trim()) {
      setError('Customer name is required.');
      return;
    }
    setSaving(true);
    setError('');
    setSuccess('');
    const payload = {
      name: form.name.trim(),
      phone_country_code: form.phone ? form.phone_country_code : null,
      phone: form.phone || null,
      email: form.email.trim() || null,
      credit_limit: form.credit_limit === '' ? null : form.credit_limit,
      notes: form.notes.trim() || null,
    };
    try {
      if (editing) {
        await updateCustomer(editing.id, payload);
        setSuccess('Customer updated successfully.');
      } else {
        await createCustomer(payload);
        setSuccess('Customer created successfully.');
      }
      setOpen(false);
      await load(editing ? page : 1, q);
    } catch (err) {
      setError(err.response?.data?.error?.message || 'Failed to save customer');
    } finally {
      setSaving(false);
    }
  };

  const toggleActive = async (customer) => {
    setError('');
    try {
      if (customer.is_active) {
        await deactivateCustomer(customer.id);
      } else {
        await setCustomerStatus(customer.id, true);
      }
      await load(page, q);
    } catch (err) {
      setError(err.response?.data?.error?.message || 'Failed to update customer status');
    }
  };

  const openHistory = async (customer) => {
    setHistoryCustomer(customer);
    setHistoryBills([]);
    setHistoryLoading(true);
    try {
      if (clothingEnabled) {
        const res = await fetchClothingCustomerHistory(customer.id, { per_page: 20 });
        setHistoryBills(res.data?.bills || []);
      } else {
        const res = await listCustomerBills(customer.id, { per_page: 20 });
        setHistoryBills(res.data || []);
      }
    } catch (err) {
      setError(err.response?.data?.error?.message || 'Unable to load purchase history.');
    } finally {
      setHistoryLoading(false);
    }
  };

  const openLedger = async (customer) => {
    setLedgerCustomer(customer);
    setLedgerLoading(true);
    setError('');
    try {
      const res = await listCustomerLedger(customer.id, { per_page: 50 });
      setLedgerData(res.data);
    } catch (err) {
      setError(err.response?.data?.error?.message || 'Unable to load ledger.');
    } finally {
      setLedgerLoading(false);
    }
  };

  const openPay = (customer) => {
    setPayCustomer(customer);
    setPayAmount('');
    setPayMethod(PAYMENT_CASH);
    setPayNotes('');
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
      await recordCustomerPayment(payCustomer.id, {
        amount: payAmount,
        collection_method: payMethod,
        notes: payNotes.trim() || null,
      });
      setSuccess(`Payment recorded for ${payCustomer.name}.`);
      setPayCustomer(null);
      await load(page, q, outstandingOnly);
    } catch (err) {
      setError(err.response?.data?.error?.message || 'Failed to record payment.');
    } finally {
      setSaving(false);
    }
  };

  return (
    <>
      <PageActions>
        <Button variant="contained" startIcon={<AddOutlinedIcon />} onClick={openCreate}>
          Add Customer
        </Button>
      </PageActions>

      <PageShell>
        <FilterBar
          actions={
            <Button variant="outlined" onClick={() => load(1, q)}>
              Search
            </Button>
          }
        >
          <TextField
            label="Search name, phone, or email"
            value={q}
            onChange={(e) => setQ(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Enter') load(1, q);
            }}
            sx={{ ...filterControlWideSx, flex: 1 }}
          />
          <FormControl sx={{ minWidth: 180 }}>
            <InputLabel id="customer-filter-label">View</InputLabel>
            <Select
              labelId="customer-filter-label"
              label="View"
              value={outstandingOnly ? 'outstanding' : 'all'}
              onChange={(e) => {
                const only = e.target.value === 'outstanding';
                setOutstandingOnly(only);
                load(1, q, only);
              }}
            >
              <MenuItem value="all">All customers</MenuItem>
              <MenuItem value="outstanding">Outstanding only</MenuItem>
            </Select>
          </FormControl>
        </FilterBar>

        {error ? <Alert severity="error">{error}</Alert> : null}
        {success ? <Alert severity="success">{success}</Alert> : null}

        <TableCard>
          {loading ? (
            <LoadingBlock />
          ) : (
            <Table size="small" sx={{ minWidth: 980 }}>
              <TableHead>
                <TableRow>
                  <TableCell>Name</TableCell>
                  <TableCell>Phone</TableCell>
                  <TableCell>Email</TableCell>
                  <TableCell align="right">Credit Limit</TableCell>
                  <TableCell align="right">Balance</TableCell>
                  <TableCell>Status</TableCell>
                  <TableCell align="right">Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {customers.map((customer) => (
                  <TableRow key={customer.id} hover>
                    <TableCell>
                      <TruncateText value={customer.name} maxWidth={180} />
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2" color="text.secondary">
                        {customer.phone_masked || '—'}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <TruncateText value={customer.email_masked || '—'} maxWidth={200} />
                    </TableCell>
                    <TableCell align="right">{money(customer.credit_limit)}</TableCell>
                    <TableCell align="right">
                      {Number(customer.balance || 0) > 0 ? (
                        <Chip size="small" color="warning" label={money(customer.balance)} />
                      ) : (
                        money(customer.balance)
                      )}
                    </TableCell>
                    <TableCell>
                      <Stack direction="row" alignItems="center" spacing={1}>
                        <Switch
                          size="small"
                          checked={customer.is_active}
                          onChange={() => toggleActive(customer)}
                          inputProps={{ 'aria-label': `Toggle ${customer.name}` }}
                        />
                        <Chip
                          size="small"
                          label={customer.is_active ? 'Active' : 'Inactive'}
                          variant="outlined"
                        />
                      </Stack>
                    </TableCell>
                    <TableCell align="right">
                      <Stack direction="row" spacing={0.5} justifyContent="flex-end">
                        <Tooltip title="Ledger">
                          <IconButton
                            size="small"
                            aria-label={`Ledger for ${customer.name}`}
                            onClick={() => openLedger(customer)}
                          >
                            <AccountBalanceWalletOutlinedIcon fontSize="small" />
                          </IconButton>
                        </Tooltip>
                        {Number(customer.balance || 0) > 0 ? (
                          <Button size="small" variant="outlined" onClick={() => openPay(customer)}>
                            Pay
                          </Button>
                        ) : null}
                        <Tooltip title="Purchase history">
                          <IconButton
                            size="small"
                            aria-label={`View bills for ${customer.name}`}
                            onClick={() => openHistory(customer)}
                          >
                            <ReceiptLongOutlinedIcon fontSize="small" />
                          </IconButton>
                        </Tooltip>
                        <Tooltip title="Edit">
                          <IconButton
                            size="small"
                            aria-label={`Edit ${customer.name}`}
                            onClick={() => openEdit(customer)}
                          >
                            <EditOutlinedIcon fontSize="small" />
                          </IconButton>
                        </Tooltip>
                      </Stack>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
          {!loading && !customers.length ? (
            <EmptyState
              title="No customers found"
              description="Add customers to link bills and track purchase history."
              actionLabel="Add Customer"
              onAction={openCreate}
            />
          ) : null}
        </TableCard>

        {!loading && customers.length ? (
          <PaginationBar
            page={page}
            total={meta.total}
            pageSize={PAGE_SIZE}
            onPageChange={(next) => load(next, q)}
          />
        ) : null}
      </PageShell>

      <Dialog open={open} onClose={() => setOpen(false)} fullWidth maxWidth="sm">
        <DialogTitle>{editing ? 'Edit Customer' : 'Add Customer'}</DialogTitle>
        <DialogContent>
          <Stack spacing={2.5} sx={{ mt: 1 }}>
            <TextField
              label="Name"
              value={form.name}
              onChange={(e) => setForm((f) => ({ ...f, name: e.target.value }))}
              fullWidth
              required
            />
            <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2}>
              <TextField
                label="Country code"
                value={form.phone_country_code}
                onChange={(e) =>
                  setForm((f) => ({
                    ...f,
                    phone_country_code: e.target.value.replace(/\D/g, '').slice(0, 3),
                  }))
                }
                sx={{ width: { xs: '100%', sm: 120 } }}
              />
              <TextField
                label="Mobile"
                value={form.phone}
                onChange={(e) =>
                  setForm((f) => ({ ...f, phone: e.target.value.replace(/\D/g, '').slice(0, 14) }))
                }
                fullWidth
              />
            </Stack>
            <TextField
              label="Email"
              type="email"
              value={form.email}
              onChange={(e) => setForm((f) => ({ ...f, email: e.target.value }))}
              fullWidth
            />
            <TextField
              label="Credit limit (optional)"
              type="number"
              value={form.credit_limit}
              onChange={(e) => setForm((f) => ({ ...f, credit_limit: e.target.value }))}
              fullWidth
              inputProps={{ min: 0, step: '0.01' }}
            />
            <TextField
              label="Notes"
              value={form.notes}
              onChange={(e) => setForm((f) => ({ ...f, notes: e.target.value }))}
              fullWidth
              multiline
              minRows={2}
            />
          </Stack>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpen(false)}>Cancel</Button>
          <Button variant="contained" onClick={onSave} disabled={saving}>
            {saving ? 'Saving...' : 'Save'}
          </Button>
        </DialogActions>
      </Dialog>

      <Dialog
        open={Boolean(historyCustomer)}
        onClose={() => setHistoryCustomer(null)}
        fullWidth
        maxWidth="md"
      >
        <DialogTitle>Purchase History — {historyCustomer?.name}</DialogTitle>
        <DialogContent>
          {historyLoading ? (
            <LoadingBlock />
          ) : (
            <Table size="small">
              <TableHead>
                <TableRow>
                  <TableCell>Bill #</TableCell>
                  <TableCell>Date</TableCell>
                  <TableCell>Items</TableCell>
                  <TableCell align="right">Total</TableCell>
                  <TableCell>Status</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {historyBills.map((bill) => (
                  <TableRow key={bill.id}>
                    <TableCell>{bill.bill_number}</TableCell>
                    <TableCell>
                      {bill.created_at ? new Date(bill.created_at).toLocaleString() : '—'}
                    </TableCell>
                    <TableCell>
                      {bill.items?.length
                        ? bill.items.map((line) => line.item_name).join(', ')
                        : '—'}
                    </TableCell>
                    <TableCell align="right">₹{Number(bill.grand_total).toFixed(2)}</TableCell>
                    <TableCell>{bill.status}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
          {!historyLoading && !historyBills.length ? (
            <Typography variant="body2" color="text.secondary" sx={{ py: 2 }}>
              No linked bills yet.
            </Typography>
          ) : null}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setHistoryCustomer(null)}>Close</Button>
        </DialogActions>
      </Dialog>

      <Dialog
        open={Boolean(ledgerCustomer)}
        onClose={() => setLedgerCustomer(null)}
        fullWidth
        maxWidth="md"
      >
        <DialogTitle>Credit Ledger — {ledgerCustomer?.name}</DialogTitle>
        <DialogContent>
          {ledgerLoading ? (
            <LoadingBlock />
          ) : (
            <Stack spacing={2} sx={{ mt: 1 }}>
              <Typography variant="body2">
                Outstanding balance: <strong>{money(ledgerData?.balance)}</strong>
                {ledgerData?.credit_limit != null ? (
                  <> · Limit: {money(ledgerData.credit_limit)}</>
                ) : null}
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
                        <TruncateText value={entry.notes || '—'} maxWidth={200} />
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
        <DialogTitle>Collect Payment — {payCustomer?.name}</DialogTitle>
        <DialogContent>
          <Stack spacing={2.5} sx={{ mt: 1 }}>
            <Typography variant="body2" color="text.secondary">
              Outstanding: {money(payCustomer?.balance)}
            </Typography>
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
              <InputLabel id="collection-method-label">Collection method</InputLabel>
              <Select
                labelId="collection-method-label"
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
          <Button variant="contained" onClick={onCollectPayment} disabled={saving}>
            {saving ? 'Saving...' : 'Record payment'}
          </Button>
        </DialogActions>
      </Dialog>
    </>
  );
}
