import AddOutlinedIcon from '@mui/icons-material/AddOutlined';
import DeleteOutlineOutlinedIcon from '@mui/icons-material/DeleteOutlineOutlined';
import EditOutlinedIcon from '@mui/icons-material/EditOutlined';
import {
  Alert,
  Button,
  Chip,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
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
import { useEffect, useMemo, useState } from 'react';
import CategoryHierarchyAutocomplete from '../../components/CategoryHierarchyAutocomplete';
import EmptyState from '../../components/EmptyState';
import LoadingBlock from '../../components/LoadingBlock';
import PageShell from '../../components/PageShell';
import TableCard from '../../components/TableCard';
import TruncateText from '../../components/TruncateText';
import ConfirmDialog from '../../components/ui/ConfirmDialog';
import IconActionButton from '../../components/ui/IconActionButton';
import StatusBadge from '../../components/ui/StatusBadge';
import { PageActions } from '../../context/PageActionsContext';
import {
  createCategory,
  listCategories,
  setCategoryStatus,
  updateCategory,
} from '../../services/categoryService';
import { getApiErrorMessage } from '../../utils/apiError';
import {
  buildHierarchyRows,
  collectDescendantIds,
  formatCategoryPath,
} from '../../utils/categoryHierarchy';

const emptyForm = { name: '', description: '', parent_id: '' };

const ROOT_OPTION = {
  id: '',
  name: 'No Parent / Main Category',
  isRoot: true,
};

const PARENT_HELPER =
  'Leave this as No Parent / Main Category to create a main category. Select a category to create a subcategory.';

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
  const [deleteTarget, setDeleteTarget] = useState(null);

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

  const excludedParentIds = useMemo(() => {
    if (!editing?.id) return [];
    return [editing.id, ...collectDescendantIds(categories, editing.id)];
  }, [categories, editing]);

  const selectedParentName = useMemo(() => {
    if (!form.parent_id) return null;
    return categories.find((c) => c.id === form.parent_id)?.name || null;
  }, [categories, form.parent_id]);

  const placementHint = form.parent_id
    ? `This will be saved as a subcategory under “${selectedParentName || 'selected parent'}”.`
    : 'This will be saved as a main category (no parent).';

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
      setError(getApiErrorMessage(err, 'Failed to update status'));
    }
  };

  const confirmDelete = async () => {
    if (!deleteTarget) return;
    setSaving(true);
    setError('');
    setSuccess('');
    try {
      await setCategoryStatus(deleteTarget.id, false);
      setSuccess(`Category “${deleteTarget.name}” deleted (deactivated).`);
      setDeleteTarget(null);
      await load();
    } catch (err) {
      setError(getApiErrorMessage(err, 'Failed to delete category'));
      setDeleteTarget(null);
    } finally {
      setSaving(false);
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

        <Alert severity="info" variant="outlined">
          <Typography variant="body2" sx={{ fontWeight: 650, mb: 0.5 }}>
            Main categories and subcategories
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Create a main category first (for example Food or Clothing). Then add
            subcategories under it (Food → Veg / Non-Veg). Use Parent Category in the form
            to choose the level.
          </Typography>
        </Alert>

        <TableCard>
          {loading ? (
            <LoadingBlock />
          ) : (
            <Table size="small" sx={{ minWidth: 960 }}>
              <TableHead>
                <TableRow>
                  <TableCell>Category Name</TableCell>
                  <TableCell>Type</TableCell>
                  <TableCell>Path</TableCell>
                  <TableCell>Description</TableCell>
                  <TableCell>Parent Category</TableCell>
                  <TableCell>Status</TableCell>
                  <TableCell>Created At</TableCell>
                  <TableCell align="right">Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {hierarchyRows.map(({ category, depth }) => {
                  const isMain = !category.parent_id;
                  return (
                    <TableRow key={category.id} hover>
                      <TableCell>
                        <Typography
                          variant="body2"
                          sx={{
                            pl: depth * 2,
                            fontWeight: isMain ? 650 : 500,
                            color: category.is_active ? 'text.primary' : 'text.secondary',
                          }}
                        >
                          {depth > 0 ? `${'· '.repeat(Math.min(depth, 3))}→ ` : ''}
                          {category.name}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Chip
                          size="small"
                          label={isMain ? 'Main' : 'Sub'}
                          variant={isMain ? 'filled' : 'outlined'}
                          color={isMain ? 'primary' : 'default'}
                          sx={{ fontWeight: 600 }}
                        />
                      </TableCell>
                      <TableCell>
                        <TruncateText
                          value={formatCategoryPath(category.hierarchy_path || category.name)}
                          maxWidth={220}
                        />
                      </TableCell>
                      <TableCell>
                        <TruncateText value={category.description || '—'} maxWidth={180} />
                      </TableCell>
                      <TableCell>
                        <TruncateText
                          value={
                            category.parent_category_name || 'No Parent / Main Category'
                          }
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
                          <StatusBadge label={category.is_active ? 'Active' : 'Unavailable'} />
                        </Stack>
                      </TableCell>
                      <TableCell>
                        <Typography
                          variant="body2"
                          color="text.secondary"
                          sx={{ whiteSpace: 'nowrap' }}
                        >
                          {category.created_at
                            ? new Date(category.created_at).toLocaleDateString()
                            : '—'}
                        </Typography>
                      </TableCell>
                      <TableCell align="right">
                        <Stack direction="row" spacing={0.25} justifyContent="flex-end">
                          <IconActionButton title="Edit Category" onClick={() => openEdit(category)}>
                            <EditOutlinedIcon fontSize="small" />
                          </IconActionButton>
                          {category.is_active ? (
                            <IconActionButton
                              title="Delete Category"
                              color="error"
                              onClick={() => setDeleteTarget(category)}
                            >
                              <DeleteOutlineOutlinedIcon fontSize="small" />
                            </IconActionButton>
                          ) : null}
                        </Stack>
                      </TableCell>
                    </TableRow>
                  );
                })}
              </TableBody>
            </Table>
          )}
          {!loading && !categories.length ? (
            <EmptyState
              title="No categories yet"
              description="Create a main category (for example Food), then add subcategories such as Veg and Non-Veg under it."
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
              helperText="Example: Food, Veg, Clothing, Men"
            />
            <TextField
              label="Description"
              value={form.description}
              onChange={(e) => setForm((f) => ({ ...f, description: e.target.value }))}
              fullWidth
              multiline
              minRows={2}
            />
            <CategoryHierarchyAutocomplete
              categories={categories}
              valueId={form.parent_id}
              onChange={(id) => setForm((f) => ({ ...f, parent_id: id }))}
              label="Parent Category"
              helperText={PARENT_HELPER}
              allowEmpty
              emptyOption={ROOT_OPTION}
              excludeIds={excludedParentIds}
              activeOnly
              includeInactiveIds={[form.parent_id]}
            />
            <Typography variant="body2" color="text.secondary">
              {placementHint}
            </Typography>
          </Stack>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpen(false)}>Cancel</Button>
          <Button variant="contained" onClick={onSave} disabled={saving}>
            {saving ? 'Saving...' : 'Save Category'}
          </Button>
        </DialogActions>
      </Dialog>

      <ConfirmDialog
        open={Boolean(deleteTarget)}
        title="Delete Category?"
        description={`Are you sure you want to delete “${deleteTarget?.name || ''}”? Categories with items cannot be deleted until items are moved or removed.`}
        confirmLabel="Delete"
        loading={saving}
        onClose={() => setDeleteTarget(null)}
        onConfirm={confirmDelete}
      />
    </>
  );
}
