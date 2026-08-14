import AddOutlinedIcon from '@mui/icons-material/AddOutlined';
import EditOutlinedIcon from '@mui/icons-material/EditOutlined';
import HistoryOutlinedIcon from '@mui/icons-material/HistoryOutlined';
import {
  Alert,
  Box,
  Button,
  CircularProgress,
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
import { Link as RouterLink } from 'react-router-dom';
import EmptyState from '../../components/EmptyState';
import FilterBar from '../../components/FilterBar';
import PageShell from '../../components/PageShell';
import TableCard from '../../components/TableCard';
import TruncateText from '../../components/TruncateText';
import { PageActions } from '../../context/PageActionsContext';
import { PATHS } from '../../routes/paths';
import { listCategories } from '../../services/categoryService';
import {
  createItem,
  listItems,
  setItemStatus,
  updateItem,
} from '../../services/itemService';

const emptyForm = {
  name: '',
  sku: '',
  category_id: '',
  description: '',
  price: '',
  cost_price: '',
  gst_percentage: '2.5',
  stock_quantity: '',
};

function money(value) {
  if (value === null || value === undefined || value === '') return '—';
  return `₹${Number(value).toFixed(2)}`;
}

export default function ItemsPage() {
  const [items, setItems] = useState([]);
  const [categories, setCategories] = useState([]);
  const [q, setQ] = useState('');
  const [categoryFilter, setCategoryFilter] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [open, setOpen] = useState(false);
  const [editing, setEditing] = useState(null);
  const [form, setForm] = useState(emptyForm);
  const [saving, setSaving] = useState(false);
  const [loading, setLoading] = useState(true);
  const [deactivateTarget, setDeactivateTarget] = useState(null);
  const [deactivateReason, setDeactivateReason] = useState('');

  const load = async () => {
    setError('');
    setLoading(true);
    try {
      const params = {
        q: q || undefined,
        category_id: categoryFilter || undefined,
        per_page: 100,
      };
      if (statusFilter === 'active') params.is_active = true;
      if (statusFilter === 'inactive') params.is_active = false;

      const [catRes, itemRes] = await Promise.all([
        listCategories(),
        listItems(params),
      ]);
      setCategories(catRes.data || []);
      setItems(itemRes.data || []);
    } catch (err) {
      setError(err.response?.data?.error?.message || 'Unable to load items.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [categoryFilter, statusFilter]);

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
      category_id: item.category_id || '',
      description: item.description || '',
      price: String(item.price ?? ''),
      cost_price: item.cost_price === null || item.cost_price === undefined ? '' : String(item.cost_price),
      gst_percentage: String(item.gst_percentage ?? '0'),
      stock_quantity:
        item.stock_quantity === null || item.stock_quantity === undefined
          ? ''
          : String(item.stock_quantity),
    });
    setOpen(true);
  };

  const onSave = async () => {
    setSaving(true);
    setError('');
    setSuccess('');
    const payload = {
      name: form.name,
      sku: form.sku.trim() || null,
      category_id: form.category_id,
      description: form.description || null,
      price: Number(form.price),
      cost_price: form.cost_price === '' ? null : Number(form.cost_price),
      gst_percentage: Number(form.gst_percentage),
      stock_quantity: form.stock_quantity === '' ? null : Number(form.stock_quantity),
    };
    try {
      if (editing) {
        await updateItem(editing.id, payload);
        setSuccess('Item updated successfully.');
      } else {
        await createItem(payload);
        setSuccess('Item created successfully.');
      }
      setOpen(false);
      await load();
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
        return load();
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
      await load();
    } catch (err) {
      setError(err.response?.data?.error?.message || 'Failed to deactivate item');
    } finally {
      setSaving(false);
    }
  };

  return (
    <>
      <PageActions>
        <Button variant="contained" startIcon={<AddOutlinedIcon />} onClick={openCreate}>
          Add Item
        </Button>
      </PageActions>

      <PageShell>
        <FilterBar
          actions={
            <Button variant="outlined" onClick={load}>
              Search
            </Button>
          }
        >
          <TextField
            label="Search name or SKU"
            value={q}
            onChange={(e) => setQ(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Enter') load();
            }}
            sx={{ minWidth: { xs: '100%', sm: 220 }, flex: 1 }}
          />
          <FormControl sx={{ minWidth: { xs: '100%', sm: 180 } }}>
            <InputLabel>Category</InputLabel>
            <Select
              label="Category"
              value={categoryFilter}
              onChange={(e) => setCategoryFilter(e.target.value)}
            >
              <MenuItem value="">All</MenuItem>
              {categories.map((c) => (
                <MenuItem key={c.id} value={c.id}>
                  {c.hierarchy_path || c.name}
                </MenuItem>
              ))}
            </Select>
          </FormControl>
          <FormControl sx={{ minWidth: { xs: '100%', sm: 140 } }}>
            <InputLabel>Status</InputLabel>
            <Select
              label="Status"
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
            >
              <MenuItem value="">All</MenuItem>
              <MenuItem value="active">Active</MenuItem>
              <MenuItem value="inactive">Inactive</MenuItem>
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
            <Table size="small" sx={{ minWidth: 1100 }}>
              <TableHead>
                <TableRow>
                  <TableCell>Item Name</TableCell>
                  <TableCell>SKU</TableCell>
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
                      <TruncateText value={item.category_name || '—'} maxWidth={120} />
                    </TableCell>
                    <TableCell align="right">{money(item.price)}</TableCell>
                    <TableCell align="right">{money(item.cost_price)}</TableCell>
                    <TableCell align="right">{Number(item.gst_percentage).toFixed(2)}%</TableCell>
                    <TableCell align="right">
                      {item.stock_quantity === null || item.stock_quantity === undefined
                        ? '—'
                        : Number(item.stock_quantity)}
                    </TableCell>
                    <TableCell>
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
                    </TableCell>
                    <TableCell>
                      <TruncateText value={item.created_by_name || '—'} maxWidth={110} />
                    </TableCell>
                    <TableCell align="right">
                      <Stack direction="row" spacing={0.5} justifyContent="flex-end">
                        <Tooltip title="Edit">
                          <IconButton
                            size="small"
                            aria-label={`Edit ${item.name}`}
                            onClick={() => openEdit(item)}
                          >
                            <EditOutlinedIcon fontSize="small" />
                          </IconButton>
                        </Tooltip>
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
              actionLabel="Add Item"
              onAction={openCreate}
            />
          ) : null}
        </TableCard>
      </PageShell>

      <Dialog open={open} onClose={() => setOpen(false)} fullWidth maxWidth="sm">
        <DialogTitle>{editing ? 'Edit Item' : 'Add Item'}</DialogTitle>
        <DialogContent>
          <Box
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
            <FormControl fullWidth required>
              <InputLabel>Category</InputLabel>
              <Select
                label="Category"
                value={form.category_id}
                onChange={(e) => setForm((f) => ({ ...f, category_id: e.target.value }))}
              >
                {categories
                  .filter((c) => c.is_active || c.id === form.category_id)
                  .map((c) => (
                    <MenuItem key={c.id} value={c.id}>
                      {c.hierarchy_path || c.name}
                    </MenuItem>
                  ))}
              </Select>
            </FormControl>
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
              label="Description"
              value={form.description}
              onChange={(e) => setForm((f) => ({ ...f, description: e.target.value }))}
              fullWidth
              multiline
              minRows={2}
              sx={{ gridColumn: { sm: '1 / -1' } }}
            />
          </Box>
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
    </>
  );
}
