import DeleteOutlineOutlinedIcon from '@mui/icons-material/DeleteOutlineOutlined';
import PrintOutlinedIcon from '@mui/icons-material/PrintOutlined';
import QrCodeScannerOutlinedIcon from '@mui/icons-material/QrCodeScannerOutlined';
import ShoppingBasketOutlinedIcon from '@mui/icons-material/ShoppingBasketOutlined';
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
  FormControl,
  FormControlLabel,
  FormLabel,
  InputAdornment,
  InputLabel,
  MenuItem,
  Radio,
  RadioGroup,
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
import { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import CustomerPicker from '../../components/CustomerPicker';
import PageShell from '../../components/PageShell';
import PosCartPanel from '../../components/pos/PosCartPanel';
import TruncateText from '../../components/TruncateText';
import IconActionButton from '../../components/ui/IconActionButton';
import StatusBadge from '../../components/ui/StatusBadge';
import { useModuleGate } from '../../context/ModulesContext';
import { billPrintPath, createBill, openBillPrint } from '../../services/billService';
import { getCustomer } from '../../services/customerService';
import { fetchGroceryPosCatalog } from '../../services/groceryService';
import { getItemByBarcode } from '../../services/itemService';
import { listWarehouses } from '../../services/warehouseService';
import {
  DEFAULT_PAYMENT_METHOD,
  PAYMENT_CASH,
  PAYMENT_CREDIT,
  PAYMENT_ONLINE,
  paymentMethodLabel,
} from '../../utils/paymentMethod';
import { defaultScanQty, qtyStepForUom, uomLabel } from '../../utils/uom';
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

export default function GroceryPosPage() {
  const navigate = useNavigate();
  const moduleEnabled = useModuleGate('barcode_pos');
  const creditEnabled = useModuleGate('customer_credit');
  const priceListsEnabled = useModuleGate('price_lists');
  const warehouseEnabled = useModuleGate('warehouse');
  const barcodeRef = useRef(null);
  const [barcode, setBarcode] = useState('');
  const [cart, setCart] = useState([]);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [scanning, setScanning] = useState(false);
  const [saving, setSaving] = useState(false);
  const [recentScans, setRecentScans] = useState([]);
  const [selectedCustomer, setSelectedCustomer] = useState(null);
  const [customerName, setCustomerName] = useState('');
  const [paymentMethod, setPaymentMethod] = useState(DEFAULT_PAYMENT_METHOD);
  const [confirmOpen, setConfirmOpen] = useState(false);
  const [warehouses, setWarehouses] = useState([]);
  const [warehouseId, setWarehouseId] = useState('');
  const [createdBill, setCreatedBill] = useState(null);

  const focusScan = useCallback(() => {
    window.requestAnimationFrame(() => barcodeRef.current?.focus());
  }, []);

  useEffect(() => {
    if (!moduleEnabled || !warehouseEnabled) return;
    listWarehouses()
      .then((res) => {
        const rows = res.data || [];
        setWarehouses(rows);
        const def = rows.find((w) => w.is_default) || rows[0];
        if (def) setWarehouseId((prev) => prev || def.id);
      })
      .catch(() => {});
  }, [moduleEnabled, warehouseEnabled]);

  useEffect(() => {
    if (!moduleEnabled) return;
    fetchGroceryPosCatalog({
      limit: 50,
      customer_id: priceListsEnabled && selectedCustomer?.id ? selectedCustomer.id : undefined,
    })
      .then((res) => setRecentScans((res.data?.items || []).slice(0, 8)))
      .catch(() => {});
    focusScan();
  }, [moduleEnabled, focusScan, priceListsEnabled, selectedCustomer?.id]);

  useEffect(() => {
    if (!moduleEnabled || !priceListsEnabled || !selectedCustomer?.id) return;
    fetchGroceryPosCatalog({ limit: 100, customer_id: selectedCustomer.id })
      .then((res) => {
        const priceMap = Object.fromEntries(
          (res.data?.items || []).map((item) => [
            item.id,
            Number(item.base_price ?? item.list_price ?? item.price),
          ]),
        );
        setCart((prev) =>
          prev.map((line) =>
            priceMap[line.item_id]
              ? applyTierPrice({ ...line, base_price: priceMap[line.item_id] })
              : line,
          ),
        );
      })
      .catch(() => {});
  }, [moduleEnabled, priceListsEnabled, selectedCustomer?.id]);

  const cartTotal = useMemo(() => cart.reduce((sum, line) => sum + lineTotal(line), 0), [cart]);
  const lineCount = useMemo(() => cart.reduce((sum, line) => sum + Number(line.quantity || 0), 0), [cart]);

  const resolvedCustomerName = () => {
    const picked = selectedCustomer?.name?.trim();
    if (picked) return picked;
    const manual = customerName.trim();
    return manual || null;
  };

  const addToCart = useCallback((item, quantityOverride = null) => {
    const tracked = item.stock_quantity !== null && item.stock_quantity !== undefined;
    const available = tracked ? Number(item.stock_quantity) : null;
    const uom = item.uom || 'pcs';
    const increment = quantityOverride ?? defaultScanQty(uom);

    if (tracked && available <= 0) {
      setError(`Out of stock: ${item.name}`);
      return false;
    }

    let blocked = false;
    setCart((prev) => {
      const existing = prev.find((line) => line.item_id === item.id);
      const nextQty = existing ? Number(existing.quantity) + Number(increment) : Number(increment);
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
                base_price: Number(item.base_price ?? item.list_price ?? item.price ?? line.base_price),
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
          base_price: Number(item.base_price ?? item.list_price ?? item.price),
          price: Number(item.base_price ?? item.list_price ?? item.price),
          gst_percentage: Number(item.gst_percentage || 0),
          quantity: Number(increment),
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
    return true;
  }, []);

  const scanBarcode = async () => {
    const code = barcode.trim();
    if (!code || scanning) return;
    setScanning(true);
    setSuccess('');
    try {
      const res = await getItemByBarcode(code);
      if (addToCart(res.data)) {
        setBarcode('');
        focusScan();
      }
    } catch (err) {
      setError(err.response?.data?.error?.message || 'No active item for this barcode.');
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
      setError('Scan items to build the bill.');
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
        warehouse_id: warehouseEnabled && warehouseId ? warehouseId : undefined,
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
      setSuccess(
        `Bill ${bill.bill_number} — ${money(bill.grand_total)} (${paymentMethodLabel(bill.payment_method)})${extra}`,
      );
      resetAfterBill();
      setConfirmOpen(false);
      openBillPrint(bill.id, { auto: true });
      focusScan();
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
          <ShoppingBasketOutlinedIcon color="primary" />
          <Typography variant="h5" sx={{ fontWeight: 700 }}>
            Grocery POS
          </Typography>
        </Stack>
        <Typography variant="body2" color="text.secondary">
          Scan barcodes for fast checkout. Weight items (kg, g, l) support decimal quantities.
        </Typography>

        {error ? <Alert severity="error">{error}</Alert> : null}
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
                  Print
                </Button>
              ) : null
            }
          >
            {success}
          </Alert>
        ) : null}

        {warehouseEnabled && warehouses.length ? (
          <FormControl size="small" sx={{ maxWidth: 360 }}>
            <InputLabel id="pos-warehouse">Sell from warehouse</InputLabel>
            <Select
              labelId="pos-warehouse"
              label="Sell from warehouse"
              value={warehouseId}
              onChange={(e) => setWarehouseId(e.target.value)}
            >
              {warehouses.map((w) => (
                <MenuItem key={w.id} value={w.id}>
                  {w.code} · {w.name}
                  {w.is_default ? ' (default)' : ''}
                </MenuItem>
              ))}
            </Select>
          </FormControl>
        ) : null}

        <Stack direction={{ xs: 'column', md: 'row' }} spacing={2} alignItems="stretch">
          <Box sx={{ flex: 1.2 }}>
            <Card variant="outlined" sx={{ borderColor: 'primary.main' }}>
              <CardContent>
                <Stack direction={{ xs: 'column', sm: 'row' }} spacing={1.5} alignItems={{ sm: 'center' }}>
                  <TextField
                    inputRef={barcodeRef}
                    autoFocus
                    fullWidth
                    label="Scan barcode"
                    placeholder="Focus here and scan — Enter adds line"
                    value={barcode}
                    onChange={(e) => setBarcode(e.target.value)}
                    onKeyDown={(e) => {
                      if (e.key === 'Enter') {
                        e.preventDefault();
                        scanBarcode();
                      }
                    }}
                    disabled={scanning}
                    size="medium"
                    InputProps={{
                      startAdornment: (
                        <InputAdornment position="start">
                          <QrCodeScannerOutlinedIcon fontSize="small" color="action" />
                        </InputAdornment>
                      ),
                    }}
                    sx={{ '& .MuiInputBase-root': { fontSize: '1.05rem' } }}
                    helperText="Scanner or type barcode, then press Enter"
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
                {recentScans.length ? (
                  <Stack direction="row" flexWrap="wrap" gap={1} sx={{ mt: 2 }}>
                    <Typography variant="caption" color="text.secondary" sx={{ width: '100%' }}>
                      Quick pick
                    </Typography>
                    {recentScans.map((item) => (
                      <Button key={item.id} size="small" variant="outlined" onClick={() => addToCart(item)}>
                        {item.name}
                      </Button>
                    ))}
                  </Stack>
                ) : null}
              </CardContent>
            </Card>
          </Box>

          <Box sx={{ flex: 1, minWidth: { md: 360 } }}>
            <PosCartPanel
              title="Current Bill"
              actions={
                cart.length ? (
                  <Typography variant="body2" color="text.secondary">
                    {cart.length} lines · {lineCount} units
                  </Typography>
                ) : null
              }
              empty={
                !cart.length
                  ? 'Scan barcodes to add items. Use quick pick for frequent products.'
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
                    <>
                      <CustomerPicker
                        label="Customer (required for udhari)"
                        value={selectedCustomer}
                        onChange={(customer) => setSelectedCustomer(customer)}
                        onClear={() => {
                          setSelectedCustomer(null);
                          if (paymentMethod === PAYMENT_CREDIT) {
                            setPaymentMethod(PAYMENT_CASH);
                          }
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
                  <Typography variant="h6" sx={{ fontWeight: 700 }}>
                    Total {money(cartTotal)}
                  </Typography>
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
                    color={paymentMethod === PAYMENT_CREDIT ? 'warning' : 'primary'}
                    onClick={() => checkout()}
                    disabled={saving || !cart.length}
                  >
                    {saving
                      ? 'Creating bill…'
                      : paymentMethod === PAYMENT_CREDIT
                        ? 'Generate Bill (Credit)'
                        : 'Generate Bill'}
                  </Button>
                </Stack>
              }
            >
              {cart.length ? (
                <Box sx={{ overflowX: 'auto' }}>
                  <Table size="small">
                    <TableHead>
                      <TableRow>
                        <TableCell>Item</TableCell>
                        <TableCell align="right">Qty</TableCell>
                        <TableCell align="right">Rate</TableCell>
                        <TableCell align="right">Amount</TableCell>
                        <TableCell width={48} />
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {cart.map((line) => (
                        <TableRow key={line.item_id} hover>
                          <TableCell>
                            <TruncateText value={line.name} maxWidth={140} />
                            <Typography variant="caption" color="text.secondary" display="block">
                              {line.barcode || uomLabel(line.uom)}
                            </Typography>
                          </TableCell>
                          <TableCell align="right" sx={{ minWidth: 88 }}>
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
                              sx={{ width: 80 }}
                            />
                          </TableCell>
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
              ) : null}
            </PosCartPanel>
          </Box>
        </Stack>
      </Stack>

      <Dialog open={confirmOpen} onClose={() => !saving && setConfirmOpen(false)} fullWidth maxWidth="xs">
        <DialogTitle>Confirm credit (udhari)</DialogTitle>
        <DialogContent>
          <Stack spacing={1.5} sx={{ mt: 1 }}>
            <Alert severity="warning">
              This adds {money(cartTotal)} to {selectedCustomer?.name || 'the customer'}&apos;s outstanding
              balance. Check the customer before confirming.
            </Alert>
            {selectedCustomer ? (
              <Typography variant="body2">
                Current due: <strong>{money(selectedCustomer.balance)}</strong>
                <br />
                After this bill: <strong>{money(Number(selectedCustomer.balance || 0) + cartTotal)}</strong>
              </Typography>
            ) : null}
          </Stack>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setConfirmOpen(false)} disabled={saving}>
            Cancel
          </Button>
          <Button variant="contained" color="warning" onClick={() => checkout({ confirmed: true })} disabled={saving}>
            {saving ? 'Billing…' : 'Confirm udhari'}
          </Button>
        </DialogActions>
      </Dialog>
    </PageShell>
  );
}
