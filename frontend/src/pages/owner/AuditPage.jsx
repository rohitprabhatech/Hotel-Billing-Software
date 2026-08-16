import VisibilityOutlinedIcon from '@mui/icons-material/VisibilityOutlined';
import {
  Alert,
  Box,
  Button,
  Card,
  CardContent,
  Chip,
  CircularProgress,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  FormControl,
  IconButton,
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
  Tooltip,
  Typography,
} from '@mui/material';
import { useEffect, useState } from 'react';
import EmptyState from '../../components/EmptyState';
import FilterBar from '../../components/FilterBar';
import PageShell from '../../components/PageShell';
import TableCard from '../../components/TableCard';
import TruncateText from '../../components/TruncateText';
import {
  fetchAuditAlerts,
  getAuditLog,
  listAuditLogs,
} from '../../services/auditService';
import { listUsers } from '../../services/userService';

const ACTIONS = [
  '',
  'LOGIN',
  'LOGOUT',
  'PASSWORD_CHANGED',
  'PASSWORD_RESET_REQUESTED',
  'CREATE_BILL',
  'CANCEL_BILL',
  'PRINT_BILL',
  'REPRINT_BILL',
  'BILL_SENT_WHATSAPP',
  'BILL_WHATSAPP_FAILED',
  'BILL_SENT_EMAIL',
  'BILL_EMAIL_FAILED',
  'STOCK_ADJUSTED',
  'STOCK_UPDATED',
  'ITEM_CREATED',
  'ITEM_UPDATED',
  'ITEM_DEACTIVATED',
  'ITEM_REACTIVATED',
  'UPDATE_PRICE',
  'CHANGE_GST',
  'CREATE_CATEGORY',
  'UPDATE_CATEGORY',
  'DEACTIVATE_CATEGORY',
  'CREATE_USER',
  'UPDATE_USER',
  'DEACTIVATE_USER',
  'UPDATE_PROFILE',
  'UPDATE_TENANT',
  'REGISTER_BUSINESS',
  'EMAIL_CHANGED',
  'EMAIL_VERIFIED',
  'EMAIL_CHANGE_REQUESTED',
  'EXPORT_REPORT',
];

function severityColor(severity) {
  if (severity === 'medium') return 'warning';
  if (severity === 'low') return 'default';
  return 'info';
}

