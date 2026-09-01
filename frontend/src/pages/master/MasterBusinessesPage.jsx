import {
  Alert,
  Button,
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
import { useSearchParams } from 'react-router-dom';
import EmptyState from '../../components/EmptyState';
import FilterBar from '../../components/FilterBar';
import PageShell from '../../components/PageShell';
import PaginationBar from '../../components/PaginationBar';
import TableCard from '../../components/TableCard';
import TruncateText from '../../components/TruncateText';
import LoadingSkeleton from '../../components/ui/LoadingSkeleton';
import SearchInput from '../../components/ui/SearchInput';
import StatusBadge from '../../components/ui/StatusBadge';
import {
  activateBusiness,
  assignBusinessPlan,
  cancelBusinessSubscription,
  deactivateBusiness,
  extendBusinessTrial,
  listMasterBusinesses,
  listPlans,
  renewBusinessSubscription,
  suspendBusiness,
  unsuspendBusiness,
} from '../../services/masterService';

const STATUS_OPTIONS = ['', 'TRIAL', 'ACTIVE', 'EXPIRING', 'EXPIRED', 'CANCELLED', 'SUSPENDED', 'NONE'];
const ACCOUNT_OPTIONS = ['', 'ACTIVE', 'SUSPENDED'];

function parseChoice(value, allowed) {
  const next = (value || '').toUpperCase();
  return allowed.includes(next) ? next : '';
}

function filtersFromSearch(searchParams) {
  return {
    status: parseChoice(searchParams.get('status'), STATUS_OPTIONS),
    tenant_status: parseChoice(searchParams.get('tenant_status'), ACCOUNT_OPTIONS),
  };
}

function subscriptionVariant(status) {
  if (status === 'ACTIVE') return 'active';
  if (status === 'TRIAL' || status === 'EXPIRING') return 'pending';
  if (status === 'EXPIRED' || status === 'CANCELLED' || status === 'SUSPENDED') return 'cancelled';
  return 'info';
}

function actionTitle(type) {
  if (type === 'assign') return 'Assign plan';
  if (type === 'trial') return 'Start / extend trial';
  if (type === 'renew') return 'Record manual renewal';
  if (type === 'cancel') return 'Cancel subscription?';
  if (type === 'activate') return 'Activate business?';
  if (type === 'deactivate') return 'Deactivate business?';
  if (type === 'suspend') return 'Suspend billing access?';
  if (type === 'unsuspend') return 'Resume billing access?';
  return 'Confirm';
}

export default function MasterBusinessesPage() {
  const [searchParams, setSearchParams] = useSearchParams();
  const [rows, setRows] = useState([]);
  const [plans, setPlans] = useState([]);
  const [filters, setFilters] = useState(() => ({ ...filtersFromSearch(searchParams), q: '' }));
  const [page, setPage] = useState(1);
  const [meta, setMeta] = useState({ page: 1, per_page: 25, total: 0 });
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
      const params = { page, per_page: 25 };
      if (filters.status) params.status = filters.status;
      if (filters.tenant_status) params.tenant_status = filters.tenant_status;
      if (filters.q.trim()) params.q = filters.q.trim();
      const [businesses, planList] = await Promise.all([
        listMasterBusinesses(params),
        listPlans({ include_inactive: false }),
      ]);
      setRows(businesses.data || []);
      setMeta(businesses.meta || { page, per_page: 25, total: 0 });
      setPlans(planList.data || []);
    } catch (err) {
      setError(err.response?.data?.error?.message || 'Unable to load businesses.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    const next = filtersFromSearch(searchParams);
    setFilters((prev) => {
      if (prev.status === next.status && prev.tenant_status === next.tenant_status) return prev;
      return { ...prev, ...next };
    });
  }, [searchParams]);

  useEffect(() => {
    setLoading(true);
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [filters.status, filters.tenant_status, page]);

  const applyListFilters = (patch) => {
    const next = { ...filters, ...patch };
    setFilters(next);
    setPage(1);
    const params = {};
    if (next.status) params.status = next.status;
    if (next.tenant_status) params.tenant_status = next.tenant_status;
    setSearchParams(params, { replace: true });
  };

  const onSearch = (event) => {
    event.preventDefault();
    if (page !== 1) {
      setPage(1);
      return;
    }
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
      } else if (action.type === 'activate') {
        await activateBusiness(id);
        setSuccess('Business activated. Sign-in is allowed again.');
      } else if (action.type === 'deactivate') {
        await deactivateBusiness(id);
        setSuccess('Business deactivated. Data is retained; login is blocked.');
      } else if (action.type === 'suspend') {
        await suspendBusiness(id);
        setSuccess('Billing access suspended. Sign-in remains available.');
      } else if (action.type === 'unsuspend') {
        await unsuspendBusiness(id);
        setSuccess('Billing access resumed.');
      }
      closeAction();
      await load();
    } catch (err) {
      setError(err.response?.data?.error?.message || err.message || 'Unable to update business.');
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
          <FormControl sx={{ minWidth: 160 }}>
            <InputLabel id="biz-account">Account</InputLabel>
            <Select
              labelId="biz-account"
              label="Account"
              value={filters.tenant_status}
              onChange={(event) => applyListFilters({ tenant_status: event.target.value })}
            >
              <MenuItem value="">All</MenuItem>
              <MenuItem value="ACTIVE">Active</MenuItem>
              <MenuItem value="SUSPENDED">Deactivated</MenuItem>
            </Select>
          </FormControl>
          <FormControl sx={{ minWidth: 180 }}>
            <InputLabel id="biz-status">Subscription</InputLabel>
            <Select
              labelId="biz-status"
              label="Subscription"
              value={filters.status}
              onChange={(event) => applyListFilters({ status: event.target.value })}
            >
              {STATUS_OPTIONS.map((value) => (
                <MenuItem key={value || 'all'} value={value}>
                  {value || 'All'}
                </MenuItem>
              ))}
            </Select>
          </FormControl>
          <SearchInput
            label="Search"
            placeholder="Search businesses…"
            value={filters.q}
            onChange={(event) => setFilters((prev) => ({ ...prev, q: event.target.value }))}
          />
        </Stack>
      </FilterBar>

      {loading ? (
        <LoadingSkeleton rows={6} height={56} />
      ) : rows.length === 0 ? (
        <EmptyState title="No businesses" description="Approved businesses appear here." />
      ) : (
        <TableCard>
          <Table size="small">
            <TableHead>
              <TableRow>
                <TableCell>Business</TableCell>
                <TableCell>Plan</TableCell>
                <TableCell>Account</TableCell>
                <TableCell>Subscription</TableCell>
                <TableCell>Remaining</TableCell>
                <TableCell align="right">Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {rows.map((row) => {
                const sub = row.subscription;
                const status = sub?.status || 'NONE';
                const tenantStatus = row.tenant_status || 'ACTIVE';
                return (
                  <TableRow key={row.id} hover>
                    <TableCell>
                      <TruncateText value={row.business_name || row.name} />
                    </TableCell>
                    <TableCell>
                      <TruncateText value={sub?.plan_name || '—'} />
                    </TableCell>
                    <TableCell>
                      <StatusBadge
                        label={tenantStatus === 'ACTIVE' ? 'Active' : 'Deactivated'}
                        variant={tenantStatus === 'ACTIVE' ? 'active' : 'cancelled'}
                      />
                    </TableCell>
                    <TableCell>
                      <StatusBadge
                        label={sub?.is_expiring && status === 'TRIAL' ? 'TRIAL (expiring)' : status}
                        variant={subscriptionVariant(status)}
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
                      <Stack direction="row" spacing={0.5} justifyContent="flex-end" flexWrap="wrap" useFlexGap>
                        {tenantStatus === 'ACTIVE' ? (
                          <Button size="small" color="warning" onClick={() => open('deactivate', row)}>
                            Deactivate
                          </Button>
                        ) : (
                          <Button size="small" onClick={() => open('activate', row)}>
                            Activate
                          </Button>
                        )}
                        {status === 'SUSPENDED' ? (
                          <Button size="small" onClick={() => open('unsuspend', row)}>
                            Resume
                          </Button>
                        ) : (
                          <Button
                            size="small"
                            color="warning"
                            disabled={!sub}
                            onClick={() => open('suspend', row)}
                          >
                            Suspend
                          </Button>
                        )}
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
                      </Stack>
                    </TableCell>
                  </TableRow>
                );
              })}
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

      <Dialog open={Boolean(action)} onClose={closeAction} maxWidth="xs" fullWidth>
        <DialogTitle>{actionTitle(action?.type)}</DialogTitle>
        <DialogContent>
          <Stack spacing={2} sx={{ pt: 1 }}>
            <Typography variant="body2">
              {action?.row?.business_name}
              {action?.type === 'cancel'
                ? ' will lose billing access. Sign-in remains available. Data is not deleted.'
                : action?.type === 'renew'
                  ? ' — no payment gateway; this records a paid period you confirmed offline.'
                  : action?.type === 'deactivate'
                    ? ' will be deactivated. Login is blocked. Bills, items, and users are kept.'
                    : action?.type === 'activate'
                      ? ' will be activated. The owner can sign in again.'
                      : action?.type === 'suspend'
                        ? ' can still sign in, but billing is locked until you resume it.'
                        : action?.type === 'unsuspend'
                          ? ' will regain billing access if the subscription period is still valid.'
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
            {action?.type && ['assign', 'trial', 'renew'].includes(action.type) ? (
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
            color={
              action?.type === 'cancel' || action?.type === 'deactivate' || action?.type === 'suspend'
                ? 'error'
                : 'primary'
            }
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
