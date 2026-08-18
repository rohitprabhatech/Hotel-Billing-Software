import CheckOutlinedIcon from '@mui/icons-material/CheckOutlined';
import CloseOutlinedIcon from '@mui/icons-material/CloseOutlined';
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
  approveRegistrationRequest,
  getRegistrationRequest,
  listRegistrationRequests,
  rejectRegistrationRequest,
} from '../../services/masterService';

const STATUS_OPTIONS = ['', 'PENDING', 'APPROVED', 'REJECTED'];

function statusColor(status) {
  if (status === 'PENDING') return 'warning';
  if (status === 'APPROVED') return 'success';
  if (status === 'REJECTED') return 'error';
  return 'default';
}

function formatWhen(value) {
  if (!value) return '—';
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;
  return date.toLocaleString();
}

export default function MasterRegistrationRequestsPage() {
  const [rows, setRows] = useState([]);
  const [filters, setFilters] = useState({ status: 'PENDING', q: '' });
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [selected, setSelected] = useState(null);
  const [rejectOpen, setRejectOpen] = useState(false);
  const [rejectReason, setRejectReason] = useState('');

  const load = async () => {
    setError('');
    setLoading(true);
    try {
      const params = { per_page: 50 };
      if (filters.status) params.status = filters.status;
      if (filters.q.trim()) params.q = filters.q.trim();
      const response = await listRegistrationRequests(params);
      setRows(response.data || []);
    } catch (err) {
      setError(err.response?.data?.error?.message || 'Unable to load registration requests.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const openDetail = async (row) => {
    setError('');
    try {
      const response = await getRegistrationRequest(row.id);
      setSelected(response.data);
    } catch (err) {
      setError(err.response?.data?.error?.message || 'Unable to load request details.');
    }
  };

  const onApprove = async () => {
    if (!selected) return;
    setSaving(true);
    setError('');
    setSuccess('');
    try {
      await approveRegistrationRequest(selected.id);
      setSuccess(`${selected.business_name} approved. The owner can now sign in.`);
      setSelected(null);
      await load();
    } catch (err) {
      setError(err.response?.data?.error?.message || 'Unable to approve this request.');
    } finally {
      setSaving(false);
    }
  };

  const onReject = async () => {
    if (!selected) return;
    setSaving(true);
    setError('');
    setSuccess('');
    try {
      await rejectRegistrationRequest(selected.id, rejectReason.trim());
      setSuccess(`${selected.business_name} was rejected.`);
      setRejectOpen(false);
      setRejectReason('');
      setSelected(null);
      await load();
    } catch (err) {
      setError(err.response?.data?.error?.message || 'Unable to reject this request.');
    } finally {
      setSaving(false);
    }
  };

  return (
    <PageShell>
      {error ? <Alert severity="error">{error}</Alert> : null}
      {success ? <Alert severity="success">{success}</Alert> : null}

      <FilterBar
        actions={
          <Button variant="contained" onClick={load} disabled={loading}>
            Apply
          </Button>
        }
      >
        <FormControl sx={{ minWidth: 180 }} size="small">
          <InputLabel id="reg-status-label">Status</InputLabel>
          <Select
            labelId="reg-status-label"
            label="Status"
            value={filters.status}
            onChange={(event) => setFilters((prev) => ({ ...prev, status: event.target.value }))}
          >
            <MenuItem value="">All</MenuItem>
            {STATUS_OPTIONS.filter(Boolean).map((status) => (
              <MenuItem key={status} value={status}>
                {status}
              </MenuItem>
            ))}
          </Select>
        </FormControl>
        <TextField
          size="small"
          label="Search"
          value={filters.q}
          onChange={(event) => setFilters((prev) => ({ ...prev, q: event.target.value }))}
          onKeyDown={(event) => {
            if (event.key === 'Enter') load();
          }}
          sx={{ minWidth: 220 }}
        />
      </FilterBar>

      {loading ? (
        <Stack alignItems="center" py={6}>
          <CircularProgress size={28} />
        </Stack>
      ) : rows.length === 0 ? (
        <EmptyState
          title="No registration requests"
          description="New public signups appear here until they are approved or rejected."
        />
      ) : (
        <TableCard>
          <Table size="small">
            <TableHead>
              <TableRow>
                <TableCell>Business</TableCell>
                <TableCell>Owner</TableCell>
                <TableCell>Email</TableCell>
                <TableCell>Type</TableCell>
                <TableCell>Requested</TableCell>
                <TableCell>Status</TableCell>
                <TableCell align="right">Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {rows.map((row) => (
                <TableRow key={row.id} hover>
                  <TableCell>
                    <TruncateText>{row.business_name}</TruncateText>
                  </TableCell>
                  <TableCell>{row.owner_name}</TableCell>
                  <TableCell>{row.owner_email}</TableCell>
                  <TableCell>{row.business_type}</TableCell>
                  <TableCell>{formatWhen(row.requested_at)}</TableCell>
                  <TableCell>
                    <Chip size="small" label={row.status} color={statusColor(row.status)} />
                  </TableCell>
                  <TableCell align="right">
                    <Tooltip title="View">
                      <Button
                        size="small"
                        startIcon={<VisibilityOutlinedIcon />}
                        onClick={() => openDetail(row)}
                      >
                        View
                      </Button>
                    </Tooltip>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableCard>
      )}

      <Dialog open={Boolean(selected)} onClose={() => setSelected(null)} maxWidth="sm" fullWidth>
        <DialogTitle>Registration request</DialogTitle>
        <DialogContent>
          {selected ? (
            <Stack spacing={1.25} sx={{ pt: 1 }}>
              <Typography>
                <strong>Business:</strong> {selected.business_name}
              </Typography>
              <Typography>
                <strong>Type:</strong> {selected.business_type}
              </Typography>
              <Typography>
                <strong>Owner:</strong> {selected.owner_name} ({selected.owner_email})
              </Typography>
              <Typography>
                <strong>Mobile:</strong> {selected.mobile || '—'}
              </Typography>
              <Typography>
                <strong>Address:</strong>{' '}
                {[selected.address, selected.city, selected.state, selected.pincode, selected.country]
                  .filter(Boolean)
                  .join(', ') || '—'}
              </Typography>
              <Typography>
                <strong>GST:</strong> {selected.gst_number || '—'}
              </Typography>
              <Typography>
                <strong>FSSAI:</strong> {selected.fssai_number || '—'}
              </Typography>
              <Typography>
                <strong>Status:</strong> {selected.status}
              </Typography>
              <Typography>
                <strong>Requested:</strong> {formatWhen(selected.requested_at)}
              </Typography>
              {selected.rejection_reason ? (
                <Typography>
                  <strong>Rejection reason:</strong> {selected.rejection_reason}
                </Typography>
              ) : null}
            </Stack>
          ) : null}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setSelected(null)}>Close</Button>
          {selected?.status === 'PENDING' ? (
            <>
              <Button
                color="error"
                startIcon={<CloseOutlinedIcon />}
                onClick={() => setRejectOpen(true)}
                disabled={saving}
              >
                Reject
              </Button>
              <Button
                variant="contained"
                startIcon={saving ? <CircularProgress size={16} color="inherit" /> : <CheckOutlinedIcon />}
                onClick={onApprove}
                disabled={saving}
              >
                Approve
              </Button>
            </>
          ) : null}
        </DialogActions>
      </Dialog>

      <Dialog open={rejectOpen} onClose={() => setRejectOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Reject registration</DialogTitle>
        <DialogContent>
          <TextField
            autoFocus
            margin="dense"
            label="Reason"
            value={rejectReason}
            onChange={(event) => setRejectReason(event.target.value)}
            required
            fullWidth
            multiline
            minRows={3}
            helperText="Required. The applicant will see this reason in email."
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setRejectOpen(false)}>Cancel</Button>
          <Button
            color="error"
            variant="contained"
            onClick={onReject}
            disabled={saving || rejectReason.trim().length < 8}
          >
            Confirm reject
          </Button>
        </DialogActions>
      </Dialog>
    </PageShell>
  );
}
