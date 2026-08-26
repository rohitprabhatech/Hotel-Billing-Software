import AddOutlinedIcon from '@mui/icons-material/AddOutlined';
import BuildOutlinedIcon from '@mui/icons-material/BuildOutlined';
import RefreshOutlinedIcon from '@mui/icons-material/RefreshOutlined';
import {
  Alert,
  Autocomplete,
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
  Grid,
  Stack,
  TextField,
  Typography,
} from '@mui/material';
import { useCallback, useEffect, useMemo, useState } from 'react';
import EmptyState from '../../components/EmptyState';
import LoadingBlock from '../../components/LoadingBlock';
import PageShell from '../../components/PageShell';
import { PageActions } from '../../context/PageActionsContext';
import { useAuth } from '../../context/AuthContext';
import { useModuleGate } from '../../context/ModulesContext';
import { createRepair, listRepairs, updateRepairStatus } from '../../services/repairService';
import { listSerialUnits } from '../../services/serialService';

const COLUMNS = [
  { key: 'RECEIVED', label: 'Received', color: '#ffb74d' },
  { key: 'IN_PROGRESS', label: 'In progress', color: '#64b5f6' },
  { key: 'READY', label: 'Ready', color: '#81c784' },
  { key: 'DELIVERED', label: 'Delivered', color: '#90a4ae' },
];

const NEXT_ACTIONS = {
  RECEIVED: [{ status: 'IN_PROGRESS', label: 'Start repair' }],
  IN_PROGRESS: [{ status: 'READY', label: 'Mark ready' }],
  READY: [{ status: 'DELIVERED', label: 'Mark delivered' }],
  DELIVERED: [],
};

