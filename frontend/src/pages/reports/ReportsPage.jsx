import {
  Alert,
  Box,
  Button,
  Card,
  CardContent,
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
import {
  downloadReport,
  fetchCustomSales,
  fetchDailySales,
  fetchMonthlySales,
} from '../../services/reportService';

function money(v) {
  return `₹${Number(v || 0).toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
}

export default function ReportsPage() {
  const [type, setType] = useState('daily');
  const [date, setDate] = useState('');
  const [fromDate, setFromDate] = useState('');
  const [toDate, setToDate] = useState('');
  const [year, setYear] = useState(String(new Date().getFullYear()));
  const [month, setMonth] = useState(String(new Date().getMonth() + 1));
  const [report, setReport] = useState(null);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const load = async () => {
    setLoading(true);
    setError('');
    try {
      let res;
      if (type === 'daily') {
        res = await fetchDailySales(date ? { date } : {});
      } else if (type === 'monthly') {
        res = await fetchMonthlySales({ year, month });
      } else {
        res = await fetchCustomSales({ from: fromDate, to: toDate });
      }
      setReport(res.data);
    } catch (err) {
      setError(err.response?.data?.error?.message || 'Failed to load report');
    } finally {
      setLoading(false);
    }
  };

  const exportFile = async (format) => {
    setError('');
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
      await downloadReport(params);
    } catch (err) {
      setError(err.response?.data?.error?.message || 'Export failed');
    }
  };

  const metrics = report?.metrics || {};

  return (
    <>
      <Typography variant="h5" gutterBottom>
        Sales Reports
      </Typography>

      <Card sx={{ mb: 2 }}>
        <CardContent>
          <Stack direction={{ xs: 'column', md: 'row' }} spacing={2} alignItems="flex-start">
            <FormControl sx={{ minWidth: 160 }}>
              <InputLabel>Report Type</InputLabel>
              <Select
                label="Report Type"
                value={type}
                onChange={(e) => setType(e.target.value)}
              >
                <MenuItem value="daily">Daily</MenuItem>
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
              />
            ) : null}

            {type === 'monthly' ? (
              <>
                <TextField
                  label="Year"
                  type="number"
                  value={year}
                  onChange={(e) => setYear(e.target.value)}
                />
                <TextField
                  label="Month"
                  type="number"
                  value={month}
                  onChange={(e) => setMonth(e.target.value)}
                  inputProps={{ min: 1, max: 12 }}
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
                />
                <TextField
                  label="To"
                  type="date"
                  value={toDate}
                  onChange={(e) => setToDate(e.target.value)}
                  InputLabelProps={{ shrink: true }}
                />
              </>
            ) : null}

            <Button variant="contained" onClick={load} disabled={loading}>
              Generate
            </Button>
          </Stack>
        </CardContent>
      </Card>

      {error ? <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert> : null}

      {report ? (
        <>
          <Stack direction="row" spacing={1} mb={2}>
            <Button variant="outlined" onClick={() => exportFile('xlsx')}>
              Export Excel
            </Button>
            <Button variant="outlined" onClick={() => exportFile('csv')}>
              Export CSV
            </Button>
            <Button variant="outlined" onClick={() => exportFile('pdf')}>
              Export PDF
            </Button>
          </Stack>

          <Typography variant="h6" gutterBottom>
            {report.label}
          </Typography>

          <Box
            sx={{
              display: 'grid',
              gap: 2,
              gridTemplateColumns: { xs: '1fr', sm: '1fr 1fr', md: 'repeat(3, 1fr)' },
              mb: 3,
            }}
          >
            {[
              ['Total Sales', money(metrics.total_sales)],
              ['Bills', metrics.bill_count],
              ['Discount', money(metrics.total_discount)],
              ['GST', money(metrics.total_gst)],
              ['Average Bill', money(metrics.average_bill)],
              ['Cancelled', metrics.cancelled_bills],
            ].map(([label, value]) => (
              <Card key={label}>
                <CardContent>
                  <Typography variant="body2" color="text.secondary">{label}</Typography>
                  <Typography variant="h6">{value}</Typography>
                </CardContent>
              </Card>
            ))}
          </Box>

          <Card sx={{ mb: 3 }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Day-wise Sales
              </Typography>
              <Box sx={{ width: '100%', height: 280 }}>
                <ResponsiveContainer>
                  <BarChart data={report.day_wise || []}>
                    <CartesianGrid strokeDasharray="3 3" vertical={false} />
                    <XAxis dataKey="date" />
                    <YAxis />
                    <Tooltip />
                    <Bar dataKey="total_sales" fill="#1F4E5F" name="Sales" />
                  </BarChart>
                </ResponsiveContainer>
              </Box>
            </CardContent>
          </Card>

          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Item-wise Sales
              </Typography>
              <Table size="small">
                <TableHead>
                  <TableRow>
                    <TableCell>Item</TableCell>
                    <TableCell align="right">Qty</TableCell>
                    <TableCell align="right">Revenue</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {(report.item_wise || []).map((row) => (
                    <TableRow key={row.item_name}>
                      <TableCell>{row.item_name}</TableCell>
                      <TableCell align="right">{row.quantity}</TableCell>
                      <TableCell align="right">{money(row.revenue)}</TableCell>
                    </TableRow>
                  ))}
                  {!report.item_wise?.length ? (
                    <TableRow>
                      <TableCell colSpan={3}>
                        <Typography color="text.secondary">No data</Typography>
                      </TableCell>
                    </TableRow>
                  ) : null}
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        </>
      ) : null}
    </>
  );
}