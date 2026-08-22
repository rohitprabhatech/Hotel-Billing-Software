import AddOutlinedIcon from '@mui/icons-material/AddOutlined';
import EditOutlinedIcon from '@mui/icons-material/EditOutlined';
import {
  Alert,
  Button,
  Chip,
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
import { useEffect, useState } from 'react';
import EmptyState from '../../components/EmptyState';
import FilterBar from '../../components/FilterBar';
import LoadingBlock from '../../components/LoadingBlock';
import PageShell from '../../components/PageShell';
import PaginationBar from '../../components/PaginationBar';
import TableCard from '../../components/TableCard';
import TruncateText from '../../components/TruncateText';
import { PageActions } from '../../context/PageActionsContext';
import { usePermissions } from '../../hooks/usePermissions';
import { filterControlWideSx } from '../../layouts/shell';
import {
  createSupplier,
  deactivateSupplier,
  listSuppliers,
  setSupplierStatus,
  updateSupplier,
} from '../../services/supplierService';

const emptyForm = {
  name: '',
  phone_country_code: '91',
  phone: '',
  gstin: '',
  email: '',
  address: '',
  notes: '',
};

const PAGE_SIZE = 25;

export default function SuppliersPage() {
  const { canManageSuppliers } = usePermissions();
  const [suppliers, setSuppliers] = useState([]);
  const [meta, setMeta] = useState({ page: 1, per_page: PAGE_SIZE, total: 0 });
  const [q, setQ] = useState('');
  const [page, setPage] = useState(1);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [open, setOpen] = useState(false);
  const [editing, setEditing] = useState(null);
  const [form, setForm] = useState(emptyForm);
  const [saving, setSaving] = useState(false);
  const [loading, setLoading] = useState(true);

  const load = async (nextPage = page, search = q) => {
    setError('');
    setLoading(true);
    try {
      const res = await listSuppliers({
        q: search || undefined,
        page: nextPage,
        per_page: PAGE_SIZE,
      });
      setSuppliers(res.data || []);
      setMeta(res.meta || { page: nextPage, per_page: PAGE_SIZE, total: 0 });
      setPage(res.meta?.page || nextPage);
    } catch (err) {
      setError(err.response?.data?.error?.message || 'Unable to load suppliers.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load(1);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const openCreate = () => {
    setEditing(null);
    setForm(emptyForm);
    setOpen(true);
  };

  const openEdit = (supplier) => {
    setEditing(supplier);
    setForm({
      name: supplier.name || '',
      phone_country_code: supplier.phone_country_code || '91',
      phone: supplier.phone_national || '',
      gstin: supplier.gstin || '',
      email: supplier.email || '',
      address: supplier.address || '',
      notes: supplier.notes || '',
    });
    setOpen(true);
  };

  const onSave = async () => {
    if (!form.name.trim()) {
      setError('Supplier name is required.');
      return;
    }
    setSaving(true);
    setError('');
    setSuccess('');
    const payload = {
      name: form.name.trim(),
      phone_country_code: form.phone ? form.phone_country_code : null,
      phone: form.phone || null,
      gstin: form.gstin.trim() || null,
      email: form.email.trim() || null,
      address: form.address.trim() || null,
      notes: form.notes.trim() || null,
    };
    try {
      if (editing) {
        await updateSupplier(editing.id, payload);
        setSuccess('Supplier updated successfully.');
      } else {
        await createSupplier(payload);
        setSuccess('Supplier created successfully.');
      }
      setOpen(false);
      await load(editing ? page : 1, q);
    } catch (err) {
      setError(err.response?.data?.error?.message || 'Failed to save supplier');
    } finally {
      setSaving(false);
    }
  };

  const toggleActive = async (supplier) => {
    if (!canManageSuppliers) return;
    setError('');
    try {
      if (supplier.is_active) {
        await deactivateSupplier(supplier.id);
      } else {
        await setSupplierStatus(supplier.id, true);
      }
      await load(page, q);
    } catch (err) {
      setError(err.response?.data?.error?.message || 'Failed to update supplier status');
    }
  };

  return (
    <>
      {canManageSuppliers ? (
        <PageActions>
          <Button variant="contained" startIcon={<AddOutlinedIcon />} onClick={openCreate}>
            Add Supplier
          </Button>
        </PageActions>
      ) : null}

      <PageShell>
        <FilterBar
          actions={
            <Button variant="outlined" onClick={() => load(1, q)}>
              Search
            </Button>
          }
        >
          <TextField
            label="Search name, phone, GSTIN, or email"
            value={q}
            onChange={(e) => setQ(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Enter') load(1, q);
            }}
            sx={{ ...filterControlWideSx, flex: 1 }}
          />
        </FilterBar>

        {error ? <Alert severity="error">{error}</Alert> : null}
        {success ? <Alert severity="success">{success}</Alert> : null}

        <TableCard>
          {loading ? (
            <LoadingBlock />
          ) : (
            <Table size="small" sx={{ minWidth: 980 }}>
              <TableHead>
                <TableRow>
                  <TableCell>Name</TableCell>
                  <TableCell>Phone</TableCell>
                  <TableCell>GSTIN</TableCell>
                  <TableCell>Email</TableCell>
                  <TableCell>Status</TableCell>
                  <TableCell align="right">Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {suppliers.map((supplier) => (
                  <TableRow key={supplier.id} hover>
                    <TableCell>
                      <TruncateText value={supplier.name} maxWidth={180} />
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2" color="text.secondary">
                        {supplier.phone_masked || '—'}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2" color="text.secondary">
                        {supplier.gstin || '—'}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <TruncateText value={supplier.email_masked || '—'} maxWidth={200} />
                    </TableCell>
                    <TableCell>
                      <Stack direction="row" alignItems="center" spacing={1}>
                        <Switch
                          size="small"
                          checked={supplier.is_active}
                          onChange={() => toggleActive(supplier)}
                          disabled={!canManageSuppliers}
                          inputProps={{ 'aria-label': `Toggle ${supplier.name}` }}
                        />
                        <Chip
                          size="small"
                          label={supplier.is_active ? 'Active' : 'Inactive'}
                          variant="outlined"
                        />
                      </Stack>
                    </TableCell>
                    <TableCell align="right">
                      {canManageSuppliers ? (
                        <Tooltip title="Edit">
                          <IconButton
                            size="small"
                            aria-label={`Edit ${supplier.name}`}
                            onClick={() => openEdit(supplier)}
                          >
                            <EditOutlinedIcon fontSize="small" />
                          </IconButton>
                        </Tooltip>
                      ) : (
                        <Typography variant="caption" color="text.secondary">
                          —
                        </Typography>
                      )}
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
          {!loading && !suppliers.length ? (
            <EmptyState
              title="No suppliers found"
              description="Add suppliers to prepare for purchase and stock receive flows."
              actionLabel={canManageSuppliers ? 'Add Supplier' : undefined}
              onAction={canManageSuppliers ? openCreate : undefined}
            />
          ) : null}
        </TableCard>

        {!loading && suppliers.length ? (
          <PaginationBar
            page={page}
            total={meta.total}
            pageSize={PAGE_SIZE}
            onPageChange={(next) => load(next, q)}
          />
        ) : null}
      </PageShell>

      <Dialog open={open} onClose={() => setOpen(false)} fullWidth maxWidth="sm">
        <DialogTitle>{editing ? 'Edit Supplier' : 'Add Supplier'}</DialogTitle>
        <DialogContent>
          <Stack spacing={2.5} sx={{ mt: 1 }}>
            <TextField
              label="Name"
              value={form.name}
              onChange={(e) => setForm((f) => ({ ...f, name: e.target.value }))}
              fullWidth
              required
            />
            <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2}>
              <TextField
                label="Country code"
                value={form.phone_country_code}
                onChange={(e) =>
                  setForm((f) => ({
                    ...f,
                    phone_country_code: e.target.value.replace(/\D/g, '').slice(0, 3),
                  }))
                }
                sx={{ width: { xs: '100%', sm: 120 } }}
              />
              <TextField
                label="Mobile"
                value={form.phone}
                onChange={(e) =>
                  setForm((f) => ({ ...f, phone: e.target.value.replace(/\D/g, '').slice(0, 14) }))
                }
                fullWidth
              />
            </Stack>
            <TextField
              label="GSTIN (optional)"
              value={form.gstin}
              onChange={(e) =>
                setForm((f) => ({ ...f, gstin: e.target.value.toUpperCase().slice(0, 15) }))
              }
              fullWidth
            />
            <TextField
              label="Email"
              type="email"
              value={form.email}
              onChange={(e) => setForm((f) => ({ ...f, email: e.target.value }))}
              fullWidth
            />
            <TextField
              label="Address"
              value={form.address}
              onChange={(e) => setForm((f) => ({ ...f, address: e.target.value }))}
              fullWidth
              multiline
              minRows={2}
            />
            <TextField
              label="Notes"
              value={form.notes}
              onChange={(e) => setForm((f) => ({ ...f, notes: e.target.value }))}
              fullWidth
              multiline
              minRows={2}
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
    </>
  );
}
