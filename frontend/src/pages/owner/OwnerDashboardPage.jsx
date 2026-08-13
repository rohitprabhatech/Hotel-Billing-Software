import StorefrontOutlinedIcon from '@mui/icons-material/StorefrontOutlined';
import {
  Alert,
  Box,
  Button,
  Card,
  CardContent,
  Chip,
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
import { fetchReportSummary } from '../../services/reportService';

function money(v) {
  return `₹${Number(v || 0).toLocaleString('en-IN', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  })}`;
}

export default function OwnerDashboardPage() {
  const { user } = useAuth();
  const hotelName = user?.tenant?.business_name || user?.tenant?.name || 'Your Hotel';
  const [period, setPeriod] = useState('today');
  const [data, setData] = useState(null);
  const [alerts, setAlerts] = useState([]);
  const [itemActivity, setItemActivity] = useState([]);
  const [recentBills, setRecentBills] = useState([]);
  const [error, setError] = useState('');

  useEffect(() => {
    setError('');
    Promise.all([
      fetchReportSummary({ period }),
      fetchAuditAlerts(),
      listAuditLogs({ entity_type: 'ITEM', per_page: 6 }),
      listBills({ per_page: 8 }),
    ])
      .then(([summaryRes, alertsRes, itemRes, billsRes]) => {
        setData(summaryRes.data);
        setAlerts((alertsRes.data?.alerts || []).filter((a) => a.severity !== 'info'));
        setItemActivity(itemRes.data || []);
        setRecentBills(billsRes.data || []);
      })
      .catch((err) => {
        setError(err.response?.data?.error?.message || 'Unable to load dashboard.');
      });
  }, [period]);

  const current = data?.current || {};
  const previous = data?.previous || {};

  return (
    <PageShell spacing={4}>
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
              <Tooltip title={hotelName}>
                <Typography
                  variant="h5"
                  component="h1"
                  noWrap
                  sx={{ fontSize: { xs: '1.35rem', md: '1.5rem' } }}
                >
                  {hotelName}
                </Typography>
              </Tooltip>
              <Typography variant="subtitle1" sx={{ mt: 0.25 }}>
                Owner Dashboard
              </Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mt: 0.5 }}>
                Today&apos;s business overview
              </Typography>
            </Box>
          </Stack>
          <FormControl size="small" sx={{ minWidth: 180, alignSelf: { xs: 'stretch', sm: 'center' } }}>
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
      <Alert severity="info">
        Sales totals include FINALIZED bills only. Cancelled bills are shown separately.
      </Alert>
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
      >
        <Box
          sx={{
            display: 'grid',
            gap: 2.5,
            gridTemplateColumns: { xs: '1fr', sm: '1fr 1fr', lg: 'repeat(4, 1fr)' },
          }}
        >
          <KpiCard
            title="Sales"
            value={money(current.total_sales)}
            hint={data?.previous_label ? `${data.previous_label}: ${money(previous.total_sales)}` : undefined}
          />
          <KpiCard
            title="Cash"
            value={money(current.cash_sales)}
            hint={`${current.bill_count ?? 0} bills · Cash share of sales`}
          />
          <KpiCard
            title="Online"
            value={money(current.online_sales)}
            hint="Online payments for this period"
          />
          <KpiCard
            title="Bills"
            value={current.bill_count ?? '—'}
            hint={data?.previous_label ? `${data.previous_label}: ${previous.bill_count ?? '—'}` : undefined}
          />
          <KpiCard title="Average Bill" value={money(current.average_bill)} />
          <KpiCard title="Cancelled" value={current.cancelled_bills ?? '—'} />
        </Box>
      </Section>

      <Section title="Sales Overview">
        <Card>
          <CardContent sx={{ p: { xs: 2, sm: 3 }, '&:last-child': { pb: { xs: 2, sm: 3 } } }}>
            <Box sx={{ width: '100%', height: 300 }}>
              {(data?.day_wise || []).length ? (
                <ResponsiveContainer>
                  <BarChart data={data.day_wise}>
                    <CartesianGrid strokeDasharray="3 3" vertical={false} />
                    <XAxis dataKey="date" tick={{ fontSize: 12 }} />
                    <YAxis tick={{ fontSize: 12 }} />
                    <ChartTooltip />
                    <Bar dataKey="total_sales" fill="#1F4E5F" name="Sales" radius={[4, 4, 0, 0]} />
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
                    <Chip size="small" label={bill.status || '—'} variant="outlined" />
                  </TableCell>
                  <TableCell>
                    {bill.payment_method_label
                      || (bill.payment_method === 'online' ? 'Online' : 'Cash')}
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
              description="Create or update menu items to see activity here."
            />
          ) : null}
        </TableCard>
      </Section>
    </PageShell>
  );
}