function RepairCard({ repair, onStatusChange, updating, canWrite }) {
  const actions = NEXT_ACTIONS[repair.status] || [];

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
              {repair.repair_number}
            </Typography>
            <Chip size="small" label={repair.status.replace('_', ' ')} />
          </Stack>
          <Typography variant="body2" color="rgba(255,255,255,0.72)">
            {repair.item_name} · {repair.serial}
          </Typography>
          {repair.customer_name ? (
            <Typography variant="body2" color="rgba(255,255,255,0.72)">
              {repair.customer_name}
              {repair.customer_phone ? ` · ${repair.customer_phone}` : ''}
            </Typography>
          ) : null}
          <Typography variant="body1">{repair.issue_description}</Typography>
          {repair.estimated_charge != null ? (
            <Typography variant="body2">Est. charge ₹{Number(repair.estimated_charge).toFixed(2)}</Typography>
          ) : null}
          {repair.notes ? (
            <Typography variant="body2" color="warning.light">
              Note: {repair.notes}
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
              disabled={updating === repair.id}
              onClick={() => onStatusChange(repair.id, action.status)}
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

export default function RepairsPage() {
  const moduleEnabled = useModuleGate('repair_service');
  const { role } = useAuth();
  const canWrite = role === 'OWNER' || role === 'MANAGER';

  const [repairs, setRepairs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [updating, setUpdating] = useState('');

  const [createOpen, setCreateOpen] = useState(false);
  const [serialOptions, setSerialOptions] = useState([]);
  const [selectedUnit, setSelectedUnit] = useState(null);
  const [issue, setIssue] = useState('');
  const [customerName, setCustomerName] = useState('');
  const [customerPhone, setCustomerPhone] = useState('');
  const [estimatedCharge, setEstimatedCharge] = useState('');
  const [saving, setSaving] = useState(false);

  const load = useCallback(async () => {
    if (!moduleEnabled) return;
    setError('');
    try {
      const response = await listRepairs({ per_page: 200 });
      setRepairs(response.data || []);
    } catch (err) {
      setError(err.response?.data?.error?.message || 'Unable to load repair tickets.');
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

  const grouped = useMemo(() => {
    const map = Object.fromEntries(COLUMNS.map((col) => [col.key, []]));
    repairs.forEach((repair) => {
      if (map[repair.status]) map[repair.status].push(repair);
    });
    return map;
  }, [repairs]);

  const openCreate = async () => {
    setCreateOpen(true);
    setSelectedUnit(null);
    setIssue('');
    setCustomerName('');
    setCustomerPhone('');
    setEstimatedCharge('');
    setError('');
    try {
      const res = await listSerialUnits({ per_page: 100 });
      setSerialOptions(res.data || []);
    } catch {
      setSerialOptions([]);
    }
  };

  const onStatusChange = async (repairId, status) => {
    setUpdating(repairId);
    setError('');
    try {
      await updateRepairStatus(repairId, { status });
      await load();
    } catch (err) {
      setError(err.response?.data?.error?.message || 'Failed to update repair status.');
    } finally {
      setUpdating('');
    }
  };

  const submitCreate = async () => {
    if (!selectedUnit) {
      setError('Select the serial / IMEI unit.');
      return;
    }
    if (!issue.trim()) {
      setError('Issue description is required.');
      return;
    }
    setSaving(true);
    setError('');
    try {
      await createRepair({
        serial_unit_id: selectedUnit.id,
        issue_description: issue.trim(),
        customer_name: customerName.trim() || undefined,
        customer_phone: customerPhone.trim() || undefined,
        estimated_charge: estimatedCharge.trim() ? Number(estimatedCharge) : undefined,
      });
      setCreateOpen(false);
      await load();
    } catch (err) {
      setError(err.response?.data?.error?.message || 'Could not create repair ticket.');
    } finally {
      setSaving(false);
    }
  };

  if (!moduleEnabled) {
    return (
      <PageShell>
        <Alert severity="warning">Repair / service tracking is not enabled for this business type.</Alert>
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
            New repair ticket
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
          <Stack spacing={2}>
            <Stack direction="row" spacing={1} alignItems="center">
              <BuildOutlinedIcon />
              <Typography variant="h5" sx={{ fontWeight: 700 }}>
                Repair board
              </Typography>
            </Stack>
            {!canWrite ? (
              <Alert severity="info">Billing users can view repair tickets. Owner or manager updates status.</Alert>
            ) : null}
            {error && !createOpen ? <Alert severity="error">{error}</Alert> : null}
            {loading ? (
              <LoadingBlock />
            ) : repairs.length === 0 ? (
              <EmptyState
                title="No repair tickets yet"
                description="Create a ticket when a customer drops off a phone or device for service."
                actionLabel={canWrite ? 'New repair ticket' : undefined}
                onAction={canWrite ? openCreate : undefined}
              />
            ) : (
              <Grid container spacing={2}>
                {COLUMNS.map((column) => (
                  <Grid item xs={12} md={3} key={column.key}>
                    <Stack spacing={1.5}>
                      <Typography variant="subtitle1" sx={{ fontWeight: 700, color: column.color }}>
                        {column.label} ({grouped[column.key].length})
                      </Typography>
                      {grouped[column.key].map((repair) => (
                        <RepairCard
                          key={repair.id}
                          repair={repair}
                          onStatusChange={onStatusChange}
                          updating={updating}
                          canWrite={canWrite}
                        />
                      ))}
                    </Stack>
                  </Grid>
                ))}
              </Grid>
            )}
          </Stack>
        </Box>
      </PageShell>

      <Dialog open={createOpen} onClose={() => !saving && setCreateOpen(false)} fullWidth maxWidth="sm">
        <DialogTitle>New repair ticket</DialogTitle>
        <DialogContent>
          <Stack spacing={2} sx={{ mt: 1 }}>
            {error && createOpen ? <Alert severity="error">{error}</Alert> : null}
            <Autocomplete
              options={serialOptions}
              getOptionLabel={(option) => `${option.serial} · ${option.item_name || 'Item'} (${option.status})`}
              value={selectedUnit}
              onChange={(_, value) => setSelectedUnit(value)}
              renderInput={(params) => <TextField {...params} label="Serial / IMEI" required />}
            />
            <TextField
              label="Issue description"
              value={issue}
              onChange={(e) => setIssue(e.target.value)}
              required
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
              label="Estimated charge (₹)"
              type="number"
              value={estimatedCharge}
              onChange={(e) => setEstimatedCharge(e.target.value)}
              fullWidth
            />
          </Stack>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setCreateOpen(false)} disabled={saving}>
            Cancel
          </Button>
          <Button variant="contained" onClick={submitCreate} disabled={saving}>
            {saving ? 'Saving…' : 'Create ticket'}
          </Button>
        </DialogActions>
      </Dialog>
    </>
  );
}
