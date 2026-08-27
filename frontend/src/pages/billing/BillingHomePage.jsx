import CategoryOutlinedIcon from '@mui/icons-material/CategoryOutlined';
import Inventory2OutlinedIcon from '@mui/icons-material/Inventory2Outlined';
import LocalCafeOutlinedIcon from '@mui/icons-material/LocalCafeOutlined';
import PointOfSaleOutlinedIcon from '@mui/icons-material/PointOfSaleOutlined';
import ReceiptLongOutlinedIcon from '@mui/icons-material/ReceiptLongOutlined';
import TableRestaurantOutlinedIcon from '@mui/icons-material/TableRestaurantOutlined';
import WarningAmberOutlinedIcon from '@mui/icons-material/WarningAmberOutlined';
import {
  Alert,
  Box,
  Button,
  CircularProgress,
  Stack,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
  Typography,
} from '@mui/material';
import { useEffect, useMemo, useState } from 'react';
import { Link as RouterLink, useNavigate } from 'react-router-dom';
import EmptyState from '../../components/EmptyState';
import IndustryDashboardPanel from '../../components/IndustryDashboardPanel';
import KpiCard from '../../components/KpiCard';
import PageShell from '../../components/PageShell';
import Section from '../../components/Section';
import TableCard from '../../components/TableCard';
import { PageActions } from '../../context/PageActionsContext';
import { useAuth } from '../../context/AuthContext';
import { useModuleGate } from '../../context/ModulesContext';
import { fetchTodaySummary, listBills } from '../../services/billService';
import { listItems } from '../../services/itemService';
import { listTables } from '../../services/tableService';
import { PATHS } from '../../routes/paths';
import { paymentMethodLabel } from '../../utils/paymentMethod';

function money(value) {
  return `₹${Number(value || 0).toLocaleString('en-IN', {
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  })}`;
}

function moneyExact(value) {
  return `₹${Number(value || 0).toLocaleString('en-IN', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  })}`;
}

