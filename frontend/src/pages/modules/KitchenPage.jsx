import AddIcon from '@mui/icons-material/Add';
import DeleteOutlineOutlinedIcon from '@mui/icons-material/DeleteOutlineOutlined';
import EditOutlinedIcon from '@mui/icons-material/EditOutlined';
import PrintOutlinedIcon from '@mui/icons-material/PrintOutlined';
import RefreshOutlinedIcon from '@mui/icons-material/RefreshOutlined';
import RemoveIcon from '@mui/icons-material/Remove';
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
  Grid,
  IconButton,
  InputLabel,
  MenuItem,
  Select,
  Stack,
  TextField,
  Tooltip,
  Typography,
} from '@mui/material';
import { useCallback, useEffect, useMemo, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import EmptyState from '../../components/EmptyState';
import LoadingBlock from '../../components/LoadingBlock';
import PageShell from '../../components/PageShell';
import { PageActions } from '../../context/PageActionsContext';
import { useAuth } from '../../context/AuthContext';
import { useModuleGate } from '../../context/ModulesContext';
import { usePermissions } from '../../hooks/usePermissions';
import { PATHS } from '../../routes/paths';
import { deleteKot, getKitchenQueue, updateKot, updateKotStatus } from '../../services/kotService';

const CHANNEL_LABELS = {
  dine_in: 'Dine-in',
  takeaway: 'Takeaway',
  delivery: 'Delivery',
};

const COLUMNS = [
  { key: 'queued', label: 'Queued', color: '#ffb74d' },
  { key: 'preparing', label: 'Preparing', color: '#64b5f6' },
  { key: 'ready', label: 'Ready', color: '#81c784' },
];

const NEXT_ACTIONS = {
  queued: [{ status: 'preparing', label: 'Start preparing' }],
  preparing: [{ status: 'ready', label: 'Mark ready' }],
  ready: [],
};

const STATUS_OPTIONS = [
  { value: 'queued', label: 'New / Queued' },
  { value: 'preparing', label: 'Preparing' },
  { value: 'ready', label: 'Ready' },
];

function kitchenPathForUser(user) {
  if (user?.role === 'OWNER' || user?.role === 'MANAGER') {
    return PATHS.ownerKitchen;
  }
  return PATHS.billingKitchen;
}

function KotCard({
  kot,
  onStatusChange,
  updating,
  canUpdateStatus,
  canManageKots,
  onEdit,
  onDelete,
  onPrint,
}) {
  const actions = NEXT_ACTIONS[kot.status] || [];
  const canEditDelete = canManageKots && (kot.status === 'queued' || kot.status === 'preparing');

  return (
    <Card
      sx={{
        bgcolor: '#1e1e1e',
        color: '#f5f5f5',
        border: '1px solid rgba(255,255,255,0.08)',
      }}
    >
      <CardContent sx={{ pb: 1 }}>
        <Stack spacing={1}>
          <Stack direction="row" justifyContent="space-between" alignItems="flex-start" gap={1}>
            <Typography variant="h6" sx={{ fontWeight: 700 }}>
              {kot.kot_number}
            </Typography>
            <Stack direction="row" spacing={0.25} alignItems="center">
              <Chip size="small" label={kot.status} sx={{ textTransform: 'capitalize' }} />
              <Tooltip title="Print KOT">
                <IconButton size="small" onClick={() => onPrint(kot)} sx={{ color: 'rgba(255,255,255,0.85)' }}>
                  <PrintOutlinedIcon fontSize="small" />
                </IconButton>
              </Tooltip>
              {canEditDelete ? (
                <>
                  <Tooltip title="Edit KOT">
                    <IconButton
                      size="small"
                      onClick={() => onEdit(kot)}
                      sx={{ color: 'rgba(255,255,255,0.85)' }}
                    >
                      <EditOutlinedIcon fontSize="small" />
                    </IconButton>
                  </Tooltip>
                  <Tooltip title="Delete KOT">
                    <IconButton
                      size="small"
                      color="error"
                      onClick={() => onDelete(kot)}
                      sx={{ color: 'error.light' }}
                    >
                      <DeleteOutlineOutlinedIcon fontSize="small" />
                    </IconButton>
                  </Tooltip>
                </>
              ) : null}
            </Stack>
          </Stack>
          <Typography variant="body2" color="rgba(255,255,255,0.72)">
            {kot.order_number} · {CHANNEL_LABELS[kot.channel] || kot.channel}
            {kot.dining_table_code ? ` · Table ${kot.dining_table_code}` : ''}
          </Typography>
          <Stack spacing={0.5} sx={{ mt: 1 }}>
            {(kot.items || []).map((line) => (
              <Stack key={line.id} direction="row" justifyContent="space-between">
                <Typography variant="body1">{line.item_name}</Typography>
                <Typography variant="body1" sx={{ fontWeight: 600 }}>
                  × {line.quantity}
                </Typography>
              </Stack>
            ))}
          </Stack>
          {kot.notes ? (
            <Typography variant="body2" color="warning.light">
              Note: {kot.notes}
            </Typography>
          ) : null}
        </Stack>
      </CardContent>
      {canUpdateStatus && actions.length ? (
        <CardActions sx={{ px: 2, pb: 2, flexDirection: 'column', gap: 1 }}>
          {actions.map((action) => (
            <Button
              key={action.status}
              fullWidth
              variant="contained"
              size="large"
              disabled={updating === kot.id}
              onClick={() => onStatusChange(kot.id, action.status)}
              sx={{ minHeight: 48, fontSize: '1rem' }}
            >
              {action.label}
            </Button>
          ))}
        </CardActions>
      ) : null}
    </Card>
  );
}

export default function KitchenPage() {
  const navigate = useNavigate();
  const { user } = useAuth();
  const moduleEnabled = useModuleGate('kitchen');
  const { canUpdateKotStatus, canManageKots } = usePermissions();
  const [kots, setKots] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [updating, setUpdating] = useState('');
  const [editKot, setEditKot] = useState(null);
  const [editNotes, setEditNotes] = useState('');
  const [editStatus, setEditStatus] = useState('queued');
  const [editItems, setEditItems] = useState([]);
  const [editSaving, setEditSaving] = useState(false);
  const [deleteTarget, setDeleteTarget] = useState(null);
  const [deleteSaving, setDeleteSaving] = useState(false);

  const load = useCallback(async ({ silent = false } = {}) => {
    if (!moduleEnabled) return;
    if (!silent) setError('');
    try {
      const response = await getKitchenQueue();
      setKots(response.data || []);
      if (!silent) setError('');
    } catch (err) {
      if (!silent) {
        setError(err.response?.data?.error?.message || 'Unable to load kitchen queue.');
      }
    } finally {
      setLoading(false);
    }
  }, [moduleEnabled]);

  useEffect(() => {
    load();
  }, [load]);

  useEffect(() => {
    if (!moduleEnabled) return undefined;
    const timer = window.setInterval(() => load({ silent: true }), 20000);
    return () => window.clearInterval(timer);
  }, [load, moduleEnabled]);

  const grouped = useMemo(() => {
    const map = { queued: [], preparing: [], ready: [] };
    kots.forEach((kot) => {
      if (map[kot.status]) map[kot.status].push(kot);
    });
    return map;
  }, [kots]);

  const onStatusChange = async (kotId, status) => {
    setUpdating(kotId);
    setError('');
    try {
      const res = await updateKotStatus(kotId, status);
      const updated = res.data;
      setKots((rows) => rows.map((row) => (row.id === kotId ? { ...row, ...updated } : row)));
    } catch (err) {
      setError(err.response?.data?.error?.message || 'Failed to update KOT status.');
    } finally {
      setUpdating('');
    }
  };

  const openEdit = (kot) => {
    setEditKot(kot);
    setEditNotes(kot.notes || '');
    setEditStatus(kot.status);
    setEditItems(
      (kot.items || []).map((line) => ({
        id: line.id,
        item_name: line.item_name,
        quantity: Number(line.quantity) || 1,
      })),
    );
    setError('');
    setSuccess('');
  };

  const changeEditQty = (lineId, nextQty) => {
    if (nextQty < 1) return;
    setEditItems((rows) =>
      rows.map((row) => (row.id === lineId ? { ...row, quantity: nextQty } : row)),
    );
  };

  const saveEdit = async () => {
    if (!editKot) return;
    setEditSaving(true);
    setError('');
    try {
      await updateKot(editKot.id, {
        notes: editNotes,
        status: editStatus,
        items: editItems.map((row) => ({
          id: row.id,
          quantity: String(row.quantity),
        })),
      });
      setEditKot(null);
      setSuccess(`KOT ${editKot.kot_number} updated`);
      await load();
    } catch (err) {
      setError(err.response?.data?.error?.message || 'Failed to update KOT.');
    } finally {
      setEditSaving(false);
    }
  };

  const confirmDelete = async () => {
    if (!deleteTarget) return;
    setDeleteSaving(true);
    setError('');
    try {
      await deleteKot(deleteTarget.id);
      setSuccess(`KOT ${deleteTarget.kot_number} deleted`);
      setDeleteTarget(null);
      await load();
    } catch (err) {
      setError(err.response?.data?.error?.message || 'Failed to delete KOT.');
    } finally {
      setDeleteSaving(false);
    }
  };

  const onPrint = (kot) => {
    navigate(`/print/kots/${kot.id}`, {
      state: { from: kitchenPathForUser(user) },
    });
  };

  if (!moduleEnabled) {
    return (
      <PageShell>
        <Alert severity="warning">Kitchen dashboard is not enabled for this business type.</Alert>
      </PageShell>
    );
  }

  return (
    <>
      <PageActions>
        <Button variant="outlined" startIcon={<RefreshOutlinedIcon />} onClick={load}>
          Refresh
        </Button>
      </PageActions>

      <PageShell>
        <Box
          sx={{
            bgcolor: '#121212',
            color: '#f5f5f5',
            borderRadius: 2,
            p: { xs: 2, md: 3 },
            minHeight: '60vh',
          }}
        >
          <Stack spacing={2}>
            <Typography variant="h5" sx={{ fontWeight: 700 }}>
              Kitchen board
            </Typography>
            {error ? <Alert severity="error">{error}</Alert> : null}
            {success ? <Alert severity="success">{success}</Alert> : null}
            {loading ? (
              <LoadingBlock />
            ) : kots.length === 0 ? (
              <EmptyState
                title="Kitchen queue is empty"
                description="Fire a KOT from an open order to send items to the kitchen."
              />
            ) : (
              <Grid container spacing={2}>
                {COLUMNS.map((column) => (
                  <Grid item xs={12} md={4} key={column.key}>
                    <Stack spacing={1.5}>
                      <Typography
                        variant="subtitle1"
                        sx={{ fontWeight: 700, color: column.color, textTransform: 'uppercase' }}
                      >
                        {column.label} ({grouped[column.key].length})
                      </Typography>
                      <Stack spacing={1.5}>
                        {grouped[column.key].map((kot) => (
                          <KotCard
                            key={kot.id}
                            kot={kot}
                            updating={updating}
                            canUpdateStatus={canUpdateKotStatus}
                            canManageKots={canManageKots}
                            onStatusChange={onStatusChange}
                            onEdit={openEdit}
                            onDelete={setDeleteTarget}
                            onPrint={onPrint}
                          />
                        ))}
                        {grouped[column.key].length === 0 ? (
                          <Typography variant="body2" color="rgba(255,255,255,0.5)">
                            No tickets
                          </Typography>
                        ) : null}
                      </Stack>
                    </Stack>
                  </Grid>
                ))}
              </Grid>
            )}
          </Stack>
        </Box>
      </PageShell>

      <Dialog open={Boolean(editKot)} onClose={() => !editSaving && setEditKot(null)} fullWidth maxWidth="sm">
        <DialogTitle>Edit KOT</DialogTitle>
        <DialogContent>
          <Stack spacing={2} sx={{ pt: 1 }}>
            <Typography variant="body2" color="text.secondary">
              KOT No: <strong>{editKot?.kot_number}</strong>
              {editKot?.dining_table_code ? (
                <>
                  {' '}
                  · Table: <strong>{editKot.dining_table_code}</strong>
                </>
              ) : null}
            </Typography>
            <Stack spacing={1.25}>
              {editItems.map((line) => (
                <Stack
                  key={line.id}
                  direction="row"
                  alignItems="center"
                  justifyContent="space-between"
                  spacing={1}
                >
                  <Typography sx={{ flex: 1, minWidth: 0 }} noWrap>
                    {line.item_name}
                  </Typography>
                  <Stack direction="row" alignItems="center" spacing={0.5}>
                    <IconButton
                      size="small"
                      onClick={() => changeEditQty(line.id, line.quantity - 1)}
                      disabled={editSaving || line.quantity <= 1}
                    >
                      <RemoveIcon fontSize="small" />
                    </IconButton>
                    <Typography sx={{ minWidth: 28, textAlign: 'center', fontWeight: 600 }}>
                      {line.quantity}
                    </Typography>
                    <IconButton
                      size="small"
                      onClick={() => changeEditQty(line.id, line.quantity + 1)}
                      disabled={editSaving}
                    >
                      <AddIcon fontSize="small" />
                    </IconButton>
                  </Stack>
                </Stack>
              ))}
            </Stack>
            <FormControl size="small" fullWidth>
              <InputLabel id="kot-edit-status-label">Status</InputLabel>
              <Select
                labelId="kot-edit-status-label"
                label="Status"
                value={editStatus}
                onChange={(e) => setEditStatus(e.target.value)}
                disabled={editSaving}
              >
                {STATUS_OPTIONS.map((opt) => (
                  <MenuItem key={opt.value} value={opt.value}>
                    {opt.label}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
            <TextField
              label="Notes"
              value={editNotes}
              onChange={(e) => setEditNotes(e.target.value)}
              multiline
              minRows={2}
              fullWidth
              disabled={editSaving}
            />
          </Stack>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setEditKot(null)} disabled={editSaving}>
            Cancel
          </Button>
          <Button variant="contained" onClick={saveEdit} disabled={editSaving || !editItems.length}>
            Save Changes
          </Button>
        </DialogActions>
      </Dialog>

      <Dialog
        open={Boolean(deleteTarget)}
        onClose={() => !deleteSaving && setDeleteTarget(null)}
        fullWidth
        maxWidth="xs"
      >
        <DialogTitle>Delete KOT?</DialogTitle>
        <DialogContent>
          <Typography variant="body2" sx={{ mb: 1 }}>
            KOT: <strong>{deleteTarget?.kot_number}</strong>
          </Typography>
          {deleteTarget?.dining_table_code ? (
            <Typography variant="body2" sx={{ mb: 1 }}>
              Table: <strong>{deleteTarget.dining_table_code}</strong>
            </Typography>
          ) : null}
          <Typography variant="body2" color="text.secondary">
            Are you sure you want to delete this KOT? The related order and bills are not deleted.
            Inventory is not changed.
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDeleteTarget(null)} disabled={deleteSaving}>
            Cancel
          </Button>
          <Button color="error" variant="contained" onClick={confirmDelete} disabled={deleteSaving}>
            Delete
          </Button>
        </DialogActions>
      </Dialog>
    </>
  );
}
