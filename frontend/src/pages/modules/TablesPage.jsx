import AddOutlinedIcon from '@mui/icons-material/AddOutlined';
import DeleteOutlineOutlinedIcon from '@mui/icons-material/DeleteOutlineOutlined';
import EditOutlinedIcon from '@mui/icons-material/EditOutlined';
import MergeTypeOutlinedIcon from '@mui/icons-material/MergeTypeOutlined';
import {
  Alert,
  Box,
  Button,
  Card,
  CardActions,
  CardContent,
  Chip,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  FormControl,
  InputLabel,
  MenuItem,
  Select,
  Stack,
  TextField,
  Typography,
} from '@mui/material';
import { useCallback, useEffect, useMemo, useState } from 'react';
import EmptyState from '../../components/EmptyState';
import FilterBar from '../../components/FilterBar';
import LoadingBlock from '../../components/LoadingBlock';
import PageShell from '../../components/PageShell';
import ConfirmDialog from '../../components/ui/ConfirmDialog';
import IconActionButton from '../../components/ui/IconActionButton';
import StatusBadge from '../../components/ui/StatusBadge';
import { PageActions } from '../../context/PageActionsContext';
import { useModuleGate } from '../../context/ModulesContext';
import { usePermissions } from '../../hooks/usePermissions';
import { filterControlSx } from '../../layouts/shell';
import { getApiErrorMessage } from '../../utils/apiError';
import {
  createTable,
  deactivateTable,
  listTables,
  mergeTables,
  setTableStatus,
  unmergeTables,
  updateTable,
} from '../../services/tableService';

const STATUS_OPTIONS = [
  { value: '', label: 'All statuses' },
  { value: 'available', label: 'Available' },
  { value: 'occupied', label: 'Occupied' },
  { value: 'reserved', label: 'Reserved' },
  { value: 'bill_pending', label: 'Bill Pending' },
];

const NEXT_STATUS = {
  available: [
    { value: 'occupied', label: 'Seat / Occupy' },
    { value: 'reserved', label: 'Reserve' },
  ],
  occupied: [
    { value: 'bill_pending', label: 'Bill pending' },
    { value: 'available', label: 'Clear table' },
  ],
  reserved: [
    { value: 'occupied', label: 'Seat guests' },
    { value: 'available', label: 'Cancel reservation' },
  ],
  bill_pending: [
    { value: 'occupied', label: 'Back to occupied' },
    { value: 'available', label: 'Clear table' },
  ],
};

function statusColor(status) {
  if (status === 'occupied') return 'warning';
  if (status === 'reserved') return 'info';
  if (status === 'bill_pending') return 'error';
  return 'success';
}

function statusBadgeVariant(status) {
  if (status === 'occupied') return 'pending';
  if (status === 'reserved') return 'info';
  if (status === 'bill_pending') return 'cancelled';
  return 'active';
}

function statusLabel(status) {
  return STATUS_OPTIONS.find((row) => row.value === status)?.label || status;
}

const emptyForm = { code: '', section: '', capacity: '' };

