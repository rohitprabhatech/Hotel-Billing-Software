import DeleteOutlineOutlinedIcon from '@mui/icons-material/DeleteOutlineOutlined';
import StraightenOutlinedIcon from '@mui/icons-material/StraightenOutlined';
import {
  Alert,
  Box,
  Button,
  Card,
  CardActionArea,
  CardContent,
  FormControl,
  FormControlLabel,
  FormLabel,
  IconButton,
  Radio,
  RadioGroup,
  Stack,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
  TextField,
  Typography,
} from '@mui/material';
import { useCallback, useEffect, useMemo, useState } from 'react';
import PageShell from '../../components/PageShell';
import TruncateText from '../../components/TruncateText';
import { useModuleGate } from '../../context/ModulesContext';
import { createBill } from '../../services/billService';
import { fetchHardwarePosCatalog, quoteHardwareLine } from '../../services/hardwareService';
import {
  DEFAULT_PAYMENT_METHOD,
  PAYMENT_CASH,
  PAYMENT_CREDIT,
  PAYMENT_ONLINE,
  paymentMethodLabel,
} from '../../utils/paymentMethod';
import { qtyStepForUom, uomLabel } from '../../utils/uom';
import { resolveTierUnitPrice } from '../../utils/bulkPricing';

function money(value) {
  return `₹${Number(value || 0).toFixed(2)}`;
}

function lineTotal(line) {
  return Number(line.price || 0) * Number(line.quantity || 0);
}

function applyTierPrice(line) {
  const price = resolveTierUnitPrice(line.base_price, line.quantity, line.price_tiers);
  return { ...line, price };
}

export default function HardwarePosPage() {
  const moduleEnabled = useModuleGate('uom_measurement');
  const creditEnabled = useModuleGate('customer_credit');
  const transportEnabled = useModuleGate('transport_charges');

  const [catalog, setCatalog] = useState([]);
  const [q, setQ] = useState('');
  const [cart, setCart] = useState([]);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [saving, setSaving] = useState(false);
  const [paymentMethod, setPaymentMethod] = useState(DEFAULT_PAYMENT_METHOD);
  const [transportCharge, setTransportCharge] = useState('0');
  const [quotePreview, setQuotePreview] = useState(null);

  const loadCatalog = useCallback(async () => {
    if (!moduleEnabled) return;
    try {
      const res = await fetchHardwarePosCatalog({ q: q.trim() || undefined, limit: 80 });
      setCatalog(res.data?.items || []);
    } catch (err) {
      setError(err.response?.data?.error?.message || 'Unable to load hardware catalog.');
    }
  }, [moduleEnabled, q]);

  useEffect(() => {
    loadCatalog();
  }, [loadCatalog]);

  const cartTotal = useMemo(() => cart.reduce((sum, line) => sum + lineTotal(line), 0), [cart]);
  const transportValue = transportEnabled ? Number(transportCharge) || 0 : 0;
  const displayTotal = cartTotal + transportValue;

  const addItem = async (item) => {
    const saleUom = item.sale_uom || item.uom || 'pcs';
    const step = Number(item.qty_step || qtyStepForUom(saleUom));
    const tracked = item.stock_quantity !== null && item.stock_quantity !== undefined;
    const available = tracked ? Number(item.stock_quantity) : null;
    if (tracked && available <= 0) {
      setError(`Out of stock: ${item.name}`);
      return;
    }

    setCart((prev) => {
      const existing = prev.find((line) => line.item_id === item.id);
      const nextQty = existing ? Number(existing.quantity) + step : step;
      if (existing) {
        return prev.map((line) =>
          line.item_id === item.id
            ? applyTierPrice({
                ...line,
                quantity: nextQty,
                price_tiers: item.price_tiers || line.price_tiers || [],
                base_price: Number(item.price ?? line.base_price),
              })
            : line,
        );
      }
      return [
        ...prev,
        applyTierPrice({
          item_id: item.id,
          name: item.name,
          base_price: Number(item.price),
          price: Number(item.price),
          gst_percentage: Number(item.gst_percentage || 0),
          quantity: step,
          sale_uom: saleUom,
          uom: item.uom || 'pcs',
          stock_quantity: available,
          stock_tracked: tracked,
          price_tiers: item.price_tiers || [],
        }),
      ];
    });
    setError('');
    setSuccess('');
    try {
      const quoted = await quoteHardwareLine({ item_id: item.id, quantity: step });
      setQuotePreview(quoted.data);
    } catch {
      setQuotePreview(null);
    }
  };

  const setLineQty = (itemId, rawQty) => {
    const parsed = Number(rawQty);
    if (!Number.isFinite(parsed) || parsed <= 0) {
      setCart((prev) => prev.filter((line) => line.item_id !== itemId));
      return;
    }
    setCart((prev) =>
      prev.map((line) =>
        line.item_id === itemId ? applyTierPrice({ ...line, quantity: parsed }) : line,
      ),
    );
  };

  const removeLine = (itemId) => {
    setCart((prev) => prev.filter((line) => line.item_id !== itemId));
  };

  const checkout = async () => {
    if (!cart.length) {
      setError('Add at least one measured item.');
      return;
    }
    setSaving(true);
    setError('');
    setSuccess('');
    try {
      const res = await createBill({
        payment_method: paymentMethod,
        transport_charge: transportEnabled ? Number(transportCharge) || 0 : 0,
        items: cart.map((line) => ({
          item_id: line.item_id,
          quantity: line.quantity,
        })),
      });
      setSuccess(
        `Bill ${res.data?.bill_number} saved · ${money(res.data?.grand_total)} (${paymentMethodLabel(
          paymentMethod,
        )})`,
      );
      setCart([]);
      setTransportCharge('0');
      setQuotePreview(null);
      await loadCatalog();
    } catch (err) {
      setError(err.response?.data?.error?.message || 'Could not create bill.');
    } finally {
      setSaving(false);
    }
  };

  if (!moduleEnabled) {
    return (
      <PageShell>
        <Alert severity="warning">
          Length / weight / area billing is not enabled for this business type.
        </Alert>
      </PageShell>
    );
  }

  return (
    <PageShell>
      <Stack spacing={2}>
        <Stack direction="row" spacing={1} alignItems="center">
          <StraightenOutlinedIcon color="primary" />
          <Typography variant="h5" sx={{ fontWeight: 700 }}>
            Hardware POS
          </Typography>
        </Stack>
        <Typography variant="body2" color="text.secondary">
          Sell by metre, kg, sqm, and other units. Price is per sale unit — e.g. 10 m × ₹450 = ₹4,500.
        </Typography>

        {error ? <Alert severity="error">{error}</Alert> : null}
        {success ? (
          <Alert severity="success" onClose={() => setSuccess('')}>
            {success}
          </Alert>
        ) : null}

        <Stack direction={{ xs: 'column', md: 'row' }} spacing={2} alignItems="stretch">
          <Box sx={{ flex: 1.2 }}>
            <TextField
              label="Search items"
              value={q}
              onChange={(e) => setQ(e.target.value)}
              fullWidth
              sx={{ mb: 2 }}
              placeholder="Pipe, cement, tile…"
            />
            <Box
              sx={{
                display: 'grid',
                gap: 1.5,
                gridTemplateColumns: { xs: '1fr 1fr', sm: 'repeat(3, 1fr)' },
              }}
            >
              {catalog.map((item) => (
                <Card key={item.id} variant="outlined">
                  <CardActionArea onClick={() => addItem(item)}>
                    <CardContent sx={{ py: 1.5 }}>
                      <TruncateText value={item.name} maxWidth="100%" />
                      <Typography variant="caption" color="text.secondary" display="block">
                        {uomLabel(item.sale_uom || item.uom)} · {money(item.price)}/
                        {(item.sale_uom || item.uom || 'pcs').toUpperCase()}
                      </Typography>
                      <Typography variant="body2" sx={{ fontWeight: 600, mt: 0.5 }}>
                        {money(item.price)}
                      </Typography>
                    </CardContent>
                  </CardActionArea>
                </Card>
              ))}
            </Box>
            {!catalog.length ? (
              <Alert severity="info" sx={{ mt: 2 }}>
                No items found. Create catalog items with stock UoM (and optional sale UoM).
              </Alert>
            ) : null}
          </Box>

          <Box sx={{ flex: 1, minWidth: { md: 360 } }}>
            <Card variant="outlined">
              <CardContent>
                <Typography variant="h6" sx={{ mb: 1 }}>
                  Cart
                </Typography>
                {quotePreview ? (
                  <Alert severity="info" sx={{ mb: 1.5 }}>
                    Last quote: {quotePreview.quantity} {quotePreview.sale_uom} ×{' '}
                    {money(quotePreview.unit_price)} = {money(quotePreview.line_total)}
                    {quotePreview.stock_uom !== quotePreview.sale_uom
                      ? ` · deducts ${quotePreview.stock_quantity_deducted} ${quotePreview.stock_uom}`
                      : ''}
                  </Alert>
                ) : null}
                <Table size="small">
                  <TableHead>
                    <TableRow>
                      <TableCell>Item</TableCell>
                      <TableCell align="right">Qty</TableCell>
                      <TableCell align="right">Amount</TableCell>
                      <TableCell />
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {cart.map((line) => (
                      <TableRow key={line.item_id}>
                        <TableCell>
                          <Typography variant="body2">{line.name}</Typography>
                          <Typography variant="caption" color="text.secondary">
                            {money(line.price)} / {(line.sale_uom || 'pcs').toUpperCase()}
                          </Typography>
                        </TableCell>
                        <TableCell align="right">
                          <TextField
                            type="number"
                            size="small"
                            value={line.quantity}
                            onChange={(e) => setLineQty(line.item_id, e.target.value)}
                            inputProps={{
                              min: qtyStepForUom(line.sale_uom),
                              step: qtyStepForUom(line.sale_uom),
                            }}
                            sx={{ width: 96 }}
                          />
                          <Typography variant="caption" display="block">
                            {(line.sale_uom || 'pcs').toUpperCase()}
                          </Typography>
                        </TableCell>
                        <TableCell align="right">{money(lineTotal(line))}</TableCell>
                        <TableCell align="right">
                          <IconButton size="small" onClick={() => removeLine(line.item_id)}>
                            <DeleteOutlineOutlinedIcon fontSize="small" />
                          </IconButton>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
                {!cart.length ? (
                  <Typography variant="body2" color="text.secondary" sx={{ py: 2 }}>
                    Tap a product, then set length / weight / area quantity.
                  </Typography>
                ) : null}

                <Stack spacing={1.5} sx={{ mt: 2 }}>
                  <Typography variant="body2" color="text.secondary">
                    Lines {money(cartTotal)}
                    {transportEnabled && transportValue
                      ? ` + transport ${money(transportValue)} (non-GST)`
                      : ''}
                  </Typography>
                  <Typography variant="h6">Total {money(displayTotal)}</Typography>
                  {transportEnabled ? (
                    <TextField
                      label="Transport charge"
                      type="number"
                      size="small"
                      value={transportCharge}
                      onChange={(e) => setTransportCharge(e.target.value)}
                      inputProps={{ min: 0, step: '0.01' }}
                      helperText="Added after GST; not taxed separately"
                    />
                  ) : null}
                  <FormControl>
                    <FormLabel>Payment</FormLabel>
                    <RadioGroup
                      row
                      value={paymentMethod}
                      onChange={(e) => setPaymentMethod(e.target.value)}
                    >
                      <FormControlLabel value={PAYMENT_CASH} control={<Radio />} label="Cash" />
                      <FormControlLabel value={PAYMENT_ONLINE} control={<Radio />} label="Online" />
                      {creditEnabled ? (
                        <FormControlLabel value={PAYMENT_CREDIT} control={<Radio />} label="Credit" />
                      ) : null}
                    </RadioGroup>
                  </FormControl>
                  <Button variant="contained" size="large" disabled={saving || !cart.length} onClick={checkout}>
                    {saving ? 'Saving…' : 'Create bill'}
                  </Button>
                </Stack>
              </CardContent>
            </Card>
          </Box>
        </Stack>
      </Stack>
    </PageShell>
  );
}