/** Hotel-only simple desk home. Other business types keep the standard dashboard below. */
function HotelBillingHome({
  businessName,
  loading,
  error,
  summary,
  tableStats,
  lowStockCount,
  recent,
  navigate,
}) {
  return (
    <>
      <PageActions>
        <Stack direction="row" spacing={1}>
          <Button
            component={RouterLink}
            to={PATHS.billingRestaurantBilling}
            variant="contained"
            startIcon={<TableRestaurantOutlinedIcon />}
          >
            Table Bill
          </Button>
          <Button
            component={RouterLink}
            to={PATHS.billingNew}
            variant="outlined"
            startIcon={<PointOfSaleOutlinedIcon />}
          >
            Quick Bill
          </Button>
        </Stack>
      </PageActions>

      <PageShell spacing={2.5}>
        <Box>
          <Typography variant="h5" sx={{ fontWeight: 700, letterSpacing: '-0.02em' }}>
            {businessName}
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mt: 0.5 }}>
            Select a table, add items, take payment, print.
          </Typography>
        </Box>

        {error ? <Alert severity="error">{error}</Alert> : null}

        <Box
          sx={{
            display: 'grid',
            gap: 2,
            gridTemplateColumns: { xs: '1fr', sm: '1fr 1fr' },
          }}
        >
          <Box
            component="button"
            type="button"
            onClick={() => navigate(PATHS.billingRestaurantBilling)}
            sx={{
              textAlign: 'left',
              border: '2px solid',
              borderColor: 'primary.main',
              borderRadius: 2,
              p: { xs: 2.5, sm: 3 },
              cursor: 'pointer',
              bgcolor: 'background.paper',
              font: 'inherit',
              color: 'inherit',
              minHeight: 120,
              '&:hover': { bgcolor: 'action.hover' },
            }}
          >
            <Stack direction="row" spacing={1.5} alignItems="center" sx={{ mb: 1 }}>
              <TableRestaurantOutlinedIcon color="primary" sx={{ fontSize: 32 }} />
              <Typography variant="h5" sx={{ fontWeight: 800 }}>
                TABLE BILL
              </Typography>
            </Stack>
            <Typography variant="body2" color="text.secondary">
              Dining tables — add items, change qty, pay, print.
            </Typography>
          </Box>
          <Box
            component="button"
            type="button"
            onClick={() => navigate(PATHS.billingNew)}
            sx={{
              textAlign: 'left',
              border: '1px solid',
              borderColor: 'divider',
              borderRadius: 2,
              p: { xs: 2.5, sm: 3 },
              cursor: 'pointer',
              bgcolor: 'background.paper',
              font: 'inherit',
              color: 'inherit',
              minHeight: 120,
              '&:hover': { borderColor: 'primary.main', bgcolor: 'action.hover' },
            }}
          >
            <Stack direction="row" spacing={1.5} alignItems="center" sx={{ mb: 1 }}>
              <PointOfSaleOutlinedIcon color="primary" sx={{ fontSize: 32 }} />
              <Typography variant="h5" sx={{ fontWeight: 800 }}>
                QUICK BILL
              </Typography>
            </Stack>
            <Typography variant="body2" color="text.secondary">
              No table — walk-in / takeaway bill.
            </Typography>
          </Box>
        </Box>

        <Box
          sx={{
            display: 'grid',
            gap: 1.5,
            gridTemplateColumns: {
              xs: '1fr 1fr',
              md: 'repeat(5, 1fr)',
            },
          }}
        >
          <KpiCard
            title="Today's Sales"
            value={loading ? '—' : money(summary.total_sales)}
            icon={<PointOfSaleOutlinedIcon fontSize="small" />}
          />
          <KpiCard
            title="Active Tables"
            value={loading ? '—' : tableStats.occupied + tableStats.bill_pending}
            icon={<TableRestaurantOutlinedIcon fontSize="small" />}
          />
          <KpiCard
            title="Available Tables"
            value={loading ? '—' : tableStats.available}
            icon={<TableRestaurantOutlinedIcon fontSize="small" />}
          />
          <KpiCard
            title="Pending Bills"
            value={loading ? '—' : tableStats.bill_pending}
            icon={<WarningAmberOutlinedIcon fontSize="small" />}
          />
          <KpiCard
            title="Low Stock"
            value={loading ? '—' : lowStockCount}
            icon={<Inventory2OutlinedIcon fontSize="small" />}
          />
        </Box>

        <Stack direction="row" spacing={1} flexWrap="wrap" useFlexGap>
          <Button
            component={RouterLink}
            to={PATHS.billingRestaurantBilling}
            variant="contained"
            size="small"
            startIcon={<TableRestaurantOutlinedIcon />}
          >
            Table Bill
          </Button>
          <Button
            component={RouterLink}
            to={PATHS.billingNew}
            variant="outlined"
            size="small"
            startIcon={<PointOfSaleOutlinedIcon />}
          >
            Quick Bill
          </Button>
          <Button
            component={RouterLink}
            to={PATHS.billingTables}
            variant="outlined"
            size="small"
            startIcon={<TableRestaurantOutlinedIcon />}
          >
            Tables
          </Button>
          <Button
            component={RouterLink}
            to={PATHS.billingItems}
            variant="outlined"
            size="small"
            startIcon={<Inventory2OutlinedIcon />}
          >
            Add Item
          </Button>
          <Button
            component={RouterLink}
            to={PATHS.billingCategories}
            variant="outlined"
            size="small"
            startIcon={<CategoryOutlinedIcon />}
          >
            Add Category
          </Button>
        </Stack>

        <Section
          title="Today's Bills"
          description="Latest bills from this desk."
          actions={
            <Button component={RouterLink} to={PATHS.billingBills} size="small">
              View all
            </Button>
          }
        >
          <TableCard>
            {loading ? (
              <Box sx={{ py: 4, display: 'grid', placeItems: 'center' }}>
                <CircularProgress size={28} />
              </Box>
            ) : (
              <Table size="small" sx={{ minWidth: 360 }}>
                <TableHead>
                  <TableRow>
                    <TableCell>Bill</TableCell>
                    <TableCell>Payment</TableCell>
                    <TableCell align="right">Total</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {recent.map((bill) => (
                    <TableRow key={bill.id} hover>
                      <TableCell sx={{ fontWeight: 600 }}>#{bill.bill_number}</TableCell>
                      <TableCell>
                        {bill.payment_method_label || paymentMethodLabel(bill.payment_method)}
                      </TableCell>
                      <TableCell align="right" sx={{ fontWeight: 650 }}>
                        {moneyExact(bill.grand_total)}
                      </TableCell>
                    </TableRow>
                  ))}
                  {!recent.length ? (
                    <TableRow>
                      <TableCell colSpan={3} sx={{ p: 0, border: 0 }}>
                        <EmptyState
                          title="No bills yet today"
                          description="Start with Table Bill or Quick Bill."
                          actionLabel="Table Bill"
                          onAction={() => navigate(PATHS.billingRestaurantBilling)}
                        />
                      </TableCell>
                    </TableRow>
                  ) : null}
                </TableBody>
              </Table>
            )}
          </TableCard>
        </Section>
      </PageShell>
    </>
  );
}

