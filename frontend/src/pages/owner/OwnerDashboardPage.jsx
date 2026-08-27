import DeleteOutlineOutlinedIcon from '@mui/icons-material/DeleteOutlineOutlined';
import StorefrontOutlinedIcon from '@mui/icons-material/StorefrontOutlined';
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
import { useTheme } from '@mui/material/styles';
import { useCallback, useEffect, useMemo, useState } from 'react';
import { Link as RouterLink } from 'react-router-dom';
import {
  Bar,
  BarChart,
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip as ChartTooltip,
  XAxis,
  YAxis,
} from 'recharts';
import EmptyState from '../../components/EmptyState';
import IndustryDashboardPanel from '../../components/IndustryDashboardPanel';
import KpiCard from '../../components/KpiCard';
import PageShell from '../../components/PageShell';
import Section from '../../components/Section';
import TableCard from '../../components/TableCard';
import TruncateText from '../../components/TruncateText';
import { useAuth } from '../../context/AuthContext';
import { PATHS } from '../../routes/paths';
import { fetchAuditAlerts, listAuditLogs } from '../../services/auditService';
import { cancelBill, listBills } from '../../services/billService';
import { listNotifications } from '../../services/notificationService';
import { fetchReportSummary } from '../../services/reportService';
import { listTables } from '../../services/tableService';
import { paymentMethodLabel } from '../../utils/paymentMethod';
import { RestaurantDashboardWidgets } from '../modules/MenuPage';

const STOCK_ALERT_TYPES = new Set(['LOW_STOCK', 'OUT_OF_STOCK']);
const WA_FAILED_TYPE = 'WHATSAPP_DELIVERY_FAILED';
const EMAIL_FAILED_TYPE = 'EMAIL_DELIVERY_FAILED';

const PERIOD_HINTS = {
  today: "Today's business overview",
  yesterday: "Yesterday's business overview",
  this_week: "This week's business overview",
  this_month: "This month's business overview",
  last_month: "Last month's business overview",
  last_7_days: 'Last 7 days business overview',
  last_30_days: 'Last 30 days business overview',
  this_year: "This year's business overview",
};

function money(v) {
  return `₹${Number(v || 0).toLocaleString('en-IN', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  })}`;
}

function moneyAxis(v) {
  return `₹${Number(v || 0).toLocaleString('en-IN', { maximumFractionDigits: 0 })}`;
}

function billTableLabel(bill) {
  return bill?.dining_table_code || bill?.table_number || bill?.reference || '—';
}

function hotelBillStatus(bill) {
  if (bill?.status === 'FINALIZED') {
    return { label: 'Paid', color: 'success', variant: 'outlined' };
  }
  if (bill?.status === 'CANCELLED') {
    return { label: 'Cancelled', color: 'warning', variant: 'filled' };
  }
  return { label: 'Pending', color: 'default', variant: 'outlined' };
}

function formatDayLabel(dateStr, useWeekday) {
  if (!dateStr) return '';
  const parsed = new Date(`${dateStr}T12:00:00`);
  if (Number.isNaN(parsed.getTime())) return dateStr;
  if (useWeekday) {
    return parsed.toLocaleDateString('en-IN', { weekday: 'short' });
  }
  return parsed.toLocaleDateString('en-IN', { day: 'numeric', month: 'short' });
}

function SalesChartTooltip({ active, payload }) {
  if (!active || !payload?.length) return null;
  const row = payload[0]?.payload || {};
  return (
    <Box
      sx={{
        bgcolor: 'background.paper',
        p: 1.25,
        border: 1,
        borderColor: 'divider',
        borderRadius: 1,
        boxShadow: 1,
      }}
    >
      <Typography variant="caption" color="text.secondary" display="block">
        {row.date || row.label}
      </Typography>
      <Typography variant="body2">Sales: {money(row.total_sales)}</Typography>
      {row.bill_count != null ? (
        <Typography variant="body2">Bills: {row.bill_count}</Typography>
      ) : null}
    </Box>
  );
}

