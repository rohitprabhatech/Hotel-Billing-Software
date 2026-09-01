import DeleteOutlineOutlinedIcon from '@mui/icons-material/DeleteOutlineOutlined';
import MenuBookOutlinedIcon from '@mui/icons-material/MenuBookOutlined';
import PrintOutlinedIcon from '@mui/icons-material/PrintOutlined';
import QrCodeScannerOutlinedIcon from '@mui/icons-material/QrCodeScannerOutlined';
import SearchOutlinedIcon from '@mui/icons-material/SearchOutlined';
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
  Step,
  StepLabel,
  Stepper,
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
import PageShell from '../../components/PageShell';
import PosCartPanel from '../../components/pos/PosCartPanel';
import PosCatalogCard from '../../components/pos/PosCatalogCard';
import TruncateText from '../../components/TruncateText';
import IconActionButton from '../../components/ui/IconActionButton';
import SearchInput from '../../components/ui/SearchInput';
import StatusBadge from '../../components/ui/StatusBadge';
import { useModuleGate } from '../../context/ModulesContext';
import { billPrintPath, createBill, openBillPrint } from '../../services/billService';
import { getCustomer } from '../../services/customerService';
import {
  fetchStationeryPosCatalog,
  getStationeryByBarcode,
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

const BILL_STEPS = ['Add products', 'Review bill', 'Generate & print'];

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
  const navigate = useNavigate();
  const moduleEnabled = useModuleGate('barcode_pos');
  const creditEnabled = useModuleGate('customer_credit');
  const barcodeRef = useRef(null);
  const [catalogItems, setCatalogItems] = useState([]);
  const [catalogLoading, setCatalogLoading] = useState(true);
  const [productFilter, setProductFilter] = useState('');
  const [barcode, setBarcode] = useState('');
  const [scanning, setScanning] = useState(false);
  const [cart, setCart] = useState([]);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [saving, setSaving] = useState(false);
  const [selectedCustomer, setSelectedCustomer] = useState(null);
  const [customerName, setCustomerName] = useState('');
  const [paymentMethod, setPaymentMethod] = useState(DEFAULT_PAYMENT_METHOD);
  const [confirmOpen, setConfirmOpen] = useState(false);
  const [bulkEnabled, setBulkEnabled] = useState(false);
  const [createdBill, setCreatedBill] = useState(null);
  const [activeStep, setActiveStep] = useState(0);

  const focusBarcode = useCallback(() => {
    window.requestAnimationFrame(() => barcodeRef.current?.focus());
  }, []);

  const loadCatalog = useCallback(async () => {
    setCatalogLoading(true);
    try {
      const res = await fetchStationeryPosCatalog({ limit: 120 });
      setCatalogItems(res.data?.items || []);
      setBulkEnabled(Boolean(res.data?.bulk_pricing_enabled));
    } catch {
      setCatalogItems([]);
    } finally {
      setCatalogLoading(false);
    }
  }, []);

  useEffect(() => {
    if (!moduleEnabled) return;
    loadCatalog();
    focusBarcode();
  }, [moduleEnabled, loadCatalog, focusBarcode]);

  useEffect(() => {
    if (!cart.length) setActiveStep(0);
    else if (cart.length && !success) setActiveStep(1);
  }, [cart.length, success]);

  const filteredCatalog = useMemo(() => {
    const q = productFilter.trim().toLowerCase();
    if (!q) return catalogItems;
    return catalogItems.filter((item) => {
      const hay = [item.name, item.sku, item.barcode, item.category_name]
        .filter(Boolean)
        .join(' ')
        .toLowerCase();
      return hay.includes(q);
    });
  }, [catalogItems, productFilter]);

  const cartTotal = useMemo(() => cart.reduce((sum, line) => sum + lineTotal(line), 0), [cart]);
  const lineCount = useMemo(() => cart.reduce((sum, line) => sum + Number(line.quantity || 0), 0), [cart]);

  const resolvedCustomerName = () => {
    const picked = selectedCustomer?.name?.trim();
    if (picked) return picked;
    const manual = customerName.trim();
    return manual || null;
  };

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
                base_price: Number(item.price ?? item.base_price ?? line.base_price),
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
          base_price: Number(item.price ?? item.base_price),
          price: Number(item.price ?? item.base_price),
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

  const scanBarcode = async () => {
    const code = barcode.trim();
    if (!code || scanning) return;
    setScanning(true);
    setSuccess('');
    try {
      const res = await getStationeryByBarcode(code);
      if (addToCart(res.data)) {
        setBarcode('');
        focusBarcode();
      }
    } catch {
      setError('No product found for this barcode. Check the code or pick from the list below.');
    } finally {
      setScanning(false);
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

  const resetAfterBill = () => {
    setCart([]);
    setPaymentMethod(DEFAULT_PAYMENT_METHOD);
    setSelectedCustomer(null);
    setCustomerName('');
  };

  const checkout = async ({ confirmed = false } = {}) => {
    if (!cart.length) {
      setError('Add at least one product to the bill.');
      return;
    }
    if (paymentMethod === PAYMENT_CREDIT) {
      if (!creditEnabled) {
        setError('Credit / udhari is not enabled for this business.');
        return;
      }
      if (!selectedCustomer?.id) {
        setError('Select a customer for credit (udhari) bills.');
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
        customer_name: resolvedCustomerName(),
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
      setCreatedBill(bill);
      setActiveStep(2);
      setSuccess(
        `Bill ${bill.bill_number} — ${money(bill.grand_total)} (${paymentMethodLabel(bill.payment_method)})${extra}`,
      );
      resetAfterBill();
      setConfirmOpen(false);
      openBillPrint(bill.id, { auto: true });
      focusBarcode();
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
        <Stack direction="row" spacing={1} alignItems="center">
          <MenuBookOutlinedIcon color="primary" />
          <Typography variant="h5" sx={{ fontWeight: 700 }}>
            Stationery POS
          </Typography>
        </Stack>
        <Typography variant="body2" color="text.secondary">
          Scan a barcode or tap a product to add it. Change quantity in the cart, then generate the bill and print.
        </Typography>

        <Card variant="outlined" sx={{ bgcolor: 'background.paper' }}>
          <CardContent sx={{ py: 2, '&:last-child': { pb: 2 } }}>
            <Stepper activeStep={activeStep} alternativeLabel sx={{ mb: 0 }}>
              {BILL_STEPS.map((label) => (
                <Step key={label}>
                  <StepLabel>{label}</StepLabel>
                </Step>
              ))}
            </Stepper>
          </CardContent>
        </Card>

        {error ? (
          <Alert severity="error" onClose={() => setError('')}>
            {error}
          </Alert>
        ) : null}
        {success ? (
          <Alert
            severity="success"
            action={
              createdBill ? (
                <Button
                  color="inherit"
                  size="small"
                  startIcon={<PrintOutlinedIcon />}
                  onClick={() => navigate(billPrintPath(createdBill.id))}
                >
                  Print again
                </Button>
              ) : null
            }
          >
            {success}
          </Alert>
        ) : null}

        <Stack direction={{ xs: 'column', lg: 'row' }} spacing={2} alignItems="stretch">
          <Box sx={{ flex: 1.25, minWidth: 0 }}>
            <Card variant="outlined" sx={{ mb: 2, borderColor: 'primary.main' }}>
              <CardContent>
                <Typography variant="subtitle2" sx={{ mb: 1, fontWeight: 600 }}>
                  Step 1 — Scan barcode
                </Typography>
                <Stack direction={{ xs: 'column', sm: 'row' }} spacing={1.5} alignItems={{ sm: 'center' }}>
                  <TextField
                    inputRef={barcodeRef}
                    autoFocus
                    fullWidth
                    label="Barcode scanner"
                    placeholder="Scan here — product adds automatically"
                    value={barcode}
                    onChange={(e) => setBarcode(e.target.value)}
                    onKeyDown={(e) => {
                      if (e.key === 'Enter') {
                        e.preventDefault();
                        scanBarcode();
                      }
                    }}
                    disabled={scanning}
                    InputProps={{
                      startAdornment: (
                        <InputAdornment position="start">
                          <QrCodeScannerOutlinedIcon fontSize="small" color="action" />
                        </InputAdornment>
                      ),
                    }}
                    helperText="Use your barcode gun in this box, or type the code and press Enter"
                  />
                  <Button
                    variant="contained"
                    onClick={scanBarcode}
                    disabled={scanning || !barcode.trim()}
                    sx={{ minWidth: { sm: 100 }, width: { xs: '100%', sm: 'auto' }, flexShrink: 0 }}
                  >
                    {scanning ? '…' : 'Add'}
                  </Button>
                </Stack>
              </CardContent>
            </Card>

            <Typography variant="subtitle2" sx={{ mb: 1, fontWeight: 600 }}>
              Or pick from catalog
            </Typography>
            <SearchInput
              label="Find product"
              placeholder="Type name, SKU, or barcode…"
              value={productFilter}
              onChange={(e) => setProductFilter(e.target.value)}
              sx={{ mb: 1.5 }}
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <SearchOutlinedIcon fontSize="small" color="action" />
                  </InputAdornment>
                ),
              }}
            />
            {bulkEnabled ? (
              <Typography variant="caption" color="text.secondary" display="block" sx={{ mb: 1 }}>
                Bulk pack rates apply automatically when you increase quantity (e.g. 12 pens = lower per-piece rate).
              </Typography>
            ) : null}

            {catalogLoading ? (
              <Typography variant="body2" color="text.secondary" sx={{ py: 2 }}>
                Loading products…
              </Typography>
            ) : !filteredCatalog.length ? (
              <Alert severity="info">
                {productFilter.trim()
                  ? 'No products match your search. Try another name or SKU.'
                  : 'No products in catalog. Add items under Items first.'}
              </Alert>
            ) : (
              <Box
                sx={{
                  display: 'grid',
                  gap: 1.25,
                  gridTemplateColumns: { xs: '1fr 1fr', sm: 'repeat(3, 1fr)', md: 'repeat(4, 1fr)' },
                  maxHeight: { xs: 360, md: 420 },
                  overflowY: 'auto',
                  pr: 0.5,
                }}
              >
                {filteredCatalog.map((item) => {
                  const outOfStock =
                    item.stock_quantity !== null &&
                    item.stock_quantity !== undefined &&
                    Number(item.stock_quantity) <= 0;
                  const inCart = cart.some((line) => line.item_id === item.id);
                  return (
                    <PosCatalogCard
                      key={item.id}
                      title={item.name}
                      subtitle={`${money(item.price ?? item.base_price)}${inCart ? ' · In cart' : ''}`}
                      disabled={outOfStock}
                      selected={inCart}
                      onClick={() => addToCart(item)}
                    />
                  );
                })}
              </Box>
            )}
          </Box>

          <Box sx={{ flex: 1, minWidth: { lg: 360 } }}>
            <PosCartPanel
              title="Step 2 — Current bill"
              actions={
                cart.length ? (
                  <Typography variant="body2" color="text.secondary">
                    {cart.length} lines · {lineCount} pcs
                  </Typography>
                ) : null
              }
              empty={
                !cart.length ? (
                  <Stack spacing={1} alignItems="center">
                    <Typography variant="body2" color="text.secondary">
                      Cart is empty
                    </Typography>
                    <Typography variant="caption" color="text.secondary" textAlign="center">
                      Scan a barcode or tap a product on the left to start the bill.
                    </Typography>
                  </Stack>
                ) : null
              }
              footer={
                <Stack spacing={1.5}>
                  <Typography variant="subtitle2" sx={{ fontWeight: 600 }}>
                    Step 3 — Customer & payment
                  </Typography>
                  <TextField
                    size="small"
                    label="Customer name (optional)"
                    placeholder="Walk-in or type name on bill"
                    value={customerName}
                    onChange={(e) => setCustomerName(e.target.value)}
                    fullWidth
                  />
                  {creditEnabled ? (
                    <>
                      <CustomerPicker
                        label="Customer (required for udhari)"
                        value={selectedCustomer}
                        onChange={setSelectedCustomer}
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
                    </>
                  ) : null}
                  <Stack direction="row" justifyContent="space-between" alignItems="center">
                    <Typography variant="h6" sx={{ fontWeight: 700 }}>
                      Total {money(cartTotal)}
                    </Typography>
                    {bulkEnabled && cart.some((line) => line.price < line.base_price) ? (
                      <Chip size="small" label="Bulk rate applied" color="success" variant="outlined" />
                    ) : null}
                  </Stack>
                  <FormControl>
                    <FormLabel>Payment</FormLabel>
                    <RadioGroup
                      row
                      value={paymentMethod}
                      onChange={(e) => setPaymentMethod(e.target.value)}
                    >
                      <FormControlLabel value={PAYMENT_CASH} control={<Radio size="small" />} label="Cash" />
                      <FormControlLabel value={PAYMENT_ONLINE} control={<Radio size="small" />} label="Online" />
                      {creditEnabled ? (
                        <FormControlLabel
                          value={PAYMENT_CREDIT}
                          control={<Radio size="small" />}
                          label="Credit (Udhari)"
                          disabled={!selectedCustomer}
                        />
                      ) : null}
                    </RadioGroup>
                  </FormControl>
                  <Button
                    variant="contained"
                    size="large"
                    fullWidth
                    startIcon={<PrintOutlinedIcon />}
                    color={paymentMethod === PAYMENT_CREDIT ? 'warning' : 'primary'}
                    onClick={() => checkout()}
                    disabled={saving || !cart.length}
                  >
                    {saving
                      ? 'Creating bill…'
                      : paymentMethod === PAYMENT_CREDIT
                        ? 'Generate Bill & Print (Credit)'
                        : 'Generate Bill & Print'}
                  </Button>
                </Stack>
              }
            >
              {cart.length ? (
                <Box sx={{ overflowX: 'auto' }}>
                  <Table size="small">
                    <TableHead>
                      <TableRow>
                        <TableCell>Product</TableCell>
                        <TableCell align="right">Qty</TableCell>
                        <TableCell align="right">Rate</TableCell>
                        <TableCell align="right">Amount</TableCell>
                        <TableCell width={48} />
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {cart.map((line) => {
                        const bulkApplied = bulkEnabled && line.price < line.base_price;
                        return (
                          <TableRow key={line.item_id} hover>
                            <TableCell>
                              <TruncateText value={line.name} maxWidth={130} />
                              <Typography variant="caption" color="text.secondary" display="block">
                                {line.sku || line.barcode || uomLabel(line.uom)}
                              </Typography>
                              {bulkApplied ? (
                                <Typography variant="caption" color="success.main" display="block">
                                  Bulk {money(line.price)} (was {money(line.base_price)})
                                </Typography>
                              ) : null}
                            </TableCell>
                            <TableCell align="right" sx={{ minWidth: 80 }}>
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
                                sx={{ width: 72 }}
                              />
                            </TableCell>
                            <TableCell align="right">{money(line.price)}</TableCell>
                            <TableCell align="right">{money(lineTotal(line))}</TableCell>
                            <TableCell>
                              <IconActionButton
                                title="Remove"
                                color="error"
                                onClick={() => setLineQty(line.item_id, 0)}
                              >
                                <DeleteOutlineOutlinedIcon fontSize="small" />
                              </IconActionButton>
                            </TableCell>
                          </TableRow>
                        );
                      })}
                    </TableBody>
                  </Table>
                </Box>
              ) : null}
            </PosCartPanel>
          </Box>
        </Stack>
      </Stack>

      <Dialog open={confirmOpen} onClose={() => !saving && setConfirmOpen(false)} fullWidth maxWidth="xs">
        <DialogTitle>Confirm credit (udhari)</DialogTitle>
        <DialogContent>
          <Alert severity="warning" sx={{ mt: 1 }}>
            This adds {money(cartTotal)} to {selectedCustomer?.name || 'the customer'}&apos;s outstanding balance.
          </Alert>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setConfirmOpen(false)} disabled={saving}>
            Cancel
          </Button>
          <Button variant="contained" color="warning" onClick={() => checkout({ confirmed: true })} disabled={saving}>
            {saving ? 'Billing…' : 'Confirm & print'}
          </Button>
        </DialogActions>
      </Dialog>
    </PageShell>
  );
}