/** Cafe desk home — Cafe POS first (add-ons / combos), not Hotel table billing. */
function CafeBillingHome({
  businessName,
  loading,
  error,
  summary,
  lowStockCount,
  recent,
  navigate,
  billCount,
}) {
  return (
    <>
      <PageActions>
        <Stack direction="row" spacing={1}>
          <Button
            component={RouterLink}
            to={PATHS.billingCafe}
            variant="contained"
            startIcon={<LocalCafeOutlinedIcon />}
          >
            Cafe POS
          </Button>
          <Button
            component={RouterLink}
            to={PATHS.billingNew}
            variant="outlined"
            startIcon={<PointOfSaleOutlinedIcon />}
          >
            Quick Bill
          </Button>
        </Stack>
      </PageActions>

      <PageShell spacing={2.5}>
        <Box>
          <Typography variant="h5" sx={{ fontWeight: 700, letterSpacing: '-0.02em' }}>
            {businessName}
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mt: 0.5 }}>
            Cafe POS — add-ons, combos, take payment, print or WhatsApp.
          </Typography>
        </Box>

        {error ? <Alert severity="error">{error}</Alert> : null}

        <Box
          sx={{
            display: 'grid',
            gap: 2,
            gridTemplateColumns: { xs: '1fr', sm: '1fr 1fr' },
          }}
        >
          <Box
            component="button"
            type="button"
            onClick={() => navigate(PATHS.billingCafe)}
            sx={{
              textAlign: 'left',
              border: '2px solid',
              borderColor: 'primary.main',
              borderRadius: 2,
              p: { xs: 2.5, sm: 3 },
              cursor: 'pointer',
              bgcolor: 'background.paper',
              font: 'inherit',
              color: 'inherit',
              minHeight: 120,
              '&:hover': { bgcolor: 'action.hover' },
            }}
          >
            <Stack direction="row" spacing={1.5} alignItems="center" sx={{ mb: 1 }}>
              <LocalCafeOutlinedIcon color="primary" sx={{ fontSize: 32 }} />
              <Typography variant="h5" sx={{ fontWeight: 800 }}>
                CAFE POS
              </Typography>
            </Stack>
            <Typography variant="body2" color="text.secondary">
              Fast takeaway — menu, add-ons, combos, pay, print.
            </Typography>
          </Box>
          <Box
            component="button"
            type="button"
            onClick={() => navigate(PATHS.billingNew)}
            sx={{
              textAlign: 'left',
              border: '1px solid',
              borderColor: 'divider',
              borderRadius: 2,
              p: { xs: 2.5, sm: 3 },
              cursor: 'pointer',
              bgcolor: 'background.paper',
              font: 'inherit',
              color: 'inherit',
              minHeight: 120,
              '&:hover': { borderColor: 'primary.main', bgcolor: 'action.hover' },
            }}
          >
            <Stack direction="row" spacing={1.5} alignItems="center" sx={{ mb: 1 }}>
              <PointOfSaleOutlinedIcon color="primary" sx={{ fontSize: 32 }} />
              <Typography variant="h5" sx={{ fontWeight: 800 }}>
                QUICK BILL
              </Typography>
            </Stack>
            <Typography variant="body2" color="text.secondary">
              Standard item bill without cafe add-ons.
            </Typography>
          </Box>
        </Box>

        <Box
          sx={{
            display: 'grid',
            gap: 1.5,
            gridTemplateColumns: {
              xs: '1fr 1fr',
              md: 'repeat(3, 1fr)',
            },
          }}
        >
          <KpiCard
            title="Today's Sales"
            value={loading ? '—' : money(summary.total_sales)}
            icon={<LocalCafeOutlinedIcon fontSize="small" />}
          />
          <KpiCard
            title="Bills Today"
            value={loading ? '—' : billCount ?? summary.bill_count ?? 0}
            icon={<ReceiptLongOutlinedIcon fontSize="small" />}
          />
          <KpiCard
            title="Low Stock"
            value={loading ? '—' : lowStockCount}
            icon={<Inventory2OutlinedIcon fontSize="small" />}
          />
        </Box>

        <Stack direction="row" spacing={1} flexWrap="wrap" useFlexGap>
          <Button
            component={RouterLink}
            to={PATHS.billingCafe}
            variant="contained"
            size="small"
            startIcon={<LocalCafeOutlinedIcon />}
          >
            Cafe POS
          </Button>
          <Button
            component={RouterLink}
            to={PATHS.billingBills}
            variant="outlined"
            size="small"
            startIcon={<ReceiptLongOutlinedIcon />}
          >
            Today&apos;s Bills
          </Button>
          <Button
            component={RouterLink}
            to={PATHS.billingCustomers}
            variant="outlined"
            size="small"
          >
            Customers
          </Button>
          <Button
            component={RouterLink}
            to={PATHS.billingItems}
            variant="outlined"
            size="small"
            startIcon={<Inventory2OutlinedIcon />}
          >
            Items
          </Button>
        </Stack>

        <Section
          title="Today's Bills"
          description="Latest cafe bills from this desk."
          actions={
            <Button component={RouterLink} to={PATHS.billingBills} size="small">
              View all
            </Button>
          }
        >
          <TableCard>
            {loading ? (
              <Box sx={{ py: 4, display: 'grid', placeItems: 'center' }}>
                <CircularProgress size={28} />
              </Box>
            ) : (
              <Table size="small" sx={{ minWidth: 360 }}>
                <TableHead>
                  <TableRow>
                    <TableCell>Bill</TableCell>
                    <TableCell>Payment</TableCell>
                    <TableCell align="right">Total</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {recent.map((bill) => (
                    <TableRow key={bill.id} hover>
                      <TableCell sx={{ fontWeight: 600 }}>#{bill.bill_number}</TableCell>
                      <TableCell>
                        {bill.payment_method_label || paymentMethodLabel(bill.payment_method)}
                      </TableCell>
                      <TableCell align="right" sx={{ fontWeight: 650 }}>
                        {moneyExact(bill.grand_total)}
                      </TableCell>
                    </TableRow>
                  ))}
                  {!recent.length ? (
                    <TableRow>
                      <TableCell colSpan={3} sx={{ p: 0, border: 0 }}>
                        <EmptyState
                          title="No bills yet today"
                          description="Start with Cafe POS for takeaway with add-ons and combos."
                          actionLabel="Cafe POS"
                          onAction={() => navigate(PATHS.billingCafe)}
                        />
                      </TableCell>
                    </TableRow>
                  ) : null}
                </TableBody>
              </Table>
            )}
          </TableCard>
        </Section>
      </PageShell>
    </>
  );
}

