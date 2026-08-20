import VisibilityOutlinedIcon from '@mui/icons-material/VisibilityOutlined';
import {
  Alert,
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
  Tooltip,
  Typography,
} from '@mui/material';
import { useEffect, useState } from 'react';
import EmptyState from '../../components/EmptyState';
import FilterBar from '../../components/FilterBar';
import PageShell from '../../components/PageShell';
import PaginationBar from '../../components/PaginationBar';
import TableCard from '../../components/TableCard';
import TruncateText from '../../components/TruncateText';
import { listMasterAuditLogs } from '../../services/masterService';

const ACTIONS = [
  '',
  'BUSINESS_APPROVED',
  'BUSINESS_REJECTED',
  'BUSINESS_ACTIVATED',
  'BUSINESS_DEACTIVATED',
  'BUSINESS_SUSPENDED',
  'BUSINESS_UNSUSPENDED',
  'PLAN_CREATED',
  'PLAN_UPDATED',
  'PLAN_ACTIVATED',
  'PLAN_DEACTIVATED',
  'TRIAL_SETTINGS_UPDATED',
  'SUBSCRIPTION_UPDATED',
];

function pretty(value) {
  if (value == null) return '—';
  try {
    return JSON.stringify(value, null, 2);
  } catch {
    return String(value);
  }
}

export default function MasterAuditPage() {
  const [rows, setRows] = useState([]);
  const [meta, setMeta] = useState({ page: 1, per_page: 25, total: 0 });
  const [filters, setFilters] = useState({ action: '' });
  const [page, setPage] = useState(1);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(true);
  const [detail, setDetail] = useState(null);

  const load = async (nextPage = page) => {
    setError('');
    try {
      const params = { page: nextPage, per_page: 25 };
      if (filters.action) params.action = filters.action;
      const response = await listMasterAuditLogs(params);
      setRows(response.data || []);
      setMeta(response.meta || { page: nextPage, per_page: 25, total: 0 });
    } catch (err) {
      setError(err.response?.data?.error?.message || 'Unable to load audit logs.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    setLoading(true);
    load(page);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [filters.action, page]);

  return (
    <PageShell>
      {error ? <Alert severity="error">{error}</Alert> : null}

      <FilterBar>
        <FormControl sx={{ minWidth: 260 }}>
          <InputLabel id="audit-action">Action</InputLabel>
          <Select
            labelId="audit-action"
            label="Action"
            value={filters.action}
            onChange={(event) => {
              setPage(1);
              setFilters({ action: event.target.value });
            }}
          >
            {ACTIONS.map((value) => (
              <MenuItem key={value || 'all'} value={value}>
                {value || 'All actions'}
              </MenuItem>
            ))}
          </Select>
        </FormControl>
      </FilterBar>

      {loading ? (
        <Stack alignItems="center" py={6}>
          <CircularProgress size={28} />
        </Stack>
      ) : rows.length === 0 ? (
        <EmptyState title="No audit entries" description="Master Admin actions appear here." />
      ) : (
        <TableCard>
          <Table size="small">
            <TableHead>
              <TableRow>
                <TableCell>When</TableCell>
                <TableCell>Actor</TableCell>
                <TableCell>Action</TableCell>
                <TableCell>Entity</TableCell>
                <TableCell align="right">Detail</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {rows.map((row) => (
                <TableRow key={row.id} hover>
                  <TableCell>
                    {row.created_at ? new Date(row.created_at).toLocaleString() : '—'}
                  </TableCell>
                  <TableCell>
                    <TruncateText value={row.actor_name || row.actor_email || '—'} />
                  </TableCell>
                  <TableCell>
                    <Chip size="small" label={row.action} />
                  </TableCell>
                  <TableCell>
                    <TruncateText value={`${row.entity_type}${row.entity_id ? ` · ${row.entity_id}` : ''}`} />
                  </TableCell>
                  <TableCell align="right">
                    <Tooltip title="View snapshot">
                      <IconButton size="small" onClick={() => setDetail(row)} aria-label="View audit detail">
                        <VisibilityOutlinedIcon fontSize="small" />
                      </IconButton>
                    </Tooltip>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
          <PaginationBar
            page={meta.page}
            perPage={meta.per_page}
            total={meta.total}
            onPageChange={setPage}
          />
        </TableCard>
      )}

      <Dialog open={Boolean(detail)} onClose={() => setDetail(null)} maxWidth="sm" fullWidth>
        <DialogTitle>{detail?.action}</DialogTitle>
        <DialogContent>
          <Stack spacing={2} sx={{ pt: 1 }}>
            <Typography variant="body2" color="text.secondary">
              {detail?.actor_name} · {detail?.actor_email}
            </Typography>
            <Typography variant="subtitle2">Before</Typography>
            <Typography component="pre" variant="caption" sx={{ whiteSpace: 'pre-wrap', m: 0 }}>
              {pretty(detail?.old_data)}
            </Typography>
            <Typography variant="subtitle2">After</Typography>
            <Typography component="pre" variant="caption" sx={{ whiteSpace: 'pre-wrap', m: 0 }}>
              {pretty(detail?.new_data)}
            </Typography>
          </Stack>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDetail(null)}>Close</Button>
        </DialogActions>
      </Dialog>
    </PageShell>
  );
}
