import AddOutlinedIcon from '@mui/icons-material/AddOutlined';
import DeleteOutlinedIcon from '@mui/icons-material/DeleteOutlined';
import EmailOutlinedIcon from '@mui/icons-material/EmailOutlined';
import WhatsAppIcon from '@mui/icons-material/WhatsApp';
import {
  Alert,
  Box,
  Button,
  Card,
  CardContent,
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
  IconButton,
  Radio,
  RadioGroup,
  Stack,
  TextField,
  Tooltip,
  Typography,
} from '@mui/material';
import { useEffect, useMemo, useRef, useState } from 'react';
import EmptyState from '../../components/EmptyState';
import CustomerPicker from '../../components/CustomerPicker';
import PageShell from '../../components/PageShell';
import TruncateText from '../../components/TruncateText';
import {
  createBill,
  downloadBillPdf,
  openBillPrint,
  sendBillEmail,
  sendBillWhatsapp,
} from '../../services/billService';
import { listCategories } from '../../services/categoryService';
import { getItemByBarcode, listItems } from '../../services/itemService';
import { uomLabel } from '../../utils/uom';
import {
  DEFAULT_PAYMENT_METHOD,
  PAYMENT_CASH,
  PAYMENT_CREDIT,
  PAYMENT_ONLINE,
  isAllowedPaymentMethod,
  paymentMethodLabel,
} from '../../utils/paymentMethod';

function sortCategoriesHierarchically(categories) {
  const byParent = new Map();
  categories.forEach((category) => {
    const key = category.parent_id || 'root';
    if (!byParent.has(key)) byParent.set(key, []);
    byParent.get(key).push(category);
  });
  byParent.forEach((list) => list.sort((a, b) => a.name.localeCompare(b.name)));

  const ordered = [];
  const walk = (parentKey, depth) => {
    (byParent.get(parentKey) || []).forEach((category) => {
      ordered.push({ ...category, depth });
      walk(category.id, depth + 1);
    });
  };
  walk('root', 0);

  const listed = new Set(ordered.map((c) => c.id));
  categories
    .filter((category) => !listed.has(category.id))
    .sort((a, b) => a.name.localeCompare(b.name))
    .forEach((category) => ordered.push({ ...category, depth: 0 }));

  return ordered;
}

