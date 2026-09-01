import AddOutlinedIcon from '@mui/icons-material/AddOutlined';
import HandymanOutlinedIcon from '@mui/icons-material/HandymanOutlined';
import RefreshOutlinedIcon from '@mui/icons-material/RefreshOutlined';
import {
  Alert,
  Autocomplete,
  Box,
  Button,
  Card,
  CardActions,
  CardContent,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  Grid,
  Stack,
  TextField,
  Typography,
} from '@mui/material';
import { useCallback, useEffect, useMemo, useState } from 'react';
import EmptyState from '../../components/EmptyState';
import LoadingBlock from '../../components/LoadingBlock';
import PageShell from '../../components/PageShell';
import StatusBadge from '../../components/ui/StatusBadge';
import { PageActions } from '../../context/PageActionsContext';
import { useAuth } from '../../context/AuthContext';
import { useModuleGate } from '../../context/ModulesContext';
import {
  createInstallation,
  listInstallations,
  updateInstallationStatus,
} from '../../services/installationService';
import { listCustomOrders } from '../../services/customOrderService';
import { listSerialUnits } from '../../services/serialService';

const COLUMNS = [
  { key: 'SCHEDULED', label: 'Scheduled', color: '#ffb74d' },
  { key: 'IN_PROGRESS', label: 'In progress', color: '#64b5f6' },
  { key: 'COMPLETED', label: 'Completed', color: '#81c784' },
];

const NEXT_ACTIONS = {
  SCHEDULED: [{ status: 'IN_PROGRESS', label: 'Start install' }],
  IN_PROGRESS: [{ status: 'COMPLETED', label: 'Mark completed' }],
  COMPLETED: [],
};

function formatWhen(value) {
  if (!value) return 'Unscheduled';
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;
  return date.toLocaleString();
}

function dateKey(value) {
  if (!value) return 'Unscheduled';
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return 'Unscheduled';
  return date.toLocaleDateString(undefined, {
    weekday: 'short',
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  });
}

function workflowStatusVariant(status) {
  const key = String(status || '').toUpperCase();
  if (key === 'SCHEDULED') return 'pending';
  if (key === 'IN_PROGRESS') return 'info';
  if (key === 'COMPLETED') return 'active';
  return 'info';
}

function InstallationCard({ job, onStatusChange, updating, canWrite }) {
  const actions = NEXT_ACTIONS[job.status] || [];

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
          <Stack direction="row" justifyContent="space-between" alignItems="center">
            <Typography variant="h6" sx={{ fontWeight: 700 }}>
              {job.installation_number}
            </Typography>
            <StatusBadge
              label={job.status.replace('_', ' ')}
              variant={workflowStatusVariant(job.status)}
            />
          </Stack>
          <Typography variant="body2" color="rgba(255,255,255,0.72)">
            {job.item_name}
            {job.serial ? ` · ${job.serial}` : ''}
            {job.custom_order_number ? ` · ${job.custom_order_number}` : ''}
          </Typography>
          <Typography variant="body2" color="rgba(255,255,255,0.72)">
            {formatWhen(job.scheduled_at)}
          </Typography>
          {job.customer_name ? (
            <Typography variant="body2" color="rgba(255,255,255,0.72)">
              {job.customer_name}
              {job.customer_phone ? ` · ${job.customer_phone}` : ''}
            </Typography>
          ) : null}
          {job.install_address ? <Typography variant="body1">{job.install_address}</Typography> : null}
          {job.technician_name ? (
            <Typography variant="body2">Tech: {job.technician_name}</Typography>
          ) : null}
          {job.notes ? (
            <Typography variant="body2" color="warning.light">
              Note: {job.notes}
            </Typography>
          ) : null}
        </Stack>
      </CardContent>
      {canWrite && actions.length ? (
        <CardActions sx={{ px: 2, pb: 2, flexDirection: 'column', gap: 1 }}>
          {actions.map((action) => (
            <Button
              key={action.status}
              fullWidth
              variant="contained"
              size="large"
              disabled={updating === job.id}
              onClick={() => onStatusChange(job.id, action.status)}
              sx={{ minHeight: 48 }}
            >
              {action.label}
            </Button>
          ))}
        </CardActions>
      ) : null}
    </Card>
  );
}

