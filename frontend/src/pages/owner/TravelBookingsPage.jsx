import AddOutlinedIcon from '@mui/icons-material/AddOutlined';
import LuggageOutlinedIcon from '@mui/icons-material/LuggageOutlined';
import RefreshOutlinedIcon from '@mui/icons-material/RefreshOutlined';
import {
  Alert,
  Box,
  Button,
  Card,
  CardActions,
  CardContent,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  Divider,
  Grid,
  MenuItem,
  Stack,
  Tab,
  Tabs,
  TextField,
  Typography,
} from '@mui/material';
import DeleteOutlinedIcon from '@mui/icons-material/DeleteOutlined';
import { useCallback, useEffect, useMemo, useState } from 'react';
import EmptyState from '../../components/EmptyState';
import LoadingBlock from '../../components/LoadingBlock';
import PageShell from '../../components/PageShell';
import IconActionButton from '../../components/ui/IconActionButton';
import StatusBadge from '../../components/ui/StatusBadge';
import { PageActions } from '../../context/PageActionsContext';
import { useAuth } from '../../context/AuthContext';
import { useModuleGate } from '../../context/ModulesContext';
import { usePermissions } from '../../hooks/usePermissions';
import { listTourPackages } from '../../services/tourPackageService';
import { listTravelAgents } from '../../services/travelAgentService';
import {
  createTravelBooking,
  createTravelDocument,
  createTravelItineraryItem,
  deleteTravelBooking,
  deleteTravelDocument,
  deleteTravelItineraryItem,
  listTravelBookings,
  listTravelDocuments,
  listTravelItinerary,
  recordTravelBookingPayment,
  updateTravelBooking,
  updateTravelBookingStatus,
} from '../../services/travelBookingService';
import { PAYMENT_CASH, PAYMENT_ONLINE } from '../../utils/paymentMethod';

const COLUMNS = [
  { key: 'BOOKED', label: 'Booked', color: '#ffb74d' },
  { key: 'CONFIRMED', label: 'Confirmed', color: '#64b5f6' },
  { key: 'IN_PROGRESS', label: 'In progress', color: '#ba68c8' },
  { key: 'COMPLETED', label: 'Completed', color: '#81c784' },
];

const NEXT_ACTIONS = {
  BOOKED: [{ status: 'CONFIRMED', label: 'Confirm' }],
  CONFIRMED: [{ status: 'IN_PROGRESS', label: 'Start trip' }],
  IN_PROGRESS: [{ status: 'COMPLETED', label: 'Complete' }],
  COMPLETED: [],
};

const ITINERARY_TYPES = ['HOTEL', 'VEHICLE', 'TICKET', 'ACTIVITY', 'OTHER'];
const DOCUMENT_TYPES = ['PASSPORT', 'VISA', 'ID', 'TICKET_COPY', 'OTHER'];

function money(v) {
  return `₹${Number(v || 0).toFixed(2)}`;
}

function bookingStatusVariant(status) {
  if (status === 'COMPLETED') return 'active';
  if (status === 'BOOKED' || status === 'IN_PROGRESS') return 'pending';
  if (status === 'CONFIRMED') return 'info';
  return 'info';
}

