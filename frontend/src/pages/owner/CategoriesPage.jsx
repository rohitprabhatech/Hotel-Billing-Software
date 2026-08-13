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
import {
  createCategory,
  listCategories,
  setCategoryStatus,
  updateCategory,
} from '../../services/categoryService';

const emptyForm = { name: '', description: '', parent_id: '' };

export default function CategoriesPage() {
  const [categories, setCategories] = useState([]);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [open, setOpen] = useState(false);
  const [editing, setEditing] = useState(null);
  const [form, setForm] = useState(emptyForm);
  const [saving, setSaving] = useState(false);

  const load = async () => {
    setError('');
    try {
      const res = await listCategories();
      setCategories(res.data || []);
    } catch (err) {
      setError(err.response?.data?.error?.message || 'Failed to load categories');
    }
  };

  useEffect(() => {
    load();
  }, []);

  const openCreate = () => {
    setEditing(null);
    setForm(emptyForm);
    setOpen(true);
  };

  const openEdit = (category) => {
    setEditing(category);
    setForm({
      name: category.name || '',
      description: category.description || '',
      parent_id: category.parent_id || '',
    });
    setOpen(true);
  };

  const onSave = async () => {
    setSaving(true);
    setError('');
    setSuccess('');
    const payload = {
      name: form.name,
      description: form.description || null,
      parent_id: form.parent_id || null,
    };
    try {
      if (editing) {
        await updateCategory(editing.id, payload);
        setSuccess('Category updated');
      } else {
        await createCategory(payload);
        setSuccess('Category created');
      }
      setOpen(false);
      await load();
    } catch (err) {
      setError(err.response?.data?.error?.message || 'Failed to save category');
    } finally {
      setSaving(false);
    }
  };

  const toggleActive = async (category) => {
    setError('');
    try {
      await setCategoryStatus(category.id, !category.is_active);
      await load();
    } catch (err) {
      setError(err.response?.data?.error?.message || 'Failed to update status');
    }
  };

  const parentName = (parentId) =>
    categories.find((c) => c.id === parentId)?.name || '—';

  return (
    <>
      <Stack direction="row" justifyContent="space-between" alignItems="center" mb={2}>
        <Typography variant="h5">Categories</Typography>
        <Button variant="contained" onClick={openCreate}>
          Add Category
        </Button>
      </Stack>

      {error ? <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert> : null}
      {success ? <Alert severity="success" sx={{ mb: 2 }}>{success}</Alert> : null}

      <Box sx={{ bgcolor: 'background.paper', borderRadius: 2, overflow: 'auto' }}>
        <Table size="small">
          <TableHead>
            <TableRow>
              <TableCell>Name</TableCell>
              <TableCell>Parent</TableCell>
              <TableCell>Description</TableCell>
              <TableCell>Active</TableCell>
              <TableCell align="right">Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {categories.map((category) => (
              <TableRow key={category.id}>
                <TableCell>{category.name}</TableCell>
                <TableCell>{parentName(category.parent_id)}</TableCell>
                <TableCell>{category.description || '—'}</TableCell>
                <TableCell>
                  <Switch
                    checked={category.is_active}
                    onChange={() => toggleActive(category)}
                  />
                </TableCell>
                <TableCell align="right">
                  <Button size="small" onClick={() => openEdit(category)}>
                    Edit
                  </Button>
                </TableCell>
              </TableRow>
            ))}
            {!categories.length ? (
              <TableRow>
                <TableCell colSpan={5}>
                  <Typography color="text.secondary">No categories yet.</Typography>
                </TableCell>
              </TableRow>
            ) : null}
          </TableBody>
        </Table>
      </Box>

      <Dialog open={open} onClose={() => setOpen(false)} fullWidth maxWidth="sm">
        <DialogTitle>{editing ? 'Edit Category' : 'Add Category'}</DialogTitle>
        <DialogContent>
          <Stack spacing={2} sx={{ mt: 1 }}>
            <TextField
              label="Name"
              value={form.name}
              onChange={(e) => setForm((f) => ({ ...f, name: e.target.value }))}
              required
              fullWidth
            />
            <FormControl fullWidth>
              <InputLabel>Parent Category</InputLabel>
              <Select
                label="Parent Category"
                value={form.parent_id}
                onChange={(e) => setForm((f) => ({ ...f, parent_id: e.target.value }))}
              >
                <MenuItem value="">None (top level)</MenuItem>
                {categories
                  .filter((c) => !editing || c.id !== editing.id)
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