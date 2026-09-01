import AddOutlinedIcon from '@mui/icons-material/AddOutlined';
import CancelOutlinedIcon from '@mui/icons-material/CancelOutlined';
import DeleteOutlinedIcon from '@mui/icons-material/DeleteOutlined';
import VisibilityOutlinedIcon from '@mui/icons-material/VisibilityOutlined';
import {
  Alert,
  Autocomplete,
  Box,
  Button,
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
  Typography,
} from '@mui/material';
import { useEffect, useMemo, useState } from 'react';
import EmptyState from '../../components/EmptyState';
import FilterBar from '../../components/FilterBar';
import LoadingBlock from '../../components/LoadingBlock';
import PageShell from '../../components/PageShell';
import PaginationBar from '../../components/PaginationBar';
import TableCard from '../../components/TableCard';
import TruncateText from '../../components/TruncateText';
import IconActionButton from '../../components/ui/IconActionButton';
import SearchInput from '../../components/ui/SearchInput';
import StatusBadge from '../../components/ui/StatusBadge';
import { PageActions } from '../../context/PageActionsContext';
import { usePermissions } from '../../hooks/usePermissions';
import { filterControlWideSx } from '../../layouts/shell';
import { listItems } from '../../services/itemService';
import { cancelPurchase, createPurchase, getPurchase, listPurchases } from '../../services/purchaseService';
import { listSuppliers } from '../../services/supplierService';

const PAGE_SIZE = 25;

const emptyLine = () => ({ item_id: '', quantity: '1', unit_cost: '' });

function formatMoney(value) {
  if (value == null || Number.isNaN(Number(value))) return '—';
  return `₹${Number(value).toFixed(2)}`;
}

function statusChip(status) {
  if (status === 'FINALIZED') {
    return <StatusBadge label="Finalized" variant="active" />;
  }
  if (status === 'CANCELLED') {
    return <StatusBadge label="Cancelled" variant="cancelled" />;
  }
  return <StatusBadge label={status || '—'} variant="info" />;
}

