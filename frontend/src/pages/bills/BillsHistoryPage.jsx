import {
  Alert,
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
  TextField,
  Typography,
} from '@mui/material';
import { useEffect, useState } from 'react';
import { useSearchParams } from 'react-router-dom';
import EmptyState from '../../components/EmptyState';
import FilterBar from '../../components/FilterBar';
import LoadingBlock from '../../components/LoadingBlock';
import PageShell from '../../components/PageShell';
import PaginationBar from '../../components/PaginationBar';
import TableCard from '../../components/TableCard';
import { filterControlSx } from '../../layouts/shell';
import {
  cancelBill,
  downloadBillPdf,
  getBill,
  listBills,
  openBillPrint,
  sendBillWhatsapp,
  sendBillEmail,
} from '../../services/billService';
import BillPreview from '../../print/BillPreview';
import WhatsAppIcon from '@mui/icons-material/WhatsApp';
import EmailOutlinedIcon from '@mui/icons-material/EmailOutlined';
import { PAYMENT_CASH, PAYMENT_ONLINE, paymentMethodLabel } from '../../utils/paymentMethod';

const PAGE_SIZE = 25;

export default function BillsHistoryPage({ todayDefault = false }) {
  const [searchParams] = useSearchParams();
  const initialWa = (searchParams.get('whatsapp_status') || '').toUpperCase();
  const initialEmail = (searchParams.get('email_status') || '').toUpperCase();
  const allowedWa = new Set(['PENDING', 'SENT', 'DELIVERED', 'READ', 'FAILED']);
  const allowedEmail = new Set(['PENDING', 'SENT', 'FAILED']);
  const [bills, setBills] = useState([]);
  const [q, setQ] = useState('');
  const [status, setStatus] = useState('');
  const [paymentMethod, setPaymentMethod] = useState('');
  const [todayOnly, setTodayOnly] = useState(todayDefault);
  const [page, setPage] = useState(1);
  const [meta, setMeta] = useState({ page: 1, per_page: PAGE_SIZE, total: 0 });
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [selected, setSelected] = useState(null);
  const [cancelOpen, setCancelOpen] = useState(false);
  const [cancelReason, setCancelReason] = useState('');
  const [saving, setSaving] = useState(false);
  const [loading, setLoading] = useState(true);
  const [waSending, setWaSending] = useState(false);
  const [waBusyId, setWaBusyId] = useState(null);
  const [waTarget, setWaTarget] = useState(null);
  const [emailBusyId, setEmailBusyId] = useState(null);
  const [emailTarget, setEmailTarget] = useState(null);
  const [emailDialogOpen, setEmailDialogOpen] = useState(false);
  const [emailDraft, setEmailDraft] = useState('');
  const [emailDraftName, setEmailDraftName] = useState('');
  const [phoneDialogOpen, setPhoneDialogOpen] = useState(false);
  const [phoneDraftCc, setPhoneDraftCc] = useState('91');
  const [phoneDraft, setPhoneDraft] = useState('');
  const [phoneDraftName, setPhoneDraftName] = useState('');
  const [whatsappStatus, setWhatsappStatus] = useState(
    allowedWa.has(initialWa) ? initialWa : '',
  );
  const [emailStatus, setEmailStatus] = useState(
    allowedEmail.has(initialEmail) ? initialEmail : '',
  );

  const waLabel = (status) =>
    status === 'FAILED' ? 'Retry WhatsApp' : 'Send WhatsApp';

  const emailLabel = (status) =>
    status === 'FAILED' ? 'Retry Email' : 'Send Email';

  const load = async (nextPage = page, { keepAlerts = false } = {}) => {
    if (!keepAlerts) setError('');
    setLoading(true);
    try {
      const res = await listBills({
        q: q || undefined,
        status: status || undefined,
        payment_method: paymentMethod || undefined,
        whatsapp_status: whatsappStatus || undefined,
        email_status: emailStatus || undefined,
        today: todayOnly || undefined,
        page: nextPage,
        per_page: PAGE_SIZE,
      });
      setBills(res.data || []);
      setMeta(res.meta || { page: nextPage, per_page: PAGE_SIZE, total: 0 });
      setPage(res.meta?.page || nextPage);
    } catch (err) {
      setError(err.response?.data?.error?.message || 'Failed to load bills');
    } finally {
      setLoading(false);
    }
  };

  const openPhoneForBill = (bill) => {
    setWaTarget(bill);
    setPhoneDraftCc(bill.customer_phone_country_code || '91');
    setPhoneDraft(bill.customer_phone_national || '');
    setPhoneDraftName(bill.customer_name || '');
    setPhoneDialogOpen(true);
  };

  const sendWhatsappForBill = async (bill, phonePayload = null) => {
    setWaSending(true);
    setWaBusyId(bill.id);
    setError('');
    setSuccess('');
    try {
      const res = await sendBillWhatsapp(bill.id, phonePayload || {});
      setSuccess(res.data?.message || 'Bill sent on WhatsApp.');
      if (res.data?.bill && selected?.id === bill.id) {
        setSelected(res.data.bill);
      }
      setPhoneDialogOpen(false);
      setWaTarget(null);
      await load(page, { keepAlerts: true });
    } catch (err) {
      setError(
        err.response?.data?.error?.message || 'Unable to send the bill on WhatsApp.',
      );
    } finally {
      setWaSending(false);
      setWaBusyId(null);
    }
  };

  const startWhatsapp = (bill) => {
    if (!bill || bill.status !== 'FINALIZED' || waSending) return;
    setError('');
    setSuccess('');
    if (!bill.customer_phone_masked && !bill.customer_phone_national) {
      openPhoneForBill(bill);
      return;
    }
    sendWhatsappForBill(bill);
  };

  const openEmailForBill = (bill) => {
    setEmailTarget(bill);
    setEmailDraft(bill.customer_email || '');
    setEmailDraftName(bill.customer_name || '');
    setEmailDialogOpen(true);
  };

  const sendEmailForBill = async (bill, emailPayload = null) => {
    setEmailBusyId(bill.id);
    setError('');
    setSuccess('');
    try {
      const res = await sendBillEmail(bill.id, emailPayload || {});
      setSuccess(res.data?.message || 'Bill sent by email.');
      if (res.data?.bill && selected?.id === bill.id) {
        setSelected(res.data.bill);
      }
      setEmailDialogOpen(false);
      setEmailTarget(null);
      await load(page, { keepAlerts: true });
    } catch (err) {
      setError(
        err.response?.data?.error?.message || 'Unable to send the bill by email.',
      );
    } finally {
      setEmailBusyId(null);
    }
  };

  const startEmail = (bill) => {
    if (!bill || bill.status !== 'FINALIZED' || emailBusyId) return;
    setError('');
    setSuccess('');
    if (!bill.customer_email && !bill.customer_email_masked) {
      openEmailForBill(bill);
      return;
    }
    sendEmailForBill(bill);
  };

  useEffect(() => {
    const nextWa = (searchParams.get('whatsapp_status') || '').toUpperCase();
    if (allowedWa.has(nextWa) && nextWa !== whatsappStatus) {
      setWhatsappStatus(nextWa);
      setPage(1);
    }
    const nextEmail = (searchParams.get('email_status') || '').toUpperCase();
    if (allowedEmail.has(nextEmail) && nextEmail !== emailStatus) {
      setEmailStatus(nextEmail);
      setPage(1);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [searchParams]);

  useEffect(() => {
    load(1);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [status, todayOnly, paymentMethod, whatsappStatus, emailStatus]);

  const openDetails = async (bill) => {
    setError('');
    try {
      const res = await getBill(bill.id);
      setSelected(res.data);
    } catch (err) {
      setError(err.response?.data?.error?.message || 'Failed to load bill details');
    }
  };

  const onCancel = async () => {
    if (!selected) return;
    setSaving(true);
    setError('');
    setSuccess('');
    try {
      const res = await cancelBill(selected.id, cancelReason);
      setSelected(res.data);
      setCancelOpen(false);
      setCancelReason('');
      setSuccess(`Bill #${res.data.bill_number} cancelled`);
      await load(page);
    } catch (err) {
      setError(err.response?.data?.error?.message || 'Failed to cancel bill');
    } finally {
      setSaving(false);
    }
  };

  return (
    <PageShell>
      <FilterBar
        actions={
          <Button variant="outlined" onClick={() => load(1)} disabled={loading}>
            Search
          </Button>
        }
      >
        <TextField
          label="Search bill / reference"
          value={q}
          onChange={(e) => setQ(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === 'Enter') load(1);
          }}
          sx={{ flex: 1, minWidth: { xs: '100%', sm: 200 } }}
        />
        <FormControl sx={filterControlSx}>
          <InputLabel>Status</InputLabel>
          <Select
            label="Status"
            value={status}
            onChange={(e) => {
              setStatus(e.target.value);
              setPage(1);
            }}
          >
            <MenuItem value="">All</MenuItem>
            <MenuItem value="FINALIZED">Finalized</MenuItem>
            <MenuItem value="CANCELLED">Cancelled</MenuItem>
          </Select>
        </FormControl>
        <FormControl sx={filterControlSx}>
          <InputLabel>Payment Method</InputLabel>
          <Select
            label="Payment Method"
            value={paymentMethod}
            onChange={(e) => {
              setPaymentMethod(e.target.value);
              setPage(1);
            }}
          >
            <MenuItem value="">All</MenuItem>
            <MenuItem value={PAYMENT_CASH}>Cash</MenuItem>
            <MenuItem value={PAYMENT_ONLINE}>Online</MenuItem>
          </Select>
        </FormControl>
        <FormControl sx={filterControlSx}>
          <InputLabel>Period</InputLabel>
          <Select
            label="Period"
            value={todayOnly ? 'today' : 'all'}
            onChange={(e) => {
              setTodayOnly(e.target.value === 'today');
              setPage(1);
            }}
          >
            <MenuItem value="all">All</MenuItem>
            <MenuItem value="today">Today</MenuItem>
          </Select>
        </FormControl>
        <FormControl sx={filterControlSx}>
          <InputLabel>WhatsApp</InputLabel>
          <Select
            label="WhatsApp"
            value={whatsappStatus}
            onChange={(e) => {
              setWhatsappStatus(e.target.value);
              setPage(1);
            }}
          >
            <MenuItem value="">All</MenuItem>
            <MenuItem value="PENDING">Pending</MenuItem>
            <MenuItem value="SENT">Sent</MenuItem>
            <MenuItem value="DELIVERED">Delivered</MenuItem>
            <MenuItem value="READ">Read</MenuItem>
            <MenuItem value="FAILED">Failed</MenuItem>
          </Select>
        </FormControl>
        <FormControl sx={filterControlSx}>
          <InputLabel>Email</InputLabel>
          <Select
            label="Email"
            value={emailStatus}
            onChange={(e) => {
              setEmailStatus(e.target.value);
              setPage(1);
            }}
          >
            <MenuItem value="">All</MenuItem>
            <MenuItem value="PENDING">Pending</MenuItem>
            <MenuItem value="SENT">Sent</MenuItem>
            <MenuItem value="FAILED">Failed</MenuItem>
          </Select>
        </FormControl>
      </FilterBar>

      {error ? <Alert severity="error">{error}</Alert> : null}
      {success ? <Alert severity="success">{success}</Alert> : null}

      <TableCard>
        {loading ? (
          <LoadingBlock />
        ) : (
          <Table size="small" sx={{ minWidth: 960 }}>
            <TableHead>
              <TableRow>
                <TableCell>Bill No</TableCell>
                <TableCell>Reference</TableCell>
                <TableCell>Status</TableCell>
                <TableCell>Payment Method</TableCell>
                <TableCell align="right">Total</TableCell>
                <TableCell>Prints</TableCell>
                <TableCell>WhatsApp</TableCell>
                <TableCell>Created By</TableCell>
                <TableCell>Time</TableCell>
                <TableCell align="right">Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {bills.map((bill) => (
                <TableRow key={bill.id} hover>
                  <TableCell sx={{ fontVariantNumeric: 'tabular-nums', fontWeight: 600 }}>
                    {bill.bill_number}
                  </TableCell>
                  <TableCell>{bill.reference || bill.table_number || '—'}</TableCell>
                  <TableCell>
                    <Chip
                      size="small"
                      label={bill.status === 'CANCELLED' ? 'Cancelled' : 'Finalized'}
                      color={bill.status === 'CANCELLED' ? 'warning' : 'success'}
                      variant={bill.status === 'CANCELLED' ? 'filled' : 'outlined'}
                    />
                  </TableCell>
                  <TableCell>{paymentMethodLabel(bill.payment_method)}</TableCell>
                  <TableCell align="right">₹{Number(bill.grand_total).toFixed(2)}</TableCell>
                  <TableCell>{bill.printed_count}</TableCell>
                  <TableCell>
                    {bill.whatsapp_delivery_status === 'READ' ? (
                      <Chip size="small" label="Read" color="success" variant="outlined" />
                    ) : bill.whatsapp_delivery_status === 'DELIVERED' ? (
                      <Chip size="small" label="Delivered" color="success" variant="outlined" />
                    ) : bill.whatsapp_delivery_status === 'SENT' ? (
                      <Chip size="small" label="Sent" color="success" variant="outlined" />
                    ) : bill.whatsapp_delivery_status === 'FAILED' ? (
                      <Chip size="small" label="Failed" color="error" variant="outlined" />
                    ) : bill.whatsapp_delivery_status === 'PENDING' ? (
                      <Chip size="small" label="Pending" color="warning" variant="outlined" />
                    ) : (
                      '—'
                    )}
                  </TableCell>
                  <TableCell>{bill.created_by_name || '—'}</TableCell>
                  <TableCell>
                    {bill.created_at ? new Date(bill.created_at).toLocaleString() : '—'}
                  </TableCell>
                  <TableCell align="right">
                    <Stack direction="row" spacing={0.5} justifyContent="flex-end" useFlexGap flexWrap="wrap">
                      <Button size="small" onClick={() => openDetails(bill)}>
                        View
                      </Button>
                      <Button size="small" onClick={() => openBillPrint(bill.id)}>
                        Print
                      </Button>
                      {bill.status === 'FINALIZED' ? (
                        <Button
                          size="small"
                          color="success"
                          startIcon={<WhatsAppIcon fontSize="inherit" />}
                          disabled={waSending || Boolean(emailBusyId)}
                          onClick={() => startWhatsapp(bill)}
                        >
                          {waBusyId === bill.id
                            ? 'Sending…'
                            : waLabel(bill.whatsapp_delivery_status)}
                        </Button>
                      ) : null}
                      {bill.status === 'FINALIZED' ? (
                        <Button
                          size="small"
                          startIcon={<EmailOutlinedIcon fontSize="inherit" />}
                          disabled={Boolean(emailBusyId) || waSending}
                          onClick={() => startEmail(bill)}
                        >
                          {emailBusyId === bill.id
                            ? 'Sending…'
                            : emailLabel(bill.email_delivery_status)}
                        </Button>
                      ) : null}
                    </Stack>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        )}
        {!loading && !bills.length ? (
          <EmptyState
            title="No bills found"
            description="Try another search, status, payment method, or period."
          />
        ) : null}
        {!loading && bills.length ? (
          <PaginationBar
            page={meta.page}
            perPage={meta.per_page}
            total={meta.total}
            onPageChange={(next) => load(next)}
          />
        ) : null}
      </TableCard>

      <Dialog
        open={Boolean(selected)}
        onClose={() => setSelected(null)}
        fullWidth
        maxWidth="md"
      >
        <DialogTitle>
          Bill #{selected?.bill_number}{' '}
          {selected?.status === 'CANCELLED' ? '(Cancelled)' : ''}
        </DialogTitle>
        <DialogContent>
          {selected ? (
            <Stack spacing={2.5} sx={{ pt: 1 }}>
              {selected.status === 'CANCELLED' ? (
                <Alert severity="warning">
                  Reason: {selected.cancellation_reason || '—'}
                  {selected.cancelled_at
                    ? ` · ${new Date(selected.cancelled_at).toLocaleString()}`
                    : ''}
                </Alert>
              ) : null}
              {selected.whatsapp_delivery_status || selected.customer_phone_masked ? (
                <Alert
                  severity={
                    selected.whatsapp_delivery_status === 'FAILED'
                      ? 'error'
                      : selected.whatsapp_delivery_status === 'READ' ||
                          selected.whatsapp_delivery_status === 'DELIVERED' ||
                          selected.whatsapp_delivery_status === 'SENT'
                        ? 'success'
                        : 'info'
                  }
                >
                  Delivery:{' '}
                  {selected.whatsapp_delivery_status === 'READ'
                    ? 'WhatsApp read'
                    : selected.whatsapp_delivery_status === 'DELIVERED'
                      ? 'WhatsApp delivered'
                      : selected.whatsapp_delivery_status === 'SENT'
                        ? 'WhatsApp sent'
                        : selected.whatsapp_delivery_status === 'FAILED'
                          ? 'WhatsApp failed'
                          : selected.whatsapp_delivery_status === 'PENDING'
                            ? 'WhatsApp pending'
                            : 'Not sent on WhatsApp'}
                  {selected.customer_phone_masked
                    ? ` · ${selected.customer_phone_masked}`
                    : ''}
                  {(() => {
                    const latest = (selected.deliveries || []).find(
                      (d) => d.delivery_method === 'WHATSAPP',
                    );
                    if (!latest) return null;
                    if (latest.status === 'FAILED' && latest.error_message) {
                      return (
                        <>
                          <br />
                          Reason: {latest.error_message}
                        </>
                      );
                    }
                    const bits = [];
                    if (latest.sent_at) bits.push(`Sent ${new Date(latest.sent_at).toLocaleString()}`);
                    if (latest.delivered_at) {
                      bits.push(`Delivered ${new Date(latest.delivered_at).toLocaleString()}`);
                    }
                    if (latest.read_at) bits.push(`Read ${new Date(latest.read_at).toLocaleString()}`);
                    return bits.length ? (
                      <>
                        <br />
                        {bits.join(' · ')}
                      </>
                    ) : null;
                  })()}
                </Alert>
              ) : null}
              {selected.deliveries?.length ? (
                <Alert severity="info">
                  Delivery attempts:{' '}
                  {selected.deliveries
                    .slice(0, 5)
                    .map((d) => {
                      const when =
                        d.read_at || d.delivered_at || d.sent_at || d.created_at
                          ? ` @ ${new Date(
                              d.read_at || d.delivered_at || d.sent_at || d.created_at,
                            ).toLocaleString()}`
                          : '';
                      const err =
                        d.status === 'FAILED' && d.error_message
                          ? ` — ${d.error_message}`
                          : '';
                      return `${d.delivery_method} ${d.status}${
                        d.recipient_phone_masked
                          ? ` (${d.recipient_phone_masked})`
                          : d.recipient_email_masked
                            ? ` (${d.recipient_email_masked})`
                            : ''
                      }${when}${err}`;
                    })
                    .join(' · ')}
                </Alert>
              ) : null}
              <BillPreview
                bill={selected}
                onPrint={() => openBillPrint(selected.id, { auto: true })}
              />
            </Stack>
          ) : null}
        </DialogContent>
        <DialogActions sx={{ flexWrap: 'wrap', gap: 1 }}>
          {selected?.status === 'FINALIZED' ? (
            <Button color="error" onClick={() => setCancelOpen(true)}>
              Cancel Bill
            </Button>
          ) : null}
          {selected?.status === 'FINALIZED' ? (
            <Button
              color="success"
              variant="outlined"
              startIcon={<WhatsAppIcon />}
              disabled={waSending || Boolean(emailBusyId)}
              onClick={() => startWhatsapp(selected)}
            >
              {waBusyId === selected?.id
                ? 'Sending…'
                : waLabel(selected?.whatsapp_delivery_status)}
            </Button>
          ) : null}
          {selected?.status === 'FINALIZED' ? (
            <Button
              variant="outlined"
              startIcon={<EmailOutlinedIcon />}
              disabled={Boolean(emailBusyId) || waSending}
              onClick={() => startEmail(selected)}
            >
              {emailBusyId === selected?.id
                ? 'Sending…'
                : emailLabel(selected?.email_delivery_status)}
            </Button>
          ) : null}
          {selected ? (
            <Button
              variant="outlined"
              onClick={async () => {
                try {
                  await downloadBillPdf(selected.id, selected.bill_number);
                } catch (err) {
                  setError(err.response?.data?.error?.message || 'Unable to download bill PDF.');
                }
              }}
            >
              Download PDF
            </Button>
          ) : null}
          <Button onClick={() => setSelected(null)}>Close</Button>
        </DialogActions>
      </Dialog>

      <Dialog
        open={phoneDialogOpen}
        onClose={() => {
          if (waSending) return;
          setPhoneDialogOpen(false);
          setWaTarget(null);
        }}
        fullWidth
        maxWidth="xs"
      >
        <DialogTitle>Customer WhatsApp number</DialogTitle>
        <DialogContent>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
            Customer WhatsApp number is required to send this bill
            {(waTarget || selected)?.bill_number
              ? ` (#${(waTarget || selected).bill_number})`
              : ''}
            .
          </Typography>
          <Stack spacing={1.5} sx={{ pt: 0.5 }}>
            <TextField
              label="Customer name (optional)"
              value={phoneDraftName}
              onChange={(e) => setPhoneDraftName(e.target.value)}
              fullWidth
            />
            <Stack direction="row" spacing={1.5}>
              <TextField
                label="Country"
                value={phoneDraftCc}
                onChange={(e) => setPhoneDraftCc(e.target.value.replace(/\D/g, '').slice(0, 3))}
                sx={{ width: 100 }}
              />
              <TextField
                label="Mobile number"
                value={phoneDraft}
                onChange={(e) => setPhoneDraft(e.target.value.replace(/\D/g, '').slice(0, 14))}
                fullWidth
                autoFocus
              />
            </Stack>
          </Stack>
        </DialogContent>
        <DialogActions>
          <Button
            onClick={() => {
              setPhoneDialogOpen(false);
              setWaTarget(null);
            }}
            disabled={waSending}
          >
            Cancel
          </Button>
          <Button
            variant="contained"
            color="success"
            disabled={waSending || !phoneDraft || !(waTarget || selected)}
            onClick={() => {
              const bill = waTarget || selected;
              if (!bill) return;
              sendWhatsappForBill(bill, {
                country_code: phoneDraftCc,
                phone: phoneDraft,
                customer_name: phoneDraftName || null,
              });
            }}
          >
            {waSending ? 'Sending…' : 'Send'}
          </Button>
        </DialogActions>
      </Dialog>

      <Dialog
        open={emailDialogOpen}
        onClose={() => {
          if (emailBusyId) return;
          setEmailDialogOpen(false);
          setEmailTarget(null);
        }}
        fullWidth
        maxWidth="xs"
      >
        <DialogTitle>Customer email</DialogTitle>
        <DialogContent>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
            Customer email is required to send this bill
            {(emailTarget || selected)?.bill_number
              ? ` (#${(emailTarget || selected).bill_number})`
              : ''}
            .
          </Typography>
          <Stack spacing={1.5} sx={{ pt: 0.5 }}>
            <TextField
              label="Customer name (optional)"
              value={emailDraftName}
              onChange={(e) => setEmailDraftName(e.target.value)}
              fullWidth
            />
            <TextField
              label="Email"
              type="email"
              value={emailDraft}
              onChange={(e) => setEmailDraft(e.target.value)}
              fullWidth
              autoFocus
            />
          </Stack>
        </DialogContent>
        <DialogActions>
          <Button
            onClick={() => {
              setEmailDialogOpen(false);
              setEmailTarget(null);
            }}
            disabled={Boolean(emailBusyId)}
          >
            Cancel
          </Button>
          <Button
            variant="contained"
            disabled={Boolean(emailBusyId) || !emailDraft.trim() || !(emailTarget || selected)}
            onClick={() => {
              const bill = emailTarget || selected;
              if (!bill) return;
              sendEmailForBill(bill, {
                email: emailDraft.trim(),
                customer_name: emailDraftName || null,
              });
            }}
          >
            {emailBusyId ? 'Sending…' : 'Send'}
          </Button>
        </DialogActions>
      </Dialog>

      <Dialog open={cancelOpen} onClose={() => setCancelOpen(false)} fullWidth maxWidth="sm">
        <DialogTitle>Cancel Bill #{selected?.bill_number}</DialogTitle>
        <DialogContent>
          <Stack spacing={2.5} sx={{ pt: 1 }}>
            <TextField
              label="Cancellation reason"
              value={cancelReason}
              onChange={(e) => setCancelReason(e.target.value)}
              fullWidth
              required
              multiline
              minRows={3}
            />
          </Stack>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setCancelOpen(false)}>Back</Button>
          <Button
            color="error"
            variant="contained"
            disabled={saving || !cancelReason.trim()}
            onClick={onCancel}
          >
            Confirm Cancel
          </Button>
        </DialogActions>
      </Dialog>
    </PageShell>
  );
}
