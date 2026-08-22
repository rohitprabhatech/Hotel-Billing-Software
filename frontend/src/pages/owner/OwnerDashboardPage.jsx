import StorefrontOutlinedIcon from '@mui/icons-material/StorefrontOutlined';
import {
  Alert,
  Box,
  Button,
  Card,
  CardContent,
  Chip,
  CircularProgress,
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
  Tooltip,
  Typography,
} from '@mui/material';
import { useTheme } from '@mui/material/styles';
import { useEffect, useState } from 'react';
import { Link as RouterLink } from 'react-router-dom';
import {
  Bar,
  BarChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip as ChartTooltip,
  XAxis,
  YAxis,
} from 'recharts';
import EmptyState from '../../components/EmptyState';
import KpiCard from '../../components/KpiCard';
import PageShell from '../../components/PageShell';
import Section from '../../components/Section';
import TableCard from '../../components/TableCard';
import TruncateText from '../../components/TruncateText';
import { useAuth } from '../../context/AuthContext';
import { PATHS } from '../../routes/paths';
import { fetchAuditAlerts, listAuditLogs } from '../../services/auditService';
import { listBills } from '../../services/billService';
import { listNotifications } from '../../services/notificationService';
import { fetchReportSummary } from '../../services/reportService';
import { paymentMethodLabel } from '../../utils/paymentMethod';
import { RestaurantDashboardWidgets } from '../modules/MenuPage';

const STOCK_ALERT_TYPES = new Set(['LOW_STOCK', 'OUT_OF_STOCK']);
const WA_FAILED_TYPE = 'WHATSAPP_DELIVERY_FAILED';
const EMAIL_FAILED_TYPE = 'EMAIL_DELIVERY_FAILED';

function money(v) {
  return `₹${Number(v || 0).toLocaleString('en-IN', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  })}`;
}

const PERIOD_HINTS = {
  today: "Today's business overview",
  yesterday: "Yesterday's business overview",
  this_week: "This week's business overview",
  this_month: "This month's business overview",
  last_month: "Last month's business overview",
};

