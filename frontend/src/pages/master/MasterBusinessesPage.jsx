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
  Typography,
} from '@mui/material';
import { useEffect, useState } from 'react';
import EmptyState from '../../components/EmptyState';
import FilterBar from '../../components/FilterBar';
import PageShell from '../../components/PageShell';
import TableCard from '../../components/TableCard';
import TruncateText from '../../components/TruncateText';
import {
  assignBusinessPlan,
  cancelBusinessSubscription,
  extendBusinessTrial,
  listMasterBusinesses,
  listPlans,
  renewBusinessSubscription,
} from '../../services/masterService';

const STATUS_OPTIONS = ['', 'TRIAL', 'ACTIVE', 'EXPIRING', 'EXPIRED', 'CANCELLED', 'NONE'];

function statusColor(status) {
  if (status === 'ACTIVE') return 'success';
  if (status === 'TRIAL' || status === 'EXPIRING') return 'warning';
  if (status === 'EXPIRED' || status === 'CANCELLED') return 'error';
  return 'default';
}

export default function MasterBusinessesPage() {
  const [rows, setRows] = useState([]);
  const [plans, setPlans] = useState([]);
  const [filters, setFilters] = useState({ status: '', q: '' });
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [action, setAction] = useState(null);
  const [planId, setPlanId] = useState('');
  const [days, setDays] = useState('30');

  const load = async () => {
    setError('');
    try {
      const params = { per_page: 50 };
      if (filters.status) params.status = filters.status;
      if (filters.q.trim()) params.q = filters.q.trim();
      const [businesses, planList] = await Promise.all([
        listMasterBusinesses(params),
        listPlans({ include_inactive: false }),
      ]);
      setRows(businesses.data || []);
      setPlans(planList.data || []);
    } catch (err) {
      setError(err.response?.data?.error?.message || 'Unable to load businesses.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [filters.status]);

  const onSearch = (event) => {
    event.preventDefault();
    setLoading(true);
    load();
  };

  const closeAction = () => {
    setAction(null);
    setDays('30');
  };

  const onConfirm = async () => {
    if (!action) return;
    setSaving(true);
    setError('');
    setSuccess('');
    try {
      const id = action.row.id;
      if (action.type === 'assign') {
        if (!planId) throw new Error('Select a plan');
        const payload = { plan_id: planId };
        const n = Number(days);
        if (n > 0) payload.days = n;
        await assignBusinessPlan(id, payload);
        setSuccess('Plan assigned.');
      } else if (action.type === 'trial') {
        await extendBusinessTrial(id, Number(days));
        setSuccess('Trial updated.');
      } else if (action.type === 'renew') {
        const payload = { days: Number(days) };
        if (planId) payload.plan_id = planId;
        await renewBusinessSubscription(id, payload);
        setSuccess('Manual renewal recorded. Existing billed amounts were snapshotted.');
      } else if (action.type === 'cancel') {
        await cancelBusinessSubscription(id);
        setSuccess('Subscription cancelled. The business can still sign in.');
      }
      closeAction();
      await load();
    } catch (err) {
      setError(err.response?.data?.error?.message || err.message || 'Unable to update subscription.');
    } finally {
      setSaving(false);
    }
  };

  const open = (type, row) => {
    setPlanId(plans[0]?.id || row.subscription?.plan_id || '');
    setDays(type === 'trial' ? '15' : type === 'assign' ? '' : '30');
    setAction({ type, row });
  };

  return (
    <PageShell>
      {error ? <Alert severity="error">{error}</Alert> : null}
      {success ? <Alert severity="success">{success}</Alert> : null}

      <FilterBar
        actions={
          <Button type="submit" form="master-business-filters" variant="contained">
            Search
          </Button>
        }
      >
        <Stack
          component="form"
          id="master-business-filters"
          direction={{ xs: 'column', sm: 'row' }}
          spacing={2}
          onSubmit={onSearch}
          sx={{ width: '100%' }}
        >
          <FormControl sx={{ minWidth: 180 }}>
            <InputLabel id="biz-status">Status</InputLabel>
            <Select
              labelId="biz-status"
              label="Status"
              value={filters.status}
              onChange={(event) => setFilters((prev) => ({ ...prev, status: event.target.value }))}
            >
              {STATUS_OPTIONS.map((value) => (
                <MenuItem key={value || 'all'} value={value}>
                  {value || 'All'}
                </MenuItem>
              ))}
            </Select>
          </FormControl>
          <TextField
            label="Search"
            value={filters.q}
            onChange={(event) => setFilters((prev) => ({ ...prev, q: event.target.value }))}
            fullWidth
          />
        </Stack>
      </FilterBar>

      {loading ? (
        <Stack alignItems="center" py={6}>
          <CircularProgress size={28} />
        </Stack>
      ) : rows.length === 0 ? (
        <EmptyState title="No businesses" description="Approved businesses appear here." />
      ) : (
        <TableCard>
          <Table size="small">
            <TableHead>
              <TableRow>
                <TableCell>Business</TableCell>
                <TableCell>Plan</TableCell>
                <TableCell>Status</TableCell>
                <TableCell>Remaining</TableCell>
                <TableCell align="right">Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {rows.map((row) => {
                const sub = row.subscription;
                const status = sub?.status || 'NONE';
                return (
                  <TableRow key={row.id} hover>
                    <TableCell>
                      <TruncateText value={row.business_name || row.name} />
                    </TableCell>
                    <TableCell>
                      <TruncateText value={sub?.plan_name || '—'} />
                    </TableCell>
                    <TableCell>
                      <Chip
                        size="small"
                        color={statusColor(status)}
                        label={sub?.is_expiring && status === 'TRIAL' ? 'TRIAL (expiring)' : status}
                      />
                    </TableCell>
                    <TableCell>
                      {sub?.remaining_days == null
                        ? sub?.is_complimentary
                          ? 'No expiry'
                          : '—'
                        : `${sub.remaining_days} days`}
                    </TableCell>
                    <TableCell align="right">
                      <Button size="small" onClick={() => open('assign', row)}>
                        Assign
                      </Button>
                      <Button size="small" onClick={() => open('trial', row)}>
                        Trial
                      </Button>
                      <Button size="small" onClick={() => open('renew', row)}>
                        Renew
                      </Button>
                      <Button size="small" color="error" onClick={() => open('cancel', row)}>
                        Cancel
                      </Button>
                    </TableCell>
                  </TableRow>
                );
              })}
            </TableBody>
          </Table>
        </TableCard>
      )}

      <Dialog open={Boolean(action)} onClose={closeAction} maxWidth="xs" fullWidth>
        <DialogTitle>
          {action?.type === 'assign'
            ? 'Assign plan'
            : action?.type === 'trial'
              ? 'Start / extend trial'
              : action?.type === 'renew'
                ? 'Record manual renewal'
                : 'Cancel subscription?'}
        </DialogTitle>
        <DialogContent>
          <Stack spacing={2} sx={{ pt: 1 }}>
            <Typography variant="body2">
              {action?.row?.business_name}
              {action?.type === 'cancel'
                ? ' will lose billing access. Sign-in remains available.'
                : action?.type === 'renew'
                  ? ' — no payment gateway; this records a paid period you confirmed offline.'
                  : ''}
            </Typography>
            {action?.type === 'assign' || action?.type === 'renew' ? (
              <FormControl fullWidth>
                <InputLabel id="assign-plan">Plan</InputLabel>
                <Select
                  labelId="assign-plan"
                  label="Plan"
                  value={planId}
                  onChange={(event) => setPlanId(event.target.value)}
                >
                  {plans.map((plan) => (
                    <MenuItem key={plan.id} value={plan.id}>
                      {plan.name} · ₹{Number(plan.price).toLocaleString('en-IN')}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            ) : null}
            {action?.type && action.type !== 'cancel' ? (
              <TextField
                label={action.type === 'assign' ? 'Duration days (optional)' : 'Days'}
                type="number"
                value={days}
                onChange={(event) => setDays(event.target.value)}
                helperText={
                  action.type === 'assign'
                    ? 'Leave empty for complimentary access with no end date.'
                    : '1–365 days'
                }
              />
            ) : null}
          </Stack>
        </DialogContent>
        <DialogActions>
          <Button onClick={closeAction}>Back</Button>
          <Button
            variant="contained"
            color={action?.type === 'cancel' ? 'error' : 'primary'}
            onClick={onConfirm}
            disabled={saving}
          >
            Confirm
          </Button>
        </DialogActions>
      </Dialog>
    </PageShell>
  );
}
