import DeleteOutlineOutlinedIcon from '@mui/icons-material/DeleteOutlineOutlined';
import VisibilityOutlinedIcon from '@mui/icons-material/VisibilityOutlined';
import {
  Alert,
  Box,
  Button,
  Card,
  CardContent,
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
import EmptyState from '../../components/EmptyState';
import FilterBar from '../../components/FilterBar';
import PageShell from '../../components/PageShell';
import PaginationBar from '../../components/PaginationBar';
import Section from '../../components/Section';
import TableCard from '../../components/TableCard';
import TruncateText from '../../components/TruncateText';
import ConfirmDialog from '../../components/ui/ConfirmDialog';
import IconActionButton from '../../components/ui/IconActionButton';
import LoadingSkeleton from '../../components/ui/LoadingSkeleton';
import SearchInput from '../../components/ui/SearchInput';
import StatusBadge from '../../components/ui/StatusBadge';
import {
  ACTIVITY_CATEGORIES,
  DATE_PRESETS,
  dateRangeForPreset,
  formatAuditAction,
  formatUserRole,
} from '../../utils/auditLabels';
import {
  deleteAuditLog,
  fetchAuditAlerts,
  getAuditLog,
  listAuditLogs,
} from '../../services/auditService';
import { listUsers } from '../../services/userService';

const PAGE_SIZE = 20;

function describeLog(row) {
  if (row.action === 'DEACTIVATE_CUSTOMER') {
    return row.old_data?.name || row.new_data?.name || 'Customer removed';
  }
  if (row.action === 'CANCEL_BILL') {
    return row.new_data?.cancellation_reason || 'Bill cancelled';
  }
  if (row.action === 'DEACTIVATE_USER') {
    return row.old_data?.name || row.new_data?.name || 'User deactivated';
  }
  if (row.bill_number) return `Bill ${row.bill_number}`;
  if (row.new_data?.bill_number) return `Bill ${row.new_data.bill_number}`;
  if (row.new_data?.name) return row.new_data.name;
  if (row.old_data?.name) return row.old_data.name;
  return row.entity_type || '—';
}

function severityVariant(severity) {
  if (severity === 'medium') return 'pending';
  if (severity === 'low') return 'info';
  return 'info';
}

export default function AuditPage() {
  const [logs, setLogs] = useState([]);
  const [meta, setMeta] = useState({ page: 1, per_page: PAGE_SIZE, total: 0 });
  const [users, setUsers] = useState([]);
  const [alerts, setAlerts] = useState([]);
  const [page, setPage] = useState(1);
  const [filters, setFilters] = useState({
    user_id: '',
    category: '',
    datePreset: 'today',
    from: '',
    to: '',
    q: '',
  });
  const [error, setError] = useState('');
  const [selected, setSelected] = useState(null);
  const [deleteTarget, setDeleteTarget] = useState(null);
  const [deleting, setDeleting] = useState(false);
  const [loading, setLoading] = useState(true);

  const buildParams = (nextPage = page) => {
    const params = { page: nextPage, per_page: PAGE_SIZE };
    if (filters.user_id) params.user_id = filters.user_id;
    if (filters.category) params.category = filters.category;
    if (filters.q.trim()) params.q = filters.q.trim();

    if (filters.datePreset === 'custom') {
      if (filters.from) params.from = filters.from;
      if (filters.to) params.to = filters.to;
    } else {
      const range = dateRangeForPreset(filters.datePreset);
      if (range.from) params.from = range.from;
      if (range.to) params.to = range.to;
    }
    return params;
  };

  const load = async (nextPage = page) => {
    setError('');
    setLoading(true);
    try {
      const [logsRes, alertsRes] = await Promise.all([
        listAuditLogs(buildParams(nextPage)),
        fetchAuditAlerts(),
      ]);
      setLogs(logsRes.data || []);
      setMeta(logsRes.meta || { page: nextPage, per_page: PAGE_SIZE, total: 0 });
      setPage(logsRes.meta?.page || nextPage);
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
    load(1);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const onApplyFilters = () => load(1);

  const openDetail = async (row) => {
    setError('');
    try {
      const res = await getAuditLog(row.id);
      setSelected(res.data);
    } catch (err) {
      setError(err.response?.data?.error?.message || 'Unable to load activity details.');
    }
  };

  const onDelete = async () => {
    if (!deleteTarget) return;
    setDeleting(true);
    setError('');
    try {
      await deleteAuditLog(deleteTarget.id);
      setDeleteTarget(null);
      await load(page);
    } catch (err) {
      setError(err.response?.data?.error?.message || 'Unable to delete activity record.');
    } finally {
      setDeleting(false);
    }
  };

  return (
    <>
      <PageShell>
        <Section
          title="Audit & Activity"
          description="Review user actions, security alerts, and operational changes across your business."
        />

        {error ? <Alert severity="error">{error}</Alert> : null}

        {alerts.length ? (
          <Box
            sx={{
              display: 'grid',
              gap: 2,
              gridTemplateColumns: { xs: '1fr', md: '1fr 1fr' },
              mb: 2,
            }}
          >
            {alerts.slice(0, 4).map((alert) => (
              <Card key={`${alert.type}-${alert.message}`}>
                <CardContent sx={{ p: 2, '&:last-child': { pb: 2 } }}>
                  <Stack direction="row" spacing={1} alignItems="center" mb={0.5} flexWrap="wrap" useFlexGap>
                    <StatusBadge
                      label={alert.severity || 'info'}
                      variant={severityVariant(alert.severity)}
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
            <Button variant="contained" onClick={onApplyFilters} disabled={loading}>
              Search
            </Button>
          }
        >
          <SearchInput
            label="Search Activity"
            placeholder="Customer, user, bill #, activity…"
            value={filters.q}
            onChange={(e) => setFilters((f) => ({ ...f, q: e.target.value }))}
            onKeyDown={(e) => {
              if (e.key === 'Enter') onApplyFilters();
            }}
            sx={{ minWidth: { xs: '100%', sm: 220 }, flex: 1 }}
          />
          <FormControl sx={{ minWidth: { xs: '100%', sm: 160 } }}>
            <InputLabel>Activity Type</InputLabel>
            <Select
              label="Activity Type"
              value={filters.category}
              onChange={(e) => setFilters((f) => ({ ...f, category: e.target.value }))}
            >
              {ACTIVITY_CATEGORIES.map((opt) => (
                <MenuItem key={opt.value || 'all'} value={opt.value}>
                  {opt.label}
                </MenuItem>
              ))}
            </Select>
          </FormControl>
          <FormControl sx={{ minWidth: { xs: '100%', sm: 160 } }}>
            <InputLabel>User</InputLabel>
            <Select
              label="User"
              value={filters.user_id}
              onChange={(e) => setFilters((f) => ({ ...f, user_id: e.target.value }))}
            >
              <MenuItem value="">All Users</MenuItem>
              {users.map((u) => (
                <MenuItem key={u.id} value={u.id}>
                  {u.name}
                </MenuItem>
              ))}
            </Select>
          </FormControl>
          <FormControl sx={{ minWidth: { xs: '100%', sm: 150 } }}>
            <InputLabel>Date</InputLabel>
            <Select
              label="Date"
              value={filters.datePreset}
              onChange={(e) => setFilters((f) => ({ ...f, datePreset: e.target.value }))}
            >
              {DATE_PRESETS.map((opt) => (
                <MenuItem key={opt.value} value={opt.value}>
                  {opt.label}
                </MenuItem>
              ))}
            </Select>
          </FormControl>
          {filters.datePreset === 'custom' ? (
            <>
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
            </>
          ) : null}
        </FilterBar>

        <TableCard>
          {loading ? (
            <Box sx={{ p: 2 }}>
              <LoadingSkeleton rows={6} height={56} />
            </Box>
          ) : (
            <Table size="small" sx={{ minWidth: 860 }}>
              <TableHead>
                <TableRow>
                  <TableCell>Action</TableCell>
                  <TableCell>User</TableCell>
                  <TableCell>Role</TableCell>
                  <TableCell>Date</TableCell>
                  <TableCell align="right">Action</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {logs.map((row) => (
                  <TableRow key={row.id} hover>
                    <TableCell>
                      <Stack spacing={0.25}>
                        <Typography variant="body2" fontWeight={600}>
                          {formatAuditAction(row.action)}
                        </Typography>
                        <Typography variant="caption" color="text.secondary">
                          <TruncateText value={describeLog(row)} maxWidth={220} />
                        </Typography>
                      </Stack>
                    </TableCell>
                    <TableCell>
                      <TruncateText value={row.user_name || '—'} maxWidth={140} />
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2" color="text.secondary">
                        {row.user_role_label || formatUserRole(row.user_role)}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2" color="text.secondary" sx={{ whiteSpace: 'nowrap' }}>
                        {row.created_at
                          ? new Date(row.created_at).toLocaleDateString('en-IN', {
                              day: '2-digit',
                              month: 'short',
                            })
                          : '—'}
                      </Typography>
                    </TableCell>
                    <TableCell align="right">
                      <Stack direction="row" spacing={0.5} justifyContent="flex-end">
                        <IconActionButton title="View details" onClick={() => openDetail(row)}>
                          <VisibilityOutlinedIcon fontSize="small" />
                        </IconActionButton>
                        <IconActionButton
                          title="Delete Activity"
                          color="error"
                          onClick={() => setDeleteTarget(row)}
                        >
                          <DeleteOutlineOutlinedIcon fontSize="small" />
                        </IconActionButton>
                      </Stack>
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

        {!loading && logs.length ? (
          <PaginationBar
            page={page}
            total={meta.total}
            pageSize={PAGE_SIZE}
            onPageChange={(next) => load(next)}
          />
        ) : null}
      </PageShell>

      <ConfirmDialog
        open={Boolean(deleteTarget)}
        title="Delete Activity?"
        description="This audit record will be removed from the activity list."
        confirmLabel="Delete"
        loading={deleting}
        onClose={() => setDeleteTarget(null)}
        onConfirm={onDelete}
      >
        <Stack spacing={1}>
          <Typography variant="body2">
            <strong>Activity:</strong> {formatAuditAction(deleteTarget?.action)}
          </Typography>
          <Typography variant="body2">
            <strong>Performed By:</strong> {deleteTarget?.user_name || '—'}
          </Typography>
          <Typography variant="body2">
            <strong>Date:</strong>{' '}
            {deleteTarget?.created_at
              ? new Date(deleteTarget.created_at).toLocaleDateString('en-IN', {
                  day: '2-digit',
                  month: 'short',
                  year: 'numeric',
                })
              : '—'}
          </Typography>
        </Stack>
      </ConfirmDialog>

      <Dialog open={Boolean(selected)} onClose={() => setSelected(null)} fullWidth maxWidth="sm" scroll="paper">
        <DialogTitle>{formatAuditAction(selected?.action)}</DialogTitle>
        <DialogContent dividers>
          {selected ? (
            <Stack spacing={2}>
              <Typography variant="body2">
                <strong>User:</strong> {selected.user_name || '—'}
              </Typography>
              <Typography variant="body2">
                <strong>Role:</strong>{' '}
                {selected.user_role_label || formatUserRole(selected.user_role)}
              </Typography>
              <Typography variant="body2">
                <strong>Date:</strong>{' '}
                {selected.created_at ? new Date(selected.created_at).toLocaleString() : '—'}
              </Typography>
              <Typography variant="body2">
                <strong>Entity:</strong> {selected.entity_type} {selected.entity_id || ''}
              </Typography>
              <Typography variant="body2">
                <strong>Bill:</strong> {selected.bill_number || '—'}
              </Typography>
              {selected.action === 'CANCEL_BILL' ? (
                <>
                  <Typography variant="body2">
                    <strong>Reason:</strong> {selected.new_data?.cancellation_reason || '—'}
                  </Typography>
                  <Typography variant="body2">
                    <strong>Amount:</strong> ₹
                    {Number(selected.new_data?.grand_total || selected.old_data?.grand_total || 0).toFixed(2)}
                  </Typography>
                </>
              ) : null}
              {selected.ip_address ? (
                <Typography variant="body2">
                  <strong>IP:</strong> {selected.ip_address}
                </Typography>
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
