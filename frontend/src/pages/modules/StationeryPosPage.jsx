import DeleteOutlineOutlinedIcon from '@mui/icons-material/DeleteOutlineOutlined';
import SearchOutlinedIcon from '@mui/icons-material/SearchOutlined';
import {
  Alert,
  Box,
  Button,
  Card,
  CardContent,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  Divider,
  FormControl,
  FormControlLabel,
  FormLabel,
  List,
  ListItemButton,
  ListItemText,
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
import { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import CustomerPicker from '../../components/CustomerPicker';
import PageShell from '../../components/PageShell';
import TruncateText from '../../components/TruncateText';
import IconActionButton from '../../components/ui/IconActionButton';
import SearchInput from '../../components/ui/SearchInput';
import StatusBadge from '../../components/ui/StatusBadge';
import { useModuleGate } from '../../context/ModulesContext';
import { createBill } from '../../services/billService';
import { getCustomer } from '../../services/customerService';
import {
  fetchStationeryPosCatalog,
  getStationeryByBarcode,
  searchStationeryProducts,
} from '../../services/stationeryService';
import {
  DEFAULT_PAYMENT_METHOD,
  PAYMENT_CASH,
  PAYMENT_CREDIT,
  PAYMENT_ONLINE,
  paymentMethodLabel,
} from '../../utils/paymentMethod';
import { resolveTierUnitPrice } from '../../utils/bulkPricing';
import { qtyStepForUom, uomLabel } from '../../utils/uom';

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

export default function StationeryPosPage() {
  const moduleEnabled = useModuleGate('barcode_pos');
  const creditEnabled = useModuleGate('customer_credit');
  const searchRef = useRef(null);
  const [query, setQuery] = useState('');
  const [hits, setHits] = useState([]);
  const [searching, setSearching] = useState(false);
  const [cart, setCart] = useState([]);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [saving, setSaving] = useState(false);
  const [selectedCustomer, setSelectedCustomer] = useState(null);
  const [paymentMethod, setPaymentMethod] = useState(DEFAULT_PAYMENT_METHOD);
  const [confirmOpen, setConfirmOpen] = useState(false);
  const [bulkEnabled, setBulkEnabled] = useState(false);

  useEffect(() => {
    if (!moduleEnabled) return;
    fetchStationeryPosCatalog({ limit: 1 })
      .then((res) => setBulkEnabled(Boolean(res.data?.bulk_pricing_enabled)))
      .catch(() => {});
    window.requestAnimationFrame(() => searchRef.current?.focus());
  }, [moduleEnabled]);

  useEffect(() => {
    if (!moduleEnabled) return undefined;
    const q = query.trim();
    if (q.length < 1) {
      setHits([]);
      return undefined;
    }
    const handle = window.setTimeout(() => {
      setSearching(true);
      searchStationeryProducts({ q, limit: 25 })
        .then((res) => setHits(res.data?.items || []))
        .catch(() => setHits([]))
        .finally(() => setSearching(false));
    }, 220);
    return () => window.clearTimeout(handle);
  }, [query, moduleEnabled]);

  const cartTotal = useMemo(() => cart.reduce((sum, line) => sum + lineTotal(line), 0), [cart]);
  const lineCount = useMemo(
    () => cart.reduce((sum, line) => sum + Number(line.quantity || 0), 0),
    [cart],
  );

  const addToCart = useCallback((item, quantityOverride = 1) => {
    const tracked = item.stock_quantity !== null && item.stock_quantity !== undefined;
    const available = tracked ? Number(item.stock_quantity) : null;
    const uom = item.uom || 'pcs';
    const increment = Number(quantityOverride) || 1;

    if (tracked && available <= 0) {
      setError(`Out of stock: ${item.name}`);
      return false;
    }

    let blocked = false;
    setCart((prev) => {
      const existing = prev.find((line) => line.item_id === item.id);
      const nextQty = existing ? Number(existing.quantity) + increment : increment;
      if (tracked && nextQty > available) {
        blocked = true;
        return prev;
      }
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
          barcode: item.barcode,
          sku: item.sku,
          base_price: Number(item.price),
          price: Number(item.price),
          gst_percentage: Number(item.gst_percentage || 0),
          quantity: increment,
          uom,
          stock_quantity: available,
          stock_tracked: tracked,
          price_tiers: item.price_tiers || [],
        }),
      ];
    });
    if (blocked) {
      setError(`Insufficient stock for ${item.name}. Available: ${available}.`);
      return false;
    }
    setError('');
    setSuccess('');
    return true;
  }, []);

  const pickHit = (item) => {
    if (addToCart(item)) {
      setQuery('');
      setHits([]);
      searchRef.current?.focus();
    }
  };

  const tryBarcodeEnter = async () => {
    const code = query.trim();
    if (!code) return;
    // Prefer exact barcode when Enter pressed and no hit selected.
    setSearching(true);
    try {
      const res = await getStationeryByBarcode(code);
      if (addToCart(res.data)) {
        setQuery('');
        setHits([]);
      }
    } catch {
      if (hits.length === 1) {
        pickHit(hits[0]);
      } else if (!hits.length) {
        setError('No product matched that search or barcode.');
      }
    } finally {
      setSearching(false);
    }
  };

  const setLineQty = (itemId, rawQty) => {
    const parsed = Number(rawQty);
    if (!Number.isFinite(parsed) || parsed <= 0) {
      setCart((prev) => prev.filter((line) => line.item_id !== itemId));
      return;
    }
    setCart((prev) => {
      const line = prev.find((row) => row.item_id === itemId);
      if (line?.stock_tracked && parsed > Number(line.stock_quantity)) {
        setError(`Insufficient stock. Available: ${line.stock_quantity}.`);
        return prev;
      }
      setError('');
      return prev.map((row) =>
        row.item_id === itemId ? applyTierPrice({ ...row, quantity: parsed }) : row,
      );
    });
  };

  const checkout = async ({ confirmed = false } = {}) => {
    if (!cart.length) {
      setError('Search or scan products to build the bill.');
      return;
    }
    if (paymentMethod === PAYMENT_CREDIT) {
      if (!creditEnabled) {
        setError('Credit / udhari is not enabled for this business.');
        return;
      }
      if (!selectedCustomer?.id) {
        setError('Select a customer for credit bills.');
        return;
      }
      if (!confirmed) {
        setConfirmOpen(true);
        return;
      }
    }
    setSaving(true);
    setError('');
    setSuccess('');
    try {
      const res = await createBill({
        payment_method: paymentMethod,
        customer_id: selectedCustomer?.id || null,
        items: cart.map((line) => ({
          item_id: line.item_id,
          quantity: line.quantity,
        })),
      });
      const bill = res.data;
      let extra = '';
      if (bill.payment_method === PAYMENT_CREDIT && selectedCustomer?.id) {
        try {
          const detail = await getCustomer(selectedCustomer.id);
          const next = detail.data;
          setSelectedCustomer(next);
          extra = ` · Outstanding ${money(next.balance)}`;
        } catch {
          extra = ' · Credit posted';
        }
      }
      setSuccess(
        `Bill ${bill.bill_number} — ${money(bill.grand_total)} (${paymentMethodLabel(bill.payment_method)})${extra}`,
      );
      setCart([]);
      setPaymentMethod(DEFAULT_PAYMENT_METHOD);
      setConfirmOpen(false);
      searchRef.current?.focus();
    } catch (err) {
      setError(err.response?.data?.error?.message || 'Could not create bill.');
      setConfirmOpen(false);
    } finally {
      setSaving(false);
    }
  };

  if (!moduleEnabled) {
    return (
      <PageShell>
        <Alert severity="info">Barcode / Fast POS is not enabled for this business type.</Alert>
      </PageShell>
    );
  }

  return (
    <PageShell>
      <Stack spacing={2}>
        {error ? (
          <Alert severity="error" onClose={() => setError('')}>
            {error}
          </Alert>
        ) : null}
        {success ? <Alert severity="success">{success}</Alert> : null}
        {bulkEnabled ? (
          <Alert severity="info">Bulk price tiers apply automatically when quantity qualifies.</Alert>
        ) : null}

        <Card variant="outlined" sx={{ borderWidth: 2, borderColor: 'primary.main' }}>
          <CardContent>
            <Stack direction={{ xs: 'column', md: 'row' }} spacing={2} alignItems={{ md: 'flex-start' }}>
              <SearchOutlinedIcon color="primary" sx={{ fontSize: 40, display: { xs: 'none', md: 'block' }, mt: 1 }} />
              <Box sx={{ flex: 1, width: '100%' }}>
                <SearchInput
                  inputRef={searchRef}
                  autoFocus
                  label="Search name, SKU, or barcode"
                  placeholder="Type to search — Enter scans barcode if exact match"
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter') {
                      e.preventDefault();
                      tryBarcodeEnter();
                    }
                  }}
                  disabled={searching}
                  size="medium"
                  sx={{ '& .MuiInputBase-root': { fontSize: '1.1rem' } }}
                />
                {hits.length ? (
                  <List dense sx={{ mt: 1, maxHeight: 240, overflow: 'auto', border: 1, borderColor: 'divider', borderRadius: 1 }}>
                    {hits.map((item) => (
                      <ListItemButton key={item.id} onClick={() => pickHit(item)}>
                        <ListItemText
                          primary={item.name}
                          secondary={[item.sku, item.barcode, money(item.price), item.stock_quantity != null ? `Stock ${item.stock_quantity}` : null]
                            .filter(Boolean)
                            .join(' · ')}
                        />
                      </ListItemButton>
                    ))}
                  </List>
                ) : null}
              </Box>
            </Stack>
          </CardContent>
        </Card>

        <Card variant="outlined">
          <CardContent>
            <Stack direction="row" justifyContent="space-between" alignItems="center" sx={{ mb: 1 }}>
              <Typography variant="h6" sx={{ fontWeight: 650, fontSize: '1.05rem' }}>
                Current Bill
              </Typography>
              <Typography variant="body2" color="text.secondary">
                {cart.length} lines · {lineCount} units
              </Typography>
            </Stack>

            {!cart.length ? (
              <Typography variant="body2" color="text.secondary">
                Search products by name or scan a barcode to add lines.
              </Typography>
            ) : (
              <>
                <Box sx={{ overflowX: 'auto' }}>
                  <Table size="small">
                    <TableHead>
                      <TableRow>
                        <TableCell>Item</TableCell>
                        <TableCell>Code</TableCell>
                        <TableCell align="right">Qty</TableCell>
                        <TableCell>UoM</TableCell>
                        <TableCell align="right">Rate</TableCell>
                        <TableCell align="right">Amount</TableCell>
                        <TableCell width={48} />
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {cart.map((line) => (
                        <TableRow key={line.item_id} hover>
                          <TableCell>
                            <TruncateText value={line.name} maxWidth={180} />
                          </TableCell>
                          <TableCell>{line.sku || line.barcode || '—'}</TableCell>
                          <TableCell align="right" sx={{ minWidth: 100 }}>
                            <TextField
                              type="number"
                              size="small"
                              value={line.quantity}
                              onChange={(e) => setLineQty(line.item_id, e.target.value)}
                              inputProps={{
                                min: qtyStepForUom(line.uom),
                                step: qtyStepForUom(line.uom),
                                style: { textAlign: 'right' },
                              }}
                              sx={{ width: 96 }}
                            />
                          </TableCell>
                          <TableCell>{uomLabel(line.uom)}</TableCell>
                          <TableCell align="right">{money(line.price)}</TableCell>
                          <TableCell align="right">{money(lineTotal(line))}</TableCell>
                          <TableCell>
                            <IconActionButton title="Remove" color="error" onClick={() => setLineQty(line.item_id, 0)}>
                              <DeleteOutlineOutlinedIcon fontSize="small" />
                            </IconActionButton>
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </Box>
                <Divider sx={{ my: 2 }} />
                {creditEnabled ? (
                  <Stack spacing={1.5} sx={{ mb: 2 }}>
                    <CustomerPicker
                      label="Customer (required for credit)"
                      value={selectedCustomer}
                      onChange={(customer) => setSelectedCustomer(customer)}
                      onClear={() => {
                        setSelectedCustomer(null);
                        if (paymentMethod === PAYMENT_CREDIT) setPaymentMethod(PAYMENT_CASH);
                      }}
                    />
                    {selectedCustomer ? (
                      <StatusBadge
                        label={
                          Number(selectedCustomer.balance || 0) > 0
                            ? `Outstanding ${money(selectedCustomer.balance)}`
                            : 'No outstanding'
                        }
                        variant={Number(selectedCustomer.balance || 0) > 0 ? 'pending' : 'active'}
                      />
                    ) : null}
                    <FormControl>
                      <FormLabel>Payment</FormLabel>
                      <RadioGroup
                        row
                        value={paymentMethod}
                        onChange={(e) => setPaymentMethod(e.target.value)}
                      >
                        <FormControlLabel value={PAYMENT_CASH} control={<Radio size="small" />} label="Cash" />
                        <FormControlLabel value={PAYMENT_ONLINE} control={<Radio size="small" />} label="Online" />
                        <FormControlLabel
                          value={PAYMENT_CREDIT}
                          control={<Radio size="small" />}
                          label="Credit"
                          disabled={!selectedCustomer}
                        />
                      </RadioGroup>
                    </FormControl>
                  </Stack>
                ) : null}
                <Stack direction="row" justifyContent="space-between" alignItems="center">
                  <Typography variant="h6">{money(cartTotal)}</Typography>
                  <Button
                    variant="contained"
                    size="large"
                    color={paymentMethod === PAYMENT_CREDIT ? 'warning' : 'primary'}
                    onClick={() => checkout()}
                    disabled={saving}
                  >
                    {saving
                      ? 'Creating bill…'
                      : paymentMethod === PAYMENT_CREDIT
                        ? 'Generate Bill (Credit)'
                        : 'Generate Bill'}
                  </Button>
                </Stack>
              </>
            )}
          </CardContent>
        </Card>
      </Stack>

      <Dialog open={confirmOpen} onClose={() => !saving && setConfirmOpen(false)} fullWidth maxWidth="xs">
        <DialogTitle>Confirm credit sale</DialogTitle>
        <DialogContent>
          <Alert severity="warning" sx={{ mt: 1 }}>
            This adds {money(cartTotal)} to {selectedCustomer?.name || 'the customer'}&apos;s outstanding
            balance.
          </Alert>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setConfirmOpen(false)} disabled={saving}>
            Cancel
          </Button>
          <Button variant="contained" color="warning" onClick={() => checkout({ confirmed: true })} disabled={saving}>
            {saving ? 'Billing…' : 'Confirm credit'}
          </Button>
        </DialogActions>
      </Dialog>
    </PageShell>
  );
}