export default function NewBillPage() {
  const [q, setQ] = useState('');
  const [barcode, setBarcode] = useState('');
  const [scanning, setScanning] = useState(false);
  const barcodeInputRef = useRef(null);
  const [catalog, setCatalog] = useState([]);
  const [categories, setCategories] = useState([]);
  const [categoryId, setCategoryId] = useState('');
  const [cart, setCart] = useState([]);
  const [discount, setDiscount] = useState('0');
  const [reference, setReference] = useState('');
  const [paymentMethod, setPaymentMethod] = useState(DEFAULT_PAYMENT_METHOD);
  const [customerName, setCustomerName] = useState('');
  const [countryCode, setCountryCode] = useState('91');
  const [customerPhone, setCustomerPhone] = useState('');
  const [customerEmail, setCustomerEmail] = useState('');
  const [selectedCustomer, setSelectedCustomer] = useState(null);
  const [error, setError] = useState('');
  const [saving, setSaving] = useState(false);
  const [loadingItems, setLoadingItems] = useState(true);
  const [createdBill, setCreatedBill] = useState(null);
  const [whatsappSending, setWhatsappSending] = useState(false);
  const [whatsappMessage, setWhatsappMessage] = useState('');
  const [whatsappError, setWhatsappError] = useState('');
  const [emailSending, setEmailSending] = useState(false);
  const [emailMessage, setEmailMessage] = useState('');
  const [emailError, setEmailError] = useState('');
  const [emailDialogOpen, setEmailDialogOpen] = useState(false);
  const [emailDraft, setEmailDraft] = useState('');
  const [phoneDialogOpen, setPhoneDialogOpen] = useState(false);
  const [phoneDraftCc, setPhoneDraftCc] = useState('91');
  const [phoneDraft, setPhoneDraft] = useState('');

  const search = async (term = q, cat = categoryId) => {
    setError('');
    setLoadingItems(true);
    try {
      const res = await listItems({
        q: term || undefined,
        category_id: cat || undefined,
        is_active: true,
        per_page: 100,
      });
      setCatalog(res.data || []);
      // Keep cart stock figures in sync after catalog refresh / stock adjust.
      setCart((prev) =>
        prev.map((line) => {
          const fresh = (res.data || []).find((i) => i.id === line.item_id);
          if (!fresh) return line;
          const tracked =
            fresh.stock_quantity !== null && fresh.stock_quantity !== undefined;
          return {
            ...line,
            stock_tracked: tracked,
            stock_quantity: tracked ? Number(fresh.stock_quantity) : null,
            price: Number(fresh.price),
          };
        }),
      );
    } catch (err) {
      setError(err.response?.data?.error?.message || 'Unable to load items.');
    } finally {
      setLoadingItems(false);
    }
  };

  useEffect(() => {
    listCategories()
      .then((res) => setCategories((res.data || []).filter((c) => c.is_active)))
      .catch(() => {});
  }, []);

  // Debounce catalog search so typing stays responsive with large inventories.
  useEffect(() => {
    const handle = window.setTimeout(() => {
      search(q, categoryId);
    }, 250);
    return () => window.clearTimeout(handle);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [q, categoryId]);

  // Refresh catalog when returning to the tab (e.g. after Adjust Stock on Items).
  useEffect(() => {
    const refresh = () => {
      if (document.visibilityState === 'visible') {
        search(q, categoryId);
      }
    };
    document.addEventListener('visibilitychange', refresh);
    window.addEventListener('focus', refresh);
    return () => {
      document.removeEventListener('visibilitychange', refresh);
      window.removeEventListener('focus', refresh);
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [q, categoryId]);

  useEffect(() => {
    if (!selectedCustomer && paymentMethod === PAYMENT_CREDIT) {
      setPaymentMethod(DEFAULT_PAYMENT_METHOD);
    }
  }, [selectedCustomer, paymentMethod]);

  const subtotalPreview = useMemo(
    () => cart.reduce((sum, line) => sum + line.price * line.quantity, 0),
    [cart],
  );

  const orderedCategories = useMemo(
    () => sortCategoriesHierarchically(categories),
    [categories],
  );

  const addItem = (item) => {
    const tracked =
      item.stock_quantity !== null && item.stock_quantity !== undefined;
    const available = tracked ? Number(item.stock_quantity) : null;
    if (tracked && available <= 0) {
      setError(`Item is out of stock: ${item.name}`);
      return;
    }
    setError('');
    setCart((prev) => {
      const existing = prev.find((line) => line.item_id === item.id);
      if (existing) {
        const nextQty = existing.quantity + 1;
        if (tracked && nextQty > available) {
          setError(
            `Insufficient stock. Available: ${available}, requested: ${nextQty}.`,
          );
          return prev;
        }
        return prev.map((line) =>
          line.item_id === item.id ? { ...line, quantity: nextQty } : line,
        );
      }
      return [
        ...prev,
        {
          item_id: item.id,
          name: item.name,
          price: Number(item.price),
          gst_percentage: Number(item.gst_percentage),
          quantity: 1,
          stock_quantity: available,
          stock_tracked: tracked,
        },
      ];
    });
  };

  const scanBarcode = async () => {
    const code = barcode.trim();
    if (!code || scanning) return;
    setScanning(true);
    setError('');
    try {
      const res = await getItemByBarcode(code);
      addItem(res.data);
      setBarcode('');
      window.requestAnimationFrame(() => barcodeInputRef.current?.focus());
    } catch (err) {
      setError(err.response?.data?.error?.message || 'No active item found for this barcode.');
    } finally {
      setScanning(false);
    }
  };

  const setQty = (itemId, quantity) => {
    const qty = Number(quantity);
    if (!Number.isFinite(qty) || qty <= 0) {
      setCart((prev) => prev.filter((line) => line.item_id !== itemId));
      setError('');
      return;
    }
    setCart((prev) => {
      const line = prev.find((row) => row.item_id === itemId);
      if (
        line?.stock_tracked &&
        line.stock_quantity != null &&
        qty > Number(line.stock_quantity)
      ) {
        setError(
          `Insufficient stock. Available: ${line.stock_quantity}, requested: ${qty}.`,
        );
        return prev;
      }
      setError('');
      return prev.map((row) =>
        row.item_id === itemId ? { ...row, quantity: qty } : row,
      );
    });
  };

  const removeLine = (itemId) => {
    setCart((prev) => prev.filter((line) => line.item_id !== itemId));
  };

  const clearCart = () => {
    setCart([]);
    setDiscount('0');
    setReference('');
    setPaymentMethod(DEFAULT_PAYMENT_METHOD);
  };

  const finalize = async () => {
    if (!isAllowedPaymentMethod(paymentMethod)) {
      setError('Please select a payment method.');
      return;
    }
    const stockIssue = cart.find(
      (line) =>
        line.stock_tracked &&
        line.stock_quantity != null &&
        line.quantity > Number(line.stock_quantity),
    );
    if (stockIssue) {
      setError(
        `Insufficient stock. Available: ${stockIssue.stock_quantity}, requested: ${stockIssue.quantity}.`,
      );
      return;
    }
    setSaving(true);
    setError('');
    try {
      const res = await createBill({
        reference: reference || null,
        discount: Number(discount || 0),
        payment_method: paymentMethod,
        customer_name: customerName || null,
        customer_phone_country_code: customerPhone ? countryCode : null,
        customer_phone: customerPhone || null,
        customer_email: customerEmail.trim() || null,
        customer_id: selectedCustomer?.id || null,
        items: cart.map((line) => ({
          item_id: line.item_id,
          quantity: line.quantity,
        })),
      });
      setCreatedBill(res.data);
      setWhatsappMessage('');
      setWhatsappError('');
      setEmailMessage('');
      setEmailError('');
      clearCart();
      // Refresh catalog so stock quantities reflect deduction.
      search(q, categoryId);
    } catch (err) {
      setError(err.response?.data?.error?.message || 'Failed to generate bill');
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
        err.response?.data?.error?.message ||
          'Unable to send the bill on WhatsApp. Please try again or use Print Bill.',
      );
    } finally {
      setWhatsappSending(false);
    }
  };

  const onSendWhatsappClick = () => {
    if (!createdBill) return;
    const hasPhone = Boolean(createdBill.customer_phone_national || customerPhone);
    if (!hasPhone) {
      setPhoneDraftCc(countryCode || '91');
      setPhoneDraft(customerPhone || '');
      setPhoneDialogOpen(true);
      return;
    }
    doSendWhatsapp({
      country_code: createdBill.customer_phone_country_code || countryCode,
      phone: createdBill.customer_phone_national || customerPhone,
      customer_name: createdBill.customer_name || customerName || null,
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
      setEmailError(
        err.response?.data?.error?.message ||
          'Unable to send the bill by email. Please try again or use Print Bill.',
      );
    } finally {
      setEmailSending(false);
    }
  };

  const onSendEmailClick = () => {
    if (!createdBill) return;
    const hasEmail = Boolean(createdBill.customer_email || customerEmail.trim());
    if (!hasEmail) {
      setEmailDraft(customerEmail || '');
      setEmailDialogOpen(true);
      return;
    }
    doSendEmail({
      email: createdBill.customer_email || customerEmail.trim(),
      customer_name: createdBill.customer_name || customerName || null,
    });
  };
  const cartStockInvalid = cart.some(
    (line) =>
      line.stock_tracked &&
      line.stock_quantity != null &&
      line.quantity > Number(line.stock_quantity),
  );

  return (
    <>
      <PageShell>
        {error ? <Alert severity="error">{error}</Alert> : null}

        <Box
          sx={{
            display: 'grid',
            gap: 3,
            gridTemplateColumns: { xs: '1fr', lg: '1.15fr 0.85fr' },
            alignItems: 'start',
            minWidth: 0,
            '& > *': { minWidth: 0 },
          }}
        >
          <Card>
            <CardContent sx={{ p: { xs: 2.5, sm: 3 }, '&:last-child': { pb: { xs: 2.5, sm: 3 } } }}>
              <Typography variant="h6" component="h2" sx={{ mb: 2 }}>
                Available Items
              </Typography>

              <Stack spacing={2} sx={{ mb: 2.5 }}>
                <TextField
                  inputRef={barcodeInputRef}
                  label="Scan barcode"
                  placeholder="Focus here and scan or type barcode…"
                  value={barcode}
                  onChange={(e) => setBarcode(e.target.value)}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter') {
                      e.preventDefault();
                      scanBarcode();
                    }
                  }}
                  fullWidth
                  autoComplete="off"
                  sx={{
                    '& .MuiOutlinedInput-root': {
                      bgcolor: 'action.hover',
                      fontSize: '1.05rem',
                      letterSpacing: '0.04em',
                    },
                  }}
                  helperText="Press Enter after scan — adds item to bill"
                />
                <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2}>
                  <TextField
                    label="Search items"
                    placeholder="Name, SKU, or barcode…"
                    value={q}
                    onChange={(e) => setQ(e.target.value)}
                    onKeyDown={(e) => {
                      if (e.key === 'Enter') search(q, categoryId);
                    }}
                    fullWidth
                  />
                  <Button variant="outlined" onClick={() => search(q, categoryId)} sx={{ flexShrink: 0 }}>
                    Search
                  </Button>
                </Stack>
              </Stack>

              <Stack direction="row" spacing={1} useFlexGap flexWrap="wrap" sx={{ mb: 2.5 }}>
                <Chip
                  size="small"
                  label="All"
                  color={!categoryId ? 'primary' : 'default'}
                  onClick={() => {
                    setCategoryId('');
                    search(q, '');
                  }}
                  clickable
                />
                {orderedCategories.map((cat) => (
                  <Chip
                    key={cat.id}
                    size="small"
                    label={
                      cat.depth > 0 && cat.parent_category_name
                        ? `${cat.parent_category_name} › ${cat.name}`
                        : cat.name
                    }
                    variant={cat.depth > 0 ? 'outlined' : 'filled'}
                    color={categoryId === cat.id ? 'primary' : 'default'}
                    onClick={() => {
                      setCategoryId(cat.id);
                      search(q, cat.id);
                    }}
                    clickable
                    sx={{ maxWidth: 220 }}
                  />
                ))}
              </Stack>

              {loadingItems ? (
                <Box sx={{ py: 6, display: 'grid', placeItems: 'center' }}>
                  <CircularProgress size={28} />
                </Box>
              ) : (
                <Stack
                  spacing={1.5}
                  sx={{ maxHeight: { lg: 'calc(100vh - 320px)' }, overflowY: 'auto', pr: 0.5 }}
                >
                  {catalog.map((item) => (
                    <Box
                      key={item.id}
                      sx={{
                        display: 'flex',
                        flexDirection: { xs: 'column', sm: 'row' },
                        alignItems: { xs: 'stretch', sm: 'center' },
                        gap: { xs: 1.25, sm: 2 },
                        px: { xs: 1.5, sm: 2 },
                        py: 1.5,
                        borderRadius: 2,
                        border: '1px solid',
                        borderColor: 'divider',
                        bgcolor: 'background.paper',
                        minWidth: 0,
                      }}
                    >
                      <Box sx={{ flexGrow: 1, minWidth: 0 }}>
                        <TruncateText value={item.name} maxWidth="100%" fontWeight={600} />
                        <Typography variant="caption" color="text.secondary" noWrap display="block" sx={{ mt: 0.5 }}>
                          {item.sku ? `${item.sku} · ` : ''}
                          {item.barcode ? `${item.barcode} · ` : ''}
                          {item.category_name || 'Item'} · {uomLabel(item.uom)} · GST{' '}
                          {Number(item.gst_percentage).toFixed(1)}%
                          {item.stock_quantity !== null && item.stock_quantity !== undefined
                            ? ` · Available stock: ${Number(item.stock_quantity)}`
                            : ''}
                        </Typography>
                      </Box>
                      <Stack
                        direction="row"
                        alignItems="center"
                        justifyContent="space-between"
                        spacing={1.5}
                        sx={{ flexShrink: 0 }}
                      >
                        <Typography
                          fontWeight={650}
                          sx={{
                            minWidth: { xs: 'auto', sm: 72 },
                            textAlign: 'right',
                            fontVariantNumeric: 'tabular-nums',
                          }}
                        >
                          ₹{Number(item.price).toFixed(2)}
                        </Typography>
                        <Button
                          size="small"
                          variant="contained"
                          startIcon={<AddOutlinedIcon />}
                          onClick={() => addItem(item)}
                          disabled={
                            item.stock_quantity !== null &&
                            item.stock_quantity !== undefined &&
                            Number(item.stock_quantity) <= 0
                          }
                          sx={{ flexShrink: 0 }}
                          aria-label={`Add ${item.name}`}
                        >
                          Add
                        </Button>
                      </Stack>
                    </Box>
                  ))}
                  {!catalog.length ? (
                    <EmptyState
                      title="No items found"
                      description="No active items match your search."
                    />
                  ) : null}
                </Stack>
              )}
            </CardContent>
          </Card>

          <Card sx={{ position: { lg: 'sticky' }, top: { lg: 96 } }}>
            <CardContent sx={{ p: { xs: 2.5, sm: 3 }, '&:last-child': { pb: { xs: 2.5, sm: 3 } } }}>
              <Typography variant="h6" component="h2" sx={{ mb: 2 }}>
                Current Bill
              </Typography>

              <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2} sx={{ mb: 2.5 }}>
                <TextField
                  label="Reference (optional)"
                  placeholder="Table, counter, token…"
                  value={reference}
                  onChange={(e) => setReference(e.target.value)}
                  fullWidth
                  inputProps={{ maxLength: 30 }}
                />
                <TextField
                  label="Discount (₹)"
                  type="number"
                  value={discount}
                  onChange={(e) => setDiscount(e.target.value)}
                  fullWidth
                  inputProps={{ min: 0, step: '0.01' }}
                />
              </Stack>

              <Box sx={{ mb: 2.5 }}>
                <CustomerPicker
                  value={selectedCustomer}
                  onChange={(customer) => {
                    setSelectedCustomer(customer);
                    setCustomerName(customer.name || '');
                    setCountryCode(customer.phone_country_code || '91');
                    setCustomerPhone(customer.phone_national || '');
                    setCustomerEmail(customer.email || '');
                  }}
                  onClear={() => {
                    setSelectedCustomer(null);
                  }}
                />
              </Box>

              <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2} sx={{ mb: 2.5 }}>
                <TextField
                  label="Customer name (optional)"
                  value={customerName}
                  onChange={(e) => setCustomerName(e.target.value)}
                  fullWidth
                  inputProps={{ maxLength: 120 }}
                />
                <TextField
                  label="Country code"
                  value={countryCode}
                  onChange={(e) => setCountryCode(e.target.value.replace(/\D/g, '').slice(0, 3))}
                  sx={{ width: { xs: '100%', sm: 120 }, flexShrink: 0 }}
                  helperText="e.g. 91"
                />
                <TextField
                  label="Customer mobile (optional)"
                  value={customerPhone}
                  onChange={(e) => setCustomerPhone(e.target.value.replace(/\D/g, '').slice(0, 14))}
                  fullWidth
                  placeholder="9876543210"
                  helperText="For WhatsApp"
                />
              </Stack>
              <TextField
                label="Customer email (optional)"
                type="email"
                value={customerEmail}
                onChange={(e) => setCustomerEmail(e.target.value)}
                fullWidth
                sx={{ mb: 2.5 }}
                helperText="For email PDF bill"
              />

              <Stack spacing={1.5} sx={{ mb: 2.5, minHeight: 120 }}>
                {cart.map((line) => (
                  <Box
                    key={line.item_id}
                    sx={{
                      display: 'flex',
                      alignItems: 'center',
                      gap: 1.5,
                      py: 1.25,
                      borderBottom: '1px solid',
                      borderColor: 'divider',
                      minWidth: 0,
                    }}
                  >
                    <Box sx={{ flex: 1, minWidth: 0 }}>
                      <TruncateText value={line.name} maxWidth="100%" fontWeight={600} />
                      {line.stock_tracked ? (
                        <Typography variant="caption" color="text.secondary" display="block" sx={{ mt: 0.5 }}>
                          Available stock: {line.stock_quantity}
                          {line.quantity > Number(line.stock_quantity)
                            ? ' · Insufficient for this qty'
                            : ''}
                        </Typography>
                      ) : null}
                      <Stack direction="row" spacing={1.5} alignItems="center" sx={{ mt: 1 }}>
                        <TextField
                          type="number"
                          size="small"
                          label="Qty"
                          value={line.quantity}
                          onChange={(e) => setQty(line.item_id, e.target.value)}
                          inputProps={{ min: 0.001, step: '1' }}
                          sx={{ width: 88 }}
                        />
                        <Typography variant="caption" color="text.secondary">
                          × ₹{line.price.toFixed(2)}
                        </Typography>
                      </Stack>
                    </Box>
                    <Typography
                      fontWeight={650}
                      sx={{ flexShrink: 0, fontVariantNumeric: 'tabular-nums' }}
                    >
                      ₹{(line.price * line.quantity).toFixed(2)}
                    </Typography>
                    <Tooltip title="Remove from bill (does not delete catalog item)">
                      <IconButton
                        size="small"
                        aria-label={`Remove ${line.name} from bill`}
                        onClick={() => removeLine(line.item_id)}
                      >
                        <DeleteOutlinedIcon fontSize="small" />
                      </IconButton>
                    </Tooltip>
                  </Box>
                ))}
                {!cart.length ? (
                  <EmptyState
                    title="Cart is empty"
                    description="Add items from the left to build the bill."
                  />
                ) : null}
              </Stack>

              <Divider sx={{ mb: 2 }} />

              <Stack spacing={1.25} sx={{ mb: 2.5 }}>
                <Stack direction="row" justifyContent="space-between" spacing={2}>
                  <Typography color="text.secondary">Subtotal</Typography>
                  <Typography fontWeight={650} sx={{ fontVariantNumeric: 'tabular-nums' }}>
                    ₹{subtotalPreview.toFixed(2)}
                  </Typography>
                </Stack>
                <Stack direction="row" justifyContent="space-between" spacing={2}>
                  <Typography color="text.secondary">Discount</Typography>
                  <Typography sx={{ fontVariantNumeric: 'tabular-nums' }}>
                    ₹{Number(discount || 0).toFixed(2)}
                  </Typography>
                </Stack>
                <Typography variant="caption" color="text.secondary" sx={{ pt: 0.5 }}>
                  Final GST (CGST/SGST), round-off and grand total are calculated by the server when
                  you generate the bill.
                </Typography>
              </Stack>

              <FormControl component="fieldset" sx={{ mb: 3 }}>
                <FormLabel component="legend" sx={{ mb: 0.75, typography: 'subtitle2', color: 'text.primary' }}>
                  Payment Method
                </FormLabel>
                <RadioGroup
                  row
                  name="payment-method"
                  value={paymentMethod}
                  onChange={(e) => setPaymentMethod(e.target.value)}
                >
                  <FormControlLabel
                    value={PAYMENT_CASH}
                    control={<Radio size="small" />}
                    label="Cash"
                    sx={{ mr: 3 }}
                  />
                  <FormControlLabel
                    value={PAYMENT_ONLINE}
                    control={<Radio size="small" />}
                    label="Online"
                    sx={{ mr: 3 }}
                  />
                  {selectedCustomer ? (
                    <FormControlLabel
                      value={PAYMENT_CREDIT}
                      control={<Radio size="small" />}
                      label="Credit (Udhari)"
                    />
                  ) : null}
                </RadioGroup>
                <Typography variant="caption" color="text.secondary" display="block" sx={{ mt: 0.5 }}>
                  {selectedCustomer
                    ? 'Credit requires a linked customer and adds to their outstanding balance.'
                    : 'Required · defaults to Cash. Link a customer to enable credit.'}
                </Typography>
              </FormControl>

              <Stack direction={{ xs: 'column', sm: 'row' }} spacing={1.5}>
                <Button
                  variant="outlined"
                  color="inherit"
                  onClick={clearCart}
                  disabled={!cart.length}
                >
                  Clear
                </Button>
                <Button
                  variant="contained"
                  onClick={finalize}
                  disabled={!cart.length || saving || cartStockInvalid}
                  startIcon={saving ? <CircularProgress size={16} color="inherit" /> : null}
                  sx={{ flexGrow: 1 }}
                >
                  {saving ? 'Generating...' : 'Generate Bill'}
                </Button>
              </Stack>
            </CardContent>
          </Card>
        </Box>
      </PageShell>

      <Dialog
        open={Boolean(createdBill)}
        onClose={() => !whatsappSending && !emailSending && setCreatedBill(null)}
        fullWidth
        maxWidth="xs"
      >
        <DialogTitle>Bill generated successfully</DialogTitle>
        <DialogContent>
          <Stack spacing={1.5} sx={{ mt: 0.5 }}>
            <Typography>
              Bill <strong>#{createdBill?.bill_number}</strong> saved successfully.
            </Typography>
            <Typography>
              Grand total: ₹{Number(createdBill?.grand_total || 0).toFixed(2)}
            </Typography>
            <Typography>
              Payment Method: {paymentMethodLabel(createdBill?.payment_method)}
            </Typography>
            {createdBill?.customer_phone_masked ? (
              <Typography variant="body2" color="text.secondary">
                Customer WhatsApp: {createdBill.customer_phone_masked}
              </Typography>
            ) : null}
            {createdBill?.customer_email_masked ? (
              <Typography variant="body2" color="text.secondary">
                Customer email: {createdBill.customer_email_masked}
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
              openBillPrint(createdBill.id, { auto: true });
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
                setWhatsappError(
                  err.response?.data?.error?.message || 'Unable to download bill PDF.',
                );
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
            {whatsappSending
              ? 'Sending…'
              : whatsappError
                ? 'Retry WhatsApp'
                : 'Send on WhatsApp'}
          </Button>
          <Button
            variant="contained"
            startIcon={
              emailSending ? (
                <CircularProgress size={16} color="inherit" />
              ) : (
                <EmailOutlinedIcon />
              )
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
            Customer WhatsApp number is required to send this bill.
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
              onChange={(e) => setPhoneDraft(e.target.value.replace(/\D/g, '').slice(0, 14))}
              fullWidth
              autoFocus
            />
          </Stack>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setPhoneDialogOpen(false)} disabled={whatsappSending}>
            Cancel
          </Button>
          <Button
            variant="contained"
            color="success"
            disabled={whatsappSending || !phoneDraft}
            onClick={() =>
              doSendWhatsapp({
                country_code: phoneDraftCc,
                phone: phoneDraft,
                customer_name: customerName || null,
              })
            }
          >
            {whatsappSending ? 'Sending…' : 'Send'}
          </Button>
        </DialogActions>
      </Dialog>

      <Dialog
        open={emailDialogOpen}
        onClose={() => !emailSending && setEmailDialogOpen(false)}
        fullWidth
        maxWidth="xs"
      >
        <DialogTitle>Customer email</DialogTitle>
        <DialogContent>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
            Customer email is required to send this bill.
          </Typography>
          <TextField
            label="Email"
            type="email"
            value={emailDraft}
            onChange={(e) => setEmailDraft(e.target.value)}
            fullWidth
            autoFocus
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
                customer_name: customerName || null,
              })
            }
          >
            {emailSending ? 'Sending…' : 'Send'}
          </Button>
        </DialogActions>
      </Dialog>
    </>
  );
}
