import {
  Alert,
  Box,
  Button,
  Card,
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
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
  TextField,
  Typography,
} from '@mui/material';
import { useEffect, useState } from 'react';
import { listUsers } from '../../services/userService';
import {
  fetchAuditAlerts,
  getAuditLog,
  listAuditLogs,
} from '../../services/auditService';

const ACTIONS = [
  '',
  'LOGIN',
  'LOGOUT',
  'CREATE_BILL',
  'CANCEL_BILL',
  'PRINT_BILL',
  'REPRINT_BILL',
  'CREATE_ITEM',
  'UPDATE_ITEM',
  'UPDATE_PRICE',
  'CHANGE_GST',
  'DEACTIVATE_ITEM',
  'CREATE_CATEGORY',
  'UPDATE_CATEGORY',
  'DEACTIVATE_CATEGORY',
  'CREATE_USER',
  'UPDATE_USER',
  'DEACTIVATE_USER',
  'UPDATE_TENANT',
  'EXPORT_REPORT',
];

function severityColor(severity) {
  if (severity === 'medium') return 'warning';
  if (severity === 'low') return 'default';
  return 'info';
}

export default function AuditPage() {
  const [logs, setLogs] = useState([]);
  const [users, setUsers] = useState([]);
  const [alerts, setAlerts] = useState([]);
  const [filters, setFilters] = useState({
    user_id: '',
    action: '',
    entity_type: '',
    bill_number: '',
    from: '',
    to: '',
    q: '',
  });
  const [error, setError] = useState('');
  const [selected, setSelected] = useState(null);

  const load = async () => {
    setError('');
    try {
      const params = {};
      Object.entries(filters).forEach(([key, value]) => {
        if (value) params[key] = value;
      });
      const [logsRes, alertsRes] = await Promise.all([
        listAuditLogs({ ...params, per_page: 100 }),
        fetchAuditAlerts(),
      ]);
      setLogs(logsRes.data || []);
      setAlerts(alertsRes.data?.alerts || []);
    } catch (err) {
      setError(err.response?.data?.error?.message || 'Failed to load audit logs');
    }
  };

  useEffect(() => {
    listUsers()
      .then((res) => setUsers(res.data || []))
      .catch(() => {});
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const openDetail = async (row) => {
    setError('');
    try {
      const res = await getAuditLog(row.id);
      setSelected(res.data);
    } catch (err) {
      setError(err.response?.data?.error?.message || 'Failed to load audit detail');
    }
  };

  return (
    <>
      <Typography variant="h5" gutterBottom>
        Activity & Audit
      </Typography>
      <Alert severity="info" sx={{ mb: 2 }}>
        These are activity indicators for investigation — not automatic fraud accusations.
      </Alert>

      {error ? <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert> : null}

      <Box
        sx={{
          display: 'grid',
          gap: 2,
          gridTemplateColumns: { xs: '1fr', md: '1fr 1fr' },
          mb: 3,
        }}
      >
        {alerts.map((alert) => (
          <Card key={`${alert.type}-${alert.message}`}>
            <CardContent>
              <Stack direction="row" spacing={1} alignItems="center" mb={1}>
                <Chip
                  size="small"
                  label={alert.severity || 'info'}
                  color={severityColor(alert.severity)}
                />
                <Typography variant="subtitle1">{alert.title}</Typography>
              </Stack>
              <Typography variant="body2" color="text.secondary">
                {alert.message}
              </Typography>
            </CardContent>
          </Card>
        ))}
        {!alerts.length ? (
          <Typography color="text.secondary">No activity alerts for today.</Typography>
        ) : null}
      </Box>

      <Stack direction={{ xs: 'column', md: 'row' }} spacing={2} mb={2}>
        <FormControl sx={{ minWidth: 160 }}>
          <InputLabel>User</InputLabel>
          <Select
            label="User"
            value={filters.user_id}
            onChange={(e) => setFilters((f) => ({ ...f, user_id: e.target.value }))}
          >
            <MenuItem value="">All</MenuItem>
            {users.map((u) => (
              <MenuItem key={u.id} value={u.id}>
                {u.name}
              </MenuItem>
            ))}
          </Select>
        </FormControl>
        <FormControl sx={{ minWidth: 180 }}>
          <InputLabel>Action</InputLabel>
          <Select
            label="Action"
            value={filters.action}
            onChange={(e) => setFilters((f) => ({ ...f, action: e.target.value }))}
          >
            {ACTIONS.map((action) => (
              <MenuItem key={action || 'all'} value={action}>
                {action || 'All'}
              </MenuItem>
            ))}
          </Select>
        </FormControl>
        <TextField
          label="Bill Number"
          value={filters.bill_number}
          onChange={(e) => setFilters((f) => ({ ...f, bill_number: e.target.value }))}
        />
        <TextField
          label="From"
          type="date"
          value={filters.from}
          onChange={(e) => setFilters((f) => ({ ...f, from: e.target.value }))}
          InputLabelProps={{ shrink: true }}
        />
        <TextField
          label="To"
          type="date"
          value={filters.to}
          onChange={(e) => setFilters((f) => ({ ...f, to: e.target.value }))}
          InputLabelProps={{ shrink: true }}
        />
        <Button variant="contained" onClick={load}>
          Filter
        </Button>
      </Stack>

      <Box sx={{ bgcolor: 'background.paper', borderRadius: 2, overflow: 'auto' }}>
        <Table size="small">
          <TableHead>
            <TableRow>
              <TableCell>Date</TableCell>
              <TableCell>User</TableCell>
              <TableCell>Action</TableCell>
              <TableCell>Entity</TableCell>
              <TableCell>Bill</TableCell>
              <TableCell align="right">Details</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {logs.map((row) => (
              <TableRow key={row.id} hover>
                <TableCell>
                  {row.created_at ? new Date(row.created_at).toLocaleString() : '—'}
                </TableCell>
                <TableCell>{row.user_name || '—'}</TableCell>
                <TableCell>{row.action}</TableCell>
                <TableCell>{row.entity_type}</TableCell>
                <TableCell>{row.bill_number || '—'}</TableCell>
                <TableCell align="right">
                  <Button size="small" onClick={() => openDetail(row)}>
                    View
                  </Button>
                </TableCell>
              </TableRow>
            ))}
            {!logs.length ? (
              <TableRow>
                <TableCell colSpan={6}>
                  <Typography color="text.secondary">No audit events found.</Typography>
                </TableCell>
              </TableRow>
            ) : null}
          </TableBody>
        </Table>
      </Box>

      <Dialog open={Boolean(selected)} onClose={() => setSelected(null)} fullWidth maxWidth="sm">
        <DialogTitle>{selected?.action}</DialogTitle>
        <DialogContent>
          {selected ? (
            <Stack spacing={1.25} sx={{ mt: 1 }}>
              <Typography><strong>User:</strong> {selected.user_name || '—'}</Typography>
              <Typography><strong>Date:</strong> {selected.created_at ? new Date(selected.created_at).toLocaleString() : '—'}</Typography>
              <Typography><strong>Entity:</strong> {selected.entity_type} {selected.entity_id || ''}</Typography>
              <Typography><strong>Bill:</strong> {selected.bill_number || '—'}</Typography>
              {selected.action === 'CANCEL_BILL' ? (
                <>
                  <Typography>
                    <strong>Reason:</strong>{' '}
                    {selected.new_data?.cancellation_reason || '—'}
                  </Typography>
                  <Typography>
                    <strong>Amount:</strong>{' '}
                    ₹{Number(selected.new_data?.grand_total || selected.old_data?.grand_total || 0).toFixed(2)}
                  </Typography>
                </>
              ) : null}
              {selected.ip_address ? (
                <Typography><strong>IP:</strong> {selected.ip_address}</Typography>
              ) : null}
              <Typography variant="subtitle2" sx={{ mt: 1 }}>Old data</Typography>
              <Box
                component="pre"
                sx={{
                  m: 0,
                  p: 1.5,
                  bgcolor: 'grey.100',
                  borderRadius: 1,
                  overflow: 'auto',
                  fontSize: 12,
                }}
              >
                {JSON.stringify(selected.old_data || {}, null, 2)}
              </Box>
              <Typography variant="subtitle2">New data</Typography>
              <Box
                component="pre"
                sx={{
                  m: 0,
                  p: 1.5,
                  bgcolor: 'grey.100',
                  borderRadius: 1,
                  overflow: 'auto',
                  fontSize: 12,
                }}
              >
                {JSON.stringify(selected.new_data || {}, null, 2)}
              </Box>
            </Stack>
          ) : null}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setSelected(null)}>Close</Button>
        </DialogActions>
      </Dialog>
    </>
  );
}