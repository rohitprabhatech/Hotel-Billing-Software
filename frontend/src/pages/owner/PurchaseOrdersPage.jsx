import AddOutlinedIcon from '@mui/icons-material/AddOutlined';
import AssignmentOutlinedIcon from '@mui/icons-material/AssignmentOutlined';
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
  convertPurchaseOrder,
  createPurchaseOrder,
  listPurchaseOrders,
  updatePurchaseOrderStatus,
} from '../../services/orderDocumentService';
import { listSuppliers } from '../../services/supplierService';

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

export default function PurchaseOrdersPage() {
  const moduleEnabled = useModuleGate('purchase_orders');
  const { role } = useAuth();
  const canWrite = role === 'OWNER' || role === 'MANAGER';

  const [rows, setRows] = useState([]);
  const [catalog, setCatalog] = useState([]);
  const [suppliers, setSuppliers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [open, setOpen] = useState(false);
  const [saving, setSaving] = useState(false);
  const [supplier, setSupplier] = useState(null);
  const [notes, setNotes] = useState('');
  const [lines, setLines] = useState([{ item: null, quantity: '1', unit_cost: '' }]);

  const load = useCallback(async () => {
    if (!moduleEnabled) return;
    setLoading(true);
    setError('');
    try {
      const [orders, items, supplierRows] = await Promise.all([
        listPurchaseOrders({ per_page: 50 }),
        listItems({ per_page: 200, is_active: true }),
        listSuppliers({ per_page: 100, is_active: true }),
      ]);
      setRows(orders.data || []);
      setCatalog(items.data || []);
      setSuppliers(supplierRows.data || []);
    } catch (err) {
      setError(err.response?.data?.error?.message || 'Failed to load purchase orders');
    } finally {
      setLoading(false);
    }
  }, [moduleEnabled]);

  useEffect(() => {
    load();
  }, [load]);

  const resetForm = () => {
    setSupplier(null);
    setNotes('');
    setLines([{ item: null, quantity: '1', unit_cost: '' }]);
  };

  const onCreate = async () => {
    const payloadLines = lines
      .filter((line) => line.item?.id && line.unit_cost !== '')
      .map((line) => ({
        item_id: line.item.id,
        quantity: Number(line.quantity),
        unit_cost: Number(line.unit_cost),
      }));
    if (!payloadLines.length) {
      setError('Add at least one item with unit cost.');
      return;
    }
    setSaving(true);
    setError('');
    setSuccess('');
    try {
      const res = await createPurchaseOrder({
        supplier_id: supplier?.id || null,
        notes: notes.trim() || null,
        items: payloadLines,
      });
      setSuccess(`Purchase order ${res.data?.order_number} created`);
      setOpen(false);
      resetForm();
      await load();
    } catch (err) {
      setError(err.response?.data?.error?.message || 'Could not create purchase order');
    } finally {
      setSaving(false);
    }
  };

  const onConfirm = async (row) => {
    try {
      await updatePurchaseOrderStatus(row.id, { status: 'CONFIRMED' });
      await load();
    } catch (err) {
      setError(err.response?.data?.error?.message || 'Status update failed');
    }
  };

  const onConvert = async (row) => {
    setError('');
    setSuccess('');
    try {
      const res = await convertPurchaseOrder(row.id, { payment_method: 'cash' });
      setSuccess(
        `Converted ${row.order_number} → purchase ${
          res.data?.purchase?.purchase_number || res.data?.purchase?.id
        }`,
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
          icon={<AssignmentOutlinedIcon />}
          title="Purchase orders not enabled"
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
            New purchase order
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
          icon={<AssignmentOutlinedIcon />}
          title="No purchase orders yet"
          description="Create a PO against a supplier, then convert to a purchase to receive stock."
        />
      ) : (
        <TableCard>
          <Table size="small">
            <TableHead>
              <TableRow>
                <TableCell>Number</TableCell>
                <TableCell>Supplier</TableCell>
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
                    <TruncateText text={row.supplier_name || '—'} />
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
                          Convert to purchase
                        </Button>
                      ) : null}
                      {row.purchase_id ? (
                        <Typography variant="caption" color="text.secondary">
                          Purchase linked
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
        <DialogTitle>New purchase order</DialogTitle>
        <DialogContent>
          <Stack spacing={2} sx={{ mt: 1 }}>
            <Autocomplete
              options={suppliers}
              getOptionLabel={(opt) => opt?.name || ''}
              value={supplier}
              onChange={(_, value) => setSupplier(value)}
              renderInput={(params) => <TextField {...params} label="Supplier" />}
            />
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
                  getOptionLabel={(opt) => opt?.name || ''}
                  value={line.item}
                  onChange={(_, value) => {
                    setLines((prev) =>
                      prev.map((row, i) =>
                        i === index
                          ? {
                              ...row,
                              item: value,
                              unit_cost:
                                row.unit_cost ||
                                (value?.cost_price != null ? String(value.cost_price) : ''),
                            }
                          : row,
                      ),
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
                  sx={{ width: 100 }}
                />
                <TextField
                  label="Unit cost"
                  type="number"
                  value={line.unit_cost}
                  onChange={(e) => {
                    setLines((prev) =>
                      prev.map((row, i) =>
                        i === index ? { ...row, unit_cost: e.target.value } : row,
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
              <Button
                onClick={() =>
                  setLines((prev) => [...prev, { item: null, quantity: '1', unit_cost: '' }])
                }
              >
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
            Save purchase order
          </Button>
        </DialogActions>
      </Dialog>
    </PageShell>
  );
}
