import AddOutlinedIcon from '@mui/icons-material/AddOutlined';
import LocalShippingOutlinedIcon from '@mui/icons-material/LocalShippingOutlined';
import PictureAsPdfOutlinedIcon from '@mui/icons-material/PictureAsPdfOutlined';
import DeleteOutlineOutlinedIcon from '@mui/icons-material/DeleteOutlineOutlined';
import {
  Alert,
  Autocomplete,
  Box,
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  Stack,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
  TextField,
  Typography,
} from '@mui/material';
import { useCallback, useEffect, useState } from 'react';
import EmptyState from '../../components/EmptyState';
import LoadingBlock from '../../components/LoadingBlock';
import PageShell from '../../components/PageShell';
import TableCard from '../../components/TableCard';
import TruncateText from '../../components/TruncateText';
import IconActionButton from '../../components/ui/IconActionButton';
import StatusBadge from '../../components/ui/StatusBadge';
import { PageActions } from '../../context/PageActionsContext';
import { useAuth } from '../../context/AuthContext';
import { useModuleGate } from '../../context/ModulesContext';
import {
  convertChallan,
  createChallan,
  downloadChallanPdf,
  listChallans,
  updateChallanStatus,
} from '../../services/challanService';
import { listItems } from '../../services/itemService';

function docStatusVariant(status) {
  const key = String(status || '').toUpperCase();
  if (key === 'DRAFT') return 'pending';
  if (key === 'DISPATCHED') return 'info';
  if (key === 'CONVERTED') return 'active';
  if (key === 'CANCELLED') return 'cancelled';
  return 'info';
}

