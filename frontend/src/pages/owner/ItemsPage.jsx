import AddOutlinedIcon from '@mui/icons-material/AddOutlined';
import EditOutlinedIcon from '@mui/icons-material/EditOutlined';
import HistoryOutlinedIcon from '@mui/icons-material/HistoryOutlined';
import Inventory2OutlinedIcon from '@mui/icons-material/Inventory2Outlined';
import MoveToInboxOutlinedIcon from '@mui/icons-material/MoveToInboxOutlined';
import SwapVertOutlinedIcon from '@mui/icons-material/SwapVertOutlined';
import {
  Alert,
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
import { Link as RouterLink, useSearchParams } from 'react-router-dom';
import CategoryHierarchyAutocomplete from '../../components/CategoryHierarchyAutocomplete';
import EmptyState from '../../components/EmptyState';
import FilterBar from '../../components/FilterBar';
import LoadingBlock from '../../components/LoadingBlock';
import PageShell from '../../components/PageShell';
import PaginationBar from '../../components/PaginationBar';
import TableCard from '../../components/TableCard';
import TruncateText from '../../components/TruncateText';
import { PageActions } from '../../context/PageActionsContext';
import { useAuth } from '../../context/AuthContext';
import { useModuleGate } from '../../context/ModulesContext';
import { usePermissions } from '../../hooks/usePermissions';
import { filterControlSx, filterControlWideSx } from '../../layouts/shell';
import { PATHS } from '../../routes/paths';
import { stockMovementsPath } from '../../utils/permissions';
import { listCategories } from '../../services/categoryService';
import {
  adjustItemStock,
  createItem,
  listItems,
  receiveItemStock,
  setItemStatus,
  updateItem,
} from '../../services/itemService';
import { DEFAULT_UOM, UOM_OPTIONS } from '../../utils/uom';
import { formatCategoryPath } from '../../utils/categoryHierarchy';

const emptyForm = {
  name: '',
  sku: '',
  barcode: '',
  uom: DEFAULT_UOM,
  category_id: '',
  description: '',
  price: '',
  cost_price: '',
  gst_percentage: '2.5',
  stock_quantity: '',
  minimum_stock_level: '',
  is_menu: false,
  is_veg: '',
};

const PAGE_SIZE = 25;

function money(value) {
  if (value === null || value === undefined || value === '') return '—';
  return `₹${Number(value).toFixed(2)}`;
}

export default function ItemsPage() {
  const { role } = useAuth();
  const restaurantMenuEnabled = useModuleGate('restaurant_menu');
  const { canWriteItems, canStockItems, canAudit, canStockMovements } = usePermissions();
  const movementsPath = stockMovementsPath(role);
  const [searchParams] = useSearchParams();
  const initialStock = ['low', 'out', 'tracked'].includes(searchParams.get('stock_status') || '')
    ? searchParams.get('stock_status')
    : '';
  const [items, setItems] = useState([]);
  const [categories, setCategories] = useState([]);
  const [q, setQ] = useState('');
  const [categoryFilter, setCategoryFilter] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [stockFilter, setStockFilter] = useState(initialStock);
  const [page, setPage] = useState(1);
  const [meta, setMeta] = useState({ page: 1, per_page: PAGE_SIZE, total: 0 });
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [open, setOpen] = useState(false);
  const [editing, setEditing] = useState(null);
  const [form, setForm] = useState(emptyForm);
  const [saving, setSaving] = useState(false);
  const [loading, setLoading] = useState(true);
  const [deactivateTarget, setDeactivateTarget] = useState(null);
  const [deactivateReason, setDeactivateReason] = useState('');
  const [adjustTarget, setAdjustTarget] = useState(null);
  const [adjustDelta, setAdjustDelta] = useState('');
  const [adjustReason, setAdjustReason] = useState('');
  const [adjusting, setAdjusting] = useState(false);
  const [receiveTarget, setReceiveTarget] = useState(null);
  const [receiveQty, setReceiveQty] = useState('');
  const [receiveReason, setReceiveReason] = useState('');
  const [receiving, setReceiving] = useState(false);

  const load = async (nextPage = page) => {
    setError('');
    setLoading(true);
    try {
      const params = {
        q: q || undefined,
        category_id: categoryFilter || undefined,
        page: nextPage,
        per_page: PAGE_SIZE,
      };
      if (statusFilter === 'active') params.is_active = true;
      if (statusFilter === 'inactive') params.is_active = false;
      if (stockFilter) params.stock_status = stockFilter;

      const [catRes, itemRes] = await Promise.all([
        listCategories(),
        listItems(params),
      ]);
      setCategories(catRes.data || []);
      setItems(itemRes.data || []);
      setMeta(itemRes.meta || { page: nextPage, per_page: PAGE_SIZE, total: 0 });
      setPage(itemRes.meta?.page || nextPage);
    } catch (err) {
      setError(err.response?.data?.error?.message || 'Unable to load items.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load(1);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [categoryFilter, statusFilter, stockFilter]);

  const openCreate = () => {
    setEditing(null);
    setForm(emptyForm);
    setOpen(true);
  };

  const openEdit = (item) => {
    setEditing(item);
    setForm({
      name: item.name || '',
      sku: item.sku || '',
      barcode: item.barcode || '',
      uom: item.uom || DEFAULT_UOM,
      category_id: item.category_id || '',
      description: item.description || '',
      price: item.price ?? '',
      cost_price: item.cost_price ?? '',
      gst_percentage: item.gst_percentage ?? '2.5',
      stock_quantity: item.stock_quantity ?? '',
      minimum_stock_level: item.minimum_stock_level ?? '',
      is_menu: Boolean(item.is_menu),
      is_veg: item.is_veg === true ? 'true' : item.is_veg === false ? 'false' : '',
    });
    setOpen(true);
  };

  const onSave = async () => {
    if (!form.name.trim()) {
      setError('Item name is required.');
      return;
    }
    if (!form.category_id) {
      setError('Category is required.');
      return;
    }
    setSaving(true);
    setError('');
    setSuccess('');
    const payload = {
      name: form.name.trim(),
      sku: form.sku.trim() || null,
      barcode: form.barcode.trim() || null,
      uom: form.uom || DEFAULT_UOM,
      category_id: form.category_id,
      description: form.description || null,
      price: form.price,
      cost_price: form.cost_price === '' ? null : form.cost_price,
      gst_percentage: form.gst_percentage,
      stock_quantity: form.stock_quantity === '' ? null : form.stock_quantity,
      minimum_stock_level:
        form.minimum_stock_level === '' ? null : form.minimum_stock_level,
    };
    if (restaurantMenuEnabled) {
      payload.is_menu = Boolean(form.is_menu);
      payload.is_veg = form.is_veg === '' ? null : form.is_veg === 'true';
    }
    try {
      if (editing) {
        await updateItem(editing.id, payload);
        setSuccess('Item updated successfully.');
      } else {
        await createItem(payload);
        setSuccess('Item created successfully.');
      }
      setOpen(false);
      await load(editing ? page : 1);
    } catch (err) {
      setError(err.response?.data?.error?.message || 'Failed to save item');
    } finally {
      setSaving(false);
    }
  };

  const onToggleActive = (item) => {
    if (item.is_active) {
      setDeactivateTarget(item);
      setDeactivateReason('');
      return;
    }
    setItemStatus(item.id, true)
      .then(() => {
        setSuccess('Item reactivated successfully.');
        return load(page);
      })
      .catch((err) => {
        setError(err.response?.data?.error?.message || 'Failed to update status');
      });
  };

  const confirmDeactivate = async () => {
    if (!deactivateTarget) return;
    setSaving(true);
    setError('');
    try {
      await setItemStatus(deactivateTarget.id, false, deactivateReason || null);
      setSuccess('Item deactivated successfully.');
      setDeactivateTarget(null);
      await load(page);
    } catch (err) {
      setError(err.response?.data?.error?.message || 'Failed to deactivate item');
    } finally {
      setSaving(false);
    }
  };

  return (
    <>
      <PageActions>
        {canWriteItems ? (
          <Button variant="contained" startIcon={<AddOutlinedIcon />} onClick={openCreate}>
            Add Item
          </Button>
        ) : null}
      </PageActions>

      <PageShell>
        <FilterBar
          actions={
            <Button variant="outlined" onClick={() => load(1)}>
              Search
            </Button>
          }
        >
          <TextField
            label="Search name or SKU"
            value={q}
            onChange={(e) => setQ(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Enter') load(1);
            }}
            sx={{ ...filterControlWideSx, flex: 1 }}
          />
          <CategoryHierarchyAutocomplete
            categories={categories}
            valueId={categoryFilter}
            onChange={(id) => {
              setCategoryFilter(id);
              setPage(1);
            }}
            label="Category"
            allowEmpty
            emptyOption={{ id: '', name: 'All categories', isEmpty: true }}
            activeOnly={false}
            sx={filterControlWideSx}
          />
          <FormControl sx={filterControlSx}>
            <InputLabel>Status</InputLabel>
            <Select
              label="Status"
              value={statusFilter}
              onChange={(e) => {
                setStatusFilter(e.target.value);
                setPage(1);
              }}
            >
              <MenuItem value="">All</MenuItem>
              <MenuItem value="active">Active</MenuItem>
              <MenuItem value="inactive">Inactive</MenuItem>
            </Select>
          </FormControl>
          <FormControl sx={filterControlSx}>
            <InputLabel>Stock</InputLabel>
            <Select
              label="Stock"
              value={stockFilter}
              onChange={(e) => {
                setStockFilter(e.target.value);
                setPage(1);
              }}
            >
              <MenuItem value="">All stock</MenuItem>
              <MenuItem value="tracked">Tracked</MenuItem>
              <MenuItem value="low">Low</MenuItem>
              <MenuItem value="out">Out</MenuItem>
            </Select>
          </FormControl>
        </FilterBar>

        {error ? <Alert severity="error">{error}</Alert> : null}
        {success ? <Alert severity="success">{success}</Alert> : null}

        <TableCard>
          {loading ? (
            <LoadingBlock />
          ) : (
            <Table size="small" sx={{ minWidth: 1100 }}>
              <TableHead>
                <TableRow>
                  <TableCell>Item Name</TableCell>
                  <TableCell>SKU</TableCell>
                  <TableCell>Barcode</TableCell>
                  <TableCell>UoM</TableCell>
                  {restaurantMenuEnabled ? (
                    <>
                      <TableCell>Menu</TableCell>
                      <TableCell>Diet</TableCell>
                    </>
                  ) : null}
                  <TableCell>Category</TableCell>
                  <TableCell align="right">Price</TableCell>
                  <TableCell align="right">Cost</TableCell>
                  <TableCell align="right">GST</TableCell>
                  <TableCell align="right">Stock</TableCell>
                  <TableCell>Status</TableCell>
                  <TableCell>Created By</TableCell>
                  <TableCell align="right">Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {items.map((item) => (
                  <TableRow key={item.id} hover>
                    <TableCell>
                      <TruncateText value={item.name} maxWidth={160} />
                    </TableCell>
                    <TableCell>
                      <TruncateText value={item.sku || '—'} maxWidth={100} />
                    </TableCell>
                    <TableCell>
                      <TruncateText value={item.barcode || '—'} maxWidth={120} />
                    </TableCell>
                    <TableCell>{item.uom || DEFAULT_UOM}</TableCell>
                    {restaurantMenuEnabled ? (
                      <>
                        <TableCell>{item.is_menu ? 'Yes' : 'No'}</TableCell>
                        <TableCell>
                          {item.is_veg === true
                            ? 'Veg'
                            : item.is_veg === false
                              ? 'Non-veg'
                              : '—'}
                        </TableCell>
                      </>
                    ) : null}
                    <TableCell>
                      <TruncateText
                        value={formatCategoryPath(
                          item.category_hierarchy_path || item.category_name || '—'
                        )}
                        maxWidth={180}
                      />
                    </TableCell>
                    <TableCell align="right">{money(item.price)}</TableCell>
                    <TableCell align="right">{money(item.cost_price)}</TableCell>
                    <TableCell align="right">{Number(item.gst_percentage).toFixed(2)}%</TableCell>
                    <TableCell align="right">
                      {item.stock_quantity === null || item.stock_quantity === undefined
                        ? '—'
                        : Number(item.stock_quantity)}
                      {item.minimum_stock_level != null ? (
                        <Typography variant="caption" color="text.secondary" display="block">
                          min {Number(item.minimum_stock_level)}
                        </Typography>
                      ) : null}
                    </TableCell>
                    <TableCell>
                      {canWriteItems ? (
                        <Stack direction="row" alignItems="center" spacing={1}>
                          <Switch
                            size="small"
                            checked={item.is_active}
                            onChange={() => onToggleActive(item)}
                            inputProps={{ 'aria-label': `Toggle ${item.name}` }}
                          />
                          <Typography variant="caption" color="text.secondary">
                            {item.is_active ? 'Active' : 'Inactive'}
                          </Typography>
                        </Stack>
                      ) : (
                        <Typography variant="caption" color="text.secondary">
                          {item.is_active ? 'Active' : 'Inactive'}
                        </Typography>
                      )}
                    </TableCell>
                    <TableCell>
                      <TruncateText value={item.created_by_name || '—'} maxWidth={110} />
                    </TableCell>
                    <TableCell align="right">
                      <Stack direction="row" spacing={0.5} justifyContent="flex-end">
                        {canStockItems ? (
                          <Tooltip title="Receive stock">
                            <IconButton
                              size="small"
                              aria-label={`Receive stock for ${item.name}`}
                              onClick={() => {
                                setReceiveTarget(item);
                                setReceiveQty('');
                                setReceiveReason('');
                                setError('');
                                setSuccess('');
                              }}
                            >
                              <MoveToInboxOutlinedIcon fontSize="small" />
                            </IconButton>
                          </Tooltip>
                        ) : null}
                        {canStockItems &&
                        item.stock_quantity !== null &&
                        item.stock_quantity !== undefined ? (
                          <Tooltip title="Adjust stock">
                            <IconButton
                              size="small"
                              aria-label={`Adjust stock for ${item.name}`}
                              onClick={() => {
                                setAdjustTarget(item);
                                setAdjustDelta('');
                                setAdjustReason('');
                                setError('');
                                setSuccess('');
                              }}
                            >
                              <Inventory2OutlinedIcon fontSize="small" />
                            </IconButton>
                          </Tooltip>
                        ) : null}
                        {canWriteItems ? (
                          <Tooltip title="Edit">
                            <IconButton
                              size="small"
                              aria-label={`Edit ${item.name}`}
                              onClick={() => openEdit(item)}
                            >
                              <EditOutlinedIcon fontSize="small" />
                            </IconButton>
                          </Tooltip>
                        ) : null}
                        {canStockMovements ? (
                          <Tooltip title="View stock movements">
                            <IconButton
                              size="small"
                              component={RouterLink}
                              to={`${movementsPath}?item_id=${encodeURIComponent(item.id)}`}
                              aria-label={`View stock movements for ${item.name}`}
                            >
                              <SwapVertOutlinedIcon fontSize="small" />
                            </IconButton>
                          </Tooltip>
                        ) : null}
                        {canAudit ? (
                          <Tooltip title="View activity">
                            <IconButton
                              size="small"
                              component={RouterLink}
                              to={`${PATHS.ownerItemActivity}?q=${encodeURIComponent(item.name || '')}`}
                              aria-label={`View activity for ${item.name}`}
                            >
                              <HistoryOutlinedIcon fontSize="small" />
                            </IconButton>
                          </Tooltip>
                        ) : null}
                      </Stack>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
          {!loading && !items.length ? (
            <EmptyState
              title="No items found"
              description="Add catalog items with price, GST, optional SKU, cost, and stock."
              actionLabel={canWriteItems ? 'Add Item' : undefined}
              onAction={canWriteItems ? openCreate : undefined}
            />
          ) : null}
          {!loading && items.length ? (
            <PaginationBar
              page={meta.page}
              perPage={meta.per_page}
              total={meta.total}
              onPageChange={(next) => load(next)}
            />
          ) : null}
        </TableCard>
      </PageShell>

      <Dialog open={open} onClose={() => setOpen(false)} fullWidth maxWidth="sm">
        <DialogTitle>{editing ? 'Edit Item' : 'Add Item'}</DialogTitle>
        <DialogContent>
          <Stack
            spacing={2.5}
            sx={{
              mt: 1,
              display: 'grid',
              gap: 2.5,
              gridTemplateColumns: { xs: '1fr', sm: '1fr 1fr' },
            }}
          >
            <TextField
              label="Item Name"
              value={form.name}
              onChange={(e) => setForm((f) => ({ ...f, name: e.target.value }))}
              required
              fullWidth
              sx={{ gridColumn: { sm: '1 / -1' } }}
            />
            <TextField
              label="SKU (optional)"
              value={form.sku}
              onChange={(e) => setForm((f) => ({ ...f, sku: e.target.value }))}
              fullWidth
              helperText="Unique per business when provided"
            />
            <TextField
              label="Barcode (optional)"
              value={form.barcode}
              onChange={(e) => setForm((f) => ({ ...f, barcode: e.target.value }))}
              fullWidth
              helperText="Scannable code — unique per business"
            />
            <FormControl fullWidth>
              <InputLabel id="item-uom-label">Unit of measure</InputLabel>
              <Select
                labelId="item-uom-label"
                label="Unit of measure"
                value={form.uom}
                onChange={(e) => setForm((f) => ({ ...f, uom: e.target.value }))}
              >
                {UOM_OPTIONS.map((option) => (
                  <MenuItem key={option.value} value={option.value}>
                    {option.label}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
            <CategoryHierarchyAutocomplete
              categories={categories}
              valueId={form.category_id}
              onChange={(id) => setForm((f) => ({ ...f, category_id: id }))}
              label="Category"
              required
              activeOnly
              includeInactiveIds={[form.category_id]}
            />
            <TextField
              label="Price (₹)"
              type="number"
              value={form.price}
              onChange={(e) => setForm((f) => ({ ...f, price: e.target.value }))}
              required
              fullWidth
              inputProps={{ min: 0, step: '0.01' }}
            />
            <TextField
              label="Cost Price (₹)"
              type="number"
              value={form.cost_price}
              onChange={(e) => setForm((f) => ({ ...f, cost_price: e.target.value }))}
              fullWidth
              inputProps={{ min: 0, step: '0.01' }}
              helperText="Optional purchase/cost price"
            />
            <TextField
              label="GST %"
              type="number"
              value={form.gst_percentage}
              onChange={(e) => setForm((f) => ({ ...f, gst_percentage: e.target.value }))}
              required
              fullWidth
              inputProps={{ min: 0, max: 100, step: '0.01' }}
            />
            <TextField
              label="Stock Quantity"
              type="number"
              value={form.stock_quantity}
              onChange={(e) => setForm((f) => ({ ...f, stock_quantity: e.target.value }))}
              fullWidth
              inputProps={{ min: 0, step: '0.001' }}
              helperText="Leave blank if you are not tracking stock"
            />
            <TextField
              label="Minimum Stock Level"
              type="number"
              value={form.minimum_stock_level}
              onChange={(e) =>
                setForm((f) => ({ ...f, minimum_stock_level: e.target.value }))
              }
              fullWidth
              inputProps={{ min: 0, step: '0.001' }}
              helperText="Low-stock alert when stock reaches this level (blank = no alert)"
            />
            {restaurantMenuEnabled ? (
              <>
                <Stack direction="row" alignItems="center" spacing={1} sx={{ gridColumn: { sm: '1 / -1' } }}>
                  <Switch
                    checked={Boolean(form.is_menu)}
                    onChange={(e) => setForm((f) => ({ ...f, is_menu: e.target.checked }))}
                  />
                  <Typography variant="body2">Show on restaurant menu</Typography>
                </Stack>
                <FormControl fullWidth>
                  <InputLabel id="item-veg-label">Diet type (optional)</InputLabel>
                  <Select
                    labelId="item-veg-label"
                    label="Diet type (optional)"
                    value={form.is_veg}
                    onChange={(e) => setForm((f) => ({ ...f, is_veg: e.target.value }))}
                  >
                    <MenuItem value="">Not specified</MenuItem>
                    <MenuItem value="true">Veg</MenuItem>
                    <MenuItem value="false">Non-veg</MenuItem>
                  </Select>
                </FormControl>
              </>
            ) : null}
            <TextField
              label="Description"
              value={form.description}
              onChange={(e) => setForm((f) => ({ ...f, description: e.target.value }))}
              fullWidth
              multiline
              minRows={2}
              sx={{ gridColumn: { sm: '1 / -1' } }}
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

      <Dialog open={Boolean(deactivateTarget)} onClose={() => setDeactivateTarget(null)} fullWidth maxWidth="xs">
        <DialogTitle>Deactivate Item</DialogTitle>
        <DialogContent>
          <Stack spacing={2.5} sx={{ mt: 1 }}>
            <Typography variant="body2">
              Soft-deactivate <strong>{deactivateTarget?.name}</strong>. It will leave new bills
              but remain in history and owner item activity.
            </Typography>
            <TextField
              label="Reason (optional)"
              value={deactivateReason}
              onChange={(e) => setDeactivateReason(e.target.value)}
              fullWidth
              multiline
              minRows={2}
              placeholder="e.g. Temporarily unavailable"
            />
          </Stack>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDeactivateTarget(null)}>Cancel</Button>
          <Button variant="contained" color="warning" onClick={confirmDeactivate} disabled={saving}>
            {saving ? 'Saving...' : 'Deactivate'}
          </Button>
        </DialogActions>
      </Dialog>

      <Dialog
        open={Boolean(adjustTarget)}
        onClose={() => !adjusting && setAdjustTarget(null)}
        fullWidth
        maxWidth="xs"
      >
        <DialogTitle>Adjust stock — {adjustTarget?.name}</DialogTitle>
        <DialogContent>
          <Stack spacing={2} sx={{ mt: 1 }}>
            <Typography variant="body2" color="text.secondary">
              Current stock: <strong>{Number(adjustTarget?.stock_quantity ?? 0)}</strong>
              {adjustTarget?.minimum_stock_level != null
                ? ` · Min ${Number(adjustTarget.minimum_stock_level)}`
                : ''}
            </Typography>
            <TextField
              label="Adjustment (+ add / − remove)"
              type="number"
              value={adjustDelta}
              onChange={(e) => setAdjustDelta(e.target.value)}
              fullWidth
              helperText="Example: 10 to restock, -2 to write off"
              inputProps={{ step: '1' }}
              autoFocus
            />
            <TextField
              label="Reason (optional)"
              value={adjustReason}
              onChange={(e) => setAdjustReason(e.target.value)}
              fullWidth
            />
          </Stack>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setAdjustTarget(null)} disabled={adjusting}>
            Cancel
          </Button>
          <Button
            variant="contained"
            disabled={adjusting || !adjustDelta || Number(adjustDelta) === 0}
            onClick={async () => {
              if (!adjustTarget) return;
              setAdjusting(true);
              setError('');
              setSuccess('');
              try {
                const res = await adjustItemStock(adjustTarget.id, {
                  delta: Number(adjustDelta),
                  reason: adjustReason || null,
                });
                setSuccess(
                  `Stock for ${res.data?.name || adjustTarget.name} is now ${res.data?.stock_quantity}.`,
                );
                setAdjustTarget(null);
                await load(page);
              } catch (err) {
                setError(err.response?.data?.error?.message || 'Stock adjustment failed.');
              } finally {
                setAdjusting(false);
              }
            }}
          >
            {adjusting ? 'Saving...' : 'Apply'}
          </Button>
        </DialogActions>
      </Dialog>

      <Dialog
        open={Boolean(receiveTarget)}
        onClose={() => !receiving && setReceiveTarget(null)}
        fullWidth
        maxWidth="xs"
      >
        <DialogTitle>Receive stock — {receiveTarget?.name}</DialogTitle>
        <DialogContent>
          <Stack spacing={2} sx={{ mt: 1 }}>
            <Typography variant="body2" color="text.secondary">
              {receiveTarget?.stock_quantity === null || receiveTarget?.stock_quantity === undefined
                ? 'This item is not tracking stock yet. Receiving will start tracking at the quantity you enter.'
                : `Current stock: ${Number(receiveTarget.stock_quantity)}`}
              {receiveTarget?.minimum_stock_level != null
                ? ` · Min ${Number(receiveTarget.minimum_stock_level)}`
                : ''}
            </Typography>
            <TextField
              label="Quantity received"
              type="number"
              value={receiveQty}
              onChange={(e) => setReceiveQty(e.target.value)}
              fullWidth
              helperText="Must be greater than zero"
              inputProps={{ min: 0.001, step: '1' }}
              autoFocus
            />
            <TextField
              label="Reason (optional)"
              value={receiveReason}
              onChange={(e) => setReceiveReason(e.target.value)}
              fullWidth
              placeholder="e.g. Supplier delivery"
            />
          </Stack>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setReceiveTarget(null)} disabled={receiving}>
            Cancel
          </Button>
          <Button
            variant="contained"
            disabled={receiving || !receiveQty || Number(receiveQty) <= 0}
            onClick={async () => {
              if (!receiveTarget) return;
              setReceiving(true);
              setError('');
              setSuccess('');
              try {
                const res = await receiveItemStock(receiveTarget.id, {
                  quantity: Number(receiveQty),
                  reason: receiveReason || null,
                });
                setSuccess(
                  `Received stock for ${res.data?.name || receiveTarget.name}. Now ${res.data?.stock_quantity}.`,
                );
                setReceiveTarget(null);
                await load(page);
              } catch (err) {
                setError(err.response?.data?.error?.message || 'Receive stock failed.');
              } finally {
                setReceiving(false);
              }
            }}
          >
            {receiving ? 'Saving...' : 'Receive'}
          </Button>
        </DialogActions>
      </Dialog>
    </>
  );
}
