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
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
  TextField,
  Typography,
} from '@mui/material';
import { useCallback, useEffect, useMemo, useState } from 'react';
import EmptyState from '../../components/EmptyState';
import LoadingBlock from '../../components/LoadingBlock';
import PageShell from '../../components/PageShell';
import TableCard from '../../components/TableCard';
import TruncateText from '../../components/TruncateText';
import ConfirmDialog from '../../components/ui/ConfirmDialog';
import IconActionButton from '../../components/ui/IconActionButton';
import StatusBadge from '../../components/ui/StatusBadge';
import { PageActions } from '../../context/PageActionsContext';
import { useAuth } from '../../context/AuthContext';
import { usePermissions } from '../../hooks/usePermissions';
import {
  createCategory,
  listCategories,
  setCategoryStatus,
  updateCategory,
} from '../../services/categoryService';
import { getApiErrorMessage } from '../../utils/apiError';
import { buildHierarchyRows } from '../../utils/categoryHierarchy';

/**
 * Billing categories — hotel billing users with categories.write can add/edit/soft-delete.
 */
export default function BillingCategoriesPage() {
  const { user } = useAuth();
  const { canWriteCategories } = usePermissions();
  const isHotel = user?.tenant?.business_type === 'hotel_restaurant';
  const canManage = canWriteCategories && isHotel;

  const [categories, setCategories] = useState([]);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [loading, setLoading] = useState(true);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [editing, setEditing] = useState(null);
  const [deleteTarget, setDeleteTarget] = useState(null);
  const [saving, setSaving] = useState(false);
  const [form, setForm] = useState({ name: '', description: '' });

  const load = useCallback(async () => {
    setError('');
    try {
      const res = await listCategories();
      setCategories(res.data || []);
    } catch (err) {
      setError(getApiErrorMessage(err, 'Failed to load categories'));
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  const hierarchyRows = useMemo(() => buildHierarchyRows(categories), [categories]);

  const openCreate = () => {
    setEditing(null);
    setForm({ name: '', description: '' });
    setError('');
    setDialogOpen(true);
  };

  const openEdit = (category) => {
    setEditing(category);
    setForm({
      name: category.name || '',
      description: category.description || '',
    });
    setError('');
    setDialogOpen(true);
  };

  const saveCategory = async () => {
    if (!form.name.trim()) {
      setError('Category name is required.');
      return;
    }
    setSaving(true);
    setError('');
    try {
      if (editing) {
        await updateCategory(editing.id, {
          name: form.name.trim(),
          description: form.description.trim() || null,
        });
        setSuccess(`Category “${form.name.trim()}” updated`);
      } else {
        const created = await createCategory({
          name: form.name.trim(),
          description: form.description.trim() || null,
        });
        setSuccess(`Category “${created.data?.name || form.name}” added`);
      }
      setDialogOpen(false);
      setForm({ name: '', description: '' });
      setEditing(null);
      await load();
    } catch (err) {
      setError(getApiErrorMessage(err, 'Could not save category'));
    } finally {
      setSaving(false);
    }
  };

  const confirmDelete = async () => {
    if (!deleteTarget) return;
    setSaving(true);
    setError('');
    try {
      await setCategoryStatus(deleteTarget.id, false);
      setSuccess(`Category “${deleteTarget.name}” removed from active list`);
      setDeleteTarget(null);
      await load();
    } catch (err) {
      setError(getApiErrorMessage(err, 'Could not delete category'));
      setDeleteTarget(null);
    } finally {
      setSaving(false);
    }
  };

  return (
    <PageShell>
      {canManage ? (
        <PageActions>
          <Button
            size="small"
            variant="contained"
            startIcon={<AddOutlinedIcon />}
            onClick={openCreate}
          >
            Add Category
          </Button>
        </PageActions>
      ) : null}

      {error ? (
        <Alert severity="error" onClose={() => setError('')}>
          {error}
        </Alert>
      ) : null}
      {success ? (
        <Alert severity="success" onClose={() => setSuccess('')}>
          {success}
        </Alert>
      ) : null}

      <TableCard>
        {loading ? (
          <LoadingBlock />
        ) : (
          <Table size="small" sx={{ minWidth: 560 }}>
            <TableHead>
              <TableRow>
                <TableCell>Category Name</TableCell>
                <TableCell>Type</TableCell>
                <TableCell>Description</TableCell>
                <TableCell>Status</TableCell>
                {canManage ? <TableCell align="right">Actions</TableCell> : null}
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
                      <TruncateText value={category.description || '—'} maxWidth={220} />
                    </TableCell>
                    <TableCell>
                      <StatusBadge label={category.is_active ? 'Active' : 'Unavailable'} />
                    </TableCell>
                    {canManage ? (
                      <TableCell align="right">
                        <Stack direction="row" spacing={0.25} justifyContent="flex-end">
                          <IconActionButton
                            title="Edit Category"
                            onClick={() => openEdit(category)}
                          >
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
                    ) : null}
                  </TableRow>
                );
              })}
            </TableBody>
          </Table>
        )}
        {!loading && !categories.length ? (
          <EmptyState
            title="No categories found"
            description={
              canManage
                ? 'Click Add Category to create your first menu group.'
                : 'Ask the business owner to add categories for this workspace.'
            }
          />
        ) : null}
      </TableCard>

      <Dialog
        open={dialogOpen}
        onClose={() => !saving && setDialogOpen(false)}
        fullWidth
        maxWidth="xs"
      >
        <DialogTitle>{editing ? 'Edit Category' : 'Add Category'}</DialogTitle>
        <DialogContent>
          <Stack spacing={1.5} sx={{ pt: 1 }}>
            <TextField
              autoFocus
              label="Category Name"
              value={form.name}
              onChange={(e) => setForm((prev) => ({ ...prev, name: e.target.value }))}
              required
              fullWidth
              placeholder="Chinese Food"
            />
            <TextField
              label="Description (optional)"
              value={form.description}
              onChange={(e) => setForm((prev) => ({ ...prev, description: e.target.value }))}
              fullWidth
              multiline
              minRows={2}
            />
          </Stack>
        </DialogContent>
        <DialogActions>
          <Button disabled={saving} onClick={() => setDialogOpen(false)}>
            Cancel
          </Button>
          <Button variant="contained" disabled={saving} onClick={saveCategory}>
            {editing ? 'Save Changes' : 'Save Category'}
          </Button>
        </DialogActions>
      </Dialog>

      <ConfirmDialog
        open={Boolean(deleteTarget)}
        title="Delete Category?"
        description={`Are you sure you want to delete “${deleteTarget?.name || ''}”? It will be removed from new billing. Historical data stays unchanged.`}
        confirmLabel="Delete"
        loading={saving}
        onClose={() => setDeleteTarget(null)}
        onConfirm={confirmDelete}
      />
    </PageShell>
  );
}
