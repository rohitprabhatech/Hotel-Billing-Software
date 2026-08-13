import AddOutlinedIcon from '@mui/icons-material/AddOutlined';
import EditOutlinedIcon from '@mui/icons-material/EditOutlined';
import {
  Alert,
  Autocomplete,
  Box,
  Button,
  Card,
  CardContent,
  CircularProgress,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  IconButton,
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
import { useEffect, useMemo, useState } from 'react';
import EmptyState from '../../components/EmptyState';
import PageShell from '../../components/PageShell';
import Section from '../../components/Section';
import TableCard from '../../components/TableCard';
import TruncateText from '../../components/TruncateText';
import { PageActions } from '../../context/PageActionsContext';
import {
  createCategory,
  listCategories,
  setCategoryStatus,
  updateCategory,
} from '../../services/categoryService';

const emptyForm = { name: '', description: '', parent_id: '' };

const ROOT_OPTION = {
  id: '',
  name: 'No Parent (Root Category)',
  isRoot: true,
};

function collectDescendantIds(categories, rootId) {
  const childrenMap = new Map();
  categories.forEach((category) => {
    const parentKey = category.parent_id || '';
    if (!childrenMap.has(parentKey)) childrenMap.set(parentKey, []);
    childrenMap.get(parentKey).push(category.id);
  });

  const descendants = new Set();
  const stack = [...(childrenMap.get(rootId) || [])];
  while (stack.length) {
    const current = stack.pop();
    if (descendants.has(current)) continue;
    descendants.add(current);
    stack.push(...(childrenMap.get(current) || []));
  }
  return descendants;
}

function buildHierarchyRows(categories) {
  const byParent = new Map();
  categories.forEach((category) => {
    const key = category.parent_id || 'root';
    if (!byParent.has(key)) byParent.set(key, []);
    byParent.get(key).push(category);
  });
  byParent.forEach((list) => list.sort((a, b) => a.name.localeCompare(b.name)));

  const rows = [];
  const walk = (parentKey, depth) => {
    (byParent.get(parentKey) || []).forEach((category) => {
      rows.push({ category, depth });
      walk(category.id, depth + 1);
    });
  };
  walk('root', 0);

  // Orphans (parent missing from list) appear after roots
  const listed = new Set(rows.map((row) => row.category.id));
  categories
    .filter((category) => !listed.has(category.id))
    .sort((a, b) => a.name.localeCompare(b.name))
    .forEach((category) => rows.push({ category, depth: 0 }));

  return rows;
}

export default function CategoriesPage() {
  const [categories, setCategories] = useState([]);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [formError, setFormError] = useState('');
  const [open, setOpen] = useState(false);
  const [editing, setEditing] = useState(null);
  const [form, setForm] = useState(emptyForm);
  const [saving, setSaving] = useState(false);
  const [loading, setLoading] = useState(true);

  const load = async () => {
    setError('');
    try {
      const res = await listCategories();
      setCategories(res.data || []);
    } catch (err) {
      setError(err.response?.data?.error?.message || 'Unable to load categories.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
  }, []);

  const hierarchyRows = useMemo(() => buildHierarchyRows(categories), [categories]);

  const parentOptions = useMemo(() => {
    const blocked = new Set();
    if (editing?.id) {
      blocked.add(editing.id);
      collectDescendantIds(categories, editing.id).forEach((id) => blocked.add(id));
    }
    const options = categories
      .filter((category) => !blocked.has(category.id))
      .slice()
      .sort((a, b) => a.name.localeCompare(b.name));
    return [ROOT_OPTION, ...options];
  }, [categories, editing]);

  const selectedParent =
    parentOptions.find((option) => option.id === (form.parent_id || '')) || ROOT_OPTION;

  const openCreate = () => {
    setEditing(null);
    setForm(emptyForm);
    setFormError('');
    setOpen(true);
  };

  const openEdit = (category) => {
    setEditing(category);
    setForm({
      name: category.name || '',
      description: category.description || '',
      parent_id: category.parent_id || '',
    });
    setFormError('');
    setOpen(true);
  };

  const onSave = async () => {
    if (!form.name.trim()) {
      setFormError('Category name is required.');
      return;
    }
    if (editing && form.parent_id === editing.id) {
      setFormError('Category cannot be its own parent.');
      return;
    }

    setSaving(true);
    setError('');
    setSuccess('');
    setFormError('');
    const payload = {
      name: form.name.trim(),
      description: form.description || null,
      parent_id: form.parent_id || null,
    };
    try {
      if (editing) {
        await updateCategory(editing.id, payload);
        setSuccess('Category updated successfully.');
      } else {
        await createCategory(payload);
        setSuccess('Category created successfully.');
      }
      setOpen(false);
      await load();
    } catch (err) {
      setFormError(err.response?.data?.error?.message || 'Failed to save category');
    } finally {
      setSaving(false);
    }
  };

  const toggleActive = async (category) => {
    setError('');
    setSuccess('');
    try {
      await setCategoryStatus(category.id, !category.is_active);
      setSuccess(
        category.is_active
          ? 'Category deactivated successfully.'
          : 'Category activated successfully.',
      );
      await load();
    } catch (err) {
      setError(err.response?.data?.error?.message || 'Failed to update status');
    }
  };

  return (
    <>
      <PageActions>
        <Button variant="contained" startIcon={<AddOutlinedIcon />} onClick={openCreate}>
          Add Category
        </Button>
      </PageActions>

      <PageShell>
        {error ? <Alert severity="error">{error}</Alert> : null}
        {success ? <Alert severity="success">{success}</Alert> : null}

        {!loading && categories.length ? (
          <Section title="Category Hierarchy" description="Root categories and their subcategories.">
            <Card>
              <CardContent sx={{ p: { xs: 2, sm: 2.5 }, '&:last-child': { pb: { xs: 2, sm: 2.5 } } }}>
                <Stack spacing={0.75}>
                  {hierarchyRows.map(({ category, depth }) => (
                    <Typography
                      key={category.id}
                      variant="body2"
                      sx={{
                        pl: depth * 2.5,
                        color: category.is_active ? 'text.primary' : 'text.secondary',
                      }}
                    >
                      {depth > 0 ? '└── ' : ''}
                      <strong>{category.name}</strong>
                      {!category.is_active ? ' (Inactive)' : ''}
                    </Typography>
                  ))}
                </Stack>
              </CardContent>
            </Card>
          </Section>
        ) : null}

        <TableCard>
          {loading ? (
            <Box sx={{ py: 8, display: 'grid', placeItems: 'center' }}>
              <CircularProgress size={28} />
            </Box>
          ) : (
            <Table size="small" sx={{ minWidth: 840 }}>
              <TableHead>
                <TableRow>
                  <TableCell>Name</TableCell>
                  <TableCell>Description</TableCell>
                  <TableCell>Parent Category</TableCell>
                  <TableCell>Status</TableCell>
                  <TableCell>Created At</TableCell>
                  <TableCell align="right">Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {categories.map((category) => (
                  <TableRow key={category.id} hover>
                    <TableCell>
                      <TruncateText value={category.name} maxWidth={180} />
                    </TableCell>
                    <TableCell>
                      <TruncateText value={category.description || '—'} maxWidth={240} />
                    </TableCell>
                    <TableCell>
                      <TruncateText
                        value={category.parent_category_name || 'None'}
                        maxWidth={160}
                      />
                    </TableCell>
                    <TableCell>
                      <Stack direction="row" alignItems="center" spacing={1}>
                        <Switch
                          size="small"
                          checked={category.is_active}
                          onChange={() => toggleActive(category)}
                          inputProps={{ 'aria-label': `Toggle ${category.name}` }}
                        />
                        <Typography variant="caption" color="text.secondary">
                          {category.is_active ? 'Active' : 'Inactive'}
                        </Typography>
                      </Stack>
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2" color="text.secondary" sx={{ whiteSpace: 'nowrap' }}>
                        {category.created_at
                          ? new Date(category.created_at).toLocaleDateString()
                          : '—'}
                      </Typography>
                    </TableCell>
                    <TableCell align="right">
                      <Tooltip title="Edit">
                        <IconButton
                          size="small"
                          aria-label={`Edit ${category.name}`}
                          onClick={() => openEdit(category)}
                        >
                          <EditOutlinedIcon fontSize="small" />
                        </IconButton>
                      </Tooltip>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
          {!loading && !categories.length ? (
            <EmptyState
              title="No categories yet"
              description="Create root categories such as Food or Drinks, then add subcategories."
              actionLabel="Add Category"
              onAction={openCreate}
            />
          ) : null}
        </TableCard>
      </PageShell>

      <Dialog open={open} onClose={() => setOpen(false)} fullWidth maxWidth="sm">
        <DialogTitle>{editing ? 'Edit Category' : 'Add Category'}</DialogTitle>
        <DialogContent>
          <Stack spacing={2.5} sx={{ mt: 1 }}>
            {formError ? <Alert severity="error">{formError}</Alert> : null}
            <TextField
              label="Category Name"
              value={form.name}
              onChange={(e) => setForm((f) => ({ ...f, name: e.target.value }))}
              required
              fullWidth
              autoFocus
            />
            <TextField
              label="Description"
              value={form.description}
              onChange={(e) => setForm((f) => ({ ...f, description: e.target.value }))}
              fullWidth
              multiline
              minRows={2}
            />
            <Autocomplete
              options={parentOptions}
              value={selectedParent}
              onChange={(_, option) =>
                setForm((f) => ({ ...f, parent_id: option?.id || '' }))
              }
              getOptionLabel={(option) => option.name || ''}
              isOptionEqualToValue={(option, value) => option.id === value.id}
              renderOption={(props, option) => (
                <li {...props} key={option.id || 'root'}>
                  {option.isRoot
                    ? option.name
                    : option.parent_category_name
                      ? `${option.name} (under ${option.parent_category_name})`
                      : option.name}
                </li>
              )}
              renderInput={(params) => (
                <TextField
                  {...params}
                  label="Parent Category"
                  helperText="Choose a parent, or keep No Parent for a root category."
                />
              )}
            />
          </Stack>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpen(false)}>Cancel</Button>
          <Button variant="contained" onClick={onSave} disabled={saving}>
            {saving ? 'Saving...' : editing ? 'Save Category' : 'Save Category'}
          </Button>
        </DialogActions>
      </Dialog>
    </>
  );
}