export default function ChallansPage() {
  const moduleEnabled = useModuleGate('delivery_challan');
  const transportEnabled = useModuleGate('transport_charges');
  const { role } = useAuth();
  const canWrite = role === 'OWNER' || role === 'MANAGER';

  const [rows, setRows] = useState([]);
  const [catalog, setCatalog] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [open, setOpen] = useState(false);
  const [saving, setSaving] = useState(false);
  const [customerName, setCustomerName] = useState('');
  const [customerPhone, setCustomerPhone] = useState('');
  const [deliveryAddress, setDeliveryAddress] = useState('');
  const [vehicleNumber, setVehicleNumber] = useState('');
  const [transportCharge, setTransportCharge] = useState('0');
  const [notes, setNotes] = useState('');
  const [lines, setLines] = useState([{ item: null, quantity: '1' }]);

  const load = useCallback(async () => {
    if (!moduleEnabled) return;
    setLoading(true);
    setError('');
    try {
      const [challans, items] = await Promise.all([
        listChallans({ per_page: 50 }),
        listItems({ per_page: 200, is_active: true }),
      ]);
      setRows(challans.data || []);
      setCatalog(items.data || []);
    } catch (err) {
      setError(err.response?.data?.error?.message || 'Failed to load challans');
    } finally {
      setLoading(false);
    }
  }, [moduleEnabled]);

  useEffect(() => {
    load();
  }, [load]);

  const resetForm = () => {
    setCustomerName('');
    setCustomerPhone('');
    setDeliveryAddress('');
    setVehicleNumber('');
    setTransportCharge('0');
    setNotes('');
    setLines([{ item: null, quantity: '1' }]);
  };

  const onCreate = async () => {
    const payloadLines = lines
      .filter((line) => line.item?.id)
      .map((line) => ({
        item_id: line.item.id,
        quantity: Number(line.quantity),
      }));
    if (!payloadLines.length) {
      setError('Add at least one item.');
      return;
    }
    setSaving(true);
    setError('');
    setSuccess('');
    try {
      const res = await createChallan({
        customer_name: customerName.trim() || null,
        customer_phone: customerPhone.trim() || null,
        delivery_address: deliveryAddress.trim() || null,
        vehicle_number: vehicleNumber.trim() || null,
        transport_charge: transportEnabled ? Number(transportCharge) || 0 : 0,
        notes: notes.trim() || null,
        items: payloadLines,
      });
      setSuccess(`Challan ${res.data?.challan_number} created`);
      setOpen(false);
      resetForm();
      await load();
    } catch (err) {
      setError(err.response?.data?.error?.message || 'Could not create challan');
    } finally {
      setSaving(false);
    }
  };

  const onDispatch = async (row) => {
    try {
      await updateChallanStatus(row.id, { status: 'DISPATCHED' });
      await load();
    } catch (err) {
      setError(err.response?.data?.error?.message || 'Status update failed');
    }
  };

  const onConvert = async (row) => {
    setError('');
    setSuccess('');
    try {
      const res = await convertChallan(row.id, { payment_method: 'cash' });
      setSuccess(
        `Converted ${row.challan_number} → bill ${res.data?.bill?.bill_number || res.data?.bill?.id}`,
      );
      await load();
    } catch (err) {
      setError(err.response?.data?.error?.message || 'Convert failed');
    }
  };

  const onPdf = async (row) => {
    try {
      await downloadChallanPdf(row.id, row.challan_number);
      setSuccess(`Downloaded ${row.challan_number}.pdf`);
    } catch (err) {
      setError(err.response?.data?.error?.message || 'PDF download failed');
    }
  };

  if (!moduleEnabled) {
    return (
      <PageShell>
        <EmptyState
          icon={<LocalShippingOutlinedIcon />}
          title="Delivery challans not enabled"
          description="Available for hardware, building material, and wholesale tenants."
        />
      </PageShell>
    );
  }

  return (
    <PageShell>
      <PageActions>
        {canWrite ? (
          <Button
            variant="contained"
            startIcon={<AddOutlinedIcon />}
            onClick={() => {
              resetForm();
              setOpen(true);
            }}
          >
            New challan
          </Button>
        ) : null}
      </PageActions>

      {error ? <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert> : null}
      {success ? <Alert severity="success" sx={{ mb: 2 }}>{success}</Alert> : null}

      {loading ? (
        <LoadingBlock />
      ) : rows.length === 0 ? (
        <EmptyState
          icon={<LocalShippingOutlinedIcon />}
          title="No delivery challans yet"
          description="Create a challan for dispatch, print the PDF, then convert to a bill when needed."
        />
      ) : (
        <TableCard>
          <Table size="small">
            <TableHead>
              <TableRow>
                <TableCell>Number</TableCell>
                <TableCell>Customer</TableCell>
                <TableCell>Status</TableCell>
                <TableCell>Address</TableCell>
                <TableCell>Lines</TableCell>
                <TableCell align="right">Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {rows.map((row) => (
                <TableRow key={row.id} hover>
                  <TableCell>{row.challan_number}</TableCell>
                  <TableCell>
                    <TruncateText text={row.customer_name || '—'} />
                  </TableCell>
                  <TableCell>
                    <StatusBadge label={row.status} variant={docStatusVariant(row.status)} />
                  </TableCell>
                  <TableCell>
                    <TruncateText text={row.delivery_address || '—'} maxWidth={160} />
                  </TableCell>
                  <TableCell>{(row.items || []).length}</TableCell>
                  <TableCell align="right">
                    <Stack direction="row" spacing={1} justifyContent="flex-end" flexWrap="wrap">
                      <Button
                        size="small"
                        startIcon={<PictureAsPdfOutlinedIcon />}
                        onClick={() => onPdf(row)}
                      >
                        PDF
                      </Button>
                      {canWrite && row.status === 'DRAFT' ? (
                        <Button size="small" onClick={() => onDispatch(row)}>
                          Dispatch
                        </Button>
                      ) : null}
                      {canWrite &&
                      row.status !== 'CONVERTED' &&
                      row.status !== 'CANCELLED' ? (
                        <Button size="small" variant="contained" onClick={() => onConvert(row)}>
                          Convert to bill
                        </Button>
                      ) : null}
                      {row.bill_id ? (
                        <Typography variant="caption" color="text.secondary">
                          Bill linked
                        </Typography>
                      ) : null}
                    </Stack>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableCard>
      )}

      <Dialog open={open} onClose={() => !saving && setOpen(false)} fullWidth maxWidth="md">
        <DialogTitle>New delivery challan</DialogTitle>
        <DialogContent>
          <Stack spacing={2} sx={{ mt: 1 }}>
            <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2}>
              <TextField
                label="Customer name"
                value={customerName}
                onChange={(e) => setCustomerName(e.target.value)}
                fullWidth
              />
              <TextField
                label="Phone"
                value={customerPhone}
                onChange={(e) => setCustomerPhone(e.target.value)}
                fullWidth
              />
              <TextField
                label="Vehicle"
                value={vehicleNumber}
                onChange={(e) => setVehicleNumber(e.target.value)}
                fullWidth
              />
            </Stack>
            {transportEnabled ? (
              <TextField
                label="Transport charge"
                type="number"
                value={transportCharge}
                onChange={(e) => setTransportCharge(e.target.value)}
                helperText="Carried onto bill on convert (non-GST)"
                inputProps={{ min: 0, step: '0.01' }}
              />
            ) : null}
            <TextField
              label="Delivery address"
              value={deliveryAddress}
              onChange={(e) => setDeliveryAddress(e.target.value)}
              fullWidth
              multiline
              minRows={2}
            />
            <TextField
              label="Notes"
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              fullWidth
            />
            {lines.map((line, index) => (
              <Stack key={index} direction={{ xs: 'column', sm: 'row' }} spacing={1} alignItems="center">
                <Autocomplete
                  options={catalog}
                  getOptionLabel={(opt) =>
                    opt
                      ? `${opt.name} · ${(opt.sale_uom || opt.uom || 'pcs').toUpperCase()}`
                      : ''
                  }
                  value={line.item}
                  onChange={(_, value) => {
                    setLines((prev) =>
                      prev.map((row, i) => (i === index ? { ...row, item: value } : row)),
                    );
                  }}
                  sx={{ flex: 1, minWidth: 220 }}
                  renderInput={(params) => <TextField {...params} label="Item" />}
                />
                <TextField
                  label="Qty"
                  type="number"
                  value={line.quantity}
                  onChange={(e) => {
                    setLines((prev) =>
                      prev.map((row, i) =>
                        i === index ? { ...row, quantity: e.target.value } : row,
                      ),
                    );
                  }}
                  sx={{ width: 120 }}
                />
                <IconActionButton
                  title="Remove line"
                  color="error"
                  disabled={lines.length === 1}
                  onClick={() => setLines((prev) => prev.filter((_, i) => i !== index))}
                >
                  <DeleteOutlineOutlinedIcon fontSize="small" />
                </IconActionButton>
              </Stack>
            ))}
            <Box>
              <Button onClick={() => setLines((prev) => [...prev, { item: null, quantity: '1' }])}>
                Add line
              </Button>
            </Box>
          </Stack>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpen(false)} disabled={saving}>
            Cancel
          </Button>
          <Button variant="contained" onClick={onCreate} disabled={saving}>
            Save challan
          </Button>
        </DialogActions>
      </Dialog>
    </PageShell>
  );
}
