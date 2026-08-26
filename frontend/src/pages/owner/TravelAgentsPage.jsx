import AddOutlinedIcon from '@mui/icons-material/AddOutlined';
import HandshakeOutlinedIcon from '@mui/icons-material/HandshakeOutlined';
import RefreshOutlinedIcon from '@mui/icons-material/RefreshOutlined';
import {
  Alert,
  Box,
  Button,
  Chip,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  FormControlLabel,
  Stack,
  Switch,
  Tab,
  Tabs,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
  TextField,
  Typography,
} from '@mui/material';
import { useCallback, useEffect, useState } from 'react';
import EmptyState from '../../components/EmptyState';
import LoadingBlock from '../../components/LoadingBlock';
import PageShell from '../../components/PageShell';
import { PageActions } from '../../context/PageActionsContext';
import { useAuth } from '../../context/AuthContext';
import { useModuleGate } from '../../context/ModulesContext';
import {
  createTravelAgent,
  getTravelCommissionReport,
  listTravelAgents,
  listTravelCommissions,
  updateTravelAgent,
  updateTravelCommissionStatus,
} from '../../services/travelAgentService';

function money(v) {
  return `₹${Number(v || 0).toLocaleString('en-IN', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  })}`;
}

const emptyAgent = {
  code: '',
  name: '',
  phone: '',
  email: '',
  commission_percent: '10',
  notes: '',
  is_active: true,
};

