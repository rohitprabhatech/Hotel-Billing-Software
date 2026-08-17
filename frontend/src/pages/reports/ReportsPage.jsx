import {
  Alert,
  Box,
  Button,
  Card,
  CardContent,
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
  TextField,
} from '@mui/material';
import { useTheme } from '@mui/material/styles';
import { useState } from 'react';
import {
  Bar,
  BarChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts';
import EmptyState from '../../components/EmptyState';
import FilterBar from '../../components/FilterBar';
import KpiCard from '../../components/KpiCard';
import PageShell from '../../components/PageShell';
import Section from '../../components/Section';
import TableCard from '../../components/TableCard';
import TruncateText from '../../components/TruncateText';
import {
  downloadReport,
  fetchCustomSales,
  fetchDailySales,
  fetchMonthlySales,
  fetchWeeklySales,
} from '../../services/reportService';
import { PAYMENT_CASH, PAYMENT_ONLINE, paymentMethodLabel } from '../../utils/paymentMethod';

function money(v) {
  return `₹${Number(v || 0).toLocaleString('en-IN', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  })}`;
}

function ItemSalesTable({ rows, emptyTitle, emptyDescription }) {
  return (
    <TableCard>
      <Table size="small" sx={{ minWidth: 480 }}>
        <TableHead>
          <TableRow>
            <TableCell>Item</TableCell>
            <TableCell align="right">Qty</TableCell>
            <TableCell align="right">Revenue</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {(rows || []).map((row) => (
            <TableRow key={row.item_name} hover>
              <TableCell>
                <TruncateText value={row.item_name} maxWidth={280} />
              </TableCell>
              <TableCell align="right">{row.quantity}</TableCell>
              <TableCell align="right">{money(row.revenue)}</TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
      {!rows?.length ? (
        <EmptyState title={emptyTitle} description={emptyDescription} />
      ) : null}
    </TableCard>
  );
}

export default function ReportsPage() {
  const theme = useTheme();
  const [type, setType] = useState('daily');
  const [date, setDate] = useState('');
  const [fromDate, setFromDate] = useState('');
  const [toDate, setToDate] = useState('');
  const [year, setYear] = useState(String(new Date().getFullYear()));
  const [month, setMonth] = useState(String(new Date().getMonth() + 1));
  const [paymentMethod, setPaymentMethod] = useState('');
  const [report, setReport] = useState(null);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [exporting, setExporting] = useState('');

  const load = async () => {
    setLoading(true);
    setError('');
    try {
      const paymentParams = paymentMethod ? { payment_method: paymentMethod } : {};
      let res;
      if (type === 'daily') {
        res = await fetchDailySales({ ...(date ? { date } : {}), ...paymentParams });
      } else if (type === 'weekly') {
        res = await fetchWeeklySales(paymentParams);
      } else if (type === 'monthly') {
        res = await fetchMonthlySales({ year, month, ...paymentParams });
      } else {
        res = await fetchCustomSales({ from: fromDate, to: toDate, ...paymentParams });
      }
      setReport(res.data);
    } catch (err) {
      setError(err.response?.data?.error?.message || 'Unable to generate report.');
    } finally {
      setLoading(false);
    }
  };

  const exportFile = async (format) => {
    setError('');
    setExporting(format);
    try {
      const params = { type, format };
      if (type === 'daily' && date) params.date = date;
      if (type === 'monthly') {
        params.year = year;
        params.month = month;
      }
      if (type === 'custom') {
        params.from = fromDate;
        params.to = toDate;
      }
      if (paymentMethod) params.payment_method = paymentMethod;
      await downloadReport(params);
    } catch (err) {
      setError(err.response?.data?.error?.message || 'Export failed');
    } finally {
      setExporting('');
    }
  };

  const metrics = report?.metrics || {};

  return (
    <PageShell>
      <FilterBar
        actions={
          <Button
            variant="contained"
            onClick={load}
            disabled={loading}
            startIcon={loading ? <CircularProgress size={16} color="inherit" /> : null}
          >
            {loading ? 'Generating...' : 'Generate'}
          </Button>
        }
      >
        <FormControl sx={{ minWidth: { xs: '100%', sm: 160 } }}>
          <InputLabel>Report Type</InputLabel>
          <Select
            label="Report Type"
            value={type}
            onChange={(e) => setType(e.target.value)}
          >
            <MenuItem value="daily">Daily</MenuItem>
            <MenuItem value="weekly">Weekly</MenuItem>
            <MenuItem value="monthly">Monthly</MenuItem>
            <MenuItem value="custom">Custom Range</MenuItem>
          </Select>
        </FormControl>

        {type === 'daily' ? (
          <TextField
            label="Date"
            type="date"
            value={date}
            onChange={(e) => setDate(e.target.value)}
            InputLabelProps={{ shrink: true }}
            helperText="Leave empty for today"
            sx={{ minWidth: { xs: '100%', sm: 180 } }}
          />
        ) : null}

        {type === 'weekly' ? (
          <Alert severity="info" sx={{ py: 0, alignItems: 'center' }}>
            Current calendar week (business timezone)
          </Alert>
        ) : null}

        {type === 'monthly' ? (
          <>
            <TextField
              label="Year"
              type="number"
              value={year}
              onChange={(e) => setYear(e.target.value)}
              sx={{ width: { xs: '100%', sm: 120 } }}
            />
            <TextField
              label="Month"
              type="number"
              value={month}
              onChange={(e) => setMonth(e.target.value)}
              inputProps={{ min: 1, max: 12 }}
              sx={{ width: { xs: '100%', sm: 120 } }}
            />
          </>
        ) : null}

        {type === 'custom' ? (
          <>
            <TextField
              label="From"
              type="date"
              value={fromDate}
              onChange={(e) => setFromDate(e.target.value)}
              InputLabelProps={{ shrink: true }}
              sx={{ minWidth: { xs: '100%', sm: 160 } }}
            />
            <TextField
              label="To"
              type="date"
              value={toDate}
              onChange={(e) => setToDate(e.target.value)}
              InputLabelProps={{ shrink: true }}
              sx={{ minWidth: { xs: '100%', sm: 160 } }}
            />
          </>
        ) : null}

        <FormControl sx={{ minWidth: { xs: '100%', sm: 160 } }}>
          <InputLabel>Payment Method</InputLabel>
          <Select
            label="Payment Method"
            value={paymentMethod}
            onChange={(e) => setPaymentMethod(e.target.value)}
          >
            <MenuItem value="">All</MenuItem>
            <MenuItem value={PAYMENT_CASH}>Cash</MenuItem>
            <MenuItem value={PAYMENT_ONLINE}>Online</MenuItem>
          </Select>
        </FormControl>
      </FilterBar>

      {error ? <Alert severity="error">{error}</Alert> : null}

      {report ? (
        <>
          <Section
            title={report.label}
            description={
              report.payment_method
                ? `Filtered by ${paymentMethodLabel(report.payment_method)} payments`
                : 'All payment methods'
            }
            actions={
              <Stack direction="row" spacing={1} useFlexGap flexWrap="wrap">
                <Button
                  size="small"
                  variant="outlined"
                  onClick={() => exportFile('xlsx')}
                  disabled={Boolean(exporting)}
                >
                  {exporting === 'xlsx' ? 'Exporting...' : 'Export Excel'}
                </Button>
                <Button
                  size="small"
                  variant="outlined"
                  onClick={() => exportFile('csv')}
                  disabled={Boolean(exporting)}
                >
                  {exporting === 'csv' ? 'Exporting...' : 'Export CSV'}
                </Button>
                <Button
                  size="small"
                  variant="outlined"
                  onClick={() => exportFile('pdf')}
                  disabled={Boolean(exporting)}
                >
                  {exporting === 'pdf' ? 'Exporting...' : 'Export PDF'}
                </Button>
              </Stack>
            }
          >
            <Box
              sx={{
                display: 'grid',
                gap: 2,
                gridTemplateColumns: { xs: '1fr', sm: '1fr 1fr', md: 'repeat(3, 1fr)' },
              }}
            >
              <KpiCard title="Total Sales" value={money(metrics.total_sales)} />
              <KpiCard title="Bills" value={metrics.bill_count ?? '—'} />
              <KpiCard title="Average Bill" value={money(metrics.average_bill)} />
              <KpiCard
                title="Cash Sales"
                value={money(metrics.cash_sales)}
                hint={`${metrics.cash_bill_count ?? 0} cash bills`}
              />
              <KpiCard
                title="Online Sales"
                value={money(metrics.online_sales)}
                hint={`${metrics.online_bill_count ?? 0} online bills`}
              />
              <KpiCard title="Items Sold" value={metrics.items_sold ?? '—'} />
              <KpiCard title="Discount" value={money(metrics.total_discount)} />
              <KpiCard title="GST" value={money(metrics.total_gst)} />
              <KpiCard title="Cancelled" value={metrics.cancelled_bills ?? '—'} />
            </Box>
          </Section>

          <Section title="Day-wise Sales">
            <Card>
              <CardContent sx={{ p: { xs: 2, sm: 3 }, '&:last-child': { pb: { xs: 2, sm: 3 } } }}>
                <Box sx={{ width: '100%', height: 300 }}>
                  {(report.day_wise || []).length ? (
                    <ResponsiveContainer>
                      <BarChart data={report.day_wise || []}>
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
                        <Tooltip />
                        <Bar dataKey="total_sales" fill={theme.palette.primary.main} name="Sales" radius={[4, 4, 0, 0]} />
                      </BarChart>
                    </ResponsiveContainer>
                  ) : (
                    <EmptyState
                      title="No chart data"
                      description="Generate a report with sales to see the chart."
                    />
                  )}
                </Box>
              </CardContent>
            </Card>
          </Section>

          <Box
            sx={{
              display: 'grid',
              gap: 3,
              gridTemplateColumns: { xs: '1fr', lg: '1fr 1fr' },
            }}
          >
            <Section title="Top Items">
              <ItemSalesTable
                rows={report.top_items}
                emptyTitle="No top items"
                emptyDescription="No item sales in this period."
              />
            </Section>
            <Section title="Low Items">
              <ItemSalesTable
                rows={report.low_items}
                emptyTitle="No low items"
                emptyDescription="No item sales in this period."
              />
            </Section>
          </Box>

          <Section title="Category Sales">
            <TableCard>
              <Table size="small" sx={{ minWidth: 480 }}>
                <TableHead>
                  <TableRow>
                    <TableCell>Category</TableCell>
                    <TableCell align="right">Qty</TableCell>
                    <TableCell align="right">Revenue</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {(report.category_wise || []).map((row) => (
                    <TableRow key={row.category_name} hover>
                      <TableCell>
                        <TruncateText value={row.category_name} maxWidth={280} />
                      </TableCell>
                      <TableCell align="right">{row.quantity}</TableCell>
                      <TableCell align="right">{money(row.revenue)}</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
              {!report.category_wise?.length ? (
                <EmptyState
                  title="No category sales"
                  description="No category-wise data for this report period."
                />
              ) : null}
            </TableCard>
          </Section>

          <Section title="Item-wise Sales">
            <ItemSalesTable
              rows={report.item_wise}
              emptyTitle="No item sales"
              emptyDescription="No item-wise data for this report period."
            />
          </Section>

          <Section title="Bills">
            <TableCard>
              <Table size="small" sx={{ minWidth: 640 }}>
                <TableHead>
                  <TableRow>
                    <TableCell>Bill No</TableCell>
                    <TableCell>Date</TableCell>
                    <TableCell align="right">Amount</TableCell>
                    <TableCell>Payment Method</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {(report.bills || []).map((bill) => (
                    <TableRow key={bill.id} hover>
                      <TableCell>
                        <TruncateText value={bill.bill_number} maxWidth={140} />
                      </TableCell>
                      <TableCell>
                        {bill.created_at
                          ? new Date(bill.created_at).toLocaleString()
                          : '—'}
                      </TableCell>
                      <TableCell align="right">{money(bill.grand_total)}</TableCell>
                      <TableCell>
                        {paymentMethodLabel(bill.payment_method)}
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
              {!report.bills?.length ? (
                <EmptyState
                  title="No bills found"
                  description="No bills match this report period and payment filter."
                />
              ) : null}
            </TableCard>
          </Section>
        </>
      ) : !loading ? (
        <EmptyState
          title="No report generated yet"
          description="Choose daily, weekly, monthly, or a custom range, then click Generate."
          actionLabel="Generate"
          onAction={load}
        />
      ) : null}
    </PageShell>
  );
}