function describeLog(row) {
  if (row.action === 'CANCEL_BILL') {
    return row.new_data?.cancellation_reason || 'Bill cancelled';
  }
  if (row.action === 'BILL_SENT_WHATSAPP') {
    return `WhatsApp sent${row.new_data?.recipient ? ` · ${row.new_data.recipient}` : ''}`;
  }
  if (row.action === 'BILL_WHATSAPP_FAILED') {
    return `WhatsApp failed${row.new_data?.recipient ? ` · ${row.new_data.recipient}` : ''}`;
  }
  if (row.action === 'BILL_SENT_EMAIL') {
    return `Email sent${row.new_data?.recipient ? ` · ${row.new_data.recipient}` : ''}`;
  }
  if (row.action === 'BILL_EMAIL_FAILED') {
    return `Email failed${row.new_data?.recipient ? ` · ${row.new_data.recipient}` : ''}`;
  }
  if (row.action === 'STOCK_ADJUSTED') {
    const d = row.new_data?.delta;
    const stock = row.new_data?.stock_quantity;
    const bits = [];
    if (d != null) bits.push(`${Number(d) > 0 ? '+' : ''}${Number(d)}`);
    if (stock != null) bits.push(`→ ${stock}`);
    if (row.new_data?.reason) bits.push(row.new_data.reason);
    return bits.length ? bits.join(' · ') : 'Stock adjusted';
  }
  if (row.action === 'PASSWORD_CHANGED') return 'Password changed';
  if (row.action === 'LOGIN') return 'Signed in';
  if (row.action === 'LOGOUT') return 'Signed out';
  if (row.bill_number) return `Bill ${row.bill_number}`;
  if (row.new_data?.bill_number) return `Bill ${row.new_data.bill_number}`;
  if (row.new_data?.name) return row.new_data.name;
  if (row.old_data?.name) return row.old_data.name;
  return row.entity_type || '—';
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
  const [loading, setLoading] = useState(true);

  const load = async () => {
    setError('');
    setLoading(true);
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
      setError(err.response?.data?.error?.message || 'Unable to load audit activity.');
    } finally {
      setLoading(false);
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
      setError(err.response?.data?.error?.message || 'Unable to load activity details.');
    }
  };

  return (
    <>
      <PageShell>
        <Alert severity="info">
          Immutable activity trail for your business — indicators for investigation, not automatic
          fraud accusations. Audit entries cannot be deleted.
        </Alert>

        {error ? <Alert severity="error">{error}</Alert> : null}

        {alerts.length ? (
          <Box
            sx={{
              display: 'grid',
              gap: 2,
              gridTemplateColumns: { xs: '1fr', md: '1fr 1fr' },
            }}
          >
            {alerts.map((alert) => (
              <Card key={`${alert.type}-${alert.message}`}>
                <CardContent sx={{ p: 2.5, '&:last-child': { pb: 2.5 } }}>
                  <Stack direction="row" spacing={1} alignItems="center" mb={1} flexWrap="wrap" useFlexGap>
                    <Chip
                      size="small"
                      label={alert.severity || 'info'}
                      color={severityColor(alert.severity)}
                    />
                    <Typography variant="subtitle2">{alert.title}</Typography>
                  </Stack>
                  <Typography variant="body2" color="text.secondary">
                    {alert.message}
                  </Typography>
                </CardContent>
              </Card>
            ))}
          </Box>
        ) : null}

        <FilterBar
          actions={
            <Button variant="contained" onClick={load} disabled={loading}>
              Apply
            </Button>
          }
        >
          <FormControl sx={{ minWidth: { xs: '100%', sm: 160 } }}>
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
          <FormControl sx={{ minWidth: { xs: '100%', sm: 180 } }}>
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
            label="Search"
            value={filters.q}
            onChange={(e) => setFilters((f) => ({ ...f, q: e.target.value }))}
            sx={{ minWidth: { xs: '100%', sm: 160 }, flex: 1 }}
          />
          <TextField
            label="From"
            type="date"
            value={filters.from}
            onChange={(e) => setFilters((f) => ({ ...f, from: e.target.value }))}
            InputLabelProps={{ shrink: true }}
            sx={{ minWidth: { xs: '100%', sm: 150 } }}
          />
          <TextField
            label="To"
            type="date"
            value={filters.to}
            onChange={(e) => setFilters((f) => ({ ...f, to: e.target.value }))}
            InputLabelProps={{ shrink: true }}
            sx={{ minWidth: { xs: '100%', sm: 150 } }}
          />
        </FilterBar>

        <TableCard>
          {loading ? (
            <Box sx={{ py: 8, display: 'grid', placeItems: 'center' }}>
              <CircularProgress size={28} />
            </Box>
          ) : (
            <Table size="small" sx={{ minWidth: 900 }}>
              <TableHead>
                <TableRow>
                  <TableCell>Date & Time</TableCell>
                  <TableCell>User</TableCell>
                  <TableCell>Action</TableCell>
                  <TableCell>Entity</TableCell>
                  <TableCell>Description</TableCell>
                  <TableCell align="right">Details</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {logs.map((row) => (
                  <TableRow key={row.id} hover>
                    <TableCell>
                      <Typography variant="body2" color="text.secondary" sx={{ whiteSpace: 'nowrap' }}>
                        {row.created_at ? new Date(row.created_at).toLocaleString() : '—'}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <TruncateText value={row.user_name || '—'} maxWidth={140} />
                    </TableCell>
                    <TableCell>
                      <Chip size="small" label={row.action} variant="outlined" />
                    </TableCell>
                    <TableCell>
                      <TruncateText value={row.entity_type || '—'} maxWidth={100} />
                    </TableCell>
                    <TableCell>
                      <TruncateText value={describeLog(row)} maxWidth={220} />
                    </TableCell>
                    <TableCell align="right">
                      <Tooltip title="View details">
                        <IconButton
                          size="small"
                          aria-label="View activity details"
                          onClick={() => openDetail(row)}
                        >
                          <VisibilityOutlinedIcon fontSize="small" />
                        </IconButton>
                      </Tooltip>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
          {!loading && !logs.length ? (
            <EmptyState
              title="No audit events found"
              description="Try adjusting filters or check back after more activity."
            />
          ) : null}
        </TableCard>
      </PageShell>

      <Dialog
        open={Boolean(selected)}
        onClose={() => setSelected(null)}
        fullWidth
        maxWidth="sm"
        scroll="paper"
      >
        <DialogTitle>
          <TruncateText value={selected?.action || 'Activity details'} maxWidth="100%" variant="h6" />
        </DialogTitle>
        <DialogContent dividers>
          {selected ? (
            <Stack spacing={2}>
              <Typography variant="body2"><strong>User:</strong> {selected.user_name || '—'}</Typography>
              <Typography variant="body2">
                <strong>Date:</strong>{' '}
                {selected.created_at ? new Date(selected.created_at).toLocaleString() : '—'}
              </Typography>
              <Typography variant="body2">
                <strong>Entity:</strong> {selected.entity_type} {selected.entity_id || ''}
              </Typography>
              <Typography variant="body2"><strong>Bill:</strong> {selected.bill_number || '—'}</Typography>
              {selected.action === 'CANCEL_BILL' ? (
                <>
                  <Typography variant="body2">
                    <strong>Reason:</strong>{' '}
                    {selected.new_data?.cancellation_reason || '—'}
                  </Typography>
                  <Typography variant="body2">
                    <strong>Amount:</strong>{' '}
                    ₹{Number(selected.new_data?.grand_total || selected.old_data?.grand_total || 0).toFixed(2)}
                  </Typography>
                </>
              ) : null}
              {selected.ip_address ? (
                <Typography variant="body2"><strong>IP:</strong> {selected.ip_address}</Typography>
              ) : null}
              <Typography variant="subtitle2">Previous values</Typography>
              <Box
                component="pre"
                sx={{
                  m: 0,
                  p: 2,
                  bgcolor: 'grey.50',
                  borderRadius: 1,
                  overflow: 'auto',
                  maxHeight: 180,
                  fontSize: 12,
                  whiteSpace: 'pre-wrap',
                  wordBreak: 'break-word',
                }}
              >
                {JSON.stringify(selected.old_data || {}, null, 2)}
              </Box>
              <Typography variant="subtitle2">New values</Typography>
              <Box
                component="pre"
                sx={{
                  m: 0,
                  p: 2,
                  bgcolor: 'grey.50',
                  borderRadius: 1,
                  overflow: 'auto',
                  maxHeight: 180,
                  fontSize: 12,
                  whiteSpace: 'pre-wrap',
                  wordBreak: 'break-word',
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