export default function TravelAgentsPage() {
  const moduleEnabled = useModuleGate('travel_commission');
  const { role } = useAuth();
  const canWrite = role === 'OWNER' || role === 'MANAGER';

  const [tab, setTab] = useState(0);
  const [agents, setAgents] = useState([]);
  const [report, setReport] = useState([]);
  const [entries, setEntries] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [saving, setSaving] = useState(false);

  const [open, setOpen] = useState(false);
  const [editId, setEditId] = useState(null);
  const [form, setForm] = useState(emptyAgent);

  const load = useCallback(async () => {
    if (!moduleEnabled) return;
    setLoading(true);
    setError('');
    try {
      const [agentRes, reportRes, entryRes] = await Promise.all([
        listTravelAgents({ per_page: 100 }),
        getTravelCommissionReport(),
        listTravelCommissions({ per_page: 100 }),
      ]);
      setAgents(agentRes.data || []);
      setReport(reportRes.data || []);
      setEntries(entryRes.data || []);
    } catch (err) {
      setError(err.response?.data?.error?.message || 'Failed to load agents / commissions');
    } finally {
      setLoading(false);
    }
  }, [moduleEnabled]);

  useEffect(() => {
    load();
  }, [load]);

  const openCreate = () => {
    setEditId(null);
    setForm(emptyAgent);
    setOpen(true);
  };

  const openEdit = (agent) => {
    setEditId(agent.id);
    setForm({
      code: agent.code || '',
      name: agent.name || '',
      phone: agent.phone || '',
      email: agent.email || '',
      commission_percent: String(agent.commission_percent ?? ''),
      notes: agent.notes || '',
      is_active: Boolean(agent.is_active),
    });
    setOpen(true);
  };

  const saveAgent = async () => {
    if (!form.code.trim() || !form.name.trim()) {
      setError('Code and name are required.');
      return;
    }
    setSaving(true);
    setError('');
    try {
      const payload = {
        code: form.code.trim(),
        name: form.name.trim(),
        phone: form.phone.trim() || null,
        email: form.email.trim() || null,
        commission_percent: Number(form.commission_percent || 0),
        notes: form.notes.trim() || null,
        is_active: form.is_active,
      };
      if (editId) {
        await updateTravelAgent(editId, payload);
        setSuccess('Agent updated');
      } else {
        await createTravelAgent(payload);
        setSuccess('Agent created');
      }
      setOpen(false);
      await load();
    } catch (err) {
      setError(err.response?.data?.error?.message || 'Could not save agent');
    } finally {
      setSaving(false);
    }
  };

  const markPaid = async (entryId) => {
    setSaving(true);
    setError('');
    try {
      await updateTravelCommissionStatus(entryId, { status: 'PAID' });
      setSuccess('Commission marked paid');
      await load();
    } catch (err) {
      setError(err.response?.data?.error?.message || 'Could not update commission');
    } finally {
      setSaving(false);
    }
  };

  if (!moduleEnabled) {
    return (
      <PageShell>
        <EmptyState
          icon={<HandshakeOutlinedIcon />}
          title="Agent commission not enabled"
          description="Available for travel agency tenants."
        />
      </PageShell>
    );
  }

  return (
    <PageShell>
      <PageActions>
        <Stack direction="row" spacing={1}>
          <Button startIcon={<RefreshOutlinedIcon />} onClick={load} disabled={loading}>
            Refresh
          </Button>
          {canWrite ? (
            <Button variant="contained" startIcon={<AddOutlinedIcon />} onClick={openCreate}>
              Agent
            </Button>
          ) : null}
        </Stack>
      </PageActions>

      {error ? (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      ) : null}
      {success ? (
        <Alert severity="success" sx={{ mb: 2 }}>
          {success}
        </Alert>
      ) : null}

      <Tabs value={tab} onChange={(_, v) => setTab(v)} sx={{ mb: 2 }}>
        <Tab label="Commission report" />
        <Tab label="Agents" />
        <Tab label="Entries" />
      </Tabs>

      {loading ? (
        <LoadingBlock />
      ) : tab === 0 ? (
        report.length === 0 ? (
          <EmptyState
            icon={<HandshakeOutlinedIcon />}
            title="No commissions yet"
            description="Assign an agent when creating a booking to accrue commission."
          />
        ) : (
          <Box sx={{ overflowX: 'auto' }}>
            <Table size="small">
              <TableHead>
                <TableRow>
                  <TableCell>Agent</TableCell>
                  <TableCell align="right">Bookings</TableCell>
                  <TableCell align="right">Booking total</TableCell>
                  <TableCell align="right">Commission</TableCell>
                  <TableCell align="right">Pending</TableCell>
                  <TableCell align="right">Paid</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {report.map((row) => (
                  <TableRow key={row.agent_id}>
                    <TableCell>
                      <Typography fontWeight={600}>
                        {row.agent_code} · {row.agent_name}
                      </Typography>
                    </TableCell>
                    <TableCell align="right">{row.entry_count}</TableCell>
                    <TableCell align="right">{money(row.booking_total)}</TableCell>
                    <TableCell align="right">{money(row.commission_total)}</TableCell>
                    <TableCell align="right">{money(row.pending_total)}</TableCell>
                    <TableCell align="right">{money(row.paid_total)}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </Box>
        )
      ) : tab === 1 ? (
        agents.length === 0 ? (
          <EmptyState
            icon={<HandshakeOutlinedIcon />}
            title="No agents"
            description="Create agents with a default commission percent."
          />
        ) : (
          <Stack spacing={1.5}>
            {agents.map((agent) => (
              <Box
                key={agent.id}
                sx={{ border: 1, borderColor: 'divider', borderRadius: 1, p: 1.5 }}
              >
                <Stack
                  direction={{ xs: 'column', sm: 'row' }}
                  justifyContent="space-between"
                  spacing={1}
                >
                  <Stack spacing={0.5}>
                    <Stack direction="row" spacing={1} alignItems="center">
                      <Typography fontWeight={700}>
                        {agent.code} · {agent.name}
                      </Typography>
                      <Chip
                        size="small"
                        label={agent.is_active ? 'Active' : 'Inactive'}
                        color={agent.is_active ? 'success' : 'default'}
                      />
                    </Stack>
                    <Typography variant="body2" color="text.secondary">
                      Default commission {Number(agent.commission_percent).toFixed(2)}%
                      {agent.phone ? ` · ${agent.phone}` : ''}
                    </Typography>
                  </Stack>
                  {canWrite ? (
                    <Button size="small" onClick={() => openEdit(agent)}>
                      Edit
                    </Button>
                  ) : null}
                </Stack>
              </Box>
            ))}
          </Stack>
        )
      ) : entries.length === 0 ? (
        <EmptyState
          icon={<HandshakeOutlinedIcon />}
          title="No commission entries"
          description="Entries appear when bookings are linked to agents."
        />
      ) : (
        <Box sx={{ overflowX: 'auto' }}>
          <Table size="small">
            <TableHead>
              <TableRow>
                <TableCell>Booking</TableCell>
                <TableCell>Agent</TableCell>
                <TableCell align="right">Total</TableCell>
                <TableCell align="right">%</TableCell>
                <TableCell align="right">Commission</TableCell>
                <TableCell>Status</TableCell>
                <TableCell />
              </TableRow>
            </TableHead>
            <TableBody>
              {entries.map((entry) => (
                <TableRow key={entry.id}>
                  <TableCell>{entry.booking_number}</TableCell>
                  <TableCell>
                    {entry.agent_code} · {entry.agent_name}
                  </TableCell>
                  <TableCell align="right">{money(entry.booking_total)}</TableCell>
                  <TableCell align="right">{Number(entry.commission_percent).toFixed(2)}</TableCell>
                  <TableCell align="right">{money(entry.commission_amount)}</TableCell>
                  <TableCell>
                    <Chip size="small" label={entry.status} />
                  </TableCell>
                  <TableCell align="right">
                    {canWrite && entry.status === 'PENDING' ? (
                      <Button size="small" disabled={saving} onClick={() => markPaid(entry.id)}>
                        Mark paid
                      </Button>
                    ) : null}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </Box>
      )}

      <Dialog open={open} onClose={() => !saving && setOpen(false)} fullWidth maxWidth="sm">
        <DialogTitle>{editId ? 'Edit agent' : 'New travel agent'}</DialogTitle>
        <DialogContent>
          <Stack spacing={2} sx={{ mt: 1 }}>
            <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2}>
              <TextField
                label="Code"
                value={form.code}
                onChange={(e) => setForm((f) => ({ ...f, code: e.target.value }))}
                fullWidth
                required
              />
              <TextField
                label="Name"
                value={form.name}
                onChange={(e) => setForm((f) => ({ ...f, name: e.target.value }))}
                fullWidth
                required
              />
            </Stack>
            <TextField
              label="Commission %"
              type="number"
              value={form.commission_percent}
              onChange={(e) => setForm((f) => ({ ...f, commission_percent: e.target.value }))}
              fullWidth
            />
            <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2}>
              <TextField
                label="Phone"
                value={form.phone}
                onChange={(e) => setForm((f) => ({ ...f, phone: e.target.value }))}
                fullWidth
              />
              <TextField
                label="Email"
                value={form.email}
                onChange={(e) => setForm((f) => ({ ...f, email: e.target.value }))}
                fullWidth
              />
            </Stack>
            <TextField
              label="Notes"
              value={form.notes}
              onChange={(e) => setForm((f) => ({ ...f, notes: e.target.value }))}
              fullWidth
              multiline
              minRows={2}
            />
            <FormControlLabel
              control={
                <Switch
                  checked={form.is_active}
                  onChange={(e) => setForm((f) => ({ ...f, is_active: e.target.checked }))}
                />
              }
              label="Active"
            />
          </Stack>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpen(false)} disabled={saving}>
            Cancel
          </Button>
          <Button variant="contained" onClick={saveAgent} disabled={saving}>
            Save
          </Button>
        </DialogActions>
      </Dialog>
    </PageShell>
  );
}