export default function PurchasesPage() {
  const { canManagePurchases, canViewPurchases } = usePermissions();
  const [purchases, setPurchases] = useState([]);
  const [meta, setMeta] = useState({ page: 1, per_page: PAGE_SIZE, total: 0 });
  const [q, setQ] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [page, setPage] = useState(1);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  const [createOpen, setCreateOpen] = useState(false);
  const [detailOpen, setDetailOpen] = useState(false);
  const [cancelOpen, setCancelOpen] = useState(false);
  const [selected, setSelected] = useState(null);
  const [cancelReason, setCancelReason] = useState('');

  const [suppliers, setSuppliers] = useState([]);
  const [items, setItems] = useState([]);
  const [form, setForm] = useState({
    supplier_id: '',
    invoice_number: '',
    notes: '',
    payment_method: 'cash',
    lines: [emptyLine()],
  });

  const itemOptions = useMemo(
    () => items.filter((item) => item.is_active && item.stock_quantity != null),
    [items],
  );

  const load = async (nextPage = page, search = q, status = statusFilter) => {
    setError('');
    setLoading(true);
    try {
      const res = await listPurchases({
        q: search || undefined,
        status: status || undefined,
        page: nextPage,
        per_page: PAGE_SIZE,
      });
      setPurchases(res.data || []);
      setMeta(res.meta || { page: nextPage, per_page: PAGE_SIZE, total: 0 });
      setPage(res.meta?.page || nextPage);
    } catch (err) {
      setError(err.response?.data?.error?.message || 'Unable to load purchases.');
    } finally {
      setLoading(false);
    }
  };

  const loadFormData = async () => {
    try {
      const [supplierRes, itemRes] = await Promise.all([
        listSuppliers({ per_page: 100, is_active: true }),
        listItems({ per_page: 100, is_active: true }),
      ]);
      setSuppliers(supplierRes.data || []);
      setItems(itemRes.data || []);
    } catch (err) {
      setError(err.response?.data?.error?.message || 'Unable to load suppliers or items.');
    }
  };

  useEffect(() => {
    if (canViewPurchases) load(1);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [canViewPurchases]);

  const openCreate = async () => {
    setForm({
      supplier_id: '',
      invoice_number: '',
      notes: '',
      payment_method: 'cash',
      lines: [emptyLine()],
    });
    await loadFormData();
    setCreateOpen(true);
  };

  const openDetail = async (purchase) => {
    setError('');
    try {
      const res = await getPurchase(purchase.id);
      setSelected(res.data);
      setDetailOpen(true);
    } catch (err) {
      setError(err.response?.data?.error?.message || 'Unable to load purchase details.');
    }
  };

  const openCancel = (purchase) => {
    setSelected(purchase);
    setCancelReason('');
    setCancelOpen(true);
  };

  const updateLine = (index, patch) => {
    setForm((prev) => ({
      ...prev,
      lines: prev.lines.map((line, i) => (i === index ? { ...line, ...patch } : line)),
    }));
  };

  const addLine = () => {
    setForm((prev) => ({ ...prev, lines: [...prev.lines, emptyLine()] }));
  };

  const removeLine = (index) => {
    setForm((prev) => ({
      ...prev,
      lines: prev.lines.length > 1 ? prev.lines.filter((_, i) => i !== index) : prev.lines,
    }));
  };

  const onCreate = async () => {
    const lines = form.lines
      .filter((line) => line.item_id && line.quantity && line.unit_cost !== '')
      .map((line) => ({
        item_id: line.item_id,
        quantity: line.quantity,
        unit_cost: line.unit_cost,
      }));

    if (!lines.length) {
      setError('Add at least one line item with quantity and unit cost.');
      return;
    }

    setSaving(true);
    setError('');
    setSuccess('');
    try {
      await createPurchase({
        supplier_id: form.supplier_id || null,
        invoice_number: form.invoice_number.trim() || null,
        notes: form.notes.trim() || null,
        payment_method: form.payment_method || 'cash',
        items: lines,
      });
      setCreateOpen(false);
      setSuccess('Purchase recorded and stock updated.');
      await load(1, q, statusFilter);
    } catch (err) {
      setError(err.response?.data?.error?.message || 'Failed to create purchase.');
    } finally {
      setSaving(false);
    }
  };

  const onCancel = async () => {
    if (!cancelReason.trim()) {
      setError('Cancellation reason is required.');
      return;
    }
    setSaving(true);
    setError('');
    setSuccess('');
    try {
      await cancelPurchase(selected.id, cancelReason.trim());
      setCancelOpen(false);
      setSuccess('Purchase cancelled and stock reversed.');
      await load(page, q, statusFilter);
    } catch (err) {
      setError(err.response?.data?.error?.message || 'Failed to cancel purchase.');
    } finally {
      setSaving(false);
    }
  };

  if (!canViewPurchases) {
    return (
      <PageShell>
        <Alert severity="warning">You do not have permission to view purchases.</Alert>
      </PageShell>
    );
  }

  return (
    <>
      {canManagePurchases ? (
        <PageActions>
          <Button variant="contained" startIcon={<AddOutlinedIcon />} onClick={openCreate}>
            New Purchase
          </Button>
        </PageActions>
      ) : null}

      <PageShell>
        <FilterBar
          actions={
            <Button variant="outlined" onClick={() => load(1, q, statusFilter)}>
              Search
            </Button>
          }
        >
          <SearchInput
            label="Search PO number, supplier, or invoice"
            placeholder="Search PO number, supplier, or invoice"
            value={q}
            onChange={(e) => setQ(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Enter') load(1, q, statusFilter);
            }}
            sx={{ ...filterControlWideSx, flex: 1 }}
          />
          <FormControl sx={{ minWidth: 160 }}>
            <InputLabel id="purchase-status-label">Status</InputLabel>
            <Select
              labelId="purchase-status-label"
              label="Status"
              value={statusFilter}
              onChange={(e) => {
                setStatusFilter(e.target.value);
                load(1, q, e.target.value);
              }}
            >
              <MenuItem value="">All</MenuItem>
              <MenuItem value="FINALIZED">Finalized</MenuItem>
              <MenuItem value="CANCELLED">Cancelled</MenuItem>
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
                  <TableCell>PO Number</TableCell>
                  <TableCell>Supplier</TableCell>
                  <TableCell>Invoice</TableCell>
                  <TableCell align="right">Total</TableCell>
                  <TableCell>Status</TableCell>
                  <TableCell>Date</TableCell>
                  <TableCell align="right">Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {purchases.map((purchase) => (
                  <TableRow key={purchase.id} hover>
                    <TableCell>{purchase.purchase_number}</TableCell>
                    <TableCell>
                      <TruncateText value={purchase.supplier_name || '—'} maxWidth={160} />
                    </TableCell>
                    <TableCell>{purchase.invoice_number || '—'}</TableCell>
                    <TableCell align="right">{formatMoney(purchase.total_amount)}</TableCell>
                    <TableCell>{statusChip(purchase.status)}</TableCell>
                    <TableCell>
                      <Typography variant="body2" color="text.secondary">
                        {purchase.created_at ? new Date(purchase.created_at).toLocaleString() : '—'}
                      </Typography>
                    </TableCell>
                    <TableCell align="right">
                      <Stack direction="row" spacing={0.5} justifyContent="flex-end">
                        <IconActionButton title="View" onClick={() => openDetail(purchase)}>
                          <VisibilityOutlinedIcon fontSize="small" />
                        </IconActionButton>
                        {canManagePurchases && purchase.status === 'FINALIZED' ? (
                          <IconActionButton
                            title="Cancel purchase"
                            color="error"
                            onClick={() => openCancel(purchase)}
                          >
                            <CancelOutlinedIcon fontSize="small" />
                          </IconActionButton>
                        ) : null}
                      </Stack>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
          {!loading && !purchases.length ? (
            <EmptyState
              title="No purchases found"
              description="Record supplier purchases to increase stock and update cost price."
              actionLabel={canManagePurchases ? 'New Purchase' : undefined}
              onAction={canManagePurchases ? openCreate : undefined}
            />
          ) : null}
        </TableCard>

        {!loading && purchases.length ? (
          <PaginationBar
            page={page}
            total={meta.total}
            pageSize={PAGE_SIZE}
            onPageChange={(next) => load(next, q, statusFilter)}
          />
        ) : null}
      </PageShell>

      <Dialog open={createOpen} onClose={() => setCreateOpen(false)} fullWidth maxWidth="md">
        <DialogTitle>New Purchase</DialogTitle>
        <DialogContent>
          <Stack spacing={2.5} sx={{ mt: 1 }}>
            <FormControl fullWidth>
              <InputLabel id="purchase-supplier-label">Supplier (optional)</InputLabel>
              <Select
                labelId="purchase-supplier-label"
                label="Supplier (optional)"
                value={form.supplier_id}
                onChange={(e) => setForm((f) => ({ ...f, supplier_id: e.target.value }))}
              >
                <MenuItem value="">None</MenuItem>
                {suppliers.map((supplier) => (
                  <MenuItem key={supplier.id} value={supplier.id}>
                    {supplier.name}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
            <FormControl fullWidth>
              <InputLabel id="purchase-pay-label">Payment</InputLabel>
              <Select
                labelId="purchase-pay-label"
                label="Payment"
                value={form.payment_method}
                onChange={(e) => setForm((f) => ({ ...f, payment_method: e.target.value }))}
              >
                <MenuItem value="cash">Cash / paid</MenuItem>
                <MenuItem value="online">Online / paid</MenuItem>
                <MenuItem value="credit">Credit (owe supplier)</MenuItem>
              </Select>
            </FormControl>
            <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2}>
              <TextField
                label="Supplier invoice number"
                value={form.invoice_number}
                onChange={(e) => setForm((f) => ({ ...f, invoice_number: e.target.value }))}
                fullWidth
              />
              <TextField
                label="Notes"
                value={form.notes}
                onChange={(e) => setForm((f) => ({ ...f, notes: e.target.value }))}
                fullWidth
              />
            </Stack>

            <Box>
              <Stack direction="row" justifyContent="space-between" alignItems="center" sx={{ mb: 1 }}>
                <Typography variant="subtitle2">Line items</Typography>
                <Button size="small" startIcon={<AddOutlinedIcon />} onClick={addLine}>
                  Add line
                </Button>
              </Stack>
              <Stack spacing={2}>
                {form.lines.map((line, index) => (
                  <Stack
                    key={`line-${index}`}
                    direction={{ xs: 'column', md: 'row' }}
                    spacing={1.5}
                    alignItems={{ md: 'center' }}
                  >
                    <Autocomplete
                      options={itemOptions}
                      getOptionLabel={(option) => option.name || ''}
                      value={itemOptions.find((item) => item.id === line.item_id) || null}
                      onChange={(_, value) => {
                        updateLine(index, {
                          item_id: value?.id || '',
                          unit_cost:
                            line.unit_cost !== ''
                              ? line.unit_cost
                              : value?.cost_price != null
                                ? String(value.cost_price)
                                : '',
                        });
                      }}
                      renderInput={(params) => (
                        <TextField {...params} label="Item" required sx={{ minWidth: 220, flex: 2 }} />
                      )}
                      sx={{ flex: 2 }}
                    />
                    <TextField
                      label="Qty"
                      type="number"
                      inputProps={{ min: 0.001, step: 'any' }}
                      value={line.quantity}
                      onChange={(e) => updateLine(index, { quantity: e.target.value })}
                      sx={{ width: { xs: '100%', md: 120 } }}
                    />
                    <TextField
                      label="Unit cost"
                      type="number"
                      inputProps={{ min: 0, step: '0.01' }}
                      value={line.unit_cost}
                      onChange={(e) => updateLine(index, { unit_cost: e.target.value })}
                      sx={{ width: { xs: '100%', md: 140 } }}
                    />
                    <IconButton
                      aria-label="Remove line"
                      onClick={() => removeLine(index)}
                      disabled={form.lines.length <= 1}
                    >
                      <DeleteOutlinedIcon fontSize="small" />
                    </IconButton>
                  </Stack>
                ))}
              </Stack>
            </Box>
          </Stack>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setCreateOpen(false)}>Cancel</Button>
          <Button variant="contained" onClick={onCreate} disabled={saving}>
            {saving ? 'Saving...' : 'Record purchase'}
          </Button>
        </DialogActions>
      </Dialog>

      <Dialog open={detailOpen} onClose={() => setDetailOpen(false)} fullWidth maxWidth="md">
        <DialogTitle>{selected?.purchase_number || 'Purchase details'}</DialogTitle>
        <DialogContent>
          {selected ? (
            <Stack spacing={2} sx={{ mt: 1 }}>
              <Stack direction="row" spacing={2} flexWrap="wrap">
                <Typography variant="body2">
                  <strong>Supplier:</strong> {selected.supplier_name || '—'}
                </Typography>
                <Typography variant="body2">
                  <strong>Invoice:</strong> {selected.invoice_number || '—'}
                </Typography>
                <Typography variant="body2">
                  <strong>Status:</strong> {selected.status}
                </Typography>
                <Typography variant="body2">
                  <strong>Total:</strong> {formatMoney(selected.total_amount)}
                </Typography>
              </Stack>
              {selected.notes ? (
                <Typography variant="body2" color="text.secondary">
                  {selected.notes}
                </Typography>
              ) : null}
              <Table size="small">
                <TableHead>
                  <TableRow>
                    <TableCell>Item</TableCell>
                    <TableCell align="right">Qty</TableCell>
                    <TableCell align="right">Unit cost</TableCell>
                    <TableCell align="right">Line total</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {(selected.items || []).map((line) => (
                    <TableRow key={line.id}>
                      <TableCell>{line.item_name}</TableCell>
                      <TableCell align="right">{line.quantity}</TableCell>
                      <TableCell align="right">{formatMoney(line.unit_cost)}</TableCell>
                      <TableCell align="right">{formatMoney(line.line_total)}</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
              {selected.status === 'CANCELLED' ? (
                <Alert severity="info">
                  Cancelled: {selected.cancellation_reason || '—'}
                </Alert>
              ) : null}
            </Stack>
          ) : (
            <LoadingBlock />
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDetailOpen(false)}>Close</Button>
        </DialogActions>
      </Dialog>

      <Dialog open={cancelOpen} onClose={() => setCancelOpen(false)} fullWidth maxWidth="sm">
        <DialogTitle>Cancel {selected?.purchase_number}</DialogTitle>
        <DialogContent>
          <Stack spacing={2} sx={{ mt: 1 }}>
            <Typography variant="body2" color="text.secondary">
              Stock quantities will be reversed. Cancellation is blocked if items were sold below
              purchased quantities.
            </Typography>
            <TextField
              label="Reason"
              value={cancelReason}
              onChange={(e) => setCancelReason(e.target.value)}
              fullWidth
              multiline
              minRows={2}
              required
            />
          </Stack>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setCancelOpen(false)}>Back</Button>
          <Button color="error" variant="contained" onClick={onCancel} disabled={saving}>
            {saving ? 'Cancelling...' : 'Cancel purchase'}
          </Button>
        </DialogActions>
      </Dialog>
    </>
  );
}