function BookingCard({ booking, onStatusChange, onPayment, onOpenDetail, onEdit, onDelete, updating, canManage, canPay, isOwner }) {
  const actions = NEXT_ACTIONS[booking.status] || [];
  return (
    <Card variant="outlined">
      <CardContent sx={{ pb: 1 }}>
        <Stack spacing={1}>
          <Stack direction="row" justifyContent="space-between" alignItems="center">
            <Typography variant="subtitle1" fontWeight={700}>
              {booking.booking_number}
            </Typography>
            <StatusBadge
              label={booking.status.replaceAll('_', ' ')}
              variant={bookingStatusVariant(booking.status)}
            />
          </Stack>
          <Typography variant="body1">{booking.package_name}</Typography>
          <Typography variant="body2" color="text.secondary">
            {booking.customer_name || 'Walk-in'}
            {booking.pax_count ? ` · ${booking.pax_count} pax` : ''}
          </Typography>
          {booking.travel_start_at ? (
            <Typography variant="body2">
              Travel {new Date(booking.travel_start_at).toLocaleDateString()}
            </Typography>
          ) : null}
          <Typography variant="body2">
            Total {money(booking.total_amount)} · Paid {money(booking.advance_paid)} · Due{' '}
            {money(booking.remaining_amount)}
          </Typography>
          {booking.agent_name ? (
            <Typography variant="caption" color="text.secondary">
              Agent {booking.agent_code || ''} {booking.agent_name}
              {booking.commission
                ? ` · commission ${money(booking.commission.commission_amount)}`
                : ''}
            </Typography>
          ) : null}
          {(booking.itinerary_count || booking.document_count) ? (
            <Typography variant="caption" color="text.secondary">
              {booking.itinerary_count || 0} itinerary · {booking.document_count || 0} docs
            </Typography>
          ) : null}
        </Stack>
      </CardContent>
      <CardActions sx={{ flexWrap: 'wrap', gap: 1, px: 2, pb: 2 }}>
        <Button size="small" variant="text" disabled={updating} onClick={() => onOpenDetail(booking)}>
          Details
        </Button>
        {canManage
          ? actions.map((action) => (
              <Button
                key={action.status}
                size="small"
                variant="contained"
                disabled={updating}
                onClick={() => onStatusChange(booking.id, action.status)}
              >
                {action.label}
              </Button>
            ))
          : null}
        {canPay && Number(booking.remaining_amount) > 0 ? (
          <Button size="small" variant="outlined" disabled={updating} onClick={() => onPayment(booking)}>
            Record payment
          </Button>
        ) : null}
        {isOwner && booking.status !== 'COMPLETED' && booking.status !== 'CANCELLED' ? (
          <>
            <Button size="small" variant="outlined" disabled={updating} onClick={() => onEdit(booking)}>
              Edit
            </Button>
            <Button size="small" color="error" variant="outlined" disabled={updating} onClick={() => onDelete(booking)}>
              Remove
            </Button>
          </>
        ) : null}
      </CardActions>
    </Card>
  );
}