export default function OwnerDashboardPage() {
  const theme = useTheme();
  const { user } = useAuth();
  const businessName = user?.tenant?.business_name || user?.tenant?.name || 'Your Business';
  const businessTypeLabel = user?.tenant?.business_type_label || null;
  const [period, setPeriod] = useState('today');
  const [data, setData] = useState(null);
  const [alerts, setAlerts] = useState([]);
  const [stockAlerts, setStockAlerts] = useState([]);
  const [waFailedAlerts, setWaFailedAlerts] = useState([]);
  const [emailFailedAlerts, setEmailFailedAlerts] = useState([]);
  const [itemActivity, setItemActivity] = useState([]);
  const [recentBills, setRecentBills] = useState([]);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let active = true;
    setError('');
    setLoading(true);
    Promise.all([
      fetchReportSummary({ period }),
      fetchAuditAlerts(),
      listAuditLogs({ entity_type: 'ITEM', per_page: 6 }),
      listBills({ per_page: 8 }),
      listNotifications({ unread_only: true, per_page: 20 }),
    ])
      .then(([summaryRes, alertsRes, itemRes, billsRes, notifRes]) => {
        if (!active) return;
        setData(summaryRes.data);
        setAlerts((alertsRes.data?.alerts || []).filter((a) => a.severity !== 'info'));
        setItemActivity(itemRes.data || []);
        setRecentBills(billsRes.data || []);
        const stock = (notifRes.data || []).filter((n) => STOCK_ALERT_TYPES.has(n.type));
        setStockAlerts(stock);
        setWaFailedAlerts(
          (notifRes.data || []).filter((n) => n.type === WA_FAILED_TYPE),
        );
        setEmailFailedAlerts(
          (notifRes.data || []).filter((n) => n.type === EMAIL_FAILED_TYPE),
        );
      })
      .catch((err) => {
        if (!active) return;
        setError(err.response?.data?.error?.message || 'Unable to load dashboard.');
      })
      .finally(() => {
        if (active) setLoading(false);
      });
    return () => {
      active = false;
    };
  }, [period]);

  const current = data?.current || {};
  const previous = data?.previous || {};

  return (
    <PageShell>
      {user?.tenant?.subscription?.status === 'TRIAL' ? (
        <Alert severity="info" sx={{ mb: 2 }}>
          Free trial: {user.tenant.subscription.remaining_days ?? '—'} day
          {user.tenant.subscription.remaining_days === 1 ? '' : 's'} remaining
          {user.tenant.subscription.trial_ends_at
            ? ` (until ${new Date(user.tenant.subscription.trial_ends_at).toLocaleDateString()}).`
            : '.'}
        </Alert>
      ) : null}
      {user?.tenant?.subscription?.is_expiring && user?.tenant?.subscription?.status !== 'TRIAL' ? (
        <Alert severity="warning" sx={{ mb: 2 }}>
          Subscription expiring: {user.tenant.subscription.remaining_days ?? '—'} day
          {user.tenant.subscription.remaining_days === 1 ? '' : 's'} remaining. Contact Prabha
          Technology to renew.
        </Alert>
      ) : null}
      <Card>
        <CardContent
          sx={{
            p: { xs: 2.5, sm: 3 },
            '&:last-child': { pb: { xs: 2.5, sm: 3 } },
            display: 'flex',
            flexDirection: { xs: 'column', sm: 'row' },
            alignItems: { xs: 'stretch', sm: 'center' },
            justifyContent: 'space-between',
            gap: 2.5,
          }}
        >
          <Stack direction="row" spacing={2} alignItems="center" sx={{ minWidth: 0 }}>
            <Box
              sx={{
                width: 48,
                height: 48,
                borderRadius: 2,
                bgcolor: 'primary.main',
                color: 'primary.contrastText',
                display: 'grid',
                placeItems: 'center',
                flexShrink: 0,
              }}
            >
              <StorefrontOutlinedIcon />
            </Box>
            <Box sx={{ minWidth: 0 }}>
              <Tooltip title={businessName}>
                <Typography
                  variant="h5"
                  component="h1"
                  noWrap
                  sx={{ fontSize: { xs: '1.35rem', md: '1.5rem' } }}
                >
                  {businessName}
                </Typography>
              </Tooltip>
              <Stack direction="row" spacing={1} alignItems="center" sx={{ mt: 0.75 }} useFlexGap flexWrap="wrap">
                {businessTypeLabel ? (
                  <Chip label={businessTypeLabel} size="small" color="primary" variant="outlined" />
                ) : null}
                <Typography variant="subtitle2" color="text.secondary">
                  Business Dashboard
                </Typography>
              </Stack>
              <Typography variant="body2" color="text.secondary" sx={{ mt: 0.5 }}>
                {PERIOD_HINTS[period] || data?.label || 'Business overview'}
              </Typography>
            </Box>
          </Stack>
          <FormControl size="small" sx={{ width: { xs: '100%', sm: 180 }, alignSelf: { xs: 'stretch', sm: 'center' } }}>
            <InputLabel>Period</InputLabel>
            <Select
              label="Period"
              value={period}
              onChange={(e) => setPeriod(e.target.value)}
            >
              <MenuItem value="today">Today</MenuItem>
              <MenuItem value="yesterday">Yesterday</MenuItem>
              <MenuItem value="this_week">This Week</MenuItem>
              <MenuItem value="this_month">This Month</MenuItem>
              <MenuItem value="last_month">Last Month</MenuItem>
            </Select>
          </FormControl>
        </CardContent>
      </Card>

      {error ? <Alert severity="error">{error}</Alert> : null}
      <RestaurantDashboardWidgets />
      <Alert severity="info">
        Sales totals include finalized bills only. Cancelled bills are shown separately.
      </Alert>
      {stockAlerts.length > 0 ? (
        <Alert
          severity={stockAlerts.some((n) => n.type === 'OUT_OF_STOCK') ? 'error' : 'warning'}
          action={
            <Button
              color="inherit"
              size="small"
              component={RouterLink}
              to={`${PATHS.ownerItems}?stock_status=${
                stockAlerts.some((n) => n.type === 'OUT_OF_STOCK') ? 'out' : 'low'
              }`}
            >
              View items
            </Button>
          }
        >
          <strong>Stock alerts:</strong>{' '}
          {(() => {
            const out = stockAlerts.filter((n) => n.type === 'OUT_OF_STOCK').length;
            const low = stockAlerts.filter((n) => n.type === 'LOW_STOCK').length;
            const parts = [];
            if (out) parts.push(`${out} out of stock`);
            if (low) parts.push(`${low} low stock`);
            return `${parts.join(', ')}. Check the notification bell for details.`;
          })()}
        </Alert>
      ) : null}
      {waFailedAlerts.length > 0 ? (
        <Alert
          severity="error"
          action={
            <Button
              color="inherit"
              size="small"
              component={RouterLink}
              to={`${PATHS.ownerBills}?whatsapp_status=FAILED`}
            >
              View failed
            </Button>
          }
        >
          <strong>WhatsApp delivery:</strong> {waFailedAlerts.length} failed delivery
          {waFailedAlerts.length === 1 ? '' : 's'} need attention. Open Bills to retry.
        </Alert>
      ) : null}
      {emailFailedAlerts.length > 0 ? (
        <Alert
          severity="error"
          action={
            <Button
              color="inherit"
              size="small"
              component={RouterLink}
              to={`${PATHS.ownerBills}?email_status=FAILED`}
            >
              View failed
            </Button>
          }
        >
          <strong>Email delivery:</strong> {emailFailedAlerts.length} failed email
          {emailFailedAlerts.length === 1 ? '' : 's'} need attention. Open Bills to retry.
        </Alert>
      ) : null}
      {alerts.slice(0, 3).map((alert) => (
        <Alert
          key={`${alert.type}-${alert.message}`}
          severity={alert.severity === 'medium' ? 'warning' : 'info'}
        >
          <strong>{alert.title}:</strong> {alert.message}
        </Alert>
      ))}

      <Section
        title={period === 'today' ? "Today's Overview" : `${data?.label || 'Period'} Overview`}
        actions={loading ? <CircularProgress size={18} /> : null}
      >
        <Box
          sx={{
            display: 'grid',
            gap: 2.5,
            gridTemplateColumns: { xs: '1fr', sm: '1fr 1fr', lg: 'repeat(3, 1fr)' },
          }}
        >
          <KpiCard
            title="Sales"
            value={money(current.total_sales)}
            hint={data?.previous_label ? `${data.previous_label}: ${money(previous.total_sales)}` : undefined}
          />
          <KpiCard
            title="Bills"
            value={current.bill_count ?? '—'}
            hint={data?.previous_label ? `${data.previous_label}: ${previous.bill_count ?? '—'}` : undefined}
          />
          <KpiCard
            title="Average Bill"
            value={money(current.average_bill)}
            hint={data?.previous_label ? `${data.previous_label}: ${money(previous.average_bill)}` : undefined}
          />
          <KpiCard
            title="Cash"
            value={money(current.cash_sales)}
            hint={`${current.cash_bill_count ?? 0} cash bills`}
          />
          <KpiCard
            title="Online"
            value={money(current.online_sales)}
            hint={`${current.online_bill_count ?? 0} online bills`}
          />
          <KpiCard
            title="Cancelled"
            value={current.cancelled_bills ?? '—'}
            hint="Excluded from sales totals"
          />
        </Box>
      </Section>

      {data?.whatsapp_delivery ? (
        <Section title="WhatsApp Delivery">
          <Stack direction="row" flexWrap="wrap" useFlexGap spacing={1} sx={{ mb: 1.5 }}>
            {[
              { key: 'sent', label: 'Sent', status: 'SENT' },
              { key: 'delivered', label: 'Delivered', status: 'DELIVERED' },
              { key: 'read', label: 'Read', status: 'READ' },
              { key: 'failed', label: 'Failed', status: 'FAILED', color: 'error' },
              { key: 'pending', label: 'Pending', status: 'PENDING' },
            ].map((item) => (
              <Chip
                key={item.key}
                component={RouterLink}
                to={`${PATHS.ownerBills}?whatsapp_status=${item.status}`}
                clickable
                color={item.color || 'default'}
                variant={item.color ? 'filled' : 'outlined'}
                label={`${item.label}: ${data.whatsapp_delivery[item.key] ?? 0}`}
              />
            ))}
          </Stack>
          <Typography variant="body2" color="text.secondary">
            {data.whatsapp_delivery.total
              ? `Success rate (delivered + read): ${
                  data.whatsapp_delivery.success_rate ?? 0
                }% of ${data.whatsapp_delivery.total} bill${
                  data.whatsapp_delivery.total === 1 ? '' : 's'
                } with WhatsApp in this period.`
              : 'No WhatsApp bill deliveries in this period.'}
          </Typography>
        </Section>
      ) : null}

      {data?.email_delivery ? (
        <Section title="Email Delivery">
          <Stack direction="row" flexWrap="wrap" useFlexGap spacing={1} sx={{ mb: 1.5 }}>
            {[
              { key: 'sent', label: 'Sent', status: 'SENT' },
              { key: 'failed', label: 'Failed', status: 'FAILED', color: 'error' },
              { key: 'pending', label: 'Pending', status: 'PENDING' },
            ].map((item) => (
              <Chip
                key={item.key}
                component={RouterLink}
                to={`${PATHS.ownerBills}?email_status=${item.status}`}
                clickable
                color={item.color || 'default'}
                variant={item.color ? 'filled' : 'outlined'}
                label={`${item.label}: ${data.email_delivery[item.key] ?? 0}`}
              />
            ))}
          </Stack>
          <Typography variant="body2" color="text.secondary">
            {data.email_delivery.total
              ? `Success rate (sent): ${data.email_delivery.success_rate ?? 0}% of ${
                  data.email_delivery.total
                } bill${data.email_delivery.total === 1 ? '' : 's'} emailed in this period.`
              : 'No email bill deliveries in this period.'}
          </Typography>
        </Section>
      ) : null}

      {data?.inventory_health ? (
        <Section
          title="Inventory Health"
          actions={
            <Button component={RouterLink} to={PATHS.ownerStockMovements} size="small">
              Stock movements
            </Button>
          }
        >
          <Stack direction="row" flexWrap="wrap" useFlexGap spacing={1} sx={{ mb: 1.5 }}>
            <Chip
              component={RouterLink}
              to={`${PATHS.ownerItems}?stock_status=tracked`}
              clickable
              variant="outlined"
              label={`Tracked: ${data.inventory_health.tracked ?? 0}`}
            />
            <Chip
              component={RouterLink}
              to={`${PATHS.ownerItems}?stock_status=low`}
              clickable
              color="warning"
              variant={data.inventory_health.low ? 'filled' : 'outlined'}
              label={`Low: ${data.inventory_health.low ?? 0}`}
            />
            <Chip
              component={RouterLink}
              to={`${PATHS.ownerItems}?stock_status=out`}
              clickable
              color="error"
              variant={data.inventory_health.out ? 'filled' : 'outlined'}
              label={`Out: ${data.inventory_health.out ?? 0}`}
            />
            <Chip
              component={RouterLink}
              to={PATHS.ownerItems}
              clickable
              variant="outlined"
              label={`Untracked: ${data.inventory_health.untracked ?? 0}`}
            />
          </Stack>
          <Typography variant="body2" color="text.secondary">
            Point-in-time catalog stock status ({data.inventory_health.total_items ?? 0} items).
            Use Receive stock on Items to restock or start tracking.
          </Typography>
        </Section>
      ) : null}

      <Section title="Sales Overview">
        <Card>
          <CardContent sx={{ p: { xs: 2, sm: 3 }, '&:last-child': { pb: { xs: 2, sm: 3 } } }}>
            <Box sx={{ width: '100%', height: 300 }}>
              {(data?.day_wise || []).length ? (
                <ResponsiveContainer>
                  <BarChart data={data.day_wise}>
                    <CartesianGrid strokeDasharray="3 3" vertical={false} stroke={theme.palette.divider} />
                    <XAxis
                      dataKey="date"
                      tick={{ fill: theme.palette.text.secondary, fontSize: 11 }}
                      interval="preserveStartEnd"
                    />
                    <YAxis
                      width={48}
                      tick={{ fill: theme.palette.text.secondary, fontSize: 11 }}
                    />
                    <ChartTooltip />
                    <Bar dataKey="total_sales" fill={theme.palette.primary.main} name="Sales" radius={[4, 4, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              ) : (
                <EmptyState title="No sales data" description="Sales for this period will appear here." />
              )}
            </Box>
          </CardContent>
        </Card>
      </Section>

      <Section
        title="Recent Bills"
        actions={
          <Button component={RouterLink} to={PATHS.ownerBills} size="small">
            View all
          </Button>
        }
      >
        <TableCard>
          <Table size="small" sx={{ minWidth: 640 }}>
            <TableHead>
              <TableRow>
                <TableCell>Bill No.</TableCell>
                <TableCell>Date & Time</TableCell>
                <TableCell>Status</TableCell>
                <TableCell>Payment</TableCell>
                <TableCell align="right">Total</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {recentBills.map((bill) => (
                <TableRow key={bill.id} hover>
                  <TableCell>
                    <TruncateText value={bill.bill_number || bill.id} maxWidth={140} />
                  </TableCell>
                  <TableCell>
                    <Typography variant="body2" color="text.secondary" sx={{ whiteSpace: 'nowrap' }}>
                      {bill.created_at ? new Date(bill.created_at).toLocaleString() : '—'}
                    </Typography>
                  </TableCell>
                  <TableCell>
                    <Chip
                      size="small"
                      label={bill.status === 'CANCELLED' ? 'Cancelled' : 'Finalized'}
                      color={bill.status === 'CANCELLED' ? 'warning' : 'success'}
                      variant={bill.status === 'CANCELLED' ? 'filled' : 'outlined'}
                    />
                  </TableCell>
                  <TableCell>
                    {paymentMethodLabel(bill.payment_method)}
                  </TableCell>
                  <TableCell align="right" sx={{ fontVariantNumeric: 'tabular-nums' }}>
                    {money(bill.grand_total)}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
          {!recentBills.length ? (
            <EmptyState title="No bills yet" description="Generated bills will appear here." />
          ) : null}
        </TableCard>
      </Section>

      <Section
        title="Recent Item Activity"
        actions={
          <Button component={RouterLink} to={PATHS.ownerItemActivity} size="small">
            View all
          </Button>
        }
      >
        <TableCard>
          <Table size="small" sx={{ minWidth: 640 }}>
            <TableHead>
              <TableRow>
                <TableCell>Action</TableCell>
                <TableCell>Item</TableCell>
                <TableCell>User</TableCell>
                <TableCell>When</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {(itemActivity || []).slice(0, 5).map((log) => (
                <TableRow key={log.id} hover>
                  <TableCell>
                    <Chip size="small" label={log.action} variant="outlined" />
                  </TableCell>
                  <TableCell>
                    <TruncateText
                      value={log.new_data?.name || log.old_data?.name || 'Item'}
                      maxWidth={180}
                    />
                  </TableCell>
                  <TableCell>
                    <TruncateText value={log.user_name || 'User'} maxWidth={140} />
                  </TableCell>
                  <TableCell>
                    <Typography variant="body2" color="text.secondary" sx={{ whiteSpace: 'nowrap' }}>
                      {log.created_at ? new Date(log.created_at).toLocaleString() : '—'}
                    </Typography>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
          {!itemActivity.length ? (
            <EmptyState
              title="No item activity yet"
              description="Create or update catalog items to see activity here."
            />
          ) : null}
        </TableCard>
      </Section>
    </PageShell>
  );
}