export default function BillingHomePage() {
  const { role, user } = useAuth();
  const navigate = useNavigate();
  const businessName = user?.tenant?.business_name || user?.tenant?.name || 'Billing';
  const businessTypeLabel = user?.tenant?.business_type_label || null;
  const businessType = user?.tenant?.business_type || '';
  const isHotel = businessType === 'hotel_restaurant';
  const isCafe = businessType === 'cafe_tea';
  const tablesEnabled = useModuleGate('table_management');
  const cafePosEnabled = useModuleGate('addons_combos');
  const [summary, setSummary] = useState({ total_sales: 0, bill_count: 0 });
  const [recent, setRecent] = useState([]);
  const [tables, setTables] = useState([]);
  const [lowStockCount, setLowStockCount] = useState(0);
  const [waFailedCount, setWaFailedCount] = useState(0);
  const [emailFailedCount, setEmailFailedCount] = useState(0);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    const tasks = [
      fetchTodaySummary(),
      listBills({ today: true, per_page: 5 }),
      listBills({ whatsapp_status: 'FAILED', per_page: 1 }),
      listBills({ email_status: 'FAILED', per_page: 1 }),
    ];
    if ((isHotel && tablesEnabled) || isCafe) {
      if (isHotel && tablesEnabled) {
        tasks.push(listTables().catch(() => ({ data: [] })));
      } else {
        tasks.push(Promise.resolve(null));
      }
      tasks.push(
        listItems({ is_active: true, per_page: 200 }).catch(() => ({ data: [] })),
      );
    }
    Promise.all(tasks)
      .then((results) => {
        const [summaryRes, billsRes, failedRes, emailFailedRes, tablesRes, itemsRes] = results;
        setSummary(summaryRes.data || { total_sales: 0, bill_count: 0 });
        setRecent(billsRes.data || []);
        setWaFailedCount(failedRes.meta?.total || 0);
        setEmailFailedCount(emailFailedRes.meta?.total || 0);
        if (tablesRes) setTables(tablesRes.data || []);
        if (itemsRes) {
          const low = (itemsRes.data || []).filter((item) => {
            if (item.stock_quantity == null || item.minimum_stock_level == null) return false;
            return Number(item.stock_quantity) <= Number(item.minimum_stock_level);
          }).length;
          setLowStockCount(low);
        }
      })
      .catch((err) => {
        setError(err.response?.data?.error?.message || 'Failed to load billing dashboard');
      })
      .finally(() => setLoading(false));
  }, [isHotel, isCafe, tablesEnabled]);

  const tableStats = useMemo(() => {
    const stats = {
      total: tables.length,
      available: 0,
      occupied: 0,
      reserved: 0,
      bill_pending: 0,
    };
    tables.forEach((table) => {
      if (stats[table.status] != null) stats[table.status] += 1;
    });
    return stats;
  }, [tables]);

  if (isHotel && tablesEnabled) {
    return (
      <HotelBillingHome
        businessName={businessName}
        loading={loading}
        error={error}
        summary={summary}
        tableStats={tableStats}
        lowStockCount={lowStockCount}
        recent={recent}
        navigate={navigate}
      />
    );
  }

  if (isCafe && cafePosEnabled) {
    return (
      <CafeBillingHome
        businessName={businessName}
        loading={loading}
        error={error}
        summary={summary}
        lowStockCount={lowStockCount}
        recent={recent}
        navigate={navigate}
        billCount={summary.bill_count}
      />
    );
  }

  return (
    <>
      <PageActions>
        <Button
          component={RouterLink}
          to={PATHS.billingNew}
          variant="contained"
          startIcon={<PointOfSaleOutlinedIcon />}
        >
          New Bill
        </Button>
      </PageActions>

      <PageShell>
        <Box sx={{ mb: 0.5 }}>
          <Typography variant="h5" component="h1" sx={{ fontWeight: 700, letterSpacing: '-0.02em' }}>
            {businessName}
          </Typography>
          {businessTypeLabel ? (
            <Typography variant="body2" color="text.secondary" sx={{ mt: 0.5 }}>
              {businessTypeLabel} · Billing dashboard
            </Typography>
          ) : (
            <Typography variant="body2" color="text.secondary" sx={{ mt: 0.5 }}>
              Billing dashboard
            </Typography>
          )}
        </Box>
        {role === 'OWNER' ? (
          <Alert severity="info">
            You are in the Billing workspace. Use <strong>Owner Dashboard</strong> in the sidebar
            to return to the main Owner console.
          </Alert>
        ) : null}
        {error ? <Alert severity="error">{error}</Alert> : null}

        <IndustryDashboardPanel compact workspace="billing" />

        {waFailedCount > 0 ? (
          <Alert
            severity="warning"
            action={
              <Button
                color="inherit"
                size="small"
                component={RouterLink}
                to={`${PATHS.billingBills}?whatsapp_status=FAILED`}
              >
                View bills
              </Button>
            }
          >
            {waFailedCount} WhatsApp bill{waFailedCount === 1 ? '' : 's'} failed to deliver — retry
            from Bills.
          </Alert>
        ) : null}
        {emailFailedCount > 0 ? (
          <Alert
            severity="warning"
            action={
              <Button
                color="inherit"
                size="small"
                component={RouterLink}
                to={`${PATHS.billingBills}?email_status=FAILED`}
              >
                View bills
              </Button>
            }
          >
            {emailFailedCount} email bill{emailFailedCount === 1 ? '' : 's'} failed to send — retry
            from Bills.
          </Alert>
        ) : null}

        <Box
          sx={{
            display: 'grid',
            gap: 2,
            gridTemplateColumns: {
              xs: '1fr',
              sm: '1fr 1fr',
              lg: 'repeat(4, 1fr)',
            },
          }}
        >
          <KpiCard
            title="Today's Bills"
            value={loading ? '—' : summary.bill_count}
            icon={<ReceiptLongOutlinedIcon fontSize="small" />}
          />
          <KpiCard
            title="Today's Sales"
            value={loading ? '—' : moneyExact(summary.total_sales)}
            icon={<PointOfSaleOutlinedIcon fontSize="small" />}
          />
          <KpiCard
            title="Cash"
            value={loading ? '—' : moneyExact(summary.cash_sales)}
            hint="Today's cash sales"
          />
          <KpiCard
            title="Online"
            value={loading ? '—' : moneyExact(summary.online_sales)}
            hint="Today's online sales"
          />
        </Box>

        <Section
          title="Recent Bills"
          description="Latest bills created today."
          actions={
            <Button component={RouterLink} to={PATHS.billingBills} size="small">
              View all
            </Button>
          }
        >
          <TableCard>
            {loading ? (
              <Box sx={{ py: 6, display: 'grid', placeItems: 'center' }}>
                <CircularProgress size={28} />
              </Box>
            ) : (
              <Table size="small" sx={{ minWidth: 480 }}>
                <TableHead>
                  <TableRow>
                    <TableCell>Bill No</TableCell>
                    <TableCell>Payment</TableCell>
                    <TableCell>Status</TableCell>
                    <TableCell align="right">Total</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {recent.map((bill) => (
                    <TableRow key={bill.id} hover>
                      <TableCell sx={{ fontWeight: 600, fontVariantNumeric: 'tabular-nums' }}>
                        #{bill.bill_number}
                      </TableCell>
                      <TableCell>
                        {bill.payment_method_label || paymentMethodLabel(bill.payment_method)}
                      </TableCell>
                      <TableCell>{bill.status}</TableCell>
                      <TableCell align="right" sx={{ fontVariantNumeric: 'tabular-nums', fontWeight: 650 }}>
                        {moneyExact(bill.grand_total)}
                      </TableCell>
                    </TableRow>
                  ))}
                  {!recent.length ? (
                    <TableRow>
                      <TableCell colSpan={4} sx={{ p: 0, border: 0 }}>
                        <EmptyState
                          title="No bills yet today"
                          description="Create a new bill to see it here."
                          actionLabel="New Bill"
                          onAction={() => navigate(PATHS.billingNew)}
                        />
                      </TableCell>
                    </TableRow>
                  ) : null}
                </TableBody>
              </Table>
            )}
          </TableCard>
        </Section>
      </PageShell>
    </>
  );
}
