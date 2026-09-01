import AddOutlinedIcon from '@mui/icons-material/AddOutlined';
import ShoppingCartCheckoutOutlinedIcon from '@mui/icons-material/ShoppingCartCheckoutOutlined';
import {
  Alert,
  Autocomplete,
  Box,
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  Stack,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
  TextField,
  Typography,
} from '@mui/material';
import DeleteOutlineOutlinedIcon from '@mui/icons-material/DeleteOutlineOutlined';
import { useCallback, useEffect, useState } from 'react';
import EmptyState from '../../components/EmptyState';
import LoadingBlock from '../../components/LoadingBlock';
import PageShell from '../../components/PageShell';
import TableCard from '../../components/TableCard';
import TruncateText from '../../components/TruncateText';
import IconActionButton from '../../components/ui/IconActionButton';
import StatusBadge from '../../components/ui/StatusBadge';
import { PageActions } from '../../context/PageActionsContext';
import { useAuth } from '../../context/AuthContext';
import { useModuleGate } from '../../context/ModulesContext';
import { listItems } from '../../services/itemService';
import {
  convertSalesOrder,
  createSalesOrder,
  listSalesOrders,
  updateSalesOrderStatus,
} from '../../services/orderDocumentService';

function money(value) {
  return `₹${Number(value || 0).toFixed(2)}`;
}

function docStatusVariant(status) {
  const key = String(status || '').toUpperCase();
  if (key === 'DRAFT') return 'pending';
  if (key === 'CONFIRMED') return 'info';
  if (key === 'CONVERTED') return 'active';
  if (key === 'CANCELLED') return 'cancelled';
  return 'info';
}

