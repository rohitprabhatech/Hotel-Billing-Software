import VisibilityOutlinedIcon from '@mui/icons-material/VisibilityOutlined';
import {
  Alert,
  Box,
  Button,
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
import { useSearchParams } from 'react-router-dom';
import EmptyState from '../../components/EmptyState';
import FilterBar from '../../components/FilterBar';
import PageShell from '../../components/PageShell';
import TableCard from '../../components/TableCard';
import TruncateText from '../../components/TruncateText';
import { getAuditLog, listAuditLogs } from '../../services/auditService';
import { listUsers } from '../../services/userService';

const ITEM_ACTIONS = [
  '',
  'ITEM_CREATED',
  'ITEM_UPDATED',
  'ITEM_DEACTIVATED',
  'ITEM_REACTIVATED',
  'UPDATE_PRICE',
  'CHANGE_GST',
  'STOCK_UPDATED',
  'STOCK_ADJUSTED',
  'STOCK_DEDUCTED',
  'STOCK_RESTORED',
];

function actionChipColor(action) {
  if (action?.includes('CREATED') || action === 'CREATE_ITEM') return 'success';
  if (action?.includes('DEACTIVATED') || action === 'DEACTIVATE_ITEM') return 'warning';
  if (action?.includes('REACTIVATED')) return 'info';
  if (action?.includes('STOCK')) return 'secondary';
  return 'default';
}

function summarizeValues(data) {
  if (!data || typeof data !== 'object') return '—';
  const parts = [];
  if (data.delta != null) {
    const d = Number(data.delta);
    parts.push(`${d > 0 ? '+' : ''}${d}`);
  }
  if (data.stock_quantity != null) parts.push(`stock ${Number(data.stock_quantity)}`);
  if (data.price != null) parts.push(`₹${Number(data.price).toFixed(2)}`);
  if (data.gst_percentage != null) parts.push(`GST ${data.gst_percentage}%`);
  if (data.is_active != null) parts.push(data.is_active ? 'Active' : 'Inactive');
  if (data.reason) parts.push(`Reason: ${data.reason}`);
  if (data.name && parts.length === 0) parts.push(data.name);
  return parts.length ? parts.join(' · ') : '—';
}

export default function ItemActivityPage() {
  const [searchParams] = useSearchParams();
  const [logs, setLogs] = useState([]);
  const [users, setUsers] = useState([]);
  const [error, setError] = useState('');
  const [selected, setSelected] = useState(null);
  const [loading, setLoading] = useState(true);
  const [filters, setFilters] = useState({
    q: searchParams.get('q') || '',
    user_id: '',
    action: '',
    from: '',
    to: '',
  });

  const load = async (nextFilters = filters) => {
    setError('');
    setLoading(true);
    try {
      const params = {
        entity_type: 'ITEM',
        per_page: 100,
      };
      Object.entries(nextFilters).forEach(([key, value]) => {
        if (value) params[key] = value;
      });
      const response = await listAuditLogs(params);
      setLogs(response.data || []);
    } catch (err) {
      setError(err.response?.data?.error?.message || 'Unable to load item activity.');
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

  const openDetail = async (id) => {
    try {
      const response = await getAuditLog(id);
      setSelected(response.data);
    } catch (err) {
      setError(err.response?.data?.error?.message || 'Unable to load activity detail.');
    }
  };

  return (
    <>
      <PageShell>
        <Alert severity="info">
          Item create, edit, and deactivate events stay here even after an item is deactivated.
          Catalog soft-deactivation does not remove activity history.
        </Alert>
        <FilterBar
          actions={
            <Button variant="contained" onClick={() => load()} disabled={loading}>
              Apply
            </Button>
          }
        >
          <TextField
            label="Item"
            value={filters.q}
            onChange={(e) => setFilters((f) => ({ ...f, q: e.target.value }))}
            sx={{ minWidth: { xs: '100%', sm: 180 }, flex: 1 }}
          />
          <FormControl sx={{ minWidth: { xs: '100%', sm: 180 } }}>
            <InputLabel>Billing User</InputLabel>
            <Select
              label="Billing User"
              value={filters.user_id}
              onChange={(e) => setFilters((f) => ({ ...f, user_id: e.target.value }))}
            >
              <MenuItem value="">All Users</MenuItem>
              {users.map((u) => (
                <MenuItem key={u.id} value={u.id}>
                  {u.name} ({u.role})
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
              {ITEM_ACTIONS.map((action) => (
                <MenuItem key={action || 'all'} value={action}>
                  {action || 'All Actions'}
                </MenuItem>
              ))}
            </Select>
          </FormControl>
          <TextField
            label="From"
            type="date"
            InputLabelProps={{ shrink: true }}
            value={filters.from}
            onChange={(e) => setFilters((f) => ({ ...f, from: e.target.value }))}
            sx={{ minWidth: { xs: '100%', sm: 150 } }}
          />
          <TextField
            label="To"
            type="date"
            InputLabelProps={{ shrink: true }}
            value={filters.to}
            onChange={(e) => setFilters((f) => ({ ...f, to: e.target.value }))}
            sx={{ minWidth: { xs: '100%', sm: 150 } }}
          />
        </FilterBar>

        {error ? <Alert severity="error">{error}</Alert> : null}

        <TableCard>
          {loading ? (
            <Box sx={{ py: 8, display: 'grid', placeItems: 'center' }}>
              <CircularProgress size={28} />
            </Box>
          ) : (
            <Table size="small" sx={{ minWidth: 960 }}>
              <TableHead>
                <TableRow>
                  <TableCell>Date & Time</TableCell>
                  <TableCell>User</TableCell>
                  <TableCell>Item</TableCell>
                  <TableCell>Action</TableCell>
                  <TableCell>Previous Value</TableCell>
                  <TableCell>New Value</TableCell>
                  <TableCell align="right">Details</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {logs.map((log) => (
                  <TableRow key={log.id} hover>
                    <TableCell>
                      <Typography variant="body2" color="text.secondary" sx={{ whiteSpace: 'nowrap' }}>
                        {log.created_at ? new Date(log.created_at).toLocaleString() : '—'}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <TruncateText value={log.user_name || '—'} maxWidth={140} />
                    </TableCell>
                    <TableCell>
                      <TruncateText
                        value={log.new_data?.name || log.old_data?.name || log.entity_id || '—'}
                        maxWidth={160}
                      />
                    </TableCell>
                    <TableCell>
                      <Chip
                        size="small"
                        label={log.action}
                        color={actionChipColor(log.action)}
                        variant="outlined"
                      />
                    </TableCell>
                    <TableCell>
                      <TruncateText value={summarizeValues(log.old_data)} maxWidth={160} />
                    </TableCell>
                    <TableCell>
                      <TruncateText value={summarizeValues(log.new_data)} maxWidth={160} />
                    </TableCell>
                    <TableCell align="right">
                      <Tooltip title="View details">
                        <IconButton
                          size="small"
                          aria-label="View item activity details"
                          onClick={() => openDetail(log.id)}
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
              title="No item activity found"
              description="Item create, update, and deactivate events will appear here."
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
        <DialogTitle>Item activity details</DialogTitle>
        <DialogContent dividers>
          {selected ? (
            <Stack spacing={2}>
              <Typography variant="body2"><strong>Action:</strong> {selected.action}</Typography>
              <Typography variant="body2"><strong>User:</strong> {selected.user_name || '—'}</Typography>
              <Typography variant="body2">
                <strong>When:</strong>{' '}
                {selected.created_at ? new Date(selected.created_at).toLocaleString() : '—'}
              </Typography>
              <Typography variant="body2"><strong>Entity ID:</strong> {selected.entity_id}</Typography>
              {selected.new_data?.reason ? (
                <Typography variant="body2"><strong>Reason:</strong> {selected.new_data.reason}</Typography>
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
