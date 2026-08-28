import AddOutlinedIcon from '@mui/icons-material/AddOutlined';
import CheckroomOutlinedIcon from '@mui/icons-material/CheckroomOutlined';
import DeleteOutlineOutlinedIcon from '@mui/icons-material/DeleteOutlineOutlined';
import QrCodeScannerOutlinedIcon from '@mui/icons-material/QrCodeScannerOutlined';
import RemoveOutlinedIcon from '@mui/icons-material/RemoveOutlined';
import WhatsAppIcon from '@mui/icons-material/WhatsApp';
import {
  Alert,
  Box,
  Button,
  Card,
  CardActionArea,
  CardContent,
  CardMedia,
  Chip,
  CircularProgress,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  Divider,
  FormControl,
  FormControlLabel,
  FormLabel,
  Grid,
  IconButton,
  InputAdornment,
  Radio,
  RadioGroup,
  Stack,
  TextField,
  Typography,
} from '@mui/material';
import { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import CustomerPicker from '../../components/CustomerPicker';
import PageShell from '../../components/PageShell';
import VariantStockGrid from '../../components/VariantStockGrid';
import { useModuleGate } from '../../context/ModulesContext';
import { PATHS } from '../../routes/paths';
import {
  billPrintPath,
  createBill,
  downloadBillPdf,
  sendBillWhatsapp,
} from '../../services/billService';
import { getCustomer } from '../../services/customerService';
import { fetchClothingPosCatalog } from '../../services/clothingService';
import { getItemByBarcode } from '../../services/itemService';
import {
  DEFAULT_PAYMENT_METHOD,
  PAYMENT_CASH,
  PAYMENT_CREDIT,
  PAYMENT_ONLINE,
  paymentMethodLabel,
} from '../../utils/paymentMethod';

function money(value) {
  return `₹${Number(value || 0).toFixed(2)}`;
}

function getApiErrorMessage(err, fallback) {
  return err?.response?.data?.error?.message || fallback;
}

export default function ClothingPosPage() {
  const moduleEnabled = useModuleGate('variants');
  const barcodePosEnabled = useModuleGate('barcode_pos');
  const creditEnabled = useModuleGate('customer_credit');
  const navigate = useNavigate();
  const location = useLocation();
  const clothingFromPath = location.pathname.startsWith('/owner')
    ? PATHS.ownerClothing
    : PATHS.billingClothing;

  const barcodeRef = useRef(null);
  const [items, setItems] = useState([]);
  const [q, setQ] = useState('');
  const [categoryId, setCategoryId] = useState('');
  const [barcode, setBarcode] = useState('');
  const [scanning, setScanning] = useState(false);
  const [cart, setCart] = useState([]);
  const [picker, setPicker] = useState(null);
  const [selectedCustomer, setSelectedCustomer] = useState(null);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [saving, setSaving] = useState(false);
  const [paymentMethod, setPaymentMethod] = useState(DEFAULT_PAYMENT_METHOD);
  const [createdBill, setCreatedBill] = useState(null);
  const [whatsappSending, setWhatsappSending] = useState(false);
  const [whatsappMessage, setWhatsappMessage] = useState('');
  const [whatsappError, setWhatsappError] = useState('');
  const [phoneDialogOpen, setPhoneDialogOpen] = useState(false);
  const [phoneDraftCc, setPhoneDraftCc] = useState('91');
  const [phoneDraft, setPhoneDraft] = useState('');
  const [confirmCreditOpen, setConfirmCreditOpen] = useState(false);

  const focusScan = useCallback(() => {
    if (!barcodePosEnabled) return;
    window.requestAnimationFrame(() => barcodeRef.current?.focus());
  }, [barcodePosEnabled]);

  const load = useCallback(async () => {
    setError('');
    try {
      const res = await fetchClothingPosCatalog({ q: q || undefined, limit: 100 });
      setItems(res.data?.items || []);
    } catch (err) {
      setError(getApiErrorMessage(err, 'Failed to load clothing catalog'));
    }
  }, [q]);

  useEffect(() => {
    if (!moduleEnabled) return;
    const handle = window.setTimeout(() => {
      load();
    }, 200);
    return () => window.clearTimeout(handle);
  }, [moduleEnabled, load]);

  useEffect(() => {
    if (moduleEnabled && barcodePosEnabled) focusScan();
  }, [moduleEnabled, barcodePosEnabled, focusScan]);

  const categories = useMemo(() => {
    const map = new Map();
    items.forEach((item) => {
      if (item.category_id) {
        map.set(item.category_id, item.category_name || 'Category');
      }
    });
    return [...map.entries()]
      .map(([id, name]) => ({ id, name }))
      .sort((a, b) => a.name.localeCompare(b.name));
  }, [items]);

  const displayItems = useMemo(() => {
    if (!categoryId) return items;
    return items.filter((item) => item.category_id === categoryId);
  }, [items, categoryId]);

  const total = useMemo(
    () => cart.reduce((sum, line) => sum + Number(line.price) * Number(line.quantity), 0),
    [cart],
  );

  const lineCount = useMemo(
    () => cart.reduce((sum, line) => sum + Number(line.quantity || 0), 0),
    [cart],
  );

  const bumpQty = (lineKey, delta) => {
    setCart((prev) =>
      prev
        .map((line) => {
          if (line.line_key !== lineKey) return line;
          const nextQty = Number(line.quantity) + delta;
          if (nextQty <= 0) return null;
          if (nextQty > Number(line.stock_quantity)) {
            setError(
              `Insufficient stock. Available: ${line.stock_quantity}, requested: ${nextQty}.`,
            );
            return line;
          }
          setError('');
          return { ...line, quantity: nextQty };
        })
        .filter(Boolean),
    );
  };

  const addVariant = (item, variant) => {
    if (Number(variant.stock_quantity) <= 0) {
      setError(`Out of stock: ${item.name} (${variant.size}/${variant.color})`);
      return;
    }
    setError('');
    setSuccess('');
    const lineKey = `${item.id}:${variant.id}`;
    setCart((prev) => {
      const existing = prev.find((line) => line.line_key === lineKey);
      if (existing) {
        const nextQty = existing.quantity + 1;
        if (nextQty > Number(variant.stock_quantity)) {
          setError(
            `Insufficient stock. Available: ${variant.stock_quantity}, requested: ${nextQty}.`,
          );
          return prev;
        }
        return prev.map((line) =>
          line.line_key === lineKey ? { ...line, quantity: nextQty } : line,
        );
      }
      return [
        ...prev,
        {
          line_key: lineKey,
          item_id: item.id,
          variant_id: variant.id,
          name: `${item.name} (${variant.size}/${variant.color})`,
          price: Number(item.price),
          quantity: 1,
          stock_quantity: Number(variant.stock_quantity),
        },
      ];
    });
    setPicker(null);
  };

  const addPlainItem = (item) => {
    if (Number(item.stock_quantity) <= 0) {
      setError(`Out of stock: ${item.name}`);
      return false;
    }
    setError('');
    setSuccess('');
    const lineKey = item.id;
    setCart((prev) => {
      const existing = prev.find((line) => line.line_key === lineKey);
      if (existing) {
        const nextQty = existing.quantity + 1;
        if (nextQty > Number(item.stock_quantity)) {
          setError(
            `Insufficient stock. Available: ${item.stock_quantity}, requested: ${nextQty}.`,
          );
          return prev;
        }
        return prev.map((line) =>
          line.line_key === lineKey ? { ...line, quantity: nextQty } : line,
        );
      }
      return [
        ...prev,
        {
          line_key: lineKey,
          item_id: item.id,
          variant_id: null,
          name: item.name,
          price: Number(item.price),
          quantity: 1,
          stock_quantity: Number(item.stock_quantity),
        },
      ];
    });
    return true;
  };

  const resolveCatalogItem = async (itemId) => {
    const cached = items.find((row) => row.id === itemId);
    if (cached) return cached;
    const res = await fetchClothingPosCatalog({ limit: 100 });
    const list = res.data?.items || [];
    setItems(list);
    return list.find((row) => row.id === itemId) || null;
  };

  const scanBarcode = async () => {
    const code = barcode.trim();
    if (!code || scanning) return;
    setScanning(true);
    setSuccess('');
    setError('');
    try {
      const res = await getItemByBarcode(code);
      const item = res.data;
      if (item.matched_variant) {
        addVariant(
          { id: item.id, name: item.name, price: Number(item.price) },
          item.matched_variant,
        );
        setBarcode('');
        setSuccess(
          `Added ${item.name} (${item.matched_variant.size}/${item.matched_variant.color})`,
        );
        focusScan();
        return;
      }
      const catalogItem = await resolveCatalogItem(item.id);
      if (!catalogItem) {
        setError('Item not found in clothing catalog.');
        return;
      }
      if (catalogItem.tracks_variants) {
        setPicker(catalogItem);
        setBarcode('');
        setError('Barcode matched the product — pick size and color.');
        return;
      }
      if (addPlainItem(catalogItem)) {
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

  const resetAfterBill = () => {
    setCart([]);
    setPaymentMethod(DEFAULT_PAYMENT_METHOD);
    setSelectedCustomer(null);
  };

  const checkout = async ({ confirmed = false } = {}) => {
    if (!cart.length) {
      setError('Add at least one size/color.');
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
        items: cart.map((line) => ({
          item_id: line.item_id,
          variant_id: line.variant_id,
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
      await load();
      focusScan();
    } catch (err) {
      setError(getApiErrorMessage(err, 'Failed to generate bill'));
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
      customer_name: createdBill.customer_name || null,
    });
  };

  if (!moduleEnabled) {
    return (
      <PageShell>
        <Alert severity="warning">The Variants module is not enabled for this business type.</Alert>
      </PageShell>
    );
  }

  return (
    <PageShell>
      <Stack spacing={2} sx={{ pb: { xs: 10, md: 0 } }}>
        {error ? <Alert severity="error">{error}</Alert> : null}
        {success ? <Alert severity="success">{success}</Alert> : null}

        <Grid container spacing={2}>
          <Grid item xs={12} md={8}>
            <Stack spacing={2}>
              {barcodePosEnabled ? (
                <Card variant="outlined" sx={{ borderWidth: 2, borderColor: 'primary.main' }}>
                  <CardContent>
                    <Stack direction={{ xs: 'column', sm: 'row' }} spacing={1.5} alignItems={{ sm: 'center' }}>
                      <TextField
                        inputRef={barcodeRef}
                        label="Scan barcode"
                        placeholder="Focus here and scan variant barcode…"
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
                        sx={{ '& .MuiInputBase-root': { fontSize: { xs: '1rem', sm: '1.1rem' } } }}
                        InputProps={{
                          startAdornment: (
                            <InputAdornment position="start">
                              <QrCodeScannerOutlinedIcon fontSize="small" color="action" />
                            </InputAdornment>
                          ),
                        }}
                        helperText="Variant barcodes add the matching size/color to the cart."
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
              ) : null}

              <TextField
                label="Search items"
                value={q}
                onChange={(e) => setQ(e.target.value)}
                fullWidth
                size="small"
              />

              {categories.length ? (
                <Box sx={{ overflowX: 'auto', pb: 0.5 }}>
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

              <Grid container spacing={1.5}>
                {displayItems.map((item) => (
                  <Grid item xs={6} sm={4} md={3} key={item.id}>
                    <Card variant="outlined" sx={{ height: '100%' }}>
                      <CardActionArea onClick={() => setPicker(item)} sx={{ height: '100%' }}>
                        {item.primary_image_url ? (
                          <CardMedia
                            component="img"
                            height="120"
                            image={item.primary_image_url}
                            alt={item.name}
                            sx={{ objectFit: 'cover' }}
                          />
                        ) : (
                          <Box
                            sx={{
                              height: 120,
                              display: 'grid',
                              placeItems: 'center',
                              bgcolor: 'action.hover',
                            }}
                          >
                            <CheckroomOutlinedIcon color="disabled" />
                          </Box>
                        )}
                        <CardContent sx={{ py: 1.25, '&:last-child': { pb: 1.25 } }}>
                          <Typography variant="subtitle2" noWrap>
                            {item.name}
                          </Typography>
                          {item.category_name ? (
                            <Typography variant="caption" color="text.secondary" noWrap display="block">
                              {item.category_name}
                            </Typography>
                          ) : null}
                          <Typography variant="body2" color="text.secondary">
                            {money(item.price)}
                          </Typography>
                          <Chip
                            size="small"
                            sx={{ mt: 0.75 }}
                            label={
                              item.tracks_variants
                                ? `${item.variants?.length || 0} variants`
                                : `Stock ${item.stock_quantity ?? '—'}`
                            }
                          />
                        </CardContent>
                      </CardActionArea>
                    </Card>
                  </Grid>
                ))}
              </Grid>
              {!displayItems.length ? (
                <Typography variant="body2" color="text.secondary">
                  {categoryId ? 'No items in this category.' : 'No items match your search.'}
                </Typography>
              ) : null}
            </Stack>
          </Grid>

          <Grid item xs={12} md={4}>
            <Card variant="outlined">
              <CardContent>
                <Stack direction="row" justifyContent="space-between" alignItems="center" sx={{ mb: 1 }}>
                  <Typography variant="h6">Cart</Typography>
                  <Typography variant="body2" color="text.secondary">
                    {cart.length} lines · {lineCount} units
                  </Typography>
                </Stack>

                {!cart.length ? (
                  <Typography variant="body2" color="text.secondary">
                    {barcodePosEnabled
                      ? 'Scan a variant barcode or tap a product to pick size/color.'
                      : 'Tap a product, then a size/color with stock.'}
                  </Typography>
                ) : (
                  <Stack spacing={1.25}>
                    {cart.map((line) => (
                      <Box key={line.line_key}>
                        <Stack direction="row" alignItems="flex-start" justifyContent="space-between">
                          <Box sx={{ flex: 1, minWidth: 0, pr: 1 }}>
                            <Typography variant="body2" fontWeight={600} noWrap>
                              {line.name}
                            </Typography>
                            <Typography variant="caption" color="text.secondary">
                              {money(Number(line.price) * Number(line.quantity))}
                            </Typography>
                          </Box>
                          <IconButton
                            size="small"
                            aria-label={`Remove ${line.name}`}
                            onClick={() =>
                              setCart((prev) => prev.filter((row) => row.line_key !== line.line_key))
                            }
                          >
                            <DeleteOutlineOutlinedIcon fontSize="small" />
                          </IconButton>
                        </Stack>
                        <Stack direction="row" alignItems="center" spacing={0.5} mt={0.5}>
                          <IconButton
                            size="small"
                            onClick={() => bumpQty(line.line_key, -1)}
                            aria-label="Decrease quantity"
                          >
                            <RemoveOutlinedIcon fontSize="small" />
                          </IconButton>
                          <Typography variant="body2" sx={{ minWidth: 24, textAlign: 'center' }}>
                            {line.quantity}
                          </Typography>
                          <IconButton
                            size="small"
                            onClick={() => bumpQty(line.line_key, 1)}
                            aria-label="Increase quantity"
                          >
                            <AddOutlinedIcon fontSize="small" />
                          </IconButton>
                        </Stack>
                      </Box>
                    ))}
                    <Divider />
                    <CustomerPicker
                      value={selectedCustomer}
                      onChange={setSelectedCustomer}
                      onClear={() => {
                        setSelectedCustomer(null);
                        if (paymentMethod === PAYMENT_CREDIT) {
                          setPaymentMethod(PAYMENT_CASH);
                        }
                      }}
                      label={creditEnabled ? 'Customer (required for udhari)' : 'Customer (optional)'}
                    />
                    {selectedCustomer ? (
                      <Chip
                        size="small"
                        color={Number(selectedCustomer.balance || 0) > 0 ? 'warning' : 'default'}
                        label={
                          Number(selectedCustomer.balance || 0) > 0
                            ? `Outstanding ${money(selectedCustomer.balance)}`
                            : 'No outstanding'
                        }
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
                        {creditEnabled ? (
                          <FormControlLabel
                            value={PAYMENT_CREDIT}
                            control={<Radio size="small" />}
                            label="Credit"
                          />
                        ) : null}
                      </RadioGroup>
                    </FormControl>
                    <Stack direction="row" justifyContent="space-between">
                      <Typography fontWeight={700}>Total</Typography>
                      <Typography fontWeight={700}>{money(total)}</Typography>
                    </Stack>
                    <Button
                      variant="contained"
                      fullWidth
                      disabled={saving}
                      onClick={() => checkout()}
                    >
                      {saving
                        ? 'Saving…'
                        : paymentMethod === PAYMENT_CREDIT
                          ? 'Charge to credit'
                          : 'Generate bill'}
                    </Button>
                  </Stack>
                )}
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </Stack>

      <Box
        sx={{
          display: { xs: 'block', md: 'none' },
          position: 'fixed',
          bottom: 0,
          left: 0,
          right: 0,
          zIndex: (theme) => theme.zIndex.appBar,
          bgcolor: 'background.paper',
          borderTop: 1,
          borderColor: 'divider',
          px: 2,
          py: 1.25,
          boxShadow: 4,
        }}
      >
        <Stack direction="row" alignItems="center" justifyContent="space-between" spacing={2}>
          <Box>
            <Typography variant="caption" color="text.secondary" display="block">
              {cart.length} lines · {lineCount} units
            </Typography>
            <Typography fontWeight={700}>{money(total)}</Typography>
          </Box>
          <Button
            variant="contained"
            disabled={saving || !cart.length}
            onClick={() => checkout()}
            sx={{ minWidth: 140 }}
          >
            {saving ? 'Saving…' : 'Bill'}
          </Button>
        </Stack>
      </Box>

      <Dialog open={Boolean(picker)} onClose={() => setPicker(null)} fullWidth maxWidth="sm">
        <DialogTitle>{picker?.name}</DialogTitle>
        <DialogContent>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
            Numbers are units in stock for that size and color. Out-of-stock cells cannot be sold.
          </Typography>
          {picker?.tracks_variants ? (
            <VariantStockGrid
              variants={picker.variants || []}
              onSelect={(variant) => addVariant(picker, variant)}
            />
          ) : (
            <Button
              variant="contained"
              onClick={() => {
                if (addPlainItem(picker)) setPicker(null);
              }}
            >
              Add without variant
            </Button>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setPicker(null)}>Close</Button>
        </DialogActions>
      </Dialog>

      <Dialog
        open={Boolean(createdBill)}
        onClose={() => !whatsappSending && setCreatedBill(null)}
        fullWidth
        maxWidth="xs"
      >
        <DialogTitle>Bill generated</DialogTitle>
        <DialogContent>
          <Stack spacing={1.5} sx={{ mt: 0.5 }}>
            <Typography>
              Bill <strong>#{createdBill?.bill_number}</strong> saved.
            </Typography>
            <Typography>Grand total: {money(createdBill?.grand_total)}</Typography>
            <Typography>Payment: {paymentMethodLabel(createdBill?.payment_method)}</Typography>
            {createdBill?.customer_phone_masked ? (
              <Typography variant="body2" color="text.secondary">
                WhatsApp: {createdBill.customer_phone_masked}
              </Typography>
            ) : null}
            {whatsappMessage ? <Alert severity="success">{whatsappMessage}</Alert> : null}
            {whatsappError ? <Alert severity="error">{whatsappError}</Alert> : null}
          </Stack>
        </DialogContent>
        <DialogActions sx={{ flexWrap: 'wrap', gap: 1, px: 3, pb: 2 }}>
          <Button onClick={() => setCreatedBill(null)} disabled={whatsappSending}>
            Close
          </Button>
          <Button
            variant="outlined"
            disabled={whatsappSending}
            onClick={() => {
              navigate(billPrintPath(createdBill.id, { auto: true }), {
                state: { from: clothingFromPath },
              });
            }}
          >
            Print Bill
          </Button>
          <Button
            variant="outlined"
            disabled={whatsappSending}
            onClick={async () => {
              try {
                await downloadBillPdf(createdBill.id, createdBill.bill_number);
              } catch (err) {
                setWhatsappError(getApiErrorMessage(err, 'Unable to download bill PDF.'));
              }
            }}
          >
            Download PDF
          </Button>
          <Button
            variant="contained"
            color="success"
            startIcon={
              whatsappSending ? <CircularProgress size={16} color="inherit" /> : <WhatsAppIcon />
            }
            disabled={whatsappSending || Boolean(whatsappMessage)}
            onClick={onSendWhatsappClick}
          >
            {whatsappSending ? 'Sending…' : whatsappError ? 'Retry WhatsApp' : 'Send WhatsApp'}
          </Button>
        </DialogActions>
      </Dialog>

      <Dialog open={phoneDialogOpen} onClose={() => !whatsappSending && setPhoneDialogOpen(false)} fullWidth maxWidth="xs">
        <DialogTitle>Customer WhatsApp number</DialogTitle>
        <DialogContent>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
            Enter a number to send this bill on WhatsApp.
          </Typography>
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
              onChange={(e) => setPhoneDraft(e.target.value.replace(/\D/g, '').slice(0, 15))}
              fullWidth
            />
          </Stack>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setPhoneDialogOpen(false)} disabled={whatsappSending}>
            Cancel
          </Button>
          <Button
            variant="contained"
            disabled={whatsappSending || !phoneDraft}
            onClick={() =>
              doSendWhatsapp({
                country_code: phoneDraftCc,
                phone: phoneDraft,
                customer_name: createdBill?.customer_name || null,
              })
            }
          >
            {whatsappSending ? 'Sending…' : 'Send'}
          </Button>
        </DialogActions>
      </Dialog>

      <Dialog open={confirmCreditOpen} onClose={() => setConfirmCreditOpen(false)} fullWidth maxWidth="xs">
        <DialogTitle>Confirm credit bill</DialogTitle>
        <DialogContent>
          <Typography>
            Charge {money(total)} to {selectedCustomer?.name || 'customer'} on credit / udhari?
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setConfirmCreditOpen(false)}>Cancel</Button>
          <Button
            variant="contained"
            color="warning"
            disabled={saving}
            onClick={() => checkout({ confirmed: true })}
          >
            Confirm credit
          </Button>
        </DialogActions>
      </Dialog>
    </PageShell>
  );
}