export default function SalesOrdersPage() {
  const moduleEnabled = useModuleGate('sales_orders');
  const { role } = useAuth();
  const canWrite = role === 'OWNER' || role === 'MANAGER';

  const [rows, setRows] = useState([]);
  const [catalog, setCatalog] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [open, setOpen] = useState(false);
  const [saving, setSaving] = useState(false);
  const [customerName, setCustomerName] = useState('');
  const [customerPhone, setCustomerPhone] = useState('');
  const [notes, setNotes] = useState('');
  const [discount, setDiscount] = useState('0');
  const [lines, setLines] = useState([{ item: null, quantity: '1' }]);

  const load = useCallback(async () => {
    if (!moduleEnabled) return;
    setLoading(true);
    setError('');
    try {
      const [orders, items] = await Promise.all([
        listSalesOrders({ per_page: 50 }),
        listItems({ per_page: 200, is_active: true }),
      ]);
      setRows(orders.data || []);
      setCatalog(items.data || []);
    } catch (err) {
      setError(err.response?.data?.error?.message || 'Failed to load sales orders');
    } finally {
      setLoading(false);
    }
  }, [moduleEnabled]);

  useEffect(() => {
    load();
  }, [load]);

  const resetForm = () => {
    setCustomerName('');
    setCustomerPhone('');
    setNotes('');
    setDiscount('0');
    setLines([{ item: null, quantity: '1' }]);
  };

  const onCreate = async () => {
    const payloadLines = lines
      .filter((line) => line.item?.id)
      .map((line) => ({
        item_id: line.item.id,
        quantity: Number(line.quantity),
        unit_price: line.item.price,
      }));
    if (!payloadLines.length) {
      setError('Add at least one item.');
      return;
    }
    setSaving(true);
    setError('');
    setSuccess('');
    try {
      const res = await createSalesOrder({
        customer_name: customerName.trim() || null,
        customer_phone: customerPhone.trim() || null,
        notes: notes.trim() || null,
        discount: Number(discount) || 0,
        items: payloadLines,
      });
      setSuccess(`Sales order ${res.data?.order_number} created`);
      setOpen(false);
      resetForm();
      await load();
    } catch (err) {
      setError(err.response?.data?.error?.message || 'Could not create sales order');
    } finally {
      setSaving(false);
    }
  };

  const onConfirm = async (row) => {
    try {
      await updateSalesOrderStatus(row.id, { status: 'CONFIRMED' });
      await load();
    } catch (err) {
      setError(err.response?.data?.error?.message || 'Status update failed');
    }
  };

  const onConvert = async (row) => {
    setError('');
    setSuccess('');
    try {
      const res = await convertSalesOrder(row.id, { payment_method: 'cash' });
      setSuccess(
        `Converted ${row.order_number} → bill ${res.data?.bill?.bill_number || res.data?.bill?.id}`,
      );
      await load();
    } catch (err) {
      setError(err.response?.data?.error?.message || 'Convert failed');
    }
  };

  if (!moduleEnabled) {
    return (
      <PageShell>
        <EmptyState
          icon={<ShoppingCartCheckoutOutlinedIcon />}
          title="Sales orders not enabled"
          description="Available for wholesale tenants."
        />
      </PageShell>
    );
  }

  return (
    <PageShell>
      <PageActions>
        {canWrite ? (
          <Button
            variant="contained"
            startIcon={<AddOutlinedIcon />}
            onClick={() => {
              resetForm();
              setOpen(true);
            }}
          >
            New sales order
          </Button>
        ) : null}
      </PageActions>

      {error ? (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      ) : null}
      {success ? (
        <Alert severity="success" sx={{ mb: 2 }}>
          {success}
        </Alert>
      ) : null}

      {loading ? (
        <LoadingBlock />
      ) : rows.length === 0 ? (
        <EmptyState
          icon={<ShoppingCartCheckoutOutlinedIcon />}
          title="No sales orders yet"
          description="Create an SO, confirm it, then convert to a bill when ready to fulfill."
        />
      ) : (
        <TableCard>
          <Table size="small">
            <TableHead>
              <TableRow>
                <TableCell>Number</TableCell>
                <TableCell>Customer</TableCell>
                <TableCell>Status</TableCell>
                <TableCell align="right">Total</TableCell>
                <TableCell>Lines</TableCell>
                <TableCell align="right">Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {rows.map((row) => (
                <TableRow key={row.id} hover>
                  <TableCell>{row.order_number}</TableCell>
                  <TableCell>
                    <TruncateText text={row.customer_name || '—'} />
                  </TableCell>
                  <TableCell>
                    <StatusBadge label={row.status} variant={docStatusVariant(row.status)} />
                  </TableCell>
                  <TableCell align="right">{money(row.grand_total)}</TableCell>
                  <TableCell>{(row.items || []).length}</TableCell>
                  <TableCell align="right">
                    <Stack direction="row" spacing={1} justifyContent="flex-end">
                      {canWrite && row.status === 'DRAFT' ? (
                        <Button size="small" onClick={() => onConfirm(row)}>
                          Confirm
                        </Button>
                      ) : null}
                      {canWrite && (row.status === 'DRAFT' || row.status === 'CONFIRMED') ? (
                        <Button size="small" variant="contained" onClick={() => onConvert(row)}>
                          Convert to bill
                        </Button>
                      ) : null}
                      {row.bill_id ? (
                        <Typography variant="caption" color="text.secondary">
                          Bill linked
                        </Typography>
                      ) : null}
                    </Stack>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableCard>
      )}

      <Dialog open={open} onClose={() => !saving && setOpen(false)} fullWidth maxWidth="md">
        <DialogTitle>New sales order</DialogTitle>
        <DialogContent>
          <Stack spacing={2} sx={{ mt: 1 }}>
            <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2}>
              <TextField
                label="Customer name"
                value={customerName}
                onChange={(e) => setCustomerName(e.target.value)}
                fullWidth
              />
              <TextField
                label="Phone"
                value={customerPhone}
                onChange={(e) => setCustomerPhone(e.target.value)}
                fullWidth
              />
              <TextField
                label="Discount"
                type="number"
                value={discount}
                onChange={(e) => setDiscount(e.target.value)}
                sx={{ minWidth: 120 }}
              />
            </Stack>
            <TextField
              label="Notes"
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              fullWidth
              multiline
              minRows={2}
            />
            {lines.map((line, index) => (
              <Stack key={index} direction={{ xs: 'column', sm: 'row' }} spacing={1} alignItems="center">
                <Autocomplete
                  options={catalog}
                  getOptionLabel={(opt) =>
                    opt ? `${opt.name} · ${money(opt.price)}` : ''
                  }
                  value={line.item}
                  onChange={(_, value) => {
                    setLines((prev) =>
                      prev.map((row, i) => (i === index ? { ...row, item: value } : row)),
                    );
                  }}
                  sx={{ flex: 1, minWidth: 220 }}
                  renderInput={(params) => <TextField {...params} label="Item" />}
                />
                <TextField
                  label="Qty"
                  type="number"
                  value={line.quantity}
                  onChange={(e) => {
                    setLines((prev) =>
                      prev.map((row, i) =>
                        i === index ? { ...row, quantity: e.target.value } : row,
                      ),
                    );
                  }}
                  sx={{ width: 120 }}
                />
                <IconActionButton
                  title="Remove line"
                  color="error"
                  disabled={lines.length === 1}
                  onClick={() => setLines((prev) => prev.filter((_, i) => i !== index))}
                >
                  <DeleteOutlineOutlinedIcon fontSize="small" />
                </IconActionButton>
              </Stack>
            ))}
            <Box>
              <Button onClick={() => setLines((prev) => [...prev, { item: null, quantity: '1' }])}>
                Add line
              </Button>
            </Box>
          </Stack>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpen(false)} disabled={saving}>
            Cancel
          </Button>
          <Button variant="contained" onClick={onCreate} disabled={saving}>
            Save sales order
          </Button>
        </DialogActions>
      </Dialog>
    </PageShell>
  );
}
