import {
  Alert,
  Box,
  Card,
  CardContent,
  FormControl,
  InputLabel,
  MenuItem,
  Select,
  Stack,
  Typography,
} from '@mui/material';
import { useEffect, useState } from 'react';
import {
  Bar,
  BarChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts';
import { fetchAuditAlerts } from '../../services/auditService';
import { fetchReportSummary } from '../../services/reportService';

function MetricCard({ title, value, compareLabel, compareValue }) {
  return (
    <Card sx={{ height: '100%' }}>
      <CardContent>
        <Typography variant="body2" color="text.secondary">
          {title}
        </Typography>
        <Typography variant="h5" sx={{ mt: 1 }}>
          {value}
        </Typography>
        {compareLabel ? (
          <Typography variant="caption" color="text.secondary" display="block" sx={{ mt: 1 }}>
            {compareLabel}: {compareValue}
          </Typography>
        ) : null}
      </CardContent>
    </Card>
  );
}

function money(v) {
  return `₹${Number(v || 0).toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
}

export default function OwnerDashboardPage() {
  const [period, setPeriod] = useState('today');
  const [data, setData] = useState(null);
  const [alerts, setAlerts] = useState([]);
  const [error, setError] = useState('');

  useEffect(() => {
    setError('');
    Promise.all([
      fetchReportSummary({ period }),
      fetchAuditAlerts(),
    ])
      .then(([summaryRes, alertsRes]) => {
        setData(summaryRes.data);
        setAlerts(
          (alertsRes.data?.alerts || []).filter((a) => a.severity !== 'info'),
        );
      })
      .catch((err) => {
        setError(err.response?.data?.error?.message || 'Failed to load dashboard');
      });
  }, [period]);

  const current = data?.current || {};
  const previous = data?.previous || {};

  return (
    <>
      <Stack direction={{ xs: 'column', sm: 'row' }} justifyContent="space-between" mb={2} spacing={2}>
        <Typography variant="h5">Business Overview</Typography>
        <FormControl size="small" sx={{ minWidth: 180 }}>
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
      </Stack>

      {error ? <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert> : null}
      <Alert severity="info" sx={{ mb: 2 }}>
        Sales totals include FINALIZED bills only. Cancelled bills are shown separately.
      </Alert>
      {alerts.slice(0, 3).map((alert) => (
        <Alert
          key={`${alert.type}-${alert.message}`}
          severity={alert.severity === 'medium' ? 'warning' : 'info'}
          sx={{ mb: 1 }}
        >
          <strong>{alert.title}:</strong> {alert.message}
        </Alert>
      ))}

      <Box
        sx={{
          display: 'grid',
          gap: 2,
          gridTemplateColumns: { xs: '1fr', sm: '1fr 1fr', md: 'repeat(4, 1fr)' },
          mb: 3,
        }}
      >
        <MetricCard
          title={`${data?.label || 'Period'} Sales`}
          value={money(current.total_sales)}
          compareLabel={data?.previous_label}
          compareValue={money(previous.total_sales)}
        />
        <MetricCard
          title="Bills"
          value={current.bill_count ?? '—'}
          compareLabel={data?.previous_label}
          compareValue={previous.bill_count ?? '—'}
        />
        <MetricCard title="Discount" value={money(current.total_discount)} />
        <MetricCard title="GST" value={money(current.total_gst)} />
        <MetricCard title="Average Bill" value={money(current.average_bill)} />
        <MetricCard title="Items Sold" value={current.items_sold ?? '—'} />
        <MetricCard title="Cancelled Bills" value={current.cancelled_bills ?? '—'} />
      </Box>

      <Box
        sx={{
          display: 'grid',
          gap: 2,
          gridTemplateColumns: { xs: '1fr', md: '1.4fr 1fr' },
        }}
      >
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Day-wise Sales
            </Typography>
            <Box sx={{ width: '100%', height: 280 }}>
              <ResponsiveContainer>
                <BarChart data={data?.day_wise || []}>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} />
                  <XAxis dataKey="date" tick={{ fontSize: 12 }} />
                  <YAxis tick={{ fontSize: 12 }} />
                  <Tooltip />
                  <Bar dataKey="total_sales" fill="#1F4E5F" name="Sales" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </Box>
          </CardContent>
        </Card>

        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Top Items
            </Typography>
            {(data?.item_wise || []).map((item) => (
              <Stack
                key={item.item_name}
                direction="row"
                justifyContent="space-between"
                sx={{ py: 0.75, borderBottom: '1px solid', borderColor: 'divider' }}
              >
                <Typography variant="body2">{item.item_name}</Typography>
                <Typography variant="body2">{money(item.revenue)}</Typography>
              </Stack>
            ))}
            {!data?.item_wise?.length ? (
              <Typography color="text.secondary">No item sales in this period.</Typography>
            ) : null}
          </CardContent>
        </Card>
      </Box>
    </>
  );
}