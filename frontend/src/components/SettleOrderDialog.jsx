import {
  Alert,
  Box,
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  FormControl,
  InputLabel,
  MenuItem,
  Select,
  Stack,
  Tab,
  Tabs,
  TextField,
  Typography,
} from '@mui/material';
import { useEffect, useMemo, useState } from 'react';
import { settleOrder } from '../services/orderSettlementService';

const PAYMENT_OPTIONS = [
  { value: 'cash', label: 'Cash' },
  { value: 'online', label: 'Online' },
  { value: 'credit', label: 'Credit (Udhari)' },
];

function money(value) {
  return `₹${Number(value || 0).toLocaleString('en-IN', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  })}`;
}

export default function SettleOrderDialog({ open, order, onClose, onSettled, initialTab = 0 }) {
  const [tab, setTab] = useState(0);
  const [discount, setDiscount] = useState('0');
  const [serviceCharge, setServiceCharge] = useState('0');
  const [serviceChargePercent, setServiceChargePercent] = useState('');
  const [paymentMethod, setPaymentMethod] = useState('cash');
  const [splitPaymentA, setSplitPaymentA] = useState('cash');
  const [splitPaymentB, setSplitPaymentB] = useState('online');
  const [splitAIds, setSplitAIds] = useState([]);
  const [splitBIds, setSplitBIds] = useState([]);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');

  const lines = order?.items || [];

  const previewSubtotal = useMemo(
    () => lines.reduce((sum, line) => sum + Number(line.line_total || 0), 0),
    [lines],
  );

  useEffect(() => {
    if (!open || !lines.length) return;
    const half = Math.ceil(lines.length / 2);
    setSplitAIds(lines.slice(0, half).map((line) => line.id));
    setSplitBIds(lines.slice(half).map((line) => line.id));
    setDiscount('0');
    setServiceCharge('0');
    setServiceChargePercent('');
    setPaymentMethod('cash');
    setTab(initialTab === 1 ? 1 : 0);
    setError('');
  }, [open, order?.id, lines, initialTab]);

  const toggleSplitLine = (lineId, bucket) => {
    if (bucket === 'A') {
      setSplitAIds((prev) => (prev.includes(lineId) ? prev.filter((id) => id !== lineId) : [...prev, lineId]));
      setSplitBIds((prev) => prev.filter((id) => id !== lineId));
      return;
    }
    setSplitBIds((prev) => (prev.includes(lineId) ? prev.filter((id) => id !== lineId) : [...prev, lineId]));
    setSplitAIds((prev) => prev.filter((id) => id !== lineId));
  };

  const buildPayload = () => {
    const payload = {
      discount: Number(discount || 0),
      service_charge: Number(serviceCharge || 0),
      service_charge_percent: serviceChargePercent ? Number(serviceChargePercent) : null,
    };
    if (tab === 0) {
      return { ...payload, payment_method: paymentMethod };
    }
    return {
      ...payload,
      splits: [
        { order_item_ids: splitAIds, payment_method: splitPaymentA },
        { order_item_ids: splitBIds, payment_method: splitPaymentB },
      ],
    };
  };

  const onSubmit = async () => {
    if (!order?.id) return;
    setSaving(true);
    setError('');
    try {
      if (tab === 1) {
        const allAssigned = new Set([...splitAIds, ...splitBIds]);
        if (allAssigned.size !== lines.length || !splitAIds.length || !splitBIds.length) {
          setError('Assign every item to exactly one split.');
          setSaving(false);
          return;
        }
      }
      const response = await settleOrder(order.id, buildPayload());
      onSettled?.(response.data);
      onClose();
    } catch (err) {
      setError(err.response?.data?.error?.message || 'Unable to settle order.');
    } finally {
      setSaving(false);
    }
  };

  return (
    <Dialog open={open} onClose={onClose} fullWidth maxWidth="sm">
      <DialogTitle>Settle order {order?.order_number || ''}</DialogTitle>
      <DialogContent>
        <Stack spacing={2} sx={{ mt: 1 }}>
          <Typography variant="body2" color="text.secondary">
            Order total (pre-settlement): {money(order?.grand_total ?? previewSubtotal)}
          </Typography>
          <Tabs value={tab} onChange={(_, value) => setTab(value)}>
            <Tab label="Full bill" />
            <Tab label="Split bill" />
          </Tabs>
          <TextField
            label="Discount (₹)"
            type="number"
            value={discount}
            onChange={(e) => setDiscount(e.target.value)}
            inputProps={{ min: 0, step: '0.01' }}
          />
          <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2}>
            <TextField
              label="Service charge (₹)"
              type="number"
              value={serviceCharge}
              onChange={(e) => setServiceCharge(e.target.value)}
              inputProps={{ min: 0, step: '0.01' }}
              fullWidth
            />
            <TextField
              label="Service charge (%)"
              type="number"
              value={serviceChargePercent}
              onChange={(e) => setServiceChargePercent(e.target.value)}
              inputProps={{ min: 0, step: '0.1' }}
              fullWidth
            />
          </Stack>
          {tab === 0 ? (
            <FormControl fullWidth>
              <InputLabel>Payment method</InputLabel>
              <Select
                label="Payment method"
                value={paymentMethod}
                onChange={(e) => setPaymentMethod(e.target.value)}
              >
                {PAYMENT_OPTIONS.map((option) => (
                  <MenuItem key={option.value} value={option.value}>
                    {option.label}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          ) : (
            <Stack spacing={2}>
              <Box>
                <Typography variant="subtitle2" gutterBottom>
                  Split A
                </Typography>
                <FormControl fullWidth sx={{ mb: 1 }}>
                  <InputLabel>Payment</InputLabel>
                  <Select label="Payment" value={splitPaymentA} onChange={(e) => setSplitPaymentA(e.target.value)}>
                    {PAYMENT_OPTIONS.map((option) => (
                      <MenuItem key={option.value} value={option.value}>
                        {option.label}
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>
                {lines.map((line) => (
                  <Button
                    key={`a-${line.id}`}
                    size="small"
                    variant={splitAIds.includes(line.id) ? 'contained' : 'outlined'}
                    onClick={() => toggleSplitLine(line.id, 'A')}
                    sx={{ mr: 1, mb: 1 }}
                  >
                    {line.item_name} × {line.quantity}
                  </Button>
                ))}
              </Box>
              <Box>
                <Typography variant="subtitle2" gutterBottom>
                  Split B
                </Typography>
                <FormControl fullWidth sx={{ mb: 1 }}>
                  <InputLabel>Payment</InputLabel>
                  <Select label="Payment" value={splitPaymentB} onChange={(e) => setSplitPaymentB(e.target.value)}>
                    {PAYMENT_OPTIONS.map((option) => (
                      <MenuItem key={option.value} value={option.value}>
                        {option.label}
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>
                {lines.map((line) => (
                  <Button
                    key={`b-${line.id}`}
                    size="small"
                    color="secondary"
                    variant={splitBIds.includes(line.id) ? 'contained' : 'outlined'}
                    onClick={() => toggleSplitLine(line.id, 'B')}
                    sx={{ mr: 1, mb: 1 }}
                  >
                    {line.item_name} × {line.quantity}
                  </Button>
                ))}
              </Box>
            </Stack>
          )}
          {error ? <Alert severity="error">{error}</Alert> : null}
        </Stack>
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose}>Cancel</Button>
        <Button variant="contained" disabled={saving} onClick={onSubmit}>
          {saving ? 'Working…' : tab === 1 ? 'Split & create bills' : 'Generate Bill'}
        </Button>
      </DialogActions>
    </Dialog>
  );
}
