import AddOutlinedIcon from '@mui/icons-material/AddOutlined';
import {
  Alert,
  Box,
  Button,
  Chip,
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
  Typography,
} from '@mui/material';
import { useCallback, useEffect, useState } from 'react';
import { Link as RouterLink, useNavigate } from 'react-router-dom';
import EmptyState from '../../components/EmptyState';
import FilterBar from '../../components/FilterBar';
import LoadingBlock from '../../components/LoadingBlock';
import PageShell from '../../components/PageShell';
import PaginationBar from '../../components/PaginationBar';
import TableCard from '../../components/TableCard';
import TruncateText from '../../components/TruncateText';
import { PageActions } from '../../context/PageActionsContext';
import { useModuleGate } from '../../context/ModulesContext';
import { useAuth } from '../../context/AuthContext';
import { filterControlSx } from '../../layouts/shell';
import { PATHS } from '../../routes/paths';
import { cancelOrder, getOrder, listOrders } from '../../services/orderService';
import { fireKot } from '../../services/kotService';
import SettleOrderDialog from '../../components/SettleOrderDialog';
import { usePermissions } from '../../hooks/usePermissions';

const CHANNEL_LABELS = {
  dine_in: 'Dine-in',
  takeaway: 'Takeaway',
  delivery: 'Delivery',
};

const STATUS_COLORS = {
  OPEN: 'warning',
  CANCELLED: 'default',
  BILLED: 'success',
};

function money(value) {
  return `₹${Number(value || 0).toLocaleString('en-IN', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  })}`;
}

