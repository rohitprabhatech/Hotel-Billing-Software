import AddOutlinedIcon from '@mui/icons-material/AddOutlined';
import AddShoppingCartOutlinedIcon from '@mui/icons-material/AddShoppingCartOutlined';
import DeleteOutlineOutlinedIcon from '@mui/icons-material/DeleteOutlineOutlined';
import EmailOutlinedIcon from '@mui/icons-material/EmailOutlined';
import LocalCafeOutlinedIcon from '@mui/icons-material/LocalCafeOutlined';
import RemoveOutlinedIcon from '@mui/icons-material/RemoveOutlined';
import WhatsAppIcon from '@mui/icons-material/WhatsApp';
import {
  Alert,
  Box,
  Button,
  Card,
  CardActionArea,
  CardContent,
  Checkbox,
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
  Radio,
  RadioGroup,
  Stack,
  TextField,
  Typography,
} from '@mui/material';
import { useEffect, useMemo, useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import CustomerPicker from '../../components/CustomerPicker';
import PageShell from '../../components/PageShell';
import { useModuleGate } from '../../context/ModulesContext';
import { PATHS } from '../../routes/paths';
import {
  billPrintPath,
  downloadBillPdf,
  sendBillEmail,
  sendBillWhatsapp,
} from '../../services/billService';
import { fetchPosCatalog } from '../../services/cafeService';
import { previewCoupon } from '../../services/couponService';
import { createOrder } from '../../services/orderService';
import { settleOrder } from '../../services/orderSettlementService';
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

function lineKey(line) {
  return `${line.kind}:${line.item_id || line.combo_id}:${(line.addon_ids || []).join(',')}`;
}

function getApiErrorMessage(err, fallback) {
  return err?.response?.data?.error?.message || fallback;
}

export default function CafePosPage() {
  const moduleEnabled = useModuleGate('addons_combos');
  const creditEnabled = useModuleGate('customer_credit');
  const navigate = useNavigate();
  const location = useLocation();
  const cafeFromPath = location.pathname.startsWith('/owner') ? PATHS.ownerCafe : PATHS.billingCafe;

  const [catalog, setCatalog] = useState({ menu_items: [], combos: [], popular_combos: [] });
  const [cart, setCart] = useState([]);
  const [q, setQ] = useState('');
  const [pickerItem, setPickerItem] = useState(null);
  const [selectedAddons, setSelectedAddons] = useState([]);
  const [pickerError, setPickerError] = useState('');
  const [paymentMethod, setPaymentMethod] = useState(DEFAULT_PAYMENT_METHOD);
  const [discount, setDiscount] = useState('0');
  const [couponCode, setCouponCode] = useState('');
  const [couponPreview, setCouponPreview] = useState(null);
  const [couponChecking, setCouponChecking] = useState(false);
  const [selectedCustomer, setSelectedCustomer] = useState(null);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [saving, setSaving] = useState(false);
  const [createdBill, setCreatedBill] = useState(null);
  const [whatsappSending, setWhatsappSending] = useState(false);
  const [whatsappMessage, setWhatsappMessage] = useState('');
  const [whatsappError, setWhatsappError] = useState('');
  const [emailSending, setEmailSending] = useState(false);
  const [emailMessage, setEmailMessage] = useState('');
  const [emailError, setEmailError] = useState('');
  const [phoneDialogOpen, setPhoneDialogOpen] = useState(false);
  const [phoneDraftCc, setPhoneDraftCc] = useState('91');
  const [phoneDraft, setPhoneDraft] = useState('');
  const [emailDialogOpen, setEmailDialogOpen] = useState(false);
  const [emailDraft, setEmailDraft] = useState('');
  const [confirmCreditOpen, setConfirmCreditOpen] = useState(false);

  useEffect(() => {
    if (!moduleEnabled) return;
    fetchPosCatalog()
      .then((res) => setCatalog(res.data || { menu_items: [], combos: [], popular_combos: [] }))
      .catch((err) => {
        setError(getApiErrorMessage(err, 'Failed to load cafe catalog'));
      });
  }, [moduleEnabled]);

  const filteredItems = useMemo(() => {
    const term = q.trim().toLowerCase();
    const items = catalog.menu_items || [];
    if (!term) return items;
    return items.filter((item) => item.name.toLowerCase().includes(term));
  }, [catalog.menu_items, q]);

  const filteredCombos = useMemo(() => {
    const term = q.trim().toLowerCase();
    const combos = catalog.combos || [];
    if (!term) return combos;
    return combos.filter((combo) => combo.name.toLowerCase().includes(term));
  }, [catalog.combos, q]);

  const cartSubtotal = useMemo(
    () => cart.reduce((sum, line) => sum + Number(line.unit_price || 0) * Number(line.quantity || 0), 0),
    [cart],
  );

  useEffect(() => {
    setCouponPreview(null);
    setCouponCode('');
  }, [cartSubtotal]);

  const discountAmount = Math.max(0, Number(discount || 0) || 0);
  const couponDiscount = Math.max(0, Number(couponPreview?.discount_amount || 0) || 0);
  const cartTotal = Math.max(0, cartSubtotal - discountAmount - couponDiscount);

  const applyCoupon = async () => {
    if (!couponCode.trim()) {
      setCouponPreview(null);
      setError('Enter a coupon code');
      return;
    }
    if (!cart.length) {
      setError('Add items before applying a coupon');
      return;
    }
    setCouponChecking(true);
    setError('');
    try {
      const res = await previewCoupon({ code: couponCode.trim(), subtotal: cartSubtotal });
      setCouponPreview(res.data);
      setCouponCode(res.data?.coupon?.code || couponCode.trim().toUpperCase());
    } catch (err) {
      setCouponPreview(null);
      setError(getApiErrorMessage(err, 'Invalid coupon'));
    } finally {
      setCouponChecking(false);
    }
  };

  const openPicker = (item) => {
    const defaults = (item.addon_groups || []).flatMap((group) =>
      (group.addons || []).filter((addon) => addon.is_default).map((addon) => addon.id),
    );
    setPickerItem(item);
    setSelectedAddons(defaults);
    setPickerError('');
  };

  const toggleAddon = (addonId, group) => {
    setSelectedAddons((prev) => {
      const inGroup = (group.addons || []).map((row) => row.id);
      const selectedInGroup = prev.filter((id) => inGroup.includes(id));
      if (prev.includes(addonId)) {
        return prev.filter((id) => id !== addonId);
      }
      if (group.max_selections === 1) {
        return [...prev.filter((id) => !inGroup.includes(id)), addonId];
      }
      if (group.max_selections && selectedInGroup.length >= group.max_selections) {
        return prev;
      }
      return [...prev, addonId];
    });
  };

  const confirmPicker = () => {
    if (!pickerItem) return;
    const missing = (pickerItem.addon_groups || []).filter((group) => {
      if (!group.is_required) return false;
      const inGroup = (group.addons || []).map((row) => row.id);
      return !selectedAddons.some((id) => inGroup.includes(id));
    });
    if (missing.length) {
      setPickerError(`Select required: ${missing.map((g) => g.name).join(', ')}`);
      return;
    }

    const selectedAddonRows = (pickerItem.addon_groups || [])
      .flatMap((group) => group.addons || [])
      .filter((addon) => selectedAddons.includes(addon.id));
    const addonExtra = selectedAddonRows.reduce((sum, addon) => sum + Number(addon.extra_price || 0), 0);
    const line = {
      kind: 'item',
      item_id: pickerItem.id,
      name: pickerItem.name,
      quantity: 1,
      unit_price: Number(pickerItem.price) + addonExtra,
      addon_ids: [...selectedAddons],
      addon_labels: selectedAddonRows.map((addon) => addon.name),
    };
    setCart((prev) => {
      const key = lineKey(line);
      const existing = prev.find((row) => lineKey(row) === key);
      if (existing) {
        return prev.map((row) =>
          lineKey(row) === key ? { ...row, quantity: Number(row.quantity) + 1 } : row,
        );
      }
      return [...prev, line];
    });
    setPickerItem(null);
    setSelectedAddons([]);
    setPickerError('');
  };

  const addCombo = (combo) => {
    const line = {
      kind: 'combo',
      combo_id: combo.id,
      name: combo.name,
      quantity: 1,
      unit_price: Number(combo.combo_price),
      addon_ids: [],
      addon_labels: [],
    };
    setCart((prev) => {
      const key = lineKey(line);
      const existing = prev.find((row) => lineKey(row) === key);
      if (existing) {
        return prev.map((row) =>
          lineKey(row) === key ? { ...row, quantity: Number(row.quantity) + 1 } : row,
        );
      }
      return [...prev, line];
    });
  };

  const bumpQty = (line, delta) => {
    setCart((prev) =>
      prev
        .map((row) => {
          if (lineKey(row) !== lineKey(line)) return row;
          return { ...row, quantity: Number(row.quantity) + delta };
        })
        .filter((row) => Number(row.quantity) > 0),
    );
  };

  const setLineQty = (line, rawQty) => {
    const parsed = Number(rawQty);
    if (!Number.isFinite(parsed) || parsed <= 0) {
      setCart((prev) => prev.filter((row) => lineKey(row) !== lineKey(line)));
      return;
    }
    setCart((prev) =>
      prev.map((row) => (lineKey(row) === lineKey(line) ? { ...row, quantity: parsed } : row)),
    );
  };

  const removeLine = (line) => {
    setCart((prev) => prev.filter((row) => lineKey(row) !== lineKey(line)));
  };

  const clearCart = () => {
    setCart([]);
    setDiscount('0');
    setError('');
  };

  const resetAfterBill = () => {
    setCart([]);
    setDiscount('0');
    setCouponCode('');
    setCouponPreview(null);
    setPaymentMethod(DEFAULT_PAYMENT_METHOD);
    setSelectedCustomer(null);
  };

  const checkout = async ({ confirmed = false } = {}) => {
    if (!cart.length) {
      setError('Add at least one item to the cart');
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
      const items = cart
        .filter((line) => line.kind === 'item')
        .map((line) => ({
          item_id: line.item_id,
          quantity: line.quantity,
          addon_ids: line.addon_ids || [],
        }));
      const combos = cart
        .filter((line) => line.kind === 'combo')
        .map((line) => ({
          combo_id: line.combo_id,
          quantity: line.quantity,
        }));
      const orderRes = await createOrder({
        channel: 'takeaway',
        customer_id: selectedCustomer?.id || null,
        items,
        combos,
      });
      const order = orderRes.data;
      const settled = await settleOrder(order.id, {
        payment_method: paymentMethod,
        discount: discountAmount,
        coupon_code: couponCode.trim() || null,
        customer_id: selectedCustomer?.id || null,
        customer_name: selectedCustomer?.name || null,
        customer_phone_country_code: selectedCustomer?.phone_country_code || null,
        customer_phone: selectedCustomer?.phone_national || null,
        customer_email: selectedCustomer?.email || null,
      });
      const bill = settled.data?.bills?.[0] || null;
      if (!bill?.id) {
        throw new Error('Bill was created but response was incomplete');
      }
      setCreatedBill(bill);
      setWhatsappMessage('');
      setWhatsappError('');
      setEmailMessage('');
      setEmailError('');
      setSuccess(
        `Bill ${bill.bill_number} — ${money(bill.grand_total)} (${paymentMethodLabel(bill.payment_method)})`,
      );
      resetAfterBill();
      setConfirmCreditOpen(false);
    } catch (err) {
      setError(getApiErrorMessage(err, 'Checkout failed'));
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
    const hasPhone = Boolean(createdBill.customer_phone_national || selectedCustomer?.phone_national);
    if (!hasPhone) {
      setPhoneDraftCc(createdBill.customer_phone_country_code || '91');
      setPhoneDraft('');
      setPhoneDialogOpen(true);
      return;
    }
    doSendWhatsapp({
      country_code: createdBill.customer_phone_country_code || selectedCustomer?.phone_country_code,
      phone: createdBill.customer_phone_national || selectedCustomer?.phone_national,
      customer_name: createdBill.customer_name || selectedCustomer?.name || null,
    });
  };

  const doSendEmail = async (payload = {}) => {
    if (!createdBill?.id || emailSending) return;
    setEmailSending(true);
    setEmailError('');
    setEmailMessage('');
    try {
      const res = await sendBillEmail(createdBill.id, payload);
      setEmailMessage(res.data?.message || 'Bill sent successfully by email.');
      if (res.data?.bill) setCreatedBill(res.data.bill);
      setEmailDialogOpen(false);
    } catch (err) {
      setEmailError(getApiErrorMessage(err, 'Unable to send the bill by email.'));
    } finally {
      setEmailSending(false);
    }
  };

  const onSendEmailClick = () => {
    if (!createdBill) return;
    const hasEmail = Boolean(createdBill.customer_email || selectedCustomer?.email);
    if (!hasEmail) {
      setEmailDraft('');
      setEmailDialogOpen(true);
      return;
    }
    doSendEmail({
      email: createdBill.customer_email || selectedCustomer?.email,
      customer_name: createdBill.customer_name || selectedCustomer?.name || null,
    });
  };

  if (!moduleEnabled) {
    return (
      <PageShell>
        <Alert severity="info">Cafe POS is not enabled for this business type.</Alert>
      </PageShell>
    );
  }

  return (
    <PageShell>
      <Stack spacing={2}>
        {error ? <Alert severity="error">{error}</Alert> : null}
        {success ? <Alert severity="success">{success}</Alert> : null}

        <Grid container spacing={2}>
          <Grid item xs={12} md={8}>
            <Stack spacing={2}>
              {(catalog.popular_combos || []).length ? (
                <Box>
                  <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                    Popular combos
                  </Typography>
                  <Stack direction="row" flexWrap="wrap" gap={1}>
                    {(catalog.popular_combos || []).map((combo) => (
                      <Chip
                        key={combo.id}
                        icon={<LocalCafeOutlinedIcon />}
                        label={`${combo.name} · ${money(combo.combo_price)}`}
                        onClick={() => addCombo(combo)}
                        clickable
                        color="primary"
                        variant="outlined"
                      />
                    ))}
                  </Stack>
                </Box>
              ) : null}

              <TextField
                size="small"
                placeholder="Search menu or combos…"
                value={q}
                onChange={(event) => setQ(event.target.value)}
                fullWidth
              />

              {filteredCombos.length ? (
                <Box>
                  <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                    Combos
                  </Typography>
                  <Grid container spacing={1}>
                    {filteredCombos.map((combo) => (
                      <Grid item xs={6} sm={4} md={3} key={combo.id}>
                        <Card variant="outlined" sx={{ height: '100%' }}>
                          <CardActionArea onClick={() => addCombo(combo)} sx={{ height: '100%' }}>
                            <CardContent sx={{ py: 1.5, '&:last-child': { pb: 1.5 } }}>
                              <Typography variant="body2" fontWeight={600} noWrap>
                                {combo.name}
                              </Typography>
                              <Typography variant="caption" color="text.secondary">
                                {money(combo.combo_price)}
                                {combo.is_popular ? ' · popular' : ''}
                              </Typography>
                            </CardContent>
                          </CardActionArea>
                        </Card>
                      </Grid>
                    ))}
                  </Grid>
                </Box>
              ) : null}

              <Box>
                <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                  Menu
                </Typography>
                <Grid container spacing={1}>
                  {filteredItems.map((item) => (
                    <Grid item xs={6} sm={4} md={3} key={item.id}>
                      <Card variant="outlined" sx={{ height: '100%' }}>
                        <CardActionArea onClick={() => openPicker(item)} sx={{ height: '100%' }}>
                          <CardContent sx={{ py: 1.5, '&:last-child': { pb: 1.5 } }}>
                            <Typography variant="body2" fontWeight={600} noWrap>
                              {item.name}
                            </Typography>
                            <Typography variant="caption" color="text.secondary">
                              {money(item.price)}
                              {(item.addon_groups || []).length ? ' +' : ''}
                            </Typography>
                          </CardContent>
                        </CardActionArea>
                      </Card>
                    </Grid>
                  ))}
                </Grid>
              </Box>
            </Stack>
          </Grid>

          <Grid item xs={12} md={4}>
            <Card variant="outlined">
              <CardContent>
                <Stack direction="row" justifyContent="space-between" alignItems="center" mb={1}>
                  <Typography variant="h6">Cart</Typography>
                  {cart.length ? (
                    <Button size="small" onClick={clearCart}>
                      Clear
                    </Button>
                  ) : null}
                </Stack>
                {!cart.length ? (
                  <Typography variant="body2" color="text.secondary">
                    Tap menu items or combos to add lines.
                  </Typography>
                ) : (
                  <Stack spacing={1.25}>
                    {cart.map((line) => (
                      <Box key={lineKey(line)}>
                        <Stack direction="row" alignItems="flex-start" justifyContent="space-between">
                          <Box sx={{ minWidth: 0, pr: 1 }}>
                            <Typography variant="body2" fontWeight={600}>
                              {line.name}
                            </Typography>
                            {(line.addon_labels || []).length ? (
                              <Typography variant="caption" color="text.secondary">
                                {line.addon_labels.join(', ')}
                              </Typography>
                            ) : null}
                            <Typography variant="caption" color="text.secondary" display="block">
                              {money(Number(line.unit_price) * Number(line.quantity))}
                            </Typography>
                          </Box>
                          <IconButton size="small" onClick={() => removeLine(line)} aria-label="Remove line">
                            <DeleteOutlineOutlinedIcon fontSize="small" />
                          </IconButton>
                        </Stack>
                        <Stack direction="row" alignItems="center" spacing={0.5} mt={0.5}>
                          <IconButton size="small" onClick={() => bumpQty(line, -1)} aria-label="Decrease qty">
                            <RemoveOutlinedIcon fontSize="small" />
                          </IconButton>
                          <TextField
                            size="small"
                            value={line.quantity}
                            onChange={(e) => setLineQty(line, e.target.value)}
                            inputProps={{ min: 1, step: 1, style: { textAlign: 'center', width: 40 } }}
                          />
                          <IconButton size="small" onClick={() => bumpQty(line, 1)} aria-label="Increase qty">
                            <AddOutlinedIcon fontSize="small" />
                          </IconButton>
                        </Stack>
                      </Box>
                    ))}
                    <Divider />
                    <CustomerPicker
                      value={selectedCustomer}
                      onChange={setSelectedCustomer}
                      onClear={() => setSelectedCustomer(null)}
                      label="Customer (optional)"
                    />
                    <TextField
                      size="small"
                      label="Discount ₹"
                      type="number"
                      value={discount}
                      onChange={(e) => setDiscount(e.target.value)}
                      inputProps={{ min: 0, step: '0.01' }}
                      fullWidth
                    />
                    <Stack direction="row" spacing={1} alignItems="flex-start">
                      <TextField
                        size="small"
                        label="Coupon code"
                        value={couponCode}
                        onChange={(e) => {
                          setCouponCode(e.target.value.toUpperCase());
                          setCouponPreview(null);
                        }}
                        fullWidth
                      />
                      <Button
                        variant="outlined"
                        size="small"
                        disabled={couponChecking || !cart.length}
                        onClick={applyCoupon}
                        sx={{ whiteSpace: 'nowrap', mt: 0.5 }}
                      >
                        {couponChecking ? '…' : 'Apply'}
                      </Button>
                    </Stack>
                    {couponPreview ? (
                      <Typography variant="caption" color="success.main">
                        {couponPreview.coupon?.name || couponPreview.coupon?.code}: −
                        {money(couponPreview.discount_amount)}
                      </Typography>
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
                      <Typography variant="body2" color="text.secondary">
                        Subtotal
                      </Typography>
                      <Typography variant="body2">{money(cartSubtotal)}</Typography>
                    </Stack>
                    {discountAmount > 0 ? (
                      <Stack direction="row" justifyContent="space-between">
                        <Typography variant="body2" color="text.secondary">
                          Discount
                        </Typography>
                        <Typography variant="body2">−{money(discountAmount)}</Typography>
                      </Stack>
                    ) : null}
                    {couponDiscount > 0 ? (
                      <Stack direction="row" justifyContent="space-between">
                        <Typography variant="body2" color="text.secondary">
                          Coupon
                        </Typography>
                        <Typography variant="body2">−{money(couponDiscount)}</Typography>
                      </Stack>
                    ) : null}
                    <Stack direction="row" justifyContent="space-between">
                      <Typography fontWeight={600}>Total</Typography>
                      <Typography fontWeight={600}>{money(cartTotal)}</Typography>
                    </Stack>
                    <Button
                      variant="contained"
                      startIcon={<AddShoppingCartOutlinedIcon />}
                      onClick={() => checkout()}
                      disabled={saving}
                      fullWidth
                    >
                      {saving
                        ? 'Processing…'
                        : paymentMethod === PAYMENT_CREDIT
                          ? 'Charge to credit'
                          : 'Quick bill'}
                    </Button>
                  </Stack>
                )}
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </Stack>

      <Dialog open={Boolean(pickerItem)} onClose={() => setPickerItem(null)} maxWidth="xs" fullWidth>
        <DialogTitle>{pickerItem?.name}</DialogTitle>
        <DialogContent dividers>
          <Stack spacing={2}>
            {pickerError ? <Alert severity="warning">{pickerError}</Alert> : null}
            {(pickerItem?.addon_groups || []).length === 0 ? (
              <Typography variant="body2" color="text.secondary">
                No add-ons for this item.
              </Typography>
            ) : (
              (pickerItem?.addon_groups || []).map((group) => (
                <Box key={group.id}>
                  <Typography variant="subtitle2">
                    {group.name}
                    {group.is_required ? ' *' : ''}
                  </Typography>
                  <Stack>
                    {(group.addons || []).map((addon) => (
                      <FormControlLabel
                        key={addon.id}
                        control={
                          <Checkbox
                            checked={selectedAddons.includes(addon.id)}
                            onChange={() => toggleAddon(addon.id, group)}
                          />
                        }
                        label={`${addon.name}${Number(addon.extra_price) ? ` (+${money(addon.extra_price)})` : ''}`}
                      />
                    ))}
                  </Stack>
                </Box>
              ))
            )}
          </Stack>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setPickerItem(null)}>Cancel</Button>
          <Button variant="contained" onClick={confirmPicker}>
            Add to cart
          </Button>
        </DialogActions>
      </Dialog>

      <Dialog
        open={Boolean(createdBill)}
        onClose={() => !whatsappSending && !emailSending && setCreatedBill(null)}
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
            {emailMessage ? <Alert severity="success">{emailMessage}</Alert> : null}
            {emailError ? <Alert severity="error">{emailError}</Alert> : null}
          </Stack>
        </DialogContent>
        <DialogActions sx={{ flexWrap: 'wrap', gap: 1, px: 3, pb: 2 }}>
          <Button onClick={() => setCreatedBill(null)} disabled={whatsappSending || emailSending}>
            Close
          </Button>
          <Button
            variant="outlined"
            disabled={whatsappSending || emailSending}
            onClick={() => {
              navigate(billPrintPath(createdBill.id, { auto: true }), {
                state: { from: cafeFromPath },
              });
            }}
          >
            Print Bill
          </Button>
          <Button
            variant="outlined"
            disabled={whatsappSending || emailSending}
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
            disabled={whatsappSending || emailSending || Boolean(whatsappMessage)}
            onClick={onSendWhatsappClick}
          >
            {whatsappSending ? 'Sending…' : whatsappError ? 'Retry WhatsApp' : 'Send WhatsApp'}
          </Button>
          <Button
            variant="contained"
            startIcon={
              emailSending ? <CircularProgress size={16} color="inherit" /> : <EmailOutlinedIcon />
            }
            disabled={emailSending || whatsappSending || Boolean(emailMessage)}
            onClick={onSendEmailClick}
          >
            {emailSending ? 'Sending…' : emailError ? 'Retry Email' : 'Send Email'}
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

      <Dialog open={emailDialogOpen} onClose={() => !emailSending && setEmailDialogOpen(false)} fullWidth maxWidth="xs">
        <DialogTitle>Customer email</DialogTitle>
        <DialogContent>
          <TextField
            label="Email"
            type="email"
            value={emailDraft}
            onChange={(e) => setEmailDraft(e.target.value)}
            fullWidth
            sx={{ mt: 1 }}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setEmailDialogOpen(false)} disabled={emailSending}>
            Cancel
          </Button>
          <Button
            variant="contained"
            disabled={emailSending || !emailDraft.trim()}
            onClick={() =>
              doSendEmail({
                email: emailDraft.trim(),
                customer_name: createdBill?.customer_name || null,
              })
            }
          >
            {emailSending ? 'Sending…' : 'Send'}
          </Button>
        </DialogActions>
      </Dialog>

      <Dialog open={confirmCreditOpen} onClose={() => setConfirmCreditOpen(false)} fullWidth maxWidth="xs">
        <DialogTitle>Confirm credit bill</DialogTitle>
        <DialogContent>
          <Typography>
            Charge {money(cartTotal)} to {selectedCustomer?.name || 'customer'} on credit / udhari?
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setConfirmCreditOpen(false)}>Cancel</Button>
          <Button variant="contained" color="warning" disabled={saving} onClick={() => checkout({ confirmed: true })}>
            Confirm credit
          </Button>
        </DialogActions>
      </Dialog>
    </PageShell>
  );
}
