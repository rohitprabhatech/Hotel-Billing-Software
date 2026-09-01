import {
  Alert,
  Box,
  Button,
  Card,
  CardActionArea,
  CardContent,
  CircularProgress,
  FormControl,
  InputLabel,
  MenuItem,
  Select,
  Stack,
  Tab,
  Tabs,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
  TextField,
  Typography,
} from '@mui/material';
import { useTheme } from '@mui/material/styles';
import { useEffect, useMemo, useState } from 'react';
import { Link as RouterLink } from 'react-router-dom';
import {
  Bar,
  BarChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts';
import ChartPanel from '../../components/ChartPanel';
import EmptyState from '../../components/EmptyState';
import FilterBar from '../../components/FilterBar';
import KpiCard from '../../components/KpiCard';
import PageShell from '../../components/PageShell';
import Section from '../../components/Section';
import TableCard from '../../components/TableCard';
import TruncateText from '../../components/TruncateText';
import {
  downloadReport,
  fetchAvailableReports,
  fetchCustomSales,
  fetchDailySales,
  fetchFbReport,
  fetchMonthlySales,
  fetchWeeklySales,
} from '../../services/reportService';
import { listCategories } from '../../services/categoryService';
import { fetchClothingSales } from '../../services/clothingService';
import { fetchGrocerySales } from '../../services/groceryService';
import { fetchMobileSales } from '../../services/mobileService';
import { PAYMENT_CASH, PAYMENT_CREDIT, PAYMENT_ONLINE, paymentMethodLabel } from '../../utils/paymentMethod';

function money(v) {
  return `₹${Number(v || 0).toLocaleString('en-IN', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  })}`;
}

function DimensionTable({ rows, labelHeader, emptyTitle, emptyDescription }) {
  return (
    <TableCard>
      <Table size="small" sx={{ minWidth: 480 }}>
        <TableHead>
          <TableRow>
            <TableCell>{labelHeader}</TableCell>
            <TableCell align="right">Qty</TableCell>
            <TableCell align="right">Bills</TableCell>
            <TableCell align="right">Revenue</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {(rows || []).map((row) => (
            <TableRow key={row.label} hover>
              <TableCell>
                <TruncateText value={row.label} maxWidth={280} />
              </TableCell>
              <TableCell align="right">{row.quantity}</TableCell>
              <TableCell align="right">{row.bill_count}</TableCell>
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
  const [hubReports, setHubReports] = useState([{ id: 'sales', view: 'sales', label: 'Sales' }]);
  const [linkReports, setLinkReports] = useState([]);
  const [maxRangeDays, setMaxRangeDays] = useState(366);
  const [view, setView] = useState('sales');
  const [type, setType] = useState('daily');
  const [date, setDate] = useState('');
  const [fromDate, setFromDate] = useState('');
  const [toDate, setToDate] = useState('');
  const [year, setYear] = useState(String(new Date().getFullYear()));
  const [month, setMonth] = useState(String(new Date().getMonth() + 1));
  const [paymentMethod, setPaymentMethod] = useState('');
  const [brandFilter, setBrandFilter] = useState('');
  const [sizeFilter, setSizeFilter] = useState('');
  const [colorFilter, setColorFilter] = useState('');
  const [modelFilter, setModelFilter] = useState('');
  const [categoryFilter, setCategoryFilter] = useState('');
  const [categories, setCategories] = useState([]);
  const [billsPage, setBillsPage] = useState(1);
  const [report, setReport] = useState(null);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [exporting, setExporting] = useState('');

  const clothingEnabled = useMemo(
    () => hubReports.some((row) => row.view === 'apparel'),
    [hubReports],
  );
  const mobileEnabled = useMemo(
    () => hubReports.some((row) => row.view === 'mobile'),
    [hubReports],
  );

  useEffect(() => {
    let cancelled = false;
    fetchAvailableReports()
      .then((res) => {
        if (cancelled) return;
        const hub = res.data?.hub_reports?.length
          ? res.data.hub_reports
          : [{ id: 'sales', view: 'sales', label: 'Sales' }];
        setHubReports(hub);
        setLinkReports(res.data?.link_reports || []);
        setMaxRangeDays(res.data?.limits?.max_custom_range_days || 366);
        setView((current) =>
          hub.some((row) => row.view === current) ? current : hub[0]?.view || 'sales',
        );
      })
      .catch(() => {
        if (!cancelled) {
          setHubReports([{ id: 'sales', view: 'sales', label: 'Sales' }]);
          setLinkReports([]);
        }
      });
    return () => {
      cancelled = true;
    };
  }, []);

  useEffect(() => {
    if (!clothingEnabled && !mobileEnabled) return undefined;
    let cancelled = false;
    listCategories()
      .then((res) => {
        if (!cancelled) setCategories(res.data || []);
      })
      .catch(() => {
        if (!cancelled) setCategories([]);
      });
    return () => {
      cancelled = true;
    };
  }, [clothingEnabled, mobileEnabled]);

  const load = async (pageOverride) => {
    const page = pageOverride || billsPage;
    setLoading(true);
    setError('');
    try {
      const paymentParams = paymentMethod ? { payment_method: paymentMethod } : {};
      const pageParams = { page, per_page: 50 };
      let res;
      if (view === 'fb') {
        if (type === 'custom') {
          res = await fetchFbReport({ from: fromDate, to: toDate });
        } else {
          res = await fetchFbReport({ ...(date ? { date } : {}) });
        }
      } else if (view === 'kirana') {
        res = await fetchGrocerySales({ ...(date ? { date } : {}), ...paymentParams });
      } else if (view === 'apparel') {
        const apparelParams = { ...paymentParams };
        if (type === 'custom') {
          apparelParams.from = fromDate;
          apparelParams.to = toDate;
        } else if (date) {
          apparelParams.date = date;
        }
        if (brandFilter.trim()) apparelParams.brand = brandFilter.trim();
        if (sizeFilter.trim()) apparelParams.size = sizeFilter.trim();
        if (colorFilter.trim()) apparelParams.color = colorFilter.trim();
        if (categoryFilter) apparelParams.category_id = categoryFilter;
        res = await fetchClothingSales(apparelParams);
      } else if (view === 'mobile') {
        const mobileParams = { ...paymentParams };
        if (type === 'custom') {
          mobileParams.from = fromDate;
          mobileParams.to = toDate;
        } else if (date) {
          mobileParams.date = date;
        }
        if (brandFilter.trim()) mobileParams.brand = brandFilter.trim();
        if (modelFilter.trim()) mobileParams.model_name = modelFilter.trim();
        if (categoryFilter) mobileParams.category_id = categoryFilter;
        res = await fetchMobileSales(mobileParams);
      } else if (type === 'daily') {
        res = await fetchDailySales({ ...(date ? { date } : {}), ...paymentParams, ...pageParams });
      } else if (type === 'weekly') {
        res = await fetchWeeklySales({ ...paymentParams, ...pageParams });
      } else if (type === 'monthly') {
        res = await fetchMonthlySales({ year, month, ...paymentParams, ...pageParams });
      } else {
        res = await fetchCustomSales({
          from: fromDate,
          to: toDate,
          ...paymentParams,
          ...pageParams,
        });
      }
      setReport(res.data);
      if (pageOverride) setBillsPage(pageOverride);
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
  const billsMeta = report?.bills_meta;
  const showIndustryTabs = hubReports.length > 1;

  return (
    <PageShell>
      {showIndustryTabs ? (
        <Tabs
          value={view}
          onChange={(_, value) => {
            setView(value);
            setReport(null);
            setBillsPage(1);
            if (value === 'kirana' || value === 'apparel' || value === 'mobile') setType('daily');
          }}
          sx={{ mb: 2 }}
          variant="scrollable"
          allowScrollButtonsMobile
        >
          {hubReports.map((row) => (
            <Tab key={row.id} value={row.view} label={row.label} />
          ))}
        </Tabs>
      ) : null}

      {linkReports.length ? (
        <Section title="More reports" description="Module-enabled reports outside this hub">
          <Box
            sx={{
              display: 'grid',
              gap: 2,
              gridTemplateColumns: { xs: '1fr', sm: '1fr 1fr', md: 'repeat(3, 1fr)' },
              mb: 2,
            }}
          >
            {linkReports.map((row) => (
              <Card key={row.id} variant="outlined">
                <CardActionArea component={RouterLink} to={row.ui_path || '/owner/reports'}>
                  <CardContent>
                    <Typography fontWeight={700}>{row.label}</Typography>
                    <Typography variant="body2" color="text.secondary">
                      {row.description}
                    </Typography>
                  </CardContent>
                </CardActionArea>
              </Card>
            ))}
          </Box>
        </Section>
      ) : null}

      <FilterBar
        actions={
          <Button
            variant="contained"
            onClick={() => load(1)}
            disabled={loading}
            startIcon={loading ? <CircularProgress size={16} color="inherit" /> : null}
          >
            {loading ? 'Generating...' : 'Generate'}
          </Button>
        }
      >
        {view === 'sales' ? (
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
        ) : view === 'fb' ? (
          <FormControl sx={{ minWidth: { xs: '100%', sm: 160 } }}>
            <InputLabel>Period</InputLabel>
            <Select label="Period" value={type} onChange={(e) => setType(e.target.value)}>
              <MenuItem value="daily">Daily</MenuItem>
              <MenuItem value="custom">Custom Range</MenuItem>
            </Select>
          </FormControl>
        ) : view === 'apparel' || view === 'mobile' ? (
          <FormControl sx={{ minWidth: { xs: '100%', sm: 160 } }}>
            <InputLabel>Period</InputLabel>
            <Select label="Period" value={type} onChange={(e) => setType(e.target.value)}>
              <MenuItem value="daily">Daily</MenuItem>
              <MenuItem value="custom">Custom Range</MenuItem>
            </Select>
          </FormControl>
        ) : (
          <Alert severity="info" sx={{ py: 0, alignItems: 'center' }}>
            Daily grocery sales plus outstanding udhari
          </Alert>
        )}

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

        {view === 'sales' && type === 'weekly' ? (
          <Alert severity="info" sx={{ py: 0, alignItems: 'center' }}>
            Current calendar week (business timezone)
          </Alert>
        ) : null}

        {view === 'sales' && type === 'monthly' ? (
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
              helperText={view === 'sales' ? `Max ${maxRangeDays} days` : undefined}
              sx={{ minWidth: { xs: '100%', sm: 160 } }}
            />
          </>
        ) : null}

        {view === 'apparel' ? (
          <>
            <TextField
              label="Brand"
              value={brandFilter}
              onChange={(e) => setBrandFilter(e.target.value)}
              placeholder="e.g. Nike"
              sx={{ minWidth: { xs: '100%', sm: 140 } }}
            />
            <TextField
              label="Size"
              value={sizeFilter}
              onChange={(e) => setSizeFilter(e.target.value)}
              placeholder="e.g. M"
              sx={{ minWidth: { xs: '100%', sm: 100 } }}
            />
            <TextField
              label="Color"
              value={colorFilter}
              onChange={(e) => setColorFilter(e.target.value)}
              placeholder="e.g. Black"
              sx={{ minWidth: { xs: '100%', sm: 120 } }}
            />
            <FormControl sx={{ minWidth: { xs: '100%', sm: 160 } }}>
              <InputLabel>Category</InputLabel>
              <Select
                label="Category"
                value={categoryFilter}
                onChange={(e) => setCategoryFilter(e.target.value)}
              >
                <MenuItem value="">All</MenuItem>
                {categories.map((cat) => (
                  <MenuItem key={cat.id} value={cat.id}>
                    {cat.name}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </>
        ) : null}

        {view === 'mobile' ? (
          <>
            <TextField
              label="Brand"
              value={brandFilter}
              onChange={(e) => setBrandFilter(e.target.value)}
              placeholder="e.g. Samsung"
              sx={{ minWidth: { xs: '100%', sm: 140 } }}
            />
            <TextField
              label="Model"
              value={modelFilter}
              onChange={(e) => setModelFilter(e.target.value)}
              placeholder="e.g. Galaxy A15"
              sx={{ minWidth: { xs: '100%', sm: 160 } }}
            />
            <FormControl sx={{ minWidth: { xs: '100%', sm: 160 } }}>
              <InputLabel>Category</InputLabel>
              <Select
                label="Category"
                value={categoryFilter}
                onChange={(e) => setCategoryFilter(e.target.value)}
              >
                <MenuItem value="">All</MenuItem>
                {categories.map((cat) => (
                  <MenuItem key={cat.id} value={cat.id}>
                    {cat.name}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </>
        ) : null}

        {view === 'sales' || view === 'kirana' || view === 'apparel' || view === 'mobile' ? (
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
              <MenuItem value={PAYMENT_CREDIT}>Credit</MenuItem>
            </Select>
          </FormControl>
        ) : null}
      </FilterBar>

      {error ? <Alert severity="error">{error}</Alert> : null}

      {report && view === 'kirana' ? (
        <>
          <Section
            title={report.label}
            description={
              report.payment_method
                ? `Filtered by ${paymentMethodLabel(report.payment_method)} payments`
                : 'Grocery daily sales and udhari outstanding'
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
              <KpiCard title="Cash" value={money(metrics.cash_sales)} />
              <KpiCard title="Online" value={money(metrics.online_sales)} />
              <KpiCard
                title="Credit / Udhari"
                value={money(metrics.credit_sales)}
                hint={`${metrics.credit_bill_count ?? 0} credit bills`}
              />
              <KpiCard
                title="Outstanding"
                value={money(report.outstanding?.outstanding_amount)}
                hint={`${report.outstanding?.customer_count ?? 0} customers`}
              />
              <KpiCard title="Items Sold" value={metrics.items_sold ?? '—'} />
            </Box>
          </Section>
          <Section title="Fast-moving items">
            <ItemSalesTable
              rows={report.top_items}
              emptyTitle="No item sales"
              emptyDescription="No grocery sales in this period."
            />
          </Section>
        </>
      ) : null}

      {report && view === 'apparel' ? (
        <>
          <Section
            title={report.label}
            description="Sales by brand, size, color, and category with current variant stock"
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
              <KpiCard title="Items Sold" value={metrics.items_sold ?? '—'} />
              <KpiCard title="Returns" value={report.returns?.return_count ?? 0} />
              <KpiCard title="Refunds" value={money(report.returns?.refund_amount)} />
              <KpiCard title="Exchanges" value={report.returns?.exchange_count ?? 0} />
            </Box>
          </Section>
          <Box
            sx={{
              display: 'grid',
              gap: 3,
              gridTemplateColumns: { xs: '1fr', lg: '1fr 1fr' },
            }}
          >
            <Section title="By brand">
              <DimensionTable
                rows={report.by_brand}
                labelHeader="Brand"
                emptyTitle="No brand sales"
                emptyDescription="No apparel sales in this period."
              />
            </Section>
            <Section title="By size">
              <DimensionTable
                rows={report.by_size}
                labelHeader="Size"
                emptyTitle="No size sales"
                emptyDescription="No apparel sales in this period."
              />
            </Section>
            <Section title="By color">
              <DimensionTable
                rows={report.by_color}
                labelHeader="Color"
                emptyTitle="No color sales"
                emptyDescription="No apparel sales in this period."
              />
            </Section>
            <Section title="By category">
              <DimensionTable
                rows={report.by_category}
                labelHeader="Category"
                emptyTitle="No category sales"
                emptyDescription="No apparel sales in this period."
              />
            </Section>
          </Box>
          <Section title="Variant stock">
            <TableCard>
              <Table size="small" sx={{ minWidth: 560 }}>
                <TableHead>
                  <TableRow>
                    <TableCell>Item</TableCell>
                    <TableCell>Size</TableCell>
                    <TableCell>Color</TableCell>
                    <TableCell>Brand</TableCell>
                    <TableCell align="right">Stock</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {(report.variant_stock || []).map((row) => (
                    <TableRow key={row.variant_id} hover>
                      <TableCell>
                        <TruncateText value={row.item_name} maxWidth={220} />
                      </TableCell>
                      <TableCell>{row.size}</TableCell>
                      <TableCell>{row.color}</TableCell>
                      <TableCell>{row.brand || '—'}</TableCell>
                      <TableCell align="right">{row.stock_quantity}</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
              {!report.variant_stock?.length ? (
                <EmptyState title="No variants" description="Add size/color rows on Items to see stock here." />
              ) : null}
            </TableCard>
          </Section>
        </>
      ) : null}

      {report && view === 'mobile' ? (
        <>
          <Section
            title={report.label}
            description="Sales by brand and model with current IMEI stock"
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
              <KpiCard title="Items Sold" value={metrics.items_sold ?? '—'} />
              <KpiCard title="In stock IMEI" value={report.serial_stock_summary?.IN_STOCK ?? 0} />
              <KpiCard title="Returns" value={report.returns?.return_count ?? 0} />
              <KpiCard title="Exchanges" value={report.returns?.exchange_count ?? 0} />
            </Box>
          </Section>
          <Box
            sx={{
              display: 'grid',
              gap: 3,
              gridTemplateColumns: { xs: '1fr', lg: '1fr 1fr' },
            }}
          >
            <Section title="By brand">
              <DimensionTable
                rows={report.by_brand}
                labelHeader="Brand"
                emptyTitle="No brand sales"
                emptyDescription="No mobile sales in this period."
              />
            </Section>
            <Section title="By model">
              <DimensionTable
                rows={report.by_model}
                labelHeader="Model"
                emptyTitle="No model sales"
                emptyDescription="No mobile sales in this period."
              />
            </Section>
            <Section title="By category">
              <DimensionTable
                rows={report.by_category}
                labelHeader="Category"
                emptyTitle="No category sales"
                emptyDescription="No mobile sales in this period."
              />
            </Section>
          </Box>
          <Section title="IMEI stock">
            <TableCard>
              <Table size="small" sx={{ minWidth: 560 }}>
                <TableHead>
                  <TableRow>
                    <TableCell>Item</TableCell>
                    <TableCell>Brand</TableCell>
                    <TableCell>Model</TableCell>
                    <TableCell>IMEI / Serial</TableCell>
                    <TableCell>Status</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {(report.serial_stock || []).map((row) => (
                    <TableRow key={row.serial_unit_id} hover>
                      <TableCell>
                        <TruncateText value={row.item_name} maxWidth={200} />
                      </TableCell>
                      <TableCell>{row.brand || '—'}</TableCell>
                      <TableCell>{row.model_name || '—'}</TableCell>
                      <TableCell>{row.serial}</TableCell>
                      <TableCell>{row.status}</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
              {!report.serial_stock?.length ? (
                <EmptyState
                  title="No serial units"
                  description="Receive IMEI units on Serial / IMEI to see stock here."
                />
              ) : null}
            </TableCard>
          </Section>
        </>
      ) : null}

      {report && view === 'fb' ? (
        <>
          <Section title={report.label} description="Sales by order channel and dining table">
            <Box
              sx={{
                display: 'grid',
                gap: 2,
                gridTemplateColumns: { xs: '1fr', sm: '1fr 1fr', md: 'repeat(3, 1fr)' },
              }}
            >
              <KpiCard title="Total Sales" value={money(metrics.total_sales)} />
              <KpiCard title="Bills" value={metrics.bill_count ?? '—'} />
              <KpiCard title="Items Sold" value={metrics.items_sold ?? '—'} />
            </Box>
          </Section>

          <Section title="Sales by Channel" description="Settled order sales grouped by channel.">
            <ChartPanel title="Channel sales" height={280}>
                  {(report.channel_wise || []).length ? (
                    <ResponsiveContainer>
                      <BarChart data={report.channel_wise || []}>
                        <CartesianGrid strokeDasharray="3 3" vertical={false} stroke={theme.palette.divider} />
                        <XAxis dataKey="channel_label" tick={{ fill: theme.palette.text.secondary, fontSize: 11 }} />
                        <YAxis tickFormatter={(v) => `₹${v}`} tick={{ fill: theme.palette.text.secondary, fontSize: 11 }} />
                        <Tooltip formatter={(v) => money(v)} />
                        <Bar dataKey="total_sales" fill={theme.palette.primary.main} radius={[4, 4, 0, 0]} />
                      </BarChart>
                    </ResponsiveContainer>
                  ) : (
                    <EmptyState title="No channel data" description="No settled order bills in this period." />
                  )}
            </ChartPanel>
          </Section>

          <Section title="Sales by Table">
            <TableCard>
              <Table size="small">
                <TableHead>
                  <TableRow>
                    <TableCell>Table</TableCell>
                    <TableCell align="right">Bills</TableCell>
                    <TableCell align="right">Sales</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {(report.table_wise || []).map((row) => (
                    <TableRow key={row.table_code} hover>
                      <TableCell>{row.table_code}</TableCell>
                      <TableCell align="right">{row.bill_count}</TableCell>
                      <TableCell align="right">{money(row.total_sales)}</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
              {!report.table_wise?.length ? (
                <EmptyState title="No table sales" description="No table-linked bills in this period." />
              ) : null}
            </TableCard>
          </Section>

          <Section title="Wastage Summary">
            <Box
              sx={{
                display: 'grid',
                gap: 2,
                gridTemplateColumns: { xs: '1fr', sm: '1fr 1fr' },
                mb: 2,
              }}
            >
              <KpiCard title="Wastage entries" value={report.wastage?.entry_count ?? 0} />
              <KpiCard title="Total quantity lost" value={report.wastage?.total_quantity ?? 0} />
            </Box>
            <ItemSalesTable
              rows={(report.wastage?.top_items || []).map((row) => ({
                item_name: row.item_name,
                quantity: row.quantity,
                revenue: row.entry_count,
              }))}
              emptyTitle="No wastage"
              emptyDescription="No wastage logged in this period."
            />
          </Section>
        </>
      ) : null}

      {report && view === 'sales' ? (
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
              <KpiCard
                title="Credit Sales"
                value={money(metrics.credit_sales)}
                hint={`${metrics.credit_bill_count ?? 0} udhari bills`}
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
              {billsMeta ? (
                <Stack
                  direction="row"
                  spacing={1}
                  justifyContent="flex-end"
                  alignItems="center"
                  sx={{ px: 2, py: 1.5 }}
                >
                  <Typography variant="body2" color="text.secondary">
                    Page {billsMeta.page} · {billsMeta.total} bills
                  </Typography>
                  <Button
                    size="small"
                    disabled={loading || billsMeta.page <= 1}
                    onClick={() => load(billsMeta.page - 1)}
                  >
                    Prev
                  </Button>
                  <Button
                    size="small"
                    disabled={
                      loading ||
                      billsMeta.page * billsMeta.per_page >= billsMeta.total
                    }
                    onClick={() => load(billsMeta.page + 1)}
                  >
                    Next
                  </Button>
                </Stack>
              ) : null}
            </TableCard>
          </Section>
        </>
      ) : !loading ? (
        <EmptyState
          title="No report generated yet"
          description="Choose daily, weekly, monthly, or a custom range, then click Generate."
          actionLabel="Generate"
          onAction={() => load(1)}
        />
      ) : null}
    </PageShell>
  );
}