export default function OrdersPage() {
  const navigate = useNavigate();
  const { role } = useAuth();
  const { canFireKot, canBilling } = usePermissions();
  const moduleEnabled = useModuleGate('order_channels');
  const newOrderPath = role === 'OWNER' ? PATHS.ownerOrdersNew : PATHS.billingOrdersNew;
  const [orders, setOrders] = useState([]);
  const [meta, setMeta] = useState({ page: 1, per_page: 25, total: 0 });
  const [statusFilter, setStatusFilter] = useState('OPEN');
  const [channelFilter, setChannelFilter] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [detail, setDetail] = useState(null);
  const [detailOpen, setDetailOpen] = useState(false);
  const [firingKot, setFiringKot] = useState(false);
  const [settleOpen, setSettleOpen] = useState(false);

  const load = useCallback(
    async (page = 1) => {
      if (!moduleEnabled) return;
      setLoading(true);
      setError('');
      try {
        const response = await listOrders({
          page,
          per_page: 25,
          status: statusFilter || undefined,
          channel: channelFilter || undefined,
        });
        setOrders(response.data || []);
        setMeta(response.meta || { page: 1, per_page: 25, total: 0 });
      } catch (err) {
        setError(err.response?.data?.error?.message || 'Unable to load orders.');
      } finally {
        setLoading(false);
      }
    },
    [moduleEnabled, statusFilter, channelFilter],
  );

  useEffect(() => {
    load(1);
  }, [load]);

  const openDetail = async (orderId) => {
    try {
      const response = await getOrder(orderId);
      setDetail(response.data);
      setDetailOpen(true);
    } catch (err) {
      setError(err.response?.data?.error?.message || 'Unable to load order.');
    }
  };

  const onCancel = async (orderId) => {
    try {
      await cancelOrder(orderId, 'Cancelled from orders list');
      setDetailOpen(false);
      await load(meta.page);
    } catch (err) {
      setError(err.response?.data?.error?.message || 'Unable to cancel order.');
    }
  };

  const onFireKot = async (orderId) => {
    setFiringKot(true);
    setError('');
    try {
      const response = await fireKot(orderId);
      const kot = response.data;
      navigate(`/print/kots/${kot.id}`, {
        state: {
          from: role === 'OWNER' || role === 'MANAGER' ? PATHS.ownerOrders : PATHS.billingOrders,
        },
      });
      setDetail((current) => (current?.id === orderId ? { ...current, last_kot_id: kot.id } : current));
    } catch (err) {
      setError(err.response?.data?.error?.message || 'Unable to fire KOT.');
    } finally {
      setFiringKot(false);
    }
  };

  const onSettled = async (result) => {
    setDetailOpen(false);
    await load(meta.page);
    const firstBill = result?.bills?.[0];
    if (firstBill?.id) {
      window.open(`/print/bills/${firstBill.id}?auto=1`, '_blank', 'noopener,noreferrer');
    }
  };

  if (!moduleEnabled) {
    return (
      <PageShell>
        <Alert severity="warning">Order channels are not enabled for this business type.</Alert>
      </PageShell>
    );
  }

  return (
    <>
      <PageActions>
        <Button component={RouterLink} to={newOrderPath} variant="contained" startIcon={<AddOutlinedIcon />}>
          New order
        </Button>
      </PageActions>

      <PageShell>
        <Stack spacing={2}>
          <FilterBar>
            <FormControl sx={filterControlSx}>
              <InputLabel>Status</InputLabel>
              <Select label="Status" value={statusFilter} onChange={(e) => setStatusFilter(e.target.value)}>
                <MenuItem value="">All</MenuItem>
                <MenuItem value="OPEN">Open</MenuItem>
                <MenuItem value="CANCELLED">Cancelled</MenuItem>
                <MenuItem value="BILLED">Billed</MenuItem>
              </Select>
            </FormControl>
            <FormControl sx={filterControlSx}>
              <InputLabel>Channel</InputLabel>
              <Select label="Channel" value={channelFilter} onChange={(e) => setChannelFilter(e.target.value)}>
                <MenuItem value="">All channels</MenuItem>
                <MenuItem value="dine_in">Dine-in</MenuItem>
                <MenuItem value="takeaway">Takeaway</MenuItem>
                <MenuItem value="delivery">Delivery</MenuItem>
              </Select>
            </FormControl>
          </FilterBar>

          {error ? <Alert severity="error">{error}</Alert> : null}

          <TableCard>
            {loading ? (
              <LoadingBlock />
            ) : orders.length === 0 ? (
              <EmptyState
                title="No orders found"
                description="Create dine-in, takeaway, or delivery orders before billing."
                actionLabel="New order"
                onAction={() => navigate(newOrderPath)}
              />
            ) : (
              <>
                <Table size="small">
                  <TableHead>
                    <TableRow>
                      <TableCell>Order #</TableCell>
                      <TableCell>Channel</TableCell>
                      <TableCell>Table / Customer</TableCell>
                      <TableCell align="right">Items</TableCell>
                      <TableCell align="right">Total</TableCell>
                      <TableCell>Status</TableCell>
                      <TableCell align="right">Actions</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {orders.map((order) => (
                      <TableRow key={order.id} hover>
                        <TableCell>{order.order_number}</TableCell>
                        <TableCell>{CHANNEL_LABELS[order.channel] || order.channel}</TableCell>
                        <TableCell>
                          <TruncateText
                            value={
                              order.dining_table_code ||
                              order.customer_name ||
                              order.delivery_address ||
                              '—'
                            }
                            maxWidth={180}
                          />
                        </TableCell>
                        <TableCell align="right">{order.item_count ?? 0}</TableCell>
                        <TableCell align="right">{money(order.grand_total)}</TableCell>
                        <TableCell>
                          <Chip size="small" label={order.status} color={STATUS_COLORS[order.status] || 'default'} />
                        </TableCell>
                        <TableCell align="right">
                          <Button size="small" onClick={() => openDetail(order.id)}>
                            View
                          </Button>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
                <PaginationBar
                  page={meta.page}
                  perPage={meta.per_page}
                  total={meta.total}
                  onPageChange={(next) => load(next)}
                />
              </>
            )}
          </TableCard>
        </Stack>
      </PageShell>

      <Dialog open={detailOpen} onClose={() => setDetailOpen(false)} fullWidth maxWidth="sm">
        <DialogTitle>{detail?.order_number || 'Order detail'}</DialogTitle>
        <DialogContent>
          {detail ? (
            <Stack spacing={2} sx={{ mt: 1 }}>
              <Box>
                <Typography variant="body2" color="text.secondary">
                  {CHANNEL_LABELS[detail.channel]} · {detail.status}
                  {detail.dining_table_code ? ` · Table ${detail.dining_table_code}` : ''}
                </Typography>
              </Box>
              {detail.items?.length ? (
                <Table size="small">
                  <TableHead>
                    <TableRow>
                      <TableCell>Item</TableCell>
                      <TableCell align="right">Qty</TableCell>
                      <TableCell align="right">Total</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {detail.items.map((line) => (
                      <TableRow key={line.id}>
                        <TableCell>{line.item_name}</TableCell>
                        <TableCell align="right">{line.quantity}</TableCell>
                        <TableCell align="right">{money(line.line_total)}</TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              ) : (
                <Typography variant="body2" color="text.secondary">
                  No items on this order yet.
                </Typography>
              )}
              <Typography variant="subtitle1" align="right">
                Grand total: {money(detail.grand_total)}
              </Typography>
            </Stack>
          ) : null}
        </DialogContent>
        <DialogActions>
          {detail?.status === 'OPEN' && canFireKot && detail.items?.length ? (
            <Button
              variant="contained"
              color="secondary"
              disabled={firingKot}
              onClick={() => onFireKot(detail.id)}
            >
              {firingKot ? 'Sending…' : 'Fire KOT'}
            </Button>
          ) : null}
          {detail?.status === 'OPEN' && canBilling && detail.items?.length ? (
            <Button variant="contained" onClick={() => setSettleOpen(true)}>
              Settle & bill
            </Button>
          ) : null}
          {detail?.status === 'OPEN' ? (
            <Button color="error" onClick={() => onCancel(detail.id)}>
              Cancel order
            </Button>
          ) : null}
          <Button onClick={() => setDetailOpen(false)}>Close</Button>
        </DialogActions>
      </Dialog>

      <SettleOrderDialog
        open={settleOpen}
        order={detail}
        onClose={() => setSettleOpen(false)}
        onSettled={onSettled}
      />
    </>
  );
}