export default function InstallationsPage() {
  const moduleEnabled = useModuleGate('installation');
  const { role, user } = useAuth();
  const isFurniture = user?.tenant?.business_type === 'furniture';
  const canWrite = role === 'OWNER' || role === 'MANAGER';

  const [jobs, setJobs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [updating, setUpdating] = useState('');

  const [createOpen, setCreateOpen] = useState(false);
  const [serialOptions, setSerialOptions] = useState([]);
  const [orderOptions, setOrderOptions] = useState([]);
  const [selectedUnit, setSelectedUnit] = useState(null);
  const [selectedOrder, setSelectedOrder] = useState(null);
  const [scheduledAt, setScheduledAt] = useState('');
  const [installAddress, setInstallAddress] = useState('');
  const [customerName, setCustomerName] = useState('');
  const [customerPhone, setCustomerPhone] = useState('');
  const [technicianName, setTechnicianName] = useState('');
  const [notes, setNotes] = useState('');
  const [saving, setSaving] = useState(false);

  const load = useCallback(async () => {
    if (!moduleEnabled) return;
    setError('');
    try {
      const response = await listInstallations({ per_page: 200 });
      setJobs(response.data || []);
    } catch (err) {
      setError(err.response?.data?.error?.message || 'Unable to load installation jobs.');
    } finally {
      setLoading(false);
    }
  }, [moduleEnabled]);

  useEffect(() => {
    load();
  }, [load]);

  useEffect(() => {
    if (!moduleEnabled) return undefined;
    const timer = window.setInterval(load, 30000);
    return () => window.clearInterval(timer);
  }, [load, moduleEnabled]);

  const groupedByStatus = useMemo(() => {
    const map = Object.fromEntries(COLUMNS.map((col) => [col.key, []]));
    jobs.forEach((job) => {
      if (map[job.status]) map[job.status].push(job);
    });
    return map;
  }, [jobs]);

  const scheduleGroups = useMemo(() => {
    const map = new Map();
    jobs
      .filter((job) => job.status !== 'CANCELLED')
      .forEach((job) => {
        const key = dateKey(job.scheduled_at);
        if (!map.has(key)) map.set(key, []);
        map.get(key).push(job);
      });
    return [...map.entries()];
  }, [jobs]);

  const openCreate = async () => {
    setCreateOpen(true);
    setSelectedUnit(null);
    setSelectedOrder(null);
    setScheduledAt('');
    setInstallAddress('');
    setCustomerName('');
    setCustomerPhone('');
    setTechnicianName('');
    setNotes('');
    setError('');
    try {
      if (isFurniture) {
        const res = await listCustomOrders({ order_type: 'furniture', status: 'READY', per_page: 100 });
        setOrderOptions(res.data || []);
        setSerialOptions([]);
      } else {
        const res = await listSerialUnits({ status: 'SOLD', per_page: 100 });
        setSerialOptions(res.data || []);
        setOrderOptions([]);
      }
    } catch {
      setSerialOptions([]);
      setOrderOptions([]);
    }
  };

  const onStatusChange = async (installationId, status) => {
    setUpdating(installationId);
    setError('');
    try {
      await updateInstallationStatus(installationId, { status });
      await load();
    } catch (err) {
      setError(err.response?.data?.error?.message || 'Failed to update installation status.');
    } finally {
      setUpdating('');
    }
  };

  const submitCreate = async () => {
    if (isFurniture) {
      if (!selectedOrder) {
        setError('Select a ready furniture order.');
        return;
      }
    } else if (!selectedUnit) {
      setError('Select the sold serial / IMEI unit.');
      return;
    }
    if (!scheduledAt) {
      setError('Scheduled date/time is required.');
      return;
    }
    setSaving(true);
    setError('');
    try {
      await createInstallation(
        isFurniture
          ? {
              custom_order_id: selectedOrder.id,
              scheduled_at: scheduledAt.length === 16 ? `${scheduledAt}:00` : scheduledAt,
              install_address: installAddress.trim() || undefined,
              customer_name: customerName.trim() || selectedOrder.customer_name || undefined,
              customer_phone: customerPhone.trim() || selectedOrder.customer_phone || undefined,
              technician_name: technicianName.trim() || undefined,
              notes: notes.trim() || undefined,
            }
          : {
              serial_unit_id: selectedUnit.id,
              scheduled_at: scheduledAt.length === 16 ? `${scheduledAt}:00` : scheduledAt,
              install_address: installAddress.trim() || undefined,
              customer_name: customerName.trim() || undefined,
              customer_phone: customerPhone.trim() || undefined,
              technician_name: technicianName.trim() || undefined,
              notes: notes.trim() || undefined,
              bill_id: selectedUnit.sold_bill_id || undefined,
            }
      );
      setCreateOpen(false);
      await load();
    } catch (err) {
      setError(err.response?.data?.error?.message || 'Could not schedule installation.');
    } finally {
      setSaving(false);
    }
  };

  if (!moduleEnabled) {
    return (
      <PageShell>
        <Alert severity="warning">Installation tracking is not enabled for this business type.</Alert>
      </PageShell>
    );
  }

  return (
    <>
      <PageActions>
        <Button variant="outlined" startIcon={<RefreshOutlinedIcon />} onClick={load}>
          Refresh
        </Button>
        {canWrite ? (
          <Button variant="contained" startIcon={<AddOutlinedIcon />} onClick={openCreate}>
            Schedule installation
          </Button>
        ) : null}
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
          <Stack spacing={3}>
            <Stack direction="row" spacing={1} alignItems="center">
              <HandymanOutlinedIcon />
              <Typography variant="h5" sx={{ fontWeight: 700 }}>
                Installation board
              </Typography>
            </Stack>
            {!canWrite ? (
              <Alert severity="info">
                Billing users can view installation jobs. Owner or manager updates status.
              </Alert>
            ) : null}
            {error && !createOpen ? <Alert severity="error">{error}</Alert> : null}
            {loading ? (
              <LoadingBlock />
            ) : jobs.length === 0 ? (
              <EmptyState
                title="No installation jobs yet"
                description={
                  isFurniture
                    ? 'Schedule installation when a ready furniture order needs on-site setup.'
                    : 'Schedule an install when a sold unit needs on-site setup.'
                }
                actionLabel={canWrite ? 'Schedule installation' : undefined}
                onAction={canWrite ? openCreate : undefined}
              />
            ) : (
              <>
                <Box>
                  <Typography variant="subtitle1" sx={{ fontWeight: 700, mb: 1.5 }}>
                    Upcoming by date
                  </Typography>
                  <Stack spacing={2}>
                    {scheduleGroups.map(([day, dayJobs]) => (
                      <Box key={day}>
                        <Typography variant="body2" color="rgba(255,255,255,0.72)" sx={{ mb: 1 }}>
                          {day} · {dayJobs.length} job{dayJobs.length === 1 ? '' : 's'}
                        </Typography>
                        <Grid container spacing={1.5}>
                          {dayJobs.map((job) => (
                            <Grid item xs={12} md={4} key={`cal-${job.id}`}>
                              <InstallationCard
                                job={job}
                                onStatusChange={onStatusChange}
                                updating={updating}
                                canWrite={canWrite}
                              />
                            </Grid>
                          ))}
                        </Grid>
                      </Box>
                    ))}
                  </Stack>
                </Box>

                <Box>
                  <Typography variant="subtitle1" sx={{ fontWeight: 700, mb: 1.5 }}>
                    Status columns
                  </Typography>
                  <Grid container spacing={2}>
                    {COLUMNS.map((column) => (
                      <Grid item xs={12} md={4} key={column.key}>
                        <Stack spacing={1.5}>
                          <Typography variant="subtitle1" sx={{ fontWeight: 700, color: column.color }}>
                            {column.label} ({groupedByStatus[column.key].length})
                          </Typography>
                          {groupedByStatus[column.key].map((job) => (
                            <InstallationCard
                              key={job.id}
                              job={job}
                              onStatusChange={onStatusChange}
                              updating={updating}
                              canWrite={canWrite}
                            />
                          ))}
                        </Stack>
                      </Grid>
                    ))}
                  </Grid>
                </Box>
              </>
            )}
          </Stack>
        </Box>
      </PageShell>

      <Dialog open={createOpen} onClose={() => !saving && setCreateOpen(false)} fullWidth maxWidth="sm">
        <DialogTitle>Schedule installation</DialogTitle>
        <DialogContent>
          <Stack spacing={2} sx={{ mt: 1 }}>
            {error && createOpen ? <Alert severity="error">{error}</Alert> : null}
            {isFurniture ? (
              <Autocomplete
                options={orderOptions}
                getOptionLabel={(option) =>
                  `${option.order_number} · ${option.title} (${option.customer_name || 'Walk-in'})`
                }
                value={selectedOrder}
                onChange={(_, value) => {
                  setSelectedOrder(value);
                  if (value) {
                    setCustomerName(value.customer_name || '');
                    setCustomerPhone(value.customer_phone || '');
                  }
                }}
                renderInput={(params) => (
                  <TextField {...params} label="Ready furniture order" required />
                )}
              />
            ) : (
              <Autocomplete
                options={serialOptions}
                getOptionLabel={(option) =>
                  `${option.serial} · ${option.item_name || 'Item'} (${option.status})`
                }
                value={selectedUnit}
                onChange={(_, value) => setSelectedUnit(value)}
                renderInput={(params) => <TextField {...params} label="Sold serial / IMEI" required />}
              />
            )}
            <TextField
              label="Scheduled at"
              type="datetime-local"
              value={scheduledAt}
              onChange={(e) => setScheduledAt(e.target.value)}
              required
              fullWidth
              InputLabelProps={{ shrink: true }}
            />
            <TextField
              label="Install address"
              value={installAddress}
              onChange={(e) => setInstallAddress(e.target.value)}
              multiline
              minRows={2}
              fullWidth
            />
            <TextField
              label="Customer name"
              value={customerName}
              onChange={(e) => setCustomerName(e.target.value)}
              fullWidth
            />
            <TextField
              label="Customer phone"
              value={customerPhone}
              onChange={(e) => setCustomerPhone(e.target.value)}
              fullWidth
            />
            <TextField
              label="Technician"
              value={technicianName}
              onChange={(e) => setTechnicianName(e.target.value)}
              fullWidth
            />
            <TextField
              label="Notes"
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              multiline
              minRows={2}
              fullWidth
            />
          </Stack>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setCreateOpen(false)} disabled={saving}>
            Cancel
          </Button>
          <Button variant="contained" onClick={submitCreate} disabled={saving}>
            {saving ? 'Saving…' : 'Schedule'}
          </Button>
        </DialogActions>
      </Dialog>
    </>
  );
}
