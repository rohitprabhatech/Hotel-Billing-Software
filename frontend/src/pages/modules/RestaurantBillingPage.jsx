import AddIcon from '@mui/icons-material/Add';
import RemoveIcon from '@mui/icons-material/Remove';
import DeleteOutlineOutlinedIcon from '@mui/icons-material/DeleteOutlineOutlined';
import KitchenOutlinedIcon from '@mui/icons-material/KitchenOutlined';
import {
  Alert,
  Box,
  Button,
  Chip,
  Collapse,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  Divider,
  FormControl,
  IconButton,
  InputLabel,
  Link,
  MenuItem,
  Select,
  Stack,
  TextField,
  Typography,
} from '@mui/material';
import { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import { Link as RouterLink, useNavigate } from 'react-router-dom';
import PageShell from '../../components/PageShell';
import SettleOrderDialog from '../../components/SettleOrderDialog';
import { useAuth } from '../../context/AuthContext';
import { useModuleGate } from '../../context/ModulesContext';
import { usePermissions } from '../../hooks/usePermissions';
import { createCategory, listCategories } from '../../services/categoryService';
import { createItem, listItems } from '../../services/itemService';
import { fireKot } from '../../services/kotService';
import {
  addOrderItem,
  createOrder,
  getOrder,
  removeOrderItem,
  updateOrderItem,
} from '../../services/orderService';
import { settleOrder } from '../../services/orderSettlementService';
import { createTable, listTables, listTableBills, setTableStatus } from '../../services/tableService';
import { PATHS } from '../../routes/paths';
import { getApiErrorMessage } from '../../utils/apiError';
import { paymentMethodLabel } from '../../utils/paymentMethod';

const STATUS_FILTERS = [
  { value: 'all', label: 'ALL' },
  { value: 'available', label: 'AVAILABLE' },
  { value: 'occupied', label: 'OCCUPIED' },
  { value: 'reserved', label: 'RESERVED' },
  { value: 'bill_pending', label: 'BILL PENDING' },
];

const STATUS_COLORS = {
  available: { bg: '#E8F5E9', border: '#2E7D32', text: '#1B5E20' },
  occupied: { bg: '#FFF3E0', border: '#EF6C00', text: '#E65100' },
  reserved: { bg: '#E3F2FD', border: '#1565C0', text: '#0D47A1' },
  bill_pending: { bg: '#FFEBEE', border: '#C62828', text: '#B71C1C' },
};

function money(value) {
  return `₹${Number(value || 0).toLocaleString('en-IN', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  })}`;
}

function statusLabel(status) {
  return STATUS_FILTERS.find((row) => row.value === status)?.label || String(status || '').toUpperCase();
}

const qtyBtnSx = {
  width: 40,
  height: 40,
  border: '1px solid',
  borderColor: 'divider',
  borderRadius: 1,
};

/**
 * Hotel / restaurant table-first POS.
 * Isolated to hotel_restaurant — cafe keeps Cafe POS.
 */
export default function RestaurantBillingPage() {
  const navigate = useNavigate();
  const { user } = useAuth();
  const { canManageTables, canWriteCategories, canWriteItems } = usePermissions();
  const tablesEnabled = useModuleGate('table_management');
  const ordersEnabled = useModuleGate('order_channels');
  const kotEnabled = useModuleGate('kot');
  const businessType = user?.tenant?.business_type || '';
  const hotelOnly = businessType === 'hotel_restaurant';
  const moduleEnabled = hotelOnly && tablesEnabled && ordersEnabled;

  const [tables, setTables] = useState([]);
  const [tableFilter, setTableFilter] = useState('all');
  const [tableSearch, setTableSearch] = useState('');
  const [selectedTableId, setSelectedTableId] = useState(null);
  const [order, setOrder] = useState(null);
  const [catalog, setCatalog] = useState([]);
  const [categories, setCategories] = useState([]);
  const [categoryId, setCategoryId] = useState('');
  const [itemSearch, setItemSearch] = useState('');
  const [discount, setDiscount] = useState('0');
  const [customerOpen, setCustomerOpen] = useState(false);
  const [customerName, setCustomerName] = useState('');
  const [customerPhone, setCustomerPhone] = useState('');
  const [billHistory, setBillHistory] = useState([]);
  const [settleOpen, setSettleOpen] = useState(false);
  const [settleInitialTab, setSettleInitialTab] = useState(0);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [busy, setBusy] = useState(false);
  const [itemPickerOpen, setItemPickerOpen] = useState(false);
  const [tableDialogOpen, setTableDialogOpen] = useState(false);
  const [categoryDialogOpen, setCategoryDialogOpen] = useState(false);
  const [itemDialogOpen, setItemDialogOpen] = useState(false);
  const [removeTarget, setRemoveTarget] = useState(null);
  const [tableForm, setTableForm] = useState({ code: '', capacity: '' });
  const [categoryForm, setCategoryForm] = useState({ name: '', description: '' });
  const [itemForm, setItemForm] = useState({
    name: '',
    price: '',
    category_id: '',
    gst_percentage: '5',
  });
  const kotTimer = useRef(null);

  const loadTables = useCallback(async () => {
    if (!moduleEnabled) return;
    try {
      const res = await listTables();
      setTables(res.data || []);
    } catch (err) {
      setError(getApiErrorMessage(err, 'Failed to load tables'));
    }
  }, [moduleEnabled]);

  const loadCatalog = useCallback(async () => {
    if (!moduleEnabled) return;
    try {
      const [itemsRes, catsRes] = await Promise.all([
        listItems({ is_active: true, per_page: 200, is_menu: true }).catch(() =>
          listItems({ is_active: true, per_page: 200 })
        ),
        listCategories(),
      ]);
      setCatalog(itemsRes.data || []);
      setCategories(catsRes.data || []);
    } catch (err) {
      setError(getApiErrorMessage(err, 'Failed to load menu'));
    }
  }, [moduleEnabled]);

  useEffect(() => {
    loadTables();
    loadCatalog();
  }, [loadTables, loadCatalog]);

  const selectedTable = useMemo(
    () => tables.find((row) => row.id === selectedTableId) || null,
    [tables, selectedTableId]
  );

  const filteredTables = useMemo(() => {
    const term = tableSearch.trim().toLowerCase();
    return tables.filter((table) => {
      if (tableFilter !== 'all' && table.status !== tableFilter) return false;
      if (!term) return true;
      return (
        table.code.toLowerCase().includes(term) ||
        (table.section || '').toLowerCase().includes(term)
      );
    });
  }, [tables, tableFilter, tableSearch]);

  const filteredItems = useMemo(() => {
    const term = itemSearch.trim().toLowerCase();
    return catalog.filter((item) => {
      if (categoryId && item.category_id !== categoryId) return false;
      if (!term) return true;
      return (
        item.name.toLowerCase().includes(term) ||
        (item.barcode || '').toLowerCase().includes(term)
      );
    });
  }, [catalog, categoryId, itemSearch]);

  const tableSummary = useMemo(() => {
    const counts = {
      total: tables.length,
      available: 0,
      occupied: 0,
      reserved: 0,
      bill_pending: 0,
    };
    tables.forEach((table) => {
      if (counts[table.status] != null) counts[table.status] += 1;
    });
    return counts;
  }, [tables]);

  const orderLines = order?.items || [];
  const orderSubtotal = useMemo(
    () => orderLines.reduce((sum, line) => sum + Number(line.line_total || 0), 0),
    [orderLines]
  );

  const scheduleKot = useCallback(
    (orderId) => {
      if (!kotEnabled || !orderId) return;
      if (kotTimer.current) window.clearTimeout(kotTimer.current);
      kotTimer.current = window.setTimeout(() => {
        fireKot(orderId).catch(() => {});
      }, 500);
    },
    [kotEnabled]
  );

  useEffect(
    () => () => {
      if (kotTimer.current) window.clearTimeout(kotTimer.current);
    },
    []
  );

  const refreshOrder = async (orderId) => {
    const res = await getOrder(orderId);
    setOrder(res.data);
    return res.data;
  };

  const selectTable = async (table) => {
    setError('');
    setSuccess('');
    setSelectedTableId(table.id);
    setDiscount('0');
    setBillHistory([]);
    try {
      const hist = await listTableBills(table.id, { per_page: 10 });
      setBillHistory(hist.data || []);
    } catch {
      setBillHistory([]);
    }
    if (table.open_order_id) {
      try {
        await refreshOrder(table.open_order_id);
      } catch (err) {
        setOrder(null);
        setError(getApiErrorMessage(err, 'Failed to load table order'));
      }
      return;
    }
    setOrder(null);
  };

  const onAddMenuItem = async (item) => {
    setError('');
    setSuccess('');
    if (!selectedTable) {
      setError('Select a table first.');
      return;
    }

    setBusy(true);
    try {
      if (!order?.id) {
        const created = await createOrder({
          channel: 'dine_in',
          dining_table_id: selectedTable.id,
          customer_name: customerName.trim() || null,
          customer_phone: customerPhone.trim() || null,
          items: [{ item_id: item.id, quantity: '1' }],
        });
        setOrder(created.data);
        scheduleKot(created.data.id);
        await loadTables();
        setSuccess(`Added ${item.name} to ${selectedTable.code}`);
      } else {
        const updated = await addOrderItem(order.id, { item_id: item.id, quantity: '1' });
        setOrder(updated.data);
        scheduleKot(order.id);
        await loadTables();
        setSuccess(`Added ${item.name}`);
      }
    } catch (err) {
      setError(getApiErrorMessage(err, 'Could not add item'));
    } finally {
      setBusy(false);
    }
  };

  const changeQty = async (line, nextQty) => {
    if (!order?.id) return;
    if (nextQty < 1) {
      setRemoveTarget({ line });
      return;
    }
    setBusy(true);
    setError('');
    try {
      const updated = await updateOrderItem(order.id, line.id, { quantity: String(nextQty) });
      setOrder(updated.data);
      if (nextQty > Number(line.quantity)) scheduleKot(order.id);
      await loadTables();
    } catch (err) {
      setError(getApiErrorMessage(err, 'Could not update quantity'));
    } finally {
      setBusy(false);
    }
  };

  const confirmRemove = async () => {
    if (!removeTarget || !order?.id) return;
    setBusy(true);
    setError('');
    try {
      const updated = await removeOrderItem(order.id, removeTarget.line.id);
      setOrder(updated.data);
      setRemoveTarget(null);
      await loadTables();
    } catch (err) {
      setError(getApiErrorMessage(err, 'Could not remove item'));
    } finally {
      setBusy(false);
    }
  };

  const saveTable = async () => {
    if (!tableForm.code.trim()) {
      setError('Table code is required.');
      return;
    }
    setBusy(true);
    setError('');
    try {
      const created = await createTable({
        code: tableForm.code.trim(),
        capacity: tableForm.capacity ? Number(tableForm.capacity) : null,
      });
      setTableDialogOpen(false);
      setTableForm({ code: '', capacity: '' });
      await loadTables();
      setSuccess(`Table ${created.data?.code || tableForm.code} added`);
      if (created.data) await selectTable(created.data);
    } catch (err) {
      setError(getApiErrorMessage(err, 'Could not add table'));
    } finally {
      setBusy(false);
    }
  };

  const saveCategory = async () => {
    if (!categoryForm.name.trim()) {
      setError('Category name is required.');
      return;
    }
    setBusy(true);
    setError('');
    try {
      const created = await createCategory({
        name: categoryForm.name.trim(),
        description: categoryForm.description.trim() || null,
      });
      const newId = created.data?.id;
      const newName = created.data?.name || categoryForm.name.trim();
      setCategoryDialogOpen(false);
      setCategoryForm({ name: '', description: '' });
      if (created.data) {
        setCategories((prev) => {
          if (prev.some((row) => row.id === created.data.id)) return prev;
          return [...prev, created.data];
        });
        setCategoryId(newId);
      }
      await loadCatalog();
      if (newId) setCategoryId(newId);
      setSuccess(`Category ${newName} added`);
    } catch (err) {
      setError(getApiErrorMessage(err, 'Could not add category'));
    } finally {
      setBusy(false);
    }
  };

  const saveItem = async () => {
    if (!itemForm.name.trim() || !itemForm.price || !itemForm.category_id) {
      setError('Item name, price, and category are required.');
      return;
    }
    setBusy(true);
    setError('');
    try {
      await createItem({
        name: itemForm.name.trim(),
        price: String(itemForm.price),
        category_id: itemForm.category_id,
        gst_percentage: String(itemForm.gst_percentage || '5'),
        stock_quantity: '0',
        is_menu: true,
      });
      setItemDialogOpen(false);
      setItemForm({ name: '', price: '', category_id: categoryId || '', gst_percentage: '5' });
      await loadCatalog();
      setSuccess('Item added to menu');
    } catch (err) {
      setError(getApiErrorMessage(err, 'Could not add item'));
    } finally {
      setBusy(false);
    }
  };

  const markBillPending = async () => {
    if (!selectedTable || selectedTable.status !== 'occupied') return;
    setBusy(true);
    try {
      await setTableStatus(selectedTable.id, 'bill_pending');
      await loadTables();
      setSuccess(`${selectedTable.code} marked bill pending`);
    } catch (err) {
      setError(getApiErrorMessage(err, 'Could not update table status'));
    } finally {
      setBusy(false);
    }
  };

  const sendKotNow = async () => {
    if (!order?.id || !kotEnabled) return;
    setBusy(true);
    try {
      const kot = await fireKot(order.id);
      setSuccess(`Kitchen ticket ${kot.data?.kot_number || ''} sent`);
    } catch (err) {
      setError(getApiErrorMessage(err, 'Could not send KOT'));
    } finally {
      setBusy(false);
    }
  };

  const quickPay = async (paymentMethod) => {
    if (!order?.id || !orderLines.length) {
      setError('Add items before payment.');
      return;
    }
    setBusy(true);
    setError('');
    try {
      const settled = await settleOrder(order.id, {
        discount: Number(discount || 0),
        payment_method: paymentMethod,
        customer_name: customerName.trim() || null,
        customer_phone: customerPhone.trim() || null,
      });
      const billId = settled.data?.bills?.[0]?.id || settled.data?.id;
      setSuccess('Bill generated — table is available for a new order');
      setOrder(null);
      setDiscount('0');
      const refreshed = await listTables();
      setTables(refreshed.data || []);
      if (selectedTableId) {
        try {
          const hist = await listTableBills(selectedTableId, { per_page: 10 });
          setBillHistory(hist.data || []);
        } catch {
          /* ignore */
        }
      }
      if (billId) navigate(`/print/bills/${billId}`);
    } catch (err) {
      setError(getApiErrorMessage(err, 'Payment failed'));
    } finally {
      setBusy(false);
    }
  };

  if (!hotelOnly) {
    return (
      <PageShell>
        <Alert severity="warning">
          Restaurant table billing is available for Hotel / Restaurant businesses only.
        </Alert>
      </PageShell>
    );
  }

  if (!moduleEnabled) {
    return (
      <PageShell>
        <Alert severity="warning">Table management and order modules are required.</Alert>
      </PageShell>
    );
  }

  return (
    <PageShell spacing={2}>
      {error ? <Alert severity="error" onClose={() => setError('')}>{error}</Alert> : null}
      {success ? <Alert severity="success" onClose={() => setSuccess('')}>{success}</Alert> : null}

      <Stack
        direction={{ xs: 'column', sm: 'row' }}
        spacing={1.5}
        alignItems={{ sm: 'center' }}
        justifyContent="space-between"
      >
        <Typography variant="h5" sx={{ fontWeight: 700, letterSpacing: '-0.02em' }}>
          Table Billing
        </Typography>
        <Button component={RouterLink} to={PATHS.billingNew} variant="outlined" size="small">
          Quick Bill (Takeaway)
        </Button>
      </Stack>

      <Stack direction="row" spacing={1} flexWrap="wrap" useFlexGap>
        {[
          { key: 'total', label: 'Total', value: tableSummary.total, filter: 'all' },
          { key: 'occupied', label: 'Occupied', value: tableSummary.occupied, filter: 'occupied' },
          { key: 'available', label: 'Available', value: tableSummary.available, filter: 'available' },
          { key: 'reserved', label: 'Reserved', value: tableSummary.reserved, filter: 'reserved' },
          {
            key: 'bill_pending',
            label: 'Bill Pending',
            value: tableSummary.bill_pending,
            filter: 'bill_pending',
          },
        ].map((row) => (
          <Chip
            key={row.key}
            label={`${row.label}: ${row.value}`}
            color={tableFilter === row.filter ? 'primary' : 'default'}
            variant={tableFilter === row.filter ? 'filled' : 'outlined'}
            onClick={() => setTableFilter(row.filter)}
            sx={{ fontWeight: 600 }}
          />
        ))}
      </Stack>

      <Box
        sx={{
          display: 'grid',
          gap: 2,
          gridTemplateColumns: { xs: '1fr', md: 'minmax(240px, 0.95fr) minmax(0, 1.05fr)' },
          alignItems: 'start',
        }}
      >
        {/* LEFT — Tables board */}
        <Box
          sx={{
            border: '1px solid',
            borderColor: 'divider',
            borderRadius: 2,
            p: 1.5,
            bgcolor: 'background.paper',
            minWidth: 0,
          }}
        >
          <Stack
            direction="row"
            spacing={1}
            alignItems="center"
            justifyContent="space-between"
            sx={{ mb: 1 }}
          >
            <Typography variant="subtitle2" sx={{ fontWeight: 700 }}>
              Tables
            </Typography>
            {canManageTables ? (
              <Button
                size="small"
                variant="outlined"
                startIcon={<AddIcon />}
                onClick={() => {
                  setError('');
                  setTableDialogOpen(true);
                }}
              >
                Add Table
              </Button>
            ) : null}
          </Stack>
          <TextField
            size="small"
            fullWidth
            placeholder="Search table…"
            value={tableSearch}
            onChange={(e) => setTableSearch(e.target.value)}
            sx={{ mb: 1 }}
          />
          <Stack direction="row" spacing={0.75} flexWrap="wrap" useFlexGap sx={{ mb: 1.5 }}>
            {STATUS_FILTERS.map((row) => (
              <Chip
                key={row.value}
                size="small"
                label={row.label}
                color={tableFilter === row.value ? 'primary' : 'default'}
                variant={tableFilter === row.value ? 'filled' : 'outlined'}
                onClick={() => setTableFilter(row.value)}
              />
            ))}
          </Stack>
          <Box
            sx={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fill, minmax(88px, 1fr))',
              gap: 1,
              maxHeight: { xs: 280, md: 'calc(100vh - 260px)' },
              overflow: 'auto',
            }}
          >
            {filteredTables.map((table) => {
              const colors = STATUS_COLORS[table.status] || STATUS_COLORS.available;
              const selected = table.id === selectedTableId;
              return (
                <Box
                  key={table.id}
                  component="button"
                  type="button"
                  onClick={() => selectTable(table)}
                  sx={{
                    border: '2px solid',
                    borderColor: colors.border,
                    bgcolor: colors.bg,
                    color: colors.text,
                    borderRadius: 1.5,
                    p: 1,
                    minHeight: 80,
                    cursor: 'pointer',
                    textAlign: 'left',
                    boxShadow: selected ? `0 0 0 2px ${colors.border}` : 'none',
                    '&:hover': { filter: 'brightness(0.97)' },
                  }}
                >
                  <Typography sx={{ fontWeight: 800, fontSize: '0.95rem', lineHeight: 1.2 }}>
                    {table.code}
                  </Typography>
                  <Typography sx={{ fontSize: '0.7rem', mt: 0.5, opacity: 0.9 }}>
                    {statusLabel(table.status)}
                  </Typography>
                  {table.open_order_id ? (
                    <>
                      <Typography sx={{ fontSize: '0.7rem', mt: 0.35, fontWeight: 600 }}>
                        {table.open_order_item_count || 0} item
                        {(table.open_order_item_count || 0) === 1 ? '' : 's'}
                      </Typography>
                      <Typography sx={{ fontSize: '0.75rem', fontWeight: 700 }}>
                        {money(table.open_order_grand_total)}
                      </Typography>
                    </>
                  ) : null}
                </Box>
              );
            })}
          </Box>
        </Box>

        {/* RIGHT — Current order */}
        <Box
          sx={{
            border: '1px solid',
            borderColor: 'divider',
            borderRadius: 2,
            p: 1.5,
            bgcolor: 'background.paper',
            minWidth: 0,
            position: { md: 'sticky' },
            top: { md: 16 },
          }}
        >
          {selectedTable ? (
            <>
              <Stack direction="row" spacing={1} alignItems="center" justifyContent="space-between" flexWrap="wrap">
                <Box>
                  <Typography variant="subtitle1" sx={{ fontWeight: 700 }}>
                    {selectedTable.code}
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    {statusLabel(selectedTable.status)}
                    {order?.id ? ' · Active order' : ''}
                  </Typography>
                </Box>
                <Button
                  variant="contained"
                  startIcon={<AddIcon />}
                  disabled={busy}
                  onClick={() => {
                    setError('');
                    setItemPickerOpen(true);
                  }}
                >
                  Add Item
                </Button>
              </Stack>

              {customerOpen ? (
                <Stack spacing={1} sx={{ mt: 1.5 }}>
                  <Button size="small" onClick={() => setCustomerOpen(false)}>
                    Hide customer
                  </Button>
                  <TextField
                    size="small"
                    label="Customer name (optional)"
                    value={customerName}
                    onChange={(e) => setCustomerName(e.target.value)}
                  />
                  <TextField
                    size="small"
                    label="Mobile (optional)"
                    value={customerPhone}
                    onChange={(e) => setCustomerPhone(e.target.value)}
                  />
                </Stack>
              ) : (
                <Button size="small" sx={{ mt: 1 }} onClick={() => setCustomerOpen(true)}>
                  Add customer (optional)
                </Button>
              )}

              <Divider sx={{ my: 1.5 }} />
              <Typography variant="subtitle2" sx={{ fontWeight: 700, mb: 1 }}>
                Current order
              </Typography>
              <Stack spacing={1.25} sx={{ maxHeight: 320, overflow: 'auto', mb: 1.5 }}>
                {!orderLines.length ? (
                  <Typography variant="body2" color="text.secondary">
                    Tap Add Item to start an order on this table.
                  </Typography>
                ) : (
                  orderLines.map((line) => (
                    <Box
                      key={line.id}
                      sx={{ borderBottom: '1px solid', borderColor: 'divider', pb: 1 }}
                    >
                      <Stack direction="row" justifyContent="space-between" spacing={1} alignItems="flex-start">
                        <Box sx={{ minWidth: 0, flex: 1 }}>
                          <Typography sx={{ fontSize: '0.9rem', fontWeight: 650 }}>
                            {line.item_name}
                          </Typography>
                          <Typography variant="caption" color="text.secondary">
                            {money(line.unit_price)} × {Number(line.quantity)}
                          </Typography>
                        </Box>
                        <Typography sx={{ fontWeight: 700, flexShrink: 0 }}>
                          {money(line.line_total)}
                        </Typography>
                      </Stack>
                      <Stack direction="row" spacing={1} alignItems="center" sx={{ mt: 0.75 }}>
                        <IconButton
                          size="small"
                          disabled={busy}
                          onClick={() => changeQty(line, Number(line.quantity) - 1)}
                          aria-label="Decrease quantity"
                          sx={qtyBtnSx}
                        >
                          <RemoveIcon fontSize="small" />
                        </IconButton>
                        <Typography sx={{ minWidth: 28, textAlign: 'center', fontWeight: 700 }}>
                          {Number(line.quantity)}
                        </Typography>
                        <IconButton
                          size="small"
                          disabled={busy}
                          onClick={() => changeQty(line, Number(line.quantity) + 1)}
                          aria-label="Increase quantity"
                          sx={qtyBtnSx}
                        >
                          <AddIcon fontSize="small" />
                        </IconButton>
                        <Button
                          size="small"
                          color="error"
                          variant="text"
                          disabled={busy}
                          startIcon={<DeleteOutlineOutlinedIcon fontSize="small" />}
                          onClick={() => setRemoveTarget({ line })}
                          sx={{ ml: 'auto' }}
                        >
                          Remove
                        </Button>
                      </Stack>
                    </Box>
                  ))
                )}
              </Stack>

              <Stack spacing={0.5} sx={{ mb: 1.5 }}>
                <Stack direction="row" justifyContent="space-between">
                  <Typography variant="body2">Subtotal</Typography>
                  <Typography variant="body2">{money(orderSubtotal)}</Typography>
                </Stack>
                <TextField
                  size="small"
                  label="Discount"
                  value={discount}
                  onChange={(e) => setDiscount(e.target.value)}
                  type="number"
                  inputProps={{ min: 0, step: '0.01' }}
                />
                <Stack direction="row" justifyContent="space-between">
                  <Typography sx={{ fontWeight: 800 }}>Grand total</Typography>
                  <Typography sx={{ fontWeight: 800 }}>
                    {money(Math.max(0, orderSubtotal - Number(discount || 0)))}
                  </Typography>
                </Stack>
                {order ? (
                  <Typography variant="caption" color="text.secondary">
                    Tax applied at bill generation from item GST.
                  </Typography>
                ) : null}
              </Stack>

              <Stack spacing={1}>
                {order?.id && kotEnabled ? (
                  <Button
                    variant="outlined"
                    startIcon={<KitchenOutlinedIcon />}
                    disabled={busy || !orderLines.length}
                    onClick={sendKotNow}
                  >
                    Send KOT
                  </Button>
                ) : null}
                {selectedTable.status === 'occupied' && order?.id ? (
                  <Button variant="outlined" color="warning" disabled={busy} onClick={markBillPending}>
                    Hold — Bill pending
                  </Button>
                ) : null}
                <Typography variant="caption" color="text.secondary" sx={{ fontWeight: 600 }}>
                  Payment
                </Typography>
                <Stack direction="row" spacing={1}>
                  <Button
                    fullWidth
                    variant="contained"
                    disabled={busy || !orderLines.length}
                    onClick={() => quickPay('cash')}
                  >
                    Cash
                  </Button>
                  <Button
                    fullWidth
                    variant="contained"
                    color="secondary"
                    disabled={busy || !orderLines.length}
                    onClick={() => quickPay('online')}
                  >
                    Online
                  </Button>
                </Stack>
                {order?.id ? (
                  <>
                    <Button
                      variant="contained"
                      color="success"
                      disabled={busy || !orderLines.length}
                      onClick={() => {
                        setSettleInitialTab(0);
                        setSettleOpen(true);
                      }}
                    >
                      Generate Bill
                    </Button>
                    <Button
                      variant="outlined"
                      disabled={busy || !orderLines.length}
                      onClick={() => {
                        setSettleInitialTab(1);
                        setSettleOpen(true);
                      }}
                    >
                      Split Bill
                    </Button>
                  </>
                ) : null}
                {billHistory[0]?.id ? (
                  <Button
                    variant="outlined"
                    onClick={() => navigate(`/print/bills/${billHistory[0].id}`)}
                  >
                    Print Bill
                  </Button>
                ) : null}
              </Stack>

              <Box sx={{ mt: 2 }}>
                <Divider sx={{ mb: 1.5 }} />
                <Typography variant="subtitle2" sx={{ fontWeight: 700, mb: 1 }}>
                  Bill history — {selectedTable.code}
                </Typography>
                {!billHistory.length ? (
                  <Typography variant="body2" color="text.secondary">
                    No completed bills for this table yet.
                  </Typography>
                ) : (
                  <Stack spacing={0.75} sx={{ maxHeight: 160, overflow: 'auto' }}>
                    {billHistory.map((bill) => (
                      <Stack
                        key={bill.id}
                        direction="row"
                        justifyContent="space-between"
                        spacing={1}
                        sx={{ fontSize: '0.8rem' }}
                      >
                        <Box sx={{ minWidth: 0 }}>
                          <Typography noWrap sx={{ fontWeight: 650, fontSize: '0.8rem' }}>
                            {bill.bill_number}
                          </Typography>
                          <Typography variant="caption" color="text.secondary">
                            {bill.created_at
                              ? new Date(bill.created_at).toLocaleString('en-IN', {
                                  day: '2-digit',
                                  month: 'short',
                                  hour: '2-digit',
                                  minute: '2-digit',
                                })
                              : '—'}{' '}
                            · {paymentMethodLabel(bill.payment_method)}
                          </Typography>
                        </Box>
                        <Stack alignItems="flex-end" spacing={0.25}>
                          <Typography sx={{ fontWeight: 700, fontSize: '0.8rem' }}>
                            {money(bill.grand_total)}
                          </Typography>
                          <Button
                            size="small"
                            sx={{ minWidth: 0, p: 0, fontSize: '0.7rem' }}
                            onClick={() => navigate(`/print/bills/${bill.id}`)}
                          >
                            Print
                          </Button>
                        </Stack>
                      </Stack>
                    ))}
                  </Stack>
                )}
              </Box>
            </>
          ) : (
            <Stack spacing={2} alignItems="center" justifyContent="center" sx={{ py: 6, textAlign: 'center' }}>
              <Typography variant="subtitle1" sx={{ fontWeight: 700 }}>
                Select a table
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Choose a table on the left to view or start an order.
              </Typography>
              <Typography variant="body2" color="text.secondary">
                For takeaway orders, use{' '}
                <Link component={RouterLink} to={PATHS.billingNew}>
                  Quick Bill
                </Link>
                .
              </Typography>
            </Stack>
          )}
        </Box>
      </Box>

      <Collapse in={Boolean(order)}>
        <SettleOrderDialog
          open={settleOpen}
          order={order}
          initialTab={settleInitialTab}
          onClose={() => setSettleOpen(false)}
          onSettled={async (result) => {
            setSettleOpen(false);
            setOrder(null);
            setDiscount('0');
            const refreshed = await listTables();
            setTables(refreshed.data || []);
            if (selectedTableId) {
              try {
                const hist = await listTableBills(selectedTableId, { per_page: 10 });
                setBillHistory(hist.data || []);
              } catch {
                /* ignore */
              }
            }
            const billId = result?.bills?.[0]?.id || result?.id;
            if (billId) navigate(`/print/bills/${billId}`);
          }}
        />
      </Collapse>

      {/* Item picker dialog */}
      <Dialog
        open={itemPickerOpen}
        onClose={() => !busy && setItemPickerOpen(false)}
        fullWidth
        maxWidth="md"
      >
        <DialogTitle>Add items to order</DialogTitle>
        <DialogContent dividers>
          <Stack
            direction="row"
            spacing={1}
            alignItems="center"
            justifyContent="space-between"
            flexWrap="wrap"
            useFlexGap
            sx={{ mb: 1 }}
          >
            <TextField
              size="small"
              placeholder="Search item…"
              value={itemSearch}
              onChange={(e) => setItemSearch(e.target.value)}
              sx={{ flex: 1, minWidth: 180 }}
            />
            <Stack direction="row" spacing={0.75} flexWrap="wrap" useFlexGap>
              {canWriteItems ? (
                <Button
                  size="small"
                  variant="outlined"
                  startIcon={<AddIcon />}
                  onClick={() => {
                    setError('');
                    setItemForm((prev) => ({
                      ...prev,
                      category_id: categoryId || prev.category_id || categories[0]?.id || '',
                    }));
                    setItemDialogOpen(true);
                  }}
                >
                  Add Item
                </Button>
              ) : null}
              {canWriteCategories ? (
                <Button
                  size="small"
                  variant="outlined"
                  startIcon={<AddIcon />}
                  onClick={() => {
                    setError('');
                    setCategoryDialogOpen(true);
                  }}
                >
                  Add Category
                </Button>
              ) : null}
            </Stack>
          </Stack>
          <Stack direction="row" spacing={0.75} flexWrap="wrap" useFlexGap sx={{ mb: 1.5 }}>
            <Chip
              size="small"
              label="All"
              color={!categoryId ? 'primary' : 'default'}
              variant={!categoryId ? 'filled' : 'outlined'}
              onClick={() => setCategoryId('')}
            />
            {categories.map((cat) => (
              <Chip
                key={cat.id}
                size="small"
                label={cat.name}
                color={categoryId === cat.id ? 'primary' : 'default'}
                variant={categoryId === cat.id ? 'filled' : 'outlined'}
                onClick={() => setCategoryId(cat.id)}
              />
            ))}
            {canWriteCategories ? (
              <Chip
                size="small"
                icon={<AddIcon sx={{ fontSize: '16px !important' }} />}
                label="Add Category"
                variant="outlined"
                color="primary"
                onClick={() => {
                  setError('');
                  setCategoryDialogOpen(true);
                }}
                sx={{ fontWeight: 600 }}
              />
            ) : null}
          </Stack>
          <Box
            sx={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fill, minmax(140px, 1fr))',
              gap: 1,
              maxHeight: 360,
              overflow: 'auto',
            }}
          >
            {filteredItems.map((item) => (
              <Box
                key={item.id}
                sx={{
                  border: '1px solid',
                  borderColor: 'divider',
                  borderRadius: 1.5,
                  p: 1.25,
                  bgcolor: 'background.default',
                  opacity: busy ? 0.55 : 1,
                  minHeight: 88,
                  display: 'flex',
                  flexDirection: 'column',
                  gap: 0.75,
                }}
              >
                <Box sx={{ flex: 1, minWidth: 0 }}>
                  <Typography sx={{ fontWeight: 650, fontSize: '0.85rem', lineHeight: 1.25 }}>
                    {item.name}
                  </Typography>
                  <Typography variant="body2" color="text.secondary" sx={{ mt: 0.35 }}>
                    {money(item.price)}
                  </Typography>
                </Box>
                <Button
                  size="small"
                  variant="contained"
                  disabled={busy || !selectedTable}
                  onClick={() => onAddMenuItem(item)}
                  sx={{ alignSelf: 'stretch', minHeight: 32 }}
                >
                  Add
                </Button>
              </Box>
            ))}
          </Box>
        </DialogContent>
        <DialogActions>
          <Button disabled={busy} onClick={() => setItemPickerOpen(false)}>
            Done
          </Button>
        </DialogActions>
      </Dialog>

      <Dialog open={tableDialogOpen} onClose={() => !busy && setTableDialogOpen(false)} fullWidth maxWidth="xs">
        <DialogTitle>Add Table</DialogTitle>
        <DialogContent>
          <Stack spacing={1.5} sx={{ pt: 1 }}>
            <TextField
              autoFocus
              label="Table code"
              placeholder="TB-01"
              value={tableForm.code}
              onChange={(e) => setTableForm((prev) => ({ ...prev, code: e.target.value }))}
              required
              fullWidth
            />
            <TextField
              label="Capacity (optional)"
              type="number"
              value={tableForm.capacity}
              onChange={(e) => setTableForm((prev) => ({ ...prev, capacity: e.target.value }))}
              inputProps={{ min: 1 }}
              fullWidth
            />
          </Stack>
        </DialogContent>
        <DialogActions>
          <Button disabled={busy} onClick={() => setTableDialogOpen(false)}>
            Cancel
          </Button>
          <Button variant="contained" disabled={busy} onClick={saveTable}>
            Save Table
          </Button>
        </DialogActions>
      </Dialog>

      <Dialog
        open={categoryDialogOpen}
        onClose={() => !busy && setCategoryDialogOpen(false)}
        fullWidth
        maxWidth="xs"
      >
        <DialogTitle>Add Category</DialogTitle>
        <DialogContent>
          <Stack spacing={1.5} sx={{ pt: 1 }}>
            <TextField
              autoFocus
              label="Category name"
              value={categoryForm.name}
              onChange={(e) => setCategoryForm((prev) => ({ ...prev, name: e.target.value }))}
              required
              fullWidth
              placeholder="Chinese Food"
            />
            <TextField
              label="Description (optional)"
              value={categoryForm.description}
              onChange={(e) => setCategoryForm((prev) => ({ ...prev, description: e.target.value }))}
              fullWidth
              multiline
              minRows={2}
            />
          </Stack>
        </DialogContent>
        <DialogActions>
          <Button disabled={busy} onClick={() => setCategoryDialogOpen(false)}>
            Cancel
          </Button>
          <Button variant="contained" disabled={busy} onClick={saveCategory}>
            Save Category
          </Button>
        </DialogActions>
      </Dialog>

      <Dialog open={itemDialogOpen} onClose={() => !busy && setItemDialogOpen(false)} fullWidth maxWidth="xs">
        <DialogTitle>Create menu item</DialogTitle>
        <DialogContent>
          <Stack spacing={1.5} sx={{ pt: 1 }}>
            <TextField
              autoFocus
              label="Item name"
              value={itemForm.name}
              onChange={(e) => setItemForm((prev) => ({ ...prev, name: e.target.value }))}
              required
              fullWidth
            />
            <TextField
              label="Price"
              type="number"
              value={itemForm.price}
              onChange={(e) => setItemForm((prev) => ({ ...prev, price: e.target.value }))}
              required
              fullWidth
              inputProps={{ min: 0, step: '0.01' }}
            />
            <FormControl fullWidth required>
              <InputLabel id="rb-item-cat">Category</InputLabel>
              <Select
                labelId="rb-item-cat"
                label="Category"
                value={itemForm.category_id}
                onChange={(e) => setItemForm((prev) => ({ ...prev, category_id: e.target.value }))}
              >
                {categories.map((cat) => (
                  <MenuItem key={cat.id} value={cat.id}>
                    {cat.name}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
            <TextField
              label="GST %"
              type="number"
              value={itemForm.gst_percentage}
              onChange={(e) => setItemForm((prev) => ({ ...prev, gst_percentage: e.target.value }))}
              fullWidth
              inputProps={{ min: 0, step: '0.01' }}
            />
          </Stack>
        </DialogContent>
        <DialogActions>
          <Button disabled={busy} onClick={() => setItemDialogOpen(false)}>
            Cancel
          </Button>
          <Button variant="contained" disabled={busy} onClick={saveItem}>
            Save Item
          </Button>
        </DialogActions>
      </Dialog>

      <Dialog open={Boolean(removeTarget)} onClose={() => !busy && setRemoveTarget(null)} fullWidth maxWidth="xs">
        <DialogTitle>Remove item</DialogTitle>
        <DialogContent>
          <Typography>Remove {removeTarget?.line?.item_name || 'item'} from order?</Typography>
        </DialogContent>
        <DialogActions>
          <Button disabled={busy} onClick={() => setRemoveTarget(null)}>
            Cancel
          </Button>
          <Button color="error" variant="contained" disabled={busy} onClick={confirmRemove}>
            Remove
          </Button>
        </DialogActions>
      </Dialog>
    </PageShell>
  );
}