function PeriodSelect({ period, onChange, isHotel, sx }) {
  return (
    <FormControl size="small" sx={{ width: { xs: '100%', sm: 180 }, ...sx }}>
      <InputLabel>Period</InputLabel>
      <Select label="Period" value={period} onChange={(e) => onChange(e.target.value)}>
        {isHotel ? (
          <>
            <MenuItem value="today">Today</MenuItem>
            <MenuItem value="last_7_days">Last 7 Days</MenuItem>
            <MenuItem value="last_30_days">Last 30 Days</MenuItem>
            <MenuItem value="this_month">This Month</MenuItem>
            <MenuItem value="last_month">Last Month</MenuItem>
            <MenuItem value="this_year">This Year</MenuItem>
          </>
        ) : (
          <>
            <MenuItem value="today">Today</MenuItem>
            <MenuItem value="yesterday">Yesterday</MenuItem>
            <MenuItem value="this_week">This Week</MenuItem>
            <MenuItem value="this_month">This Month</MenuItem>
            <MenuItem value="last_month">Last Month</MenuItem>
          </>
        )}
      </Select>
    </FormControl>
  );
}

export default function OwnerDashboardPage() {
  const theme = useTheme();
  const { user } = useAuth();
  const isHotel = user?.tenant?.business_type === 'hotel_restaurant';
  const businessName = user?.tenant?.business_name || user?.tenant?.name || 'Your Business';
  const businessTypeLabel = user?.tenant?.business_type_label || null;
  const [period, setPeriod] = useState('today');
  const [defaultPeriodSet, setDefaultPeriodSet] = useState(false);
  const [data, setData] = useState(null);
  const [alerts, setAlerts] = useState([]);
  const [stockAlerts, setStockAlerts] = useState([]);
  const [waFailedAlerts, setWaFailedAlerts] = useState([]);
  const [emailFailedAlerts, setEmailFailedAlerts] = useState([]);
  const [itemActivity, setItemActivity] = useState([]);
  const [recentBills, setRecentBills] = useState([]);
  const [tables, setTables] = useState([]);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(true);
  const [cancelTarget, setCancelTarget] = useState(null);
  const [cancelReason, setCancelReason] = useState('Removed from owner dashboard');
  const [cancelSaving, setCancelSaving] = useState(false);

  useEffect(() => {
    if (!defaultPeriodSet && user?.tenant?.business_type) {
      setPeriod(user.tenant.business_type === 'hotel_restaurant' ? 'last_7_days' : 'today');
      setDefaultPeriodSet(true);
    }
  }, [user?.tenant?.business_type, defaultPeriodSet]);

  const loadDashboard = useCallback(async () => {
    setError('');
    setLoading(true);
    try {
      const tasks = [
        fetchReportSummary({ period }),
        fetchAuditAlerts(),
        listAuditLogs({ entity_type: 'ITEM', per_page: 6 }),
        listBills({ per_page: 8 }),
        listNotifications({ unread_only: true, per_page: 20 }),
      ];
      if (isHotel) {
        tasks.push(listTables().catch(() => ({ data: [] })));
      }
      const results = await Promise.all(tasks);
      const [
        summaryRes,
        alertsRes,
        itemRes,
        billsRes,
        notifRes,
        tablesRes,
      ] = results;

      setData(summaryRes.data);
      setAlerts((alertsRes.data?.alerts || []).filter((a) => a.severity !== 'info'));
      setItemActivity(itemRes.data || []);
      setRecentBills(billsRes.data || []);
      const stock = (notifRes.data || []).filter((n) => STOCK_ALERT_TYPES.has(n.type));
      setStockAlerts(stock);
      setWaFailedAlerts((notifRes.data || []).filter((n) => n.type === WA_FAILED_TYPE));
      setEmailFailedAlerts((notifRes.data || []).filter((n) => n.type === EMAIL_FAILED_TYPE));
      if (isHotel) {
        setTables(tablesRes?.data || []);
      }
    } catch (err) {
      setError(err.response?.data?.error?.message || 'Unable to load dashboard.');
    } finally {
      setLoading(false);
    }
  }, [period, isHotel]);

  useEffect(() => {
    loadDashboard();
  }, [loadDashboard]);

  const tableStats = useMemo(() => {
    let activeTables = 0;
    let pendingBills = 0;
    tables.forEach((table) => {
      if (table.status === 'occupied' || table.status === 'bill_pending') {
        activeTables += 1;
      }
      if (table.status === 'bill_pending') {
        pendingBills += 1;
      }
    });
    return { activeTables, pendingBills };
  }, [tables]);

  const current = data?.current || {};
  const previous = data?.previous || {};
  const periodLabel = data?.label || PERIOD_HINTS[period] || 'Period';

  const salesChangeHint = useMemo(() => {
    if (!isHotel || !(previous.total_sales > 0)) return undefined;
    const change =
      ((Number(current.total_sales || 0) - Number(previous.total_sales || 0)) /
        Number(previous.total_sales)) *
      100;
    const arrow = change >= 0 ? '↑' : '↓';
    return `${arrow} ${Math.abs(change).toFixed(1)}% vs ${data?.previous_label || 'previous'}`;
  }, [isHotel, current.total_sales, previous.total_sales, data?.previous_label]);

  const chartData = useMemo(() => {
    const rows = data?.day_wise || [];
    const useWeekday = rows.length <= 14;
    return rows.map((row) => ({
      ...row,
      label: formatDayLabel(row.date, useWeekday),
    }));
  }, [data?.day_wise]);

  const onConfirmCancel = async () => {
    if (!cancelTarget) return;
    setCancelSaving(true);
    setError('');
    try {
      await cancelBill(cancelTarget.id, cancelReason.trim() || 'Removed from owner dashboard');
      setCancelTarget(null);
      setCancelReason('Removed from owner dashboard');
      await loadDashboard();
    } catch (err) {
      setError(err.response?.data?.error?.message || 'Failed to remove bill.');
    } finally {
      setCancelSaving(false);
    }
  };

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
          <PeriodSelect period={period} onChange={setPeriod} isHotel={isHotel} />
        </CardContent>
      </Card>

      {error ? <Alert severity="error">{error}</Alert> : null}
      <IndustryDashboardPanel />
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
        title={
          isHotel
            ? `${periodLabel} Overview`
            : period === 'today'
              ? "Today's Overview"
              : `${data?.label || 'Period'} Overview`
        }
        actions={loading ? <CircularProgress size={18} /> : null}
      >
        {isHotel ? (
          <Box
            sx={{
              display: 'grid',
              gap: 2.5,
              gridTemplateColumns: { xs: '1fr', sm: '1fr 1fr', lg: 'repeat(5, 1fr)' },
            }}
          >
            <KpiCard
              title={`Sales (${periodLabel})`}
              value={money(current.total_sales)}
              hint={
                salesChangeHint ||
                (period !== 'today'
                  ? `Totals for selected period (${periodLabel})`
                  : data?.previous_label
                    ? `${data.previous_label}: ${money(previous.total_sales)}`
                    : undefined)
              }
            />
            <KpiCard
              title="Bills"
              value={current.bill_count ?? '—'}
              hint={data?.previous_label ? `${data.previous_label}: ${previous.bill_count ?? '—'}` : undefined}
            />
            <KpiCard
              title="Average Bill"
              value={money(current.average_bill)}
              hint={
                data?.previous_label ? `${data.previous_label}: ${money(previous.average_bill)}` : undefined
              }
            />
            <KpiCard title="Active Tables" value={tableStats.activeTables} hint="Occupied + bill pending" />
            <KpiCard title="Pending Bills" value={tableStats.pendingBills} hint="Tables awaiting settlement" />
          </Box>
        ) : (
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
              hint={
                data?.previous_label ? `${data.previous_label}: ${money(previous.average_bill)}` : undefined
              }
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
              title="Credit"
              value={money(current.credit_sales)}
              hint={`${current.credit_bill_count ?? 0} udhari bills`}
            />
            <KpiCard
              title="Cancelled"
              value={current.cancelled_bills ?? '—'}
              hint="Excluded from sales totals"
            />
          </Box>
        )}
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

      {isHotel ? (
        <>
          <Section
            title="Sales Analytics"
            actions={<PeriodSelect period={period} onChange={setPeriod} isHotel={isHotel} sx={{ width: 180 }} />}
          >
            <Box
              sx={{
                display: 'grid',
                gap: 2.5,
                gridTemplateColumns: { xs: '1fr', lg: '1fr 1fr' },
              }}
            >
              <Card>
                <CardContent sx={{ p: { xs: 2, sm: 3 }, '&:last-child': { pb: { xs: 2, sm: 3 } } }}>
                  <Typography variant="subtitle2" sx={{ mb: 1.5 }}>
                    Sales Trend
                  </Typography>
                  <Box sx={{ width: '100%', height: 280 }}>
                    {chartData.length ? (
                      <ResponsiveContainer width="100%" height="100%">
                        <LineChart data={chartData}>
                          <CartesianGrid strokeDasharray="3 3" vertical={false} stroke={theme.palette.divider} />
                          <XAxis
                            dataKey="label"
                            tick={{ fill: theme.palette.text.secondary, fontSize: 11 }}
                            interval="preserveStartEnd"
                          />
                          <YAxis
                            width={56}
                            tick={{ fill: theme.palette.text.secondary, fontSize: 11 }}
                            tickFormatter={moneyAxis}
                          />
                          <ChartTooltip content={<SalesChartTooltip />} />
                          <Line
                            type="monotone"
                            dataKey="total_sales"
                            stroke={theme.palette.primary.main}
                            strokeWidth={2}
                            dot={{ r: 3, fill: theme.palette.primary.main }}
                            name="Sales"
                          />
                        </LineChart>
                      </ResponsiveContainer>
                    ) : (
                      <EmptyState title="No sales data" description="Sales for this period will appear here." />
                    )}
                  </Box>
                </CardContent>
              </Card>

              <Card>
                <CardContent sx={{ p: { xs: 2, sm: 3 }, '&:last-child': { pb: { xs: 2, sm: 3 } } }}>
                  <Typography variant="subtitle2" sx={{ mb: 1.5 }}>
                    Sales by Day
                  </Typography>
                  <Box sx={{ width: '100%', height: 280 }}>
                    {chartData.length ? (
                      <ResponsiveContainer width="100%" height="100%">
                        <BarChart data={chartData}>
                          <CartesianGrid strokeDasharray="3 3" vertical={false} stroke={theme.palette.divider} />
                          <XAxis
                            dataKey="label"
                            tick={{ fill: theme.palette.text.secondary, fontSize: 11 }}
                            interval="preserveStartEnd"
                          />
                          <YAxis
                            width={56}
                            tick={{ fill: theme.palette.text.secondary, fontSize: 11 }}
                            tickFormatter={moneyAxis}
                          />
                          <ChartTooltip content={<SalesChartTooltip />} />
                          <Bar
                            dataKey="total_sales"
                            fill={theme.palette.primary.main}
                            name="Sales"
                            radius={[4, 4, 0, 0]}
                          />
                        </BarChart>
                      </ResponsiveContainer>
                    ) : (
                      <EmptyState title="No sales data" description="Sales for this period will appear here." />
                    )}
                  </Box>
                </CardContent>
              </Card>
            </Box>
          </Section>

          <Section title="Top Selling Items">
            <TableCard>
              <Table size="small" sx={{ minWidth: 480 }}>
                <TableHead>
                  <TableRow>
                    <TableCell>Item</TableCell>
                    <TableCell align="right">Qty Sold</TableCell>
                    <TableCell align="right">Revenue</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {(data?.top_items || []).map((row) => (
                    <TableRow key={row.item_name || row.item_id} hover>
                      <TableCell>
                        <TruncateText value={row.item_name || 'Item'} maxWidth={280} />
                      </TableCell>
                      <TableCell align="right">{row.quantity ?? '—'}</TableCell>
                      <TableCell align="right">{money(row.revenue)}</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
              {!data?.top_items?.length ? (
                <EmptyState
                  title="No top items"
                  description="Item sales for this period will appear here."
                />
              ) : null}
            </TableCard>
          </Section>
        </>
      ) : (
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
      )}

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
                {isHotel ? <TableCell>Table</TableCell> : null}
                <TableCell>Status</TableCell>
                <TableCell>Payment</TableCell>
                <TableCell align="right">Total</TableCell>
                {isHotel ? <TableCell align="center">Action</TableCell> : null}
              </TableRow>
            </TableHead>
            <TableBody>
              {recentBills.map((bill) => {
                const statusProps = isHotel
                  ? hotelBillStatus(bill)
                  : {
                      label: bill.status === 'CANCELLED' ? 'Cancelled' : 'Finalized',
                      color: bill.status === 'CANCELLED' ? 'warning' : 'success',
                      variant: bill.status === 'CANCELLED' ? 'filled' : 'outlined',
                    };
                return (
                  <TableRow key={bill.id} hover>
                    <TableCell>
                      <TruncateText value={bill.bill_number || bill.id} maxWidth={140} />
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2" color="text.secondary" sx={{ whiteSpace: 'nowrap' }}>
                        {bill.created_at ? new Date(bill.created_at).toLocaleString() : '—'}
                      </Typography>
                    </TableCell>
                    {isHotel ? (
                      <TableCell>
                        <TruncateText value={billTableLabel(bill)} maxWidth={100} />
                      </TableCell>
                    ) : null}
                    <TableCell>
                      <Chip
                        size="small"
                        label={statusProps.label}
                        color={statusProps.color}
                        variant={statusProps.variant}
                      />
                    </TableCell>
                    <TableCell>{paymentMethodLabel(bill.payment_method)}</TableCell>
                    <TableCell align="right" sx={{ fontVariantNumeric: 'tabular-nums' }}>
                      {money(bill.grand_total)}
                    </TableCell>
                    {isHotel ? (
                      <TableCell align="center">
                        {bill.status === 'FINALIZED' ? (
                          <Tooltip title="Remove Bill">
                            <IconButton
                              size="small"
                              color="error"
                              onClick={() => {
                                setCancelTarget(bill);
                                setCancelReason('Removed from owner dashboard');
                              }}
                            >
                              <DeleteOutlineOutlinedIcon fontSize="small" />
                            </IconButton>
                          </Tooltip>
                        ) : (
                          '—'
                        )}
                      </TableCell>
                    ) : null}
                  </TableRow>
                );
              })}
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

      {isHotel ? (
        <Dialog
          open={Boolean(cancelTarget)}
          onClose={() => {
            if (cancelSaving) return;
            setCancelTarget(null);
          }}
          fullWidth
          maxWidth="sm"
        >
          <DialogTitle>Remove Bill?</DialogTitle>
          <DialogContent>
            <Stack spacing={2} sx={{ pt: 1 }}>
              <Typography variant="body2" color="text.secondary">
                Invoice: <strong>{cancelTarget?.bill_number || cancelTarget?.id}</strong>
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Amount: <strong>{money(cancelTarget?.grand_total)}</strong>
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Table: <strong>{billTableLabel(cancelTarget)}</strong>
              </Typography>
              <TextField
                label="Reason"
                value={cancelReason}
                onChange={(e) => setCancelReason(e.target.value)}
                fullWidth
                multiline
                minRows={2}
              />
            </Stack>
          </DialogContent>
          <DialogActions>
            <Button
              onClick={() => setCancelTarget(null)}
              disabled={cancelSaving}
            >
              Back
            </Button>
            <Button
              color="error"
              variant="contained"
              disabled={cancelSaving || !cancelReason.trim()}
              onClick={onConfirmCancel}
            >
              {cancelSaving ? 'Removing…' : 'Confirm'}
            </Button>
          </DialogActions>
        </Dialog>
      ) : null}
    </PageShell>
  );
}