export default function TravelBookingsPage() {
  const moduleEnabled = useModuleGate('travel_bookings');
  const { role } = useAuth();
  const { isOwner } = usePermissions();
  const canManage = role === 'OWNER' || role === 'MANAGER';
  const canPay = role === 'OWNER' || role === 'MANAGER' || role === 'BILLING_USER';

  const [rows, setRows] = useState([]);
  const [packages, setPackages] = useState([]);
  const [agents, setAgents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [updating, setUpdating] = useState(false);

  const [createOpen, setCreateOpen] = useState(false);
  const [editBooking, setEditBooking] = useState(null);
  const [deleteBooking, setDeleteBooking] = useState(null);
  const [packageId, setPackageId] = useState('');
  const [agentId, setAgentId] = useState('');
  const [customerName, setCustomerName] = useState('');
  const [paxCount, setPaxCount] = useState('1');
  const [advanceAmount, setAdvanceAmount] = useState('');
  const [createPayMethod, setCreatePayMethod] = useState(PAYMENT_CASH);
  const [travelStart, setTravelStart] = useState('');
  const [notes, setNotes] = useState('');

  const [payOpen, setPayOpen] = useState(false);
  const [payTarget, setPayTarget] = useState(null);
  const [payAmount, setPayAmount] = useState('');
  const [payMethod, setPayMethod] = useState(PAYMENT_CASH);

  const [detailOpen, setDetailOpen] = useState(false);
  const [detailBooking, setDetailBooking] = useState(null);
  const [detailTab, setDetailTab] = useState(0);
  const [itinerary, setItinerary] = useState([]);
  const [documents, setDocuments] = useState([]);
  const [detailLoading, setDetailLoading] = useState(false);

  const [itemType, setItemType] = useState('HOTEL');
  const [itemTitle, setItemTitle] = useState('');
  const [itemDay, setItemDay] = useState('1');
  const [itemLocation, setItemLocation] = useState('');
  const [itemVendor, setItemVendor] = useState('');
  const [itemRef, setItemRef] = useState('');

  const [docType, setDocType] = useState('PASSPORT');
  const [docHolder, setDocHolder] = useState('');
  const [docNumber, setDocNumber] = useState('');
  const [docCountry, setDocCountry] = useState('');
  const [docExpiry, setDocExpiry] = useState('');
  const [docFile, setDocFile] = useState('');

  const load = useCallback(async () => {
    if (!moduleEnabled) return;
    setLoading(true);
    setError('');
    try {
      const [bookings, pkgs, agentRes] = await Promise.all([
        listTravelBookings({ per_page: 100 }),
        listTourPackages({ per_page: 100, active_only: true }),
        listTravelAgents({ per_page: 100, active_only: true }).catch(() => ({ data: [] })),
      ]);
      setRows(bookings.data || []);
      setPackages(pkgs.data || []);
      setAgents(agentRes.data || []);
    } catch (err) {
      setError(err.response?.data?.error?.message || 'Failed to load bookings');
    } finally {
      setLoading(false);
    }
  }, [moduleEnabled]);

  useEffect(() => {
    load();
  }, [load]);

  const loadDetail = useCallback(async (booking) => {
    if (!booking?.id) return;
    setDetailLoading(true);
    setError('');
    try {
      const [itin, docs] = await Promise.all([
        listTravelItinerary(booking.id),
        listTravelDocuments(booking.id),
      ]);
      setItinerary(itin.data || []);
      setDocuments(docs.data || []);
    } catch (err) {
      setError(err.response?.data?.error?.message || 'Failed to load booking details');
    } finally {
      setDetailLoading(false);
    }
  }, []);

  const openDetail = async (booking) => {
    setDetailBooking(booking);
    setDetailTab(0);
    setDetailOpen(true);
    await loadDetail(booking);
  };

  const byStatus = useMemo(() => {
    const map = Object.fromEntries(COLUMNS.map((c) => [c.key, []]));
    rows.forEach((row) => {
      if (map[row.status]) map[row.status].push(row);
    });
    return map;
  }, [rows]);

  const onCreate = async () => {
    if (!packageId && !editBooking) {
      setError('Select a package.');
      return;
    }
    setUpdating(true);
    setError('');
    try {
      if (editBooking) {
        await updateTravelBooking(editBooking.id, {
          customer_name: customerName.trim() || null,
          pax_count: Number(paxCount || 1),
          travel_start_at: travelStart ? `${travelStart}T00:00:00` : null,
          notes: notes.trim() || null,
          agent_id: agentId || null,
        });
        setCreateOpen(false);
        setEditBooking(null);
        setSuccess('Booking updated');
      } else {
        await createTravelBooking({
          package_id: packageId,
          agent_id: agentId || null,
          customer_name: customerName.trim() || null,
          pax_count: Number(paxCount || 1),
          advance_amount: advanceAmount === '' ? 0 : Number(advanceAmount),
          payment_method: createPayMethod,
          travel_start_at: travelStart ? `${travelStart}T00:00:00` : null,
          notes: notes.trim() || null,
        });
        setCreateOpen(false);
        setSuccess('Booking created');
      }
      setPackageId('');
      setAgentId('');
      setCustomerName('');
      setPaxCount('1');
      setAdvanceAmount('');
      setCreatePayMethod(PAYMENT_CASH);
      setTravelStart('');
      setNotes('');
      await load();
    } catch (err) {
      setError(err.response?.data?.error?.message || 'Could not save booking');
    } finally {
      setUpdating(false);
    }
  };

  const openEditBooking = (booking) => {
    setEditBooking(booking);
    setPackageId(booking.package_id || '');
    setAgentId(booking.agent_id || '');
    setCustomerName(booking.customer_name || '');
    setPaxCount(String(booking.pax_count || 1));
    setAdvanceAmount('');
    setTravelStart(
      booking.travel_start_at ? String(booking.travel_start_at).slice(0, 10) : '',
    );
    setNotes(booking.notes || '');
    setCreateOpen(true);
  };

  const onDeleteBooking = async () => {
    if (!deleteBooking) return;
    setUpdating(true);
    setError('');
    try {
      await deleteTravelBooking(deleteBooking.id);
      setDeleteBooking(null);
      setSuccess('Booking cancelled');
      await load();
    } catch (err) {
      setError(err.response?.data?.error?.message || 'Could not remove booking');
    } finally {
      setUpdating(false);
    }
  };

  const onStatusChange = async (id, status) => {
    setUpdating(true);
    setError('');
    try {
      await updateTravelBookingStatus(id, status);
      setSuccess(`Status → ${status.replaceAll('_', ' ')}`);
      await load();
    } catch (err) {
      setError(err.response?.data?.error?.message || 'Status update failed');
    } finally {
      setUpdating(false);
    }
  };

  const onPayment = (booking) => {
    setPayTarget(booking);
    setPayAmount(String(booking.remaining_amount || ''));
    setPayMethod(PAYMENT_CASH);
    setPayOpen(true);
  };

  const submitPayment = async () => {
    if (!payTarget) return;
    setUpdating(true);
    setError('');
    try {
      await recordTravelBookingPayment(payTarget.id, {
        amount: Number(payAmount),
        payment_method: payMethod,
      });
      setPayOpen(false);
      setSuccess('Payment recorded');
      await load();
    } catch (err) {
      setError(err.response?.data?.error?.message || 'Payment failed');
    } finally {
      setUpdating(false);
    }
  };

  const addItinerary = async () => {
    if (!detailBooking || !itemTitle.trim()) {
      setError('Itinerary title is required.');
      return;
    }
    setUpdating(true);
    setError('');
    try {
      await createTravelItineraryItem(detailBooking.id, {
        item_type: itemType,
        title: itemTitle.trim(),
        day_number: itemDay ? Number(itemDay) : null,
        location: itemLocation.trim() || null,
        vendor_name: itemVendor.trim() || null,
        confirmation_ref: itemRef.trim() || null,
      });
      setItemTitle('');
      setItemLocation('');
      setItemVendor('');
      setItemRef('');
      setSuccess('Itinerary item saved');
      await loadDetail(detailBooking);
      await load();
    } catch (err) {
      setError(err.response?.data?.error?.message || 'Could not save itinerary');
    } finally {
      setUpdating(false);
    }
  };

  const removeItinerary = async (itemId) => {
    if (!detailBooking) return;
    setUpdating(true);
    setError('');
    try {
      await deleteTravelItineraryItem(detailBooking.id, itemId);
      setSuccess('Itinerary item removed');
      await loadDetail(detailBooking);
      await load();
    } catch (err) {
      setError(err.response?.data?.error?.message || 'Could not delete itinerary item');
    } finally {
      setUpdating(false);
    }
  };

  const addDocument = async () => {
    if (!detailBooking) return;
    setUpdating(true);
    setError('');
    try {
      await createTravelDocument(detailBooking.id, {
        document_type: docType,
        holder_name: docHolder.trim() || null,
        document_number: docNumber.trim() || null,
        issued_country: docCountry.trim() || null,
        expiry_date: docExpiry || null,
        file_name: docFile.trim() || null,
      });
      setDocHolder('');
      setDocNumber('');
      setDocCountry('');
      setDocExpiry('');
      setDocFile('');
      setSuccess('Document metadata saved');
      await loadDetail(detailBooking);
      await load();
    } catch (err) {
      setError(err.response?.data?.error?.message || 'Could not save document');
    } finally {
      setUpdating(false);
    }
  };

  const removeDocument = async (documentId) => {
    if (!detailBooking) return;
    setUpdating(true);
    setError('');
    try {
      await deleteTravelDocument(detailBooking.id, documentId);
      setSuccess('Document removed');
      await loadDetail(detailBooking);
      await load();
    } catch (err) {
      setError(err.response?.data?.error?.message || 'Could not delete document');
    } finally {
      setUpdating(false);
    }
  };

  if (!moduleEnabled) {
    return (
      <PageShell>
        <EmptyState
          icon={<LuggageOutlinedIcon />}
          title="Travel bookings not enabled"
          description="Available for travel agency tenants."
        />
      </PageShell>
    );
  }

  return (
    <PageShell>
      <PageActions>
        <Stack direction="row" spacing={1}>
          <Button startIcon={<RefreshOutlinedIcon />} onClick={load} disabled={loading}>
            Refresh
          </Button>
          {canPay ? (
            <Button
              variant="contained"
              startIcon={<AddOutlinedIcon />}
              onClick={() => {
                setCreatePayMethod(PAYMENT_CASH);
                setCreateOpen(true);
              }}
            >
              Booking
            </Button>
          ) : null}
        </Stack>
      </PageActions>

      {error ? <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert> : null}
      {success ? <Alert severity="success" sx={{ mb: 2 }}>{success}</Alert> : null}
      {!canManage ? (
        <Alert severity="info" sx={{ mb: 2 }}>
          Billing users can create bookings and record payments. Owner/manager confirms trips and
          manages itinerary/documents.
        </Alert>
      ) : null}

      {loading ? (
        <LoadingBlock />
      ) : rows.length === 0 ? (
        <EmptyState
          icon={<LuggageOutlinedIcon />}
          title="No bookings yet"
          description="Create a booking against a tour package and collect advances."
        />
      ) : (
        <Grid container spacing={2}>
          {COLUMNS.map((col) => (
            <Grid item xs={12} sm={6} md={3} key={col.key}>
              <Box
                sx={{
                  borderTop: `4px solid ${col.color}`,
                  bgcolor: 'action.hover',
                  borderRadius: 1,
                  p: 1.5,
                  minHeight: 120,
                }}
              >
                <Typography variant="subtitle2" sx={{ mb: 1.5 }}>
                  {col.label} ({byStatus[col.key]?.length || 0})
                </Typography>
                <Stack spacing={1.5}>
                  {(byStatus[col.key] || []).map((booking) => (
                    <BookingCard
                      key={booking.id}
                      booking={booking}
                      onStatusChange={onStatusChange}
                      onPayment={onPayment}
                      onOpenDetail={openDetail}
                      onEdit={openEditBooking}
                      onDelete={setDeleteBooking}
                      updating={updating}
                      canManage={canManage}
                      canPay={canPay}
                      isOwner={isOwner}
                    />
                  ))}
                </Stack>
              </Box>
            </Grid>
          ))}
        </Grid>
      )}

      <Dialog
        open={createOpen}
        onClose={() => !updating && (setCreateOpen(false), setEditBooking(null))}
        fullWidth
        maxWidth="sm"
      >
        <DialogTitle>{editBooking ? 'Edit travel booking' : 'New travel booking'}</DialogTitle>
        <DialogContent>
          <Stack spacing={2} sx={{ mt: 1 }}>
            {!editBooking ? (
              <TextField
                select
                label="Package"
                value={packageId}
                onChange={(e) => setPackageId(e.target.value)}
                fullWidth
              >
                {packages.map((pkg) => (
                  <MenuItem key={pkg.id} value={pkg.id}>
                    {pkg.code} · {pkg.name}
                    {pkg.transport_type_label ? ` · ${pkg.transport_type_label}` : ''} ({money(pkg.base_price)})
                  </MenuItem>
                ))}
              </TextField>
            ) : (
              <TextField label="Package" value={editBooking.package_name || ''} fullWidth disabled />
            )}
            <TextField
              select
              label="Agent (optional)"
              value={agentId}
              onChange={(e) => setAgentId(e.target.value)}
              fullWidth
            >
              <MenuItem value="">None</MenuItem>
              {agents.map((agent) => (
                <MenuItem key={agent.id} value={agent.id}>
                  {agent.code} · {agent.name} ({Number(agent.commission_percent).toFixed(1)}%)
                </MenuItem>
              ))}
            </TextField>
            <TextField
              label="Customer name"
              value={customerName}
              onChange={(e) => setCustomerName(e.target.value)}
              fullWidth
            />
            <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2}>
              <TextField
                label="Pax count"
                type="number"
                value={paxCount}
                onChange={(e) => setPaxCount(e.target.value)}
                fullWidth
                inputProps={{ min: 1 }}
              />
              {!editBooking ? (
                <TextField
                  label="Advance (₹)"
                  type="number"
                  value={advanceAmount}
                  onChange={(e) => setAdvanceAmount(e.target.value)}
                  fullWidth
                  inputProps={{ min: 0, step: '0.01' }}
                />
              ) : null}
            </Stack>
            {!editBooking ? (
              <TextField
                select
                label="Payment method"
                value={createPayMethod}
                onChange={(e) => setCreatePayMethod(e.target.value)}
                fullWidth
                helperText={
                  Number(advanceAmount || 0) > 0
                    ? 'Method used when collecting the advance payment'
                    : 'Used if an advance amount is entered'
                }
              >
                <MenuItem value={PAYMENT_CASH}>Cash</MenuItem>
                <MenuItem value={PAYMENT_ONLINE}>Online</MenuItem>
              </TextField>
            ) : null}
            <TextField
              label="Travel start date"
              type="date"
              value={travelStart}
              onChange={(e) => setTravelStart(e.target.value)}
              fullWidth
              slotProps={{
                inputLabel: { shrink: true },
              }}
            />
            <TextField
              label="Notes"
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              fullWidth
              multiline
              minRows={2}
            />
          </Stack>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => !updating && (setCreateOpen(false), setEditBooking(null))} disabled={updating}>
            Cancel
          </Button>
          <Button variant="contained" onClick={onCreate} disabled={updating}>
            {updating ? 'Saving…' : editBooking ? 'Save' : 'Create'}
          </Button>
        </DialogActions>
      </Dialog>

      <Dialog open={Boolean(deleteBooking)} onClose={() => !updating && setDeleteBooking(null)} maxWidth="xs" fullWidth>
        <DialogTitle>Remove booking?</DialogTitle>
        <DialogContent>
          <Typography>
            Cancel booking <strong>{deleteBooking?.booking_number}</strong>? This marks it as cancelled.
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDeleteBooking(null)} disabled={updating}>
            Back
          </Button>
          <Button color="error" variant="contained" onClick={onDeleteBooking} disabled={updating}>
            {updating ? 'Removing…' : 'Remove'}
          </Button>
        </DialogActions>
      </Dialog>

      <Dialog open={payOpen} onClose={() => !updating && setPayOpen(false)} fullWidth maxWidth="xs">
        <DialogTitle>Record payment</DialogTitle>
        <DialogContent>
          <Stack spacing={2} sx={{ mt: 1 }}>
            <Typography variant="body2">
              {payTarget?.booking_number} · Due {money(payTarget?.remaining_amount)}
            </Typography>
            <TextField
              label="Amount"
              type="number"
              value={payAmount}
              onChange={(e) => setPayAmount(e.target.value)}
              fullWidth
            />
            <TextField
              select
              label="Method"
              value={payMethod}
              onChange={(e) => setPayMethod(e.target.value)}
              fullWidth
            >
              <MenuItem value={PAYMENT_CASH}>Cash</MenuItem>
              <MenuItem value={PAYMENT_ONLINE}>Online</MenuItem>
            </TextField>
          </Stack>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setPayOpen(false)} disabled={updating}>
            Cancel
          </Button>
          <Button variant="contained" onClick={submitPayment} disabled={updating}>
            Save
          </Button>
        </DialogActions>
      </Dialog>

      <Dialog
        open={detailOpen}
        onClose={() => !updating && setDetailOpen(false)}
        fullWidth
        maxWidth="md"
      >
        <DialogTitle>
          {detailBooking?.booking_number} · {detailBooking?.package_name}
        </DialogTitle>
        <DialogContent>
          <Tabs value={detailTab} onChange={(_, v) => setDetailTab(v)} sx={{ mb: 2 }}>
            <Tab label="Itinerary" />
            <Tab label="Documents" />
          </Tabs>
          {detailLoading ? (
            <LoadingBlock />
          ) : detailTab === 0 ? (
            <Stack spacing={2}>
              <Typography variant="body2" color="text.secondary">
                Hotel, vehicle, ticket, and activity lines for this booking.
              </Typography>
              {itinerary.length === 0 ? (
                <Typography variant="body2">No itinerary items yet.</Typography>
              ) : (
                itinerary.map((item) => (
                  <Box key={item.id} sx={{ border: 1, borderColor: 'divider', borderRadius: 1, p: 1.5 }}>
                    <Stack direction="row" justifyContent="space-between" alignItems="flex-start">
                      <Stack spacing={0.5}>
                        <Stack direction="row" spacing={1} alignItems="center">
                          <StatusBadge label={item.item_type} variant="info" />
                          {item.day_number ? (
                            <Typography variant="caption">Day {item.day_number}</Typography>
                          ) : null}
                        </Stack>
                        <Typography fontWeight={600}>{item.title}</Typography>
                        <Typography variant="body2" color="text.secondary">
                          {[item.location, item.vendor_name, item.confirmation_ref]
                            .filter(Boolean)
                            .join(' · ') || '—'}
                        </Typography>
                      </Stack>
                      {canManage ? (
                        <IconActionButton
                          title="Delete itinerary item"
                          color="error"
                          disabled={updating}
                          onClick={() => removeItinerary(item.id)}
                        >
                          <DeleteOutlinedIcon fontSize="small" />
                        </IconActionButton>
                      ) : null}
                    </Stack>
                  </Box>
                ))
              )}
              {canManage ? (
                <>
                  <Divider />
                  <Stack spacing={2}>
                    <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2}>
                      <TextField
                        select
                        label="Type"
                        value={itemType}
                        onChange={(e) => setItemType(e.target.value)}
                        fullWidth
                      >
                        {ITINERARY_TYPES.map((t) => (
                          <MenuItem key={t} value={t}>
                            {t}
                          </MenuItem>
                        ))}
                      </TextField>
                      <TextField
                        label="Day"
                        type="number"
                        value={itemDay}
                        onChange={(e) => setItemDay(e.target.value)}
                        fullWidth
                      />
                    </Stack>
                    <TextField
                      label="Title"
                      value={itemTitle}
                      onChange={(e) => setItemTitle(e.target.value)}
                      fullWidth
                      required
                    />
                    <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2}>
                      <TextField
                        label="Location"
                        value={itemLocation}
                        onChange={(e) => setItemLocation(e.target.value)}
                        fullWidth
                      />
                      <TextField
                        label="Vendor"
                        value={itemVendor}
                        onChange={(e) => setItemVendor(e.target.value)}
                        fullWidth
                      />
                      <TextField
                        label="Confirmation ref"
                        value={itemRef}
                        onChange={(e) => setItemRef(e.target.value)}
                        fullWidth
                      />
                    </Stack>
                    <Button variant="contained" onClick={addItinerary} disabled={updating}>
                      Add itinerary item
                    </Button>
                  </Stack>
                </>
              ) : null}
            </Stack>
          ) : (
            <Stack spacing={2}>
              <Typography variant="body2" color="text.secondary">
                Metadata only (passport / visa / ID). File binary storage and encryption come later.
              </Typography>
              {documents.length === 0 ? (
                <Typography variant="body2">No documents recorded.</Typography>
              ) : (
                documents.map((doc) => (
                  <Box key={doc.id} sx={{ border: 1, borderColor: 'divider', borderRadius: 1, p: 1.5 }}>
                    <Stack direction="row" justifyContent="space-between" alignItems="flex-start">
                      <Stack spacing={0.5}>
                        <StatusBadge label={doc.document_type} variant="info" />
                        <Typography fontWeight={600}>
                          {doc.holder_name || 'Holder'} · {doc.document_number || '—'}
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                          {[doc.issued_country, doc.expiry_date, doc.file_name]
                            .filter(Boolean)
                            .join(' · ') || '—'}
                        </Typography>
                      </Stack>
                      {canManage ? (
                        <IconActionButton
                          title="Delete document"
                          color="error"
                          disabled={updating}
                          onClick={() => removeDocument(doc.id)}
                        >
                          <DeleteOutlinedIcon fontSize="small" />
                        </IconActionButton>
                      ) : null}
                    </Stack>
                  </Box>
                ))
              )}
              {canManage ? (
                <>
                  <Divider />
                  <Stack spacing={2}>
                    <TextField
                      select
                      label="Document type"
                      value={docType}
                      onChange={(e) => setDocType(e.target.value)}
                      fullWidth
                    >
                      {DOCUMENT_TYPES.map((t) => (
                        <MenuItem key={t} value={t}>
                          {t}
                        </MenuItem>
                      ))}
                    </TextField>
                    <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2}>
                      <TextField
                        label="Holder"
                        value={docHolder}
                        onChange={(e) => setDocHolder(e.target.value)}
                        fullWidth
                      />
                      <TextField
                        label="Number"
                        value={docNumber}
                        onChange={(e) => setDocNumber(e.target.value)}
                        fullWidth
                      />
                    </Stack>
                    <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2}>
                      <TextField
                        label="Issued country"
                        value={docCountry}
                        onChange={(e) => setDocCountry(e.target.value)}
                        fullWidth
                      />
                      <TextField
                        label="Expiry"
                        type="date"
                        value={docExpiry}
                        onChange={(e) => setDocExpiry(e.target.value)}
                        fullWidth
                        InputLabelProps={{ shrink: true }}
                      />
                      <TextField
                        label="File name"
                        value={docFile}
                        onChange={(e) => setDocFile(e.target.value)}
                        fullWidth
                      />
                    </Stack>
                    <Button variant="contained" onClick={addDocument} disabled={updating}>
                      Add document metadata
                    </Button>
                  </Stack>
                </>
              ) : null}
            </Stack>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDetailOpen(false)} disabled={updating}>
            Close
          </Button>
        </DialogActions>
      </Dialog>
    </PageShell>
  );
}