export default function TablesPage() {
  const moduleEnabled = useModuleGate('table_management');
  const { canManageTables, canUpdateTableStatus } = usePermissions();
  const [tables, setTables] = useState([]);
  const [sectionFilter, setSectionFilter] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [open, setOpen] = useState(false);
  const [editing, setEditing] = useState(null);
  const [form, setForm] = useState(emptyForm);
  const [deleteTarget, setDeleteTarget] = useState(null);
  const [saving, setSaving] = useState(false);
  const [mergeOpen, setMergeOpen] = useState(false);
  const [mergePrimaryId, setMergePrimaryId] = useState('');
  const [mergeSecondaryIds, setMergeSecondaryIds] = useState([]);

  const load = useCallback(async () => {
    if (!moduleEnabled) return;
    setError('');
    setLoading(true);
    try {
      const params = {};
      if (sectionFilter) params.section = sectionFilter;
      if (statusFilter) params.status = statusFilter;
      const response = await listTables(params);
      setTables(response.data || []);
    } catch (err) {
      setError(getApiErrorMessage(err, 'Unable to load tables.'));
    } finally {
      setLoading(false);
    }
  }, [moduleEnabled, sectionFilter, statusFilter]);

  useEffect(() => {
    load();
  }, [load]);

  useEffect(() => {
    if (!moduleEnabled) return undefined;
    const timer = window.setInterval(load, 30000);
    return () => window.clearInterval(timer);
  }, [load, moduleEnabled]);

  const sections = useMemo(() => {
    const values = new Set();
    tables.forEach((table) => {
      if (table.section) values.add(table.section);
    });
    return Array.from(values).sort((a, b) => a.localeCompare(b));
  }, [tables]);

  const availableForMerge = useMemo(
    () => tables.filter((table) => table.status === 'available' && !table.merged_into_id),
    [tables],
  );

  const openCreate = () => {
    setEditing(null);
    setForm(emptyForm);
    setOpen(true);
  };

  const openEdit = (table) => {
    setEditing(table);
    setForm({
      code: table.code || '',
      section: table.section || '',
      capacity: table.capacity ?? '',
    });
    setOpen(true);
  };

  const onSave = async () => {
    if (!form.code.trim()) {
      setError('Table code is required.');
      return;
    }
    setSaving(true);
    setError('');
    setSuccess('');
    try {
      const payload = {
        code: form.code.trim(),
        section: form.section.trim() || null,
        capacity: form.capacity === '' ? null : Number(form.capacity),
      };
      if (editing) {
        await updateTable(editing.id, payload);
        setSuccess(`Table ${payload.code} updated.`);
      } else {
        await createTable(payload);
        setSuccess('Table added.');
      }
      setOpen(false);
      setEditing(null);
      setForm(emptyForm);
      await load();
    } catch (err) {
      setError(getApiErrorMessage(err, 'Unable to save table.'));
    } finally {
      setSaving(false);
    }
  };

  const onRemove = async () => {
    if (!deleteTarget) return;
    setSaving(true);
    setError('');
    setSuccess('');
    try {
      await deactivateTable(deleteTarget.id);
      setSuccess(`Table ${deleteTarget.code} removed.`);
      setDeleteTarget(null);
      await load();
    } catch (err) {
      setError(getApiErrorMessage(err, 'Unable to remove table.'));
    } finally {
      setSaving(false);
    }
  };

  const onStatusChange = async (tableId, status) => {
    setError('');
    setSuccess('');
    try {
      await setTableStatus(tableId, status);
      setSuccess('Table status updated.');
      await load();
    } catch (err) {
      setError(getApiErrorMessage(err, 'Invalid status change.'));
    }
  };

  const onUnmerge = async (tableId) => {
    setError('');
    setSuccess('');
    try {
      await unmergeTables({ primary_table_id: tableId });
      setSuccess('Tables unmerged.');
      await load();
    } catch (err) {
      setError(getApiErrorMessage(err, 'Unable to unmerge tables.'));
    }
  };

  const onMerge = async () => {
    if (!mergePrimaryId || mergeSecondaryIds.length === 0) {
      setError('Select a primary table and at least one secondary table.');
      return;
    }
    setSaving(true);
    setError('');
    setSuccess('');
    try {
      await mergeTables({
        primary_table_id: mergePrimaryId,
        secondary_table_ids: mergeSecondaryIds,
      });
      setMergeOpen(false);
      setMergePrimaryId('');
      setMergeSecondaryIds([]);
      setSuccess('Tables merged.');
      await load();
    } catch (err) {
      setError(getApiErrorMessage(err, 'Unable to merge tables.'));
    } finally {
      setSaving(false);
    }
  };

  if (!moduleEnabled) {
    return (
      <PageShell>
        <Alert severity="warning">Table management is not enabled for this business type.</Alert>
      </PageShell>
    );
  }

  return (
    <>
      {canManageTables ? (
        <PageActions>
          <Button variant="contained" startIcon={<AddOutlinedIcon />} onClick={openCreate}>
            Add table
          </Button>
          {canUpdateTableStatus ? (
            <Button variant="outlined" startIcon={<MergeTypeOutlinedIcon />} onClick={() => setMergeOpen(true)}>
              Merge tables
            </Button>
          ) : null}
        </PageActions>
      ) : null}

      <PageShell>
        <Stack spacing={2}>
          <FilterBar>
            <FormControl sx={filterControlSx}>
              <InputLabel>Section</InputLabel>
              <Select
                label="Section"
                value={sectionFilter}
                onChange={(e) => setSectionFilter(e.target.value)}
              >
                <MenuItem value="">All sections</MenuItem>
                {sections.map((section) => (
                  <MenuItem key={section} value={section}>
                    {section}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
            <FormControl sx={filterControlSx}>
              <InputLabel>Status</InputLabel>
              <Select
                label="Status"
                value={statusFilter}
                onChange={(e) => setStatusFilter(e.target.value)}
              >
                {STATUS_OPTIONS.map((option) => (
                  <MenuItem key={option.value || 'all'} value={option.value}>
                    {option.label}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </FilterBar>

          {error ? <Alert severity="error">{error}</Alert> : null}
          {success ? <Alert severity="success">{success}</Alert> : null}

          {loading ? (
            <LoadingBlock />
          ) : tables.length === 0 ? (
            <EmptyState
              title="No tables configured"
              description="Add dining tables with codes, optional sections, and capacity."
              actionLabel={canManageTables ? 'Add table' : undefined}
              onAction={canManageTables ? openCreate : undefined}
            />
          ) : (
            <Box
              sx={{
                display: 'grid',
                gap: 2,
                gridTemplateColumns: {
                  xs: 'repeat(2, minmax(0, 1fr))',
                  sm: 'repeat(3, minmax(0, 1fr))',
                  md: 'repeat(4, minmax(0, 1fr))',
                  lg: 'repeat(5, minmax(0, 1fr))',
                },
              }}
            >
              {tables.map((table) => (
                <Card
                  key={table.id}
                  variant="outlined"
                  sx={{
                    minHeight: 148,
                    borderColor: (theme) =>
                      theme.palette[statusColor(table.status)]?.main || theme.palette.divider,
                    borderWidth: 2,
                  }}
                >
                  <CardContent sx={{ pb: 1 }}>
                    <Stack direction="row" justifyContent="space-between" alignItems="flex-start">
                      <Typography variant="h6" component="div">
                        {table.code}
                      </Typography>
                      <Stack direction="row" spacing={0.25} alignItems="center">
                        {canManageTables ? (
                          <>
                            <IconActionButton
                              title="Edit Table"
                              onClick={() => openEdit(table)}
                              disabled={Boolean(table.merged_into_id)}
                            >
                              <EditOutlinedIcon fontSize="small" />
                            </IconActionButton>
                            <IconActionButton
                              title="Remove Table"
                              color="error"
                              onClick={() => setDeleteTarget(table)}
                            >
                              <DeleteOutlineOutlinedIcon fontSize="small" />
                            </IconActionButton>
                          </>
                        ) : null}
                        <StatusBadge
                          label={statusLabel(table.status)}
                          variant={statusBadgeVariant(table.status)}
                        />
                      </Stack>
                    </Stack>
                    <Typography variant="body2" color="text.secondary" sx={{ mt: 0.5 }}>
                      {table.section || 'No section'}
                      {table.capacity ? ` · ${table.capacity} seats` : ''}
                    </Typography>
                    {table.merged_tables?.length ? (
                      <Stack direction="row" spacing={0.5} flexWrap="wrap" useFlexGap sx={{ mt: 1 }}>
                        {table.merged_tables.map((child) => (
                          <Chip key={child.id} size="small" variant="outlined" label={child.code} />
                        ))}
                      </Stack>
                    ) : null}
                  </CardContent>
                  {canUpdateTableStatus ? (
                    <CardActions sx={{ flexWrap: 'wrap', gap: 0.5, px: 2, pb: 2, pt: 0 }}>
                      {(NEXT_STATUS[table.status] || []).map((action) => (
                        <Button
                          key={action.value}
                          size="small"
                          variant="outlined"
                          onClick={() => onStatusChange(table.id, action.value)}
                        >
                          {action.label}
                        </Button>
                      ))}
                      {table.merged_tables?.length ? (
                        <Button size="small" color="secondary" onClick={() => onUnmerge(table.id)}>
                          Unmerge
                        </Button>
                      ) : null}
                    </CardActions>
                  ) : null}
                </Card>
              ))}
            </Box>
          )}
        </Stack>
      </PageShell>

      <Dialog
        open={open}
        onClose={() => {
          setOpen(false);
          setEditing(null);
        }}
        fullWidth
        maxWidth="xs"
      >
        <DialogTitle>{editing ? 'Edit Table' : 'Add table'}</DialogTitle>
        <DialogContent>
          <Stack spacing={2} sx={{ mt: 1 }}>
            <TextField
              label="Table Number"
              value={form.code}
              onChange={(e) => setForm((f) => ({ ...f, code: e.target.value }))}
              required
              fullWidth
              placeholder="T1"
            />
            <TextField
              label="Section / floor (optional)"
              value={form.section}
              onChange={(e) => setForm((f) => ({ ...f, section: e.target.value }))}
              fullWidth
              placeholder="Ground floor"
            />
            <TextField
              label="Capacity"
              type="number"
              value={form.capacity}
              onChange={(e) => setForm((f) => ({ ...f, capacity: e.target.value }))}
              fullWidth
              inputProps={{ min: 1, max: 999 }}
            />
            {editing ? (
              <Typography variant="body2" color="text.secondary">
                Status: {statusLabel(editing.status)} (change status from the table card)
              </Typography>
            ) : null}
          </Stack>
        </DialogContent>
        <DialogActions>
          <Button
            onClick={() => {
              setOpen(false);
              setEditing(null);
            }}
          >
            Cancel
          </Button>
          <Button variant="contained" onClick={onSave} disabled={saving}>
            {saving ? 'Saving…' : editing ? 'Save Changes' : 'Save'}
          </Button>
        </DialogActions>
      </Dialog>

      <ConfirmDialog
        open={Boolean(deleteTarget)}
        title="Delete/Remove Table?"
        description={`Remove table ${deleteTarget?.code || ''}? Historical bills keep this table number. Active orders will block removal.`}
        confirmLabel="Remove"
        loading={saving}
        onClose={() => setDeleteTarget(null)}
        onConfirm={onRemove}
      />

      <Dialog open={mergeOpen} onClose={() => setMergeOpen(false)} fullWidth maxWidth="sm">
        <DialogTitle>Merge tables</DialogTitle>
        <DialogContent>
          <Stack spacing={2} sx={{ mt: 1 }}>
            <FormControl fullWidth>
              <InputLabel id="merge-primary-label">Primary table</InputLabel>
              <Select
                labelId="merge-primary-label"
                label="Primary table"
                value={mergePrimaryId}
                onChange={(e) => {
                  setMergePrimaryId(e.target.value);
                  setMergeSecondaryIds((ids) => ids.filter((id) => id !== e.target.value));
                }}
              >
                {tables.map((table) => (
                  <MenuItem key={table.id} value={table.id}>
                    {table.code}
                    {table.section ? ` (${table.section})` : ''}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
            <FormControl fullWidth>
              <InputLabel id="merge-secondary-label">Secondary tables (available)</InputLabel>
              <Select
                labelId="merge-secondary-label"
                label="Secondary tables (available)"
                multiple
                value={mergeSecondaryIds}
                onChange={(e) => setMergeSecondaryIds(e.target.value)}
                renderValue={(selected) =>
                  availableForMerge
                    .filter((table) => selected.includes(table.id))
                    .map((table) => table.code)
                    .join(', ')
                }
              >
                {availableForMerge
                  .filter((table) => table.id !== mergePrimaryId)
                  .map((table) => (
                    <MenuItem key={table.id} value={table.id}>
                      {table.code}
                      {table.section ? ` (${table.section})` : ''}
                    </MenuItem>
                  ))}
              </Select>
            </FormControl>
          </Stack>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setMergeOpen(false)}>Cancel</Button>
          <Button variant="contained" onClick={onMerge} disabled={saving}>
            Merge
          </Button>
        </DialogActions>
      </Dialog>
    </>
  );
}
