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
  Switch,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
  TextField,
  Typography,
} from '@mui/material';
import { useEffect, useState } from 'react';
import { listCategories } from '../../services/categoryService';
import {
  createItem,
  listItems,
  setItemStatus,
  updateItem,
} from '../../services/itemService';

const emptyForm = {
  name: '',
  category_id: '',
  description: '',
  price: '',
  gst_percentage: '5',
};

export default function ItemsPage() {
  const [items, setItems] = useState([]);
  const [categories, setCategories] = useState([]);
  const [q, setQ] = useState('');
  const [categoryFilter, setCategoryFilter] = useState('');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [open, setOpen] = useState(false);
  const [editing, setEditing] = useState(null);
  const [form, setForm] = useState(emptyForm);
  const [saving, setSaving] = useState(false);

  const load = async () => {
    setError('');
    try {
      const [catRes, itemRes] = await Promise.all([
        listCategories(),
        listItems({
          q: q || undefined,
          category_id: categoryFilter || undefined,
          per_page: 100,
        }),
      ]);
      setCategories(catRes.data || []);
      setItems(itemRes.data || []);
    } catch (err) {
      setError(err.response?.data?.error?.message || 'Failed to load items');
    }
  };

  useEffect(() => {
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [categoryFilter]);

  const openCreate = () => {
    setEditing(null);
    setForm(emptyForm);
    setOpen(true);
  };

  const openEdit = (item) => {
    setEditing(item);
    setForm({
      name: item.name || '',
      category_id: item.category_id || '',
      description: item.description || '',
      price: String(item.price ?? ''),
      gst_percentage: String(item.gst_percentage ?? '0'),
    });
    setOpen(true);
  };

  const onSave = async () => {
    setSaving(true);
    setError('');
    setSuccess('');
    const payload = {
      name: form.name,
      category_id: form.category_id,
      description: form.description || null,
      price: Number(form.price),
      gst_percentage: Number(form.gst_percentage),
    };
    try {
      if (editing) {
        await updateItem(editing.id, payload);
        setSuccess('Item updated');
      } else {
        await createItem(payload);
        setSuccess('Item created');
      }
      setOpen(false);
      await load();
    } catch (err) {
      setError(err.response?.data?.error?.message || 'Failed to save item');
    } finally {
      setSaving(false);
    }
  };

  const toggleActive = async (item) => {
    setError('');
    try {
      await setItemStatus(item.id, !item.is_active);
      await load();
    } catch (err) {
      setError(err.response?.data?.error?.message || 'Failed to update status');
    }
  };

  return (
    <>
      <Stack direction="row" justifyContent="space-between" alignItems="center" mb={2}>
        <Typography variant="h5">Items</Typography>
        <Button variant="contained" onClick={openCreate}>
          Add Item
        </Button>
      </Stack>

      <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2} mb={2}>
        <TextField
          label="Search"
          value={q}
          onChange={(e) => setQ(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === 'Enter') load();
          }}
          fullWidth
        />
        <FormControl sx={{ minWidth: 200 }}>
          <InputLabel>Category</InputLabel>
          <Select
            label="Category"
            value={categoryFilter}
            onChange={(e) => setCategoryFilter(e.target.value)}
          >
            <MenuItem value="">All</MenuItem>
            {categories.map((c) => (
              <MenuItem key={c.id} value={c.id}>
                {c.name}
              </MenuItem>
            ))}
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
              <TableCell>Name</TableCell>
              <TableCell>Category</TableCell>
              <TableCell align="right">Price</TableCell>
              <TableCell align="right">GST %</TableCell>
              <TableCell>Active</TableCell>
              <TableCell align="right">Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {items.map((item) => (
              <TableRow key={item.id}>
                <TableCell>{item.name}</TableCell>
                <TableCell>{item.category_name || '—'}</TableCell>
                <TableCell align="right">₹{Number(item.price).toFixed(2)}</TableCell>
                <TableCell align="right">{Number(item.gst_percentage).toFixed(2)}</TableCell>
                <TableCell>
                  <Switch checked={item.is_active} onChange={() => toggleActive(item)} />
                </TableCell>
                <TableCell align="right">
                  <Button size="small" onClick={() => openEdit(item)}>
                    Edit
                  </Button>
                </TableCell>
              </TableRow>
            ))}
            {!items.length ? (
              <TableRow>
                <TableCell colSpan={6}>
                  <Typography color="text.secondary">No items found.</Typography>
                </TableCell>
              </TableRow>
            ) : null}
          </TableBody>
        </Table>
      </Box>

      <Dialog open={open} onClose={() => setOpen(false)} fullWidth maxWidth="sm">
        <DialogTitle>{editing ? 'Edit Item' : 'Add Item'}</DialogTitle>
        <DialogContent>
          <Stack spacing={2} sx={{ mt: 1 }}>
            <TextField
              label="Item Name"
              value={form.name}
              onChange={(e) => setForm((f) => ({ ...f, name: e.target.value }))}
              required
              fullWidth
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
                      {c.name}
                    </MenuItem>
                  ))}
              </Select>
            </FormControl>
            <TextField
              label="Description"
              value={form.description}
              onChange={(e) => setForm((f) => ({ ...f, description: e.target.value }))}
              fullWidth
              multiline
              minRows={2}
            />
            <Stack direction="row" spacing={2}>
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
                label="GST %"
                type="number"
                value={form.gst_percentage}
                onChange={(e) => setForm((f) => ({ ...f, gst_percentage: e.target.value }))}
                required
                fullWidth
                inputProps={{ min: 0, max: 100, step: '0.01' }}
              />
            </Stack>
          </Stack>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpen(false)}>Cancel</Button>
          <Button variant="contained" onClick={onSave} disabled={saving}>
            Save
          </Button>
        </DialogActions>
      </Dialog>
    </>
  );
}