import DeleteOutlineOutlinedIcon from '@mui/icons-material/DeleteOutlineOutlined';
import PrintOutlinedIcon from '@mui/icons-material/PrintOutlined';
import QrCodeScannerOutlinedIcon from '@mui/icons-material/QrCodeScannerOutlined';
import StraightenOutlinedIcon from '@mui/icons-material/StraightenOutlined';
import WhatsAppIcon from '@mui/icons-material/WhatsApp';
import {
  Alert,
  Box,
  Button,
  Card,
  CardContent,
  Chip,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  FormControl,
  FormControlLabel,
  FormLabel,
  InputAdornment,
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
import { useNavigate } from 'react-router-dom';
import CustomerPicker from '../../components/CustomerPicker';
import EmptyState from '../../components/EmptyState';
import PageShell from '../../components/PageShell';
import PosCartPanel from '../../components/pos/PosCartPanel';
import PosCatalogCard from '../../components/pos/PosCatalogCard';
import IconActionButton from '../../components/ui/IconActionButton';
import SearchInput from '../../components/ui/SearchInput';
import StatusBadge from '../../components/ui/StatusBadge';
import { useModuleGate } from '../../context/ModulesContext';
import {
  billPrintPath,
  createBill,
  sendBillWhatsapp,
} from '../../services/billService';
import { getCustomer } from '../../services/customerService';
import { fetchHardwarePosCatalog, quoteHardwareLine } from '../../services/hardwareService';
import { getItemByBarcode } from '../../services/itemService';
import {
  DEFAULT_PAYMENT_METHOD,
  PAYMENT_CASH,
  PAYMENT_CREDIT,
  PAYMENT_ONLINE,
  paymentMethodLabel,
} from '../../utils/paymentMethod';
import { qtyStepForUom, uomLabel } from '../../utils/uom';
import { resolveTierUnitPrice } from '../../utils/bulkPricing';
import { getApiErrorMessage } from '../../utils/apiError';

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

async function quoteLine(line) {
  try {
    const res = await quoteHardwareLine({ item_id: line.item_id, quantity: line.quantity });
    const quoted = res.data;
    return applyTierPrice({
      ...line,
      price: Number(quoted.unit_price),
      base_price: Number(quoted.unit_price),
      stock_quantity_deducted: quoted.stock_quantity_deducted,
      stock_uom: quoted.stock_uom,
      sufficient_stock: quoted.sufficient_stock,
    });
  } catch {
    return line;
  }
}

export default function HardwarePosPage() {
  const navigate = useNavigate();

  const moduleEnabled = useModuleGate('uom_measurement');
  const creditEnabled = useModuleGate('customer_credit');
  const transportEnabled = useModuleGate('transport_charges');

  const barcodeRef = useRef(null);
  const [catalog, setCatalog] = useState([]);
  const [q, setQ] = useState('');
  const [categoryId, setCategoryId] = useState('');
  const [barcode, setBarcode] = useState('');
  const [scanning, setScanning] = useState(false);
  const [cart, setCart] = useState([]);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [saving, setSaving] = useState(false);
  const [paymentMethod, setPaymentMethod] = useState(DEFAULT_PAYMENT_METHOD);
  const [transportCharge, setTransportCharge] = useState('0');
  const [selectedCustomer, setSelectedCustomer] = useState(null);
  const [customerName, setCustomerName] = useState('');
  const [confirmCreditOpen, setConfirmCreditOpen] = useState(false);
  const [createdBill, setCreatedBill] = useState(null);
  const [whatsappSending, setWhatsappSending] = useState(false);
  const [whatsappMessage, setWhatsappMessage] = useState('');
  const [whatsappError, setWhatsappError] = useState('');
  const [phoneDialogOpen, setPhoneDialogOpen] = useState(false);
  const [phoneDraftCc, setPhoneDraftCc] = useState('91');
  const [phoneDraft, setPhoneDraft] = useState('');

  const focusScan = useCallback(() => {
    window.requestAnimationFrame(() => barcodeRef.current?.focus());
  }, []);

  const loadCatalog = useCallback(async () => {
    if (!moduleEnabled) return;
    try {
      const res = await fetchHardwarePosCatalog({ q: q.trim() || undefined, limit: 80 });
      setCatalog(res.data?.items || []);
    } catch (err) {
      setError(getApiErrorMessage(err, 'Unable to load hardware catalog.'));
    }
  }, [moduleEnabled, q]);

  useEffect(() => {
    loadCatalog();
  }, [loadCatalog]);

  useEffect(() => {
    focusScan();
  }, [focusScan]);

  const categories = useMemo(() => {
    const map = new Map();
    catalog.forEach((item) => {
      if (item.category_id && item.category_name) {
        map.set(item.category_id, item.category_name);
      }
    });
    return [...map.entries()].map(([id, name]) => ({ id, name }));
  }, [catalog]);

  const displayCatalog = useMemo(
    () => catalog.filter((item) => !categoryId || item.category_id === categoryId),
    [catalog, categoryId],
  );

  const cartTotal = useMemo(() => cart.reduce((sum, line) => sum + lineTotal(line), 0), [cart]);
  const transportValue = transportEnabled ? Number(transportCharge) || 0 : 0;
  const displayTotal = cartTotal + transportValue;

  const addCatalogItem = async (item) => {
    const saleUom = item.sale_uom || item.uom || 'pcs';
    const step = Number(item.qty_step || qtyStepForUom(saleUom));
    const tracked = item.stock_quantity !== null && item.stock_quantity !== undefined;
    const available = tracked ? Number(item.stock_quantity) : null;
    if (tracked && available <= 0) {
      setError(`Out of stock: ${item.name}`);
      return false;
    }

    let nextCart = [];
    setCart((prev) => {
      const existing = prev.find((line) => line.item_id === item.id);
      const nextQty = existing ? Number(existing.quantity) + step : step;
      if (existing) {
        nextCart = prev.map((line) =>
          line.item_id === item.id
            ? applyTierPrice({
                ...line,
                quantity: nextQty,
                price_tiers: item.price_tiers || line.price_tiers || [],
                base_price: Number(item.price ?? line.base_price),
              })
            : line,
        );
        return nextCart;
      }
      nextCart = [
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
      return nextCart;
    });

    setError('');
    setSuccess('');
    const target = nextCart.find((line) => line.item_id === item.id);
    if (target) {
      const quoted = await quoteLine(target);
      setCart((prev) => prev.map((line) => (line.item_id === item.id ? quoted : line)));
    }
    return true;
  };

  const addItem = (item) => {
    addCatalogItem(item);
  };

  const scanBarcode = async () => {
    const code = barcode.trim();
    if (!code || scanning) return;
    setScanning(true);
    setError('');
    try {
      const res = await getItemByBarcode(code);
      const item = res.data;
      const catalogItem = catalog.find((row) => row.id === item.id);
      if (!catalogItem) {
        setError('Item not found in hardware catalog.');
        return;
      }
      if (await addCatalogItem(catalogItem)) {
        setBarcode('');
        setSuccess(`Added ${catalogItem.name}`);
        focusScan();
      }
    } catch (err) {
      setError(getApiErrorMessage(err, 'No active item for this barcode.'));
    } finally {
      setScanning(false);
    }
  };

  const setLineQty = async (itemId, rawQty) => {
    const parsed = Number(rawQty);
    if (!Number.isFinite(parsed) || parsed <= 0) {
      setCart((prev) => prev.filter((line) => line.item_id !== itemId));
      return;
    }
    let updatedLine = null;
    setCart((prev) =>
      prev.map((line) => {
        if (line.item_id !== itemId) return line;
        updatedLine = applyTierPrice({ ...line, quantity: parsed });
        return updatedLine;
      }),
    );
    if (updatedLine) {
      const quoted = await quoteLine(updatedLine);
      setCart((prev) => prev.map((line) => (line.item_id === itemId ? quoted : line)));
    }
  };

  const removeLine = (itemId) => {
    setCart((prev) => prev.filter((line) => line.item_id !== itemId));
  };

  const resolvedCustomerName = () => {
    const picked = selectedCustomer?.name?.trim();
    if (picked) return picked;
    const manual = customerName.trim();
    return manual || null;
  };

  const resetAfterBill = () => {
    setCart([]);
    setPaymentMethod(DEFAULT_PAYMENT_METHOD);
    setTransportCharge('0');
    setSelectedCustomer(null);
    setCustomerName('');
  };

  const checkout = async ({ confirmed = false } = {}) => {
    if (!cart.length) {
      setError('Add at least one measured item.');
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
        setConfirmCreditOpen(true);
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
        customer_name: resolvedCustomerName(),
        transport_charge: transportEnabled ? Number(transportCharge) || 0 : 0,
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
          extra = ` · Outstanding ${money(detail.data?.balance)}`;
        } catch {
          extra = ' · Credit posted';
        }
      }
      setCreatedBill(bill);
      setWhatsappMessage('');
      setWhatsappError('');
      setSuccess(
        `Bill ${bill.bill_number} — ${money(bill.grand_total)} (${paymentMethodLabel(bill.payment_method)})${extra}`,
      );
      resetAfterBill();
      setConfirmCreditOpen(false);
      await loadCatalog();
      focusScan();
    } catch (err) {
      setError(getApiErrorMessage(err, 'Could not create bill.'));
      setConfirmCreditOpen(false);
    } finally {
      setSaving(false);
    }
  };

  const doSendWhatsapp = async (payload = {}) => {
    if (!createdBill?.id || whatsappSending) return;
    setWhatsappSending(true);
    setWhatsappError('');
    setWhatsappMessage('');
    try {
      const res = await sendBillWhatsapp(createdBill.id, payload);
      setWhatsappMessage(res.data?.message || 'Bill sent successfully on WhatsApp.');
      if (res.data?.bill) setCreatedBill(res.data.bill);
      setPhoneDialogOpen(false);
    } catch (err) {
      setWhatsappError(
        getApiErrorMessage(err, 'Unable to send the bill on WhatsApp. Please try Print Bill.'),
      );
    } finally {
      setWhatsappSending(false);
    }
  };

  const onSendWhatsappClick = () => {
    if (!createdBill) return;
    const hasPhone = Boolean(createdBill.customer_phone_national);
    if (!hasPhone) {
      setPhoneDraftCc(createdBill.customer_phone_country_code || '91');
      setPhoneDraft('');
      setPhoneDialogOpen(true);
      return;
    }
    doSendWhatsapp({
      country_code: createdBill.customer_phone_country_code,
      phone: createdBill.customer_phone_national,
      customer_name: createdBill.customer_name || resolvedCustomerName(),
    });
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
          Sell pipes, cement, tiles, and fittings by metre, kg, sqft, and other units. Price is per
          sale unit — e.g. 10 m × ₹450 = ₹4,500.
        </Typography>

        {error ? <Alert severity="error">{error}</Alert> : null}
        {success ? (
          <Alert
            severity="success"
            action={
              createdBill ? (
                <Stack direction="row" spacing={0.5}>
                  <Button
                    color="inherit"
                    size="small"
                    startIcon={<PrintOutlinedIcon />}
                    onClick={() => navigate(billPrintPath(createdBill.id))}
                  >
                    Print
                  </Button>
                  <Button
                    color="inherit"
                    size="small"
                    startIcon={<WhatsAppIcon />}
                    disabled={whatsappSending}
                    onClick={onSendWhatsappClick}
                  >
                    WhatsApp
                  </Button>
                </Stack>
              ) : null
            }
          >
            {success}
          </Alert>
        ) : null}
        {whatsappMessage ? <Alert severity="success">{whatsappMessage}</Alert> : null}
        {whatsappError ? <Alert severity="warning">{whatsappError}</Alert> : null}

        <Stack direction={{ xs: 'column', md: 'row' }} spacing={2} alignItems="stretch">
          <Box sx={{ flex: 1.2 }}>
            <Card variant="outlined" sx={{ mb: 2, borderColor: 'primary.main' }}>
              <CardContent>
                <Stack direction={{ xs: 'column', sm: 'row' }} spacing={1.5} alignItems={{ sm: 'center' }}>
                  <TextField
                    inputRef={barcodeRef}
                    label="Scan barcode"
                    placeholder="Focus here and scan item barcode…"
                    value={barcode}
                    onChange={(e) => setBarcode(e.target.value)}
                    onKeyDown={(e) => {
                      if (e.key === 'Enter') {
                        e.preventDefault();
                        scanBarcode();
                      }
                    }}
                    disabled={scanning}
                    fullWidth
                    size="medium"
                    InputProps={{
                      startAdornment: (
                        <InputAdornment position="start">
                          <QrCodeScannerOutlinedIcon fontSize="small" color="action" />
                        </InputAdornment>
                      ),
                    }}
                    helperText="Barcode adds the item with the default quantity step."
                  />
                  <Button
                    variant="contained"
                    onClick={scanBarcode}
                    disabled={scanning || !barcode.trim()}
                    sx={{ minWidth: { sm: 100 }, width: { xs: '100%', sm: 'auto' } }}
                  >
                    {scanning ? '…' : 'Add'}
                  </Button>
                </Stack>
              </CardContent>
            </Card>

            <SearchInput
              label="Search items"
              placeholder="Pipe, cement, tile, rod…"
              value={q}
              onChange={(e) => setQ(e.target.value)}
              sx={{ mb: 2 }}
            />

            {categories.length ? (
              <Box sx={{ overflowX: 'auto', mb: 2, pb: 0.5 }}>
                <Stack direction="row" spacing={1} sx={{ minWidth: 'min-content' }}>
                  <Chip
                    label="All"
                    clickable
                    color={!categoryId ? 'primary' : 'default'}
                    variant={!categoryId ? 'filled' : 'outlined'}
                    onClick={() => setCategoryId('')}
                  />
                  {categories.map((cat) => (
                    <Chip
                      key={cat.id}
                      label={cat.name}
                      clickable
                      color={categoryId === cat.id ? 'primary' : 'default'}
                      variant={categoryId === cat.id ? 'filled' : 'outlined'}
                      onClick={() => setCategoryId(cat.id)}
                    />
                  ))}
                </Stack>
              </Box>
            ) : null}

            <Box
              sx={{
                display: 'grid',
                gap: 1.5,
                gridTemplateColumns: { xs: '1fr 1fr', sm: 'repeat(3, 1fr)' },
              }}
            >
              {displayCatalog.map((item) => {
                const saleUom = item.sale_uom || item.uom || 'pcs';
                const tracked = item.stock_quantity !== null && item.stock_quantity !== undefined;
                const outOfStock = tracked && Number(item.stock_quantity) <= 0;
                const stockLabel = tracked
                  ? `Stock ${Number(item.stock_quantity).toFixed(3).replace(/\.?0+$/, '')} ${(item.uom || 'pcs').toUpperCase()}`
                  : null;
                return (
                  <PosCatalogCard
                    key={item.id}
                    title={item.name}
                    subtitle={`${uomLabel(saleUom)} · ${money(item.price)}/${saleUom.toUpperCase()}${
                      stockLabel ? ` · ${stockLabel}` : ''
                    }`}
                    disabled={outOfStock}
                    onClick={() => addItem(item)}
                  />
                );
              })}
            </Box>
            {!displayCatalog.length ? (
              <EmptyState
                title="No items found"
                description="Try another search or category."
              />
            ) : null}
            {!displayCatalog.length ? (
              <Alert severity="info" sx={{ mt: 2 }}>
                {categoryId
                  ? 'No items in this category.'
                  : 'No items found. Create catalog items with stock UoM (and optional sale UoM).'}
              </Alert>
            ) : null}
          </Box>

          <Box sx={{ flex: 1, minWidth: { md: 360 } }}>
            <PosCartPanel
              title="Current Bill"
              empty={
                !cart.length
                  ? 'Scan or tap a product, then set length / weight / area quantity.'
                  : null
              }
              footer={
                <Stack spacing={1.5}>
                  <TextField
                    size="small"
                    label="Customer name (optional)"
                    placeholder="Walk-in or type name manually"
                    value={customerName}
                    onChange={(e) => setCustomerName(e.target.value)}
                    fullWidth
                  />
                  {creditEnabled ? (
                    <CustomerPicker
                      value={selectedCustomer}
                      onChange={setSelectedCustomer}
                      helperText="Required for credit / udhari bills"
                    />
                  ) : null}

                  <Typography variant="body2" color="text.secondary">
                    Lines {money(cartTotal)}
                    {transportEnabled && transportValue
                      ? ` + transport ${money(transportValue)} (non-GST)`
                      : ''}
                  </Typography>
                  <Typography variant="h6" sx={{ fontWeight: 700 }}>
                    Total {money(displayTotal)}
                  </Typography>
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
                  <Button
                    variant="contained"
                    size="large"
                    fullWidth
                    disabled={saving || !cart.length}
                    onClick={() => checkout()}
                  >
                    {saving ? 'Creating bill…' : 'Generate Bill'}
                  </Button>
                </Stack>
              }
            >
              {cart.length ? (
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
                          <Typography variant="caption" color="text.secondary" display="block">
                            {money(line.price)} / {(line.sale_uom || 'pcs').toUpperCase()}
                          </Typography>
                          {line.stock_uom && line.stock_uom !== line.sale_uom ? (
                            <Typography variant="caption" color="text.secondary" display="block">
                              Deducts {line.stock_quantity_deducted ?? '—'} {line.stock_uom.toUpperCase()}
                            </Typography>
                          ) : null}
                          {line.sufficient_stock === false ? (
                            <StatusBadge label="Low Stock" sx={{ mt: 0.5 }} />
                          ) : null}
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
                          <IconActionButton title="Remove" onClick={() => removeLine(line.item_id)}>
                            <DeleteOutlineOutlinedIcon fontSize="small" />
                          </IconActionButton>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              ) : null}
            </PosCartPanel>
          </Box>
        </Stack>
      </Stack>

      <Dialog open={confirmCreditOpen} onClose={() => setConfirmCreditOpen(false)}>
        <DialogTitle>Confirm credit bill?</DialogTitle>
        <DialogContent>
          <Typography variant="body2">
            Post {money(displayTotal)} to {selectedCustomer?.name || 'customer'} credit ledger?
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setConfirmCreditOpen(false)}>Cancel</Button>
          <Button variant="contained" onClick={() => checkout({ confirmed: true })} disabled={saving}>
            Confirm credit
          </Button>
        </DialogActions>
      </Dialog>

      <Dialog open={phoneDialogOpen} onClose={() => setPhoneDialogOpen(false)}>
        <DialogTitle>Customer phone for WhatsApp</DialogTitle>
        <DialogContent>
          <Stack spacing={1.5} sx={{ mt: 1, minWidth: 280 }}>
            <TextField
              label="Country code"
              value={phoneDraftCc}
              onChange={(e) => setPhoneDraftCc(e.target.value)}
              size="small"
            />
            <TextField
              label="Phone number"
              value={phoneDraft}
              onChange={(e) => setPhoneDraft(e.target.value)}
              size="small"
              autoFocus
            />
          </Stack>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setPhoneDialogOpen(false)}>Cancel</Button>
          <Button
            variant="contained"
            disabled={whatsappSending || !phoneDraft.trim()}
            onClick={() =>
              doSendWhatsapp({
                country_code: phoneDraftCc,
                phone: phoneDraft,
                customer_name: createdBill?.customer_name || resolvedCustomerName(),
              })
            }
          >
            Send
          </Button>
        </DialogActions>
      </Dialog>
    </PageShell>
  );
}
