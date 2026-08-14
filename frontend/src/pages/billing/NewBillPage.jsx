import AddOutlinedIcon from '@mui/icons-material/AddOutlined';
import DeleteOutlinedIcon from '@mui/icons-material/DeleteOutlined';
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
import { useEffect, useMemo, useState } from 'react';
import EmptyState from '../../components/EmptyState';
import PageShell from '../../components/PageShell';
import TruncateText from '../../components/TruncateText';
import { createBill, openBillPrint } from '../../services/billService';
import { listCategories } from '../../services/categoryService';
import { listItems } from '../../services/itemService';
import {
  DEFAULT_PAYMENT_METHOD,
  PAYMENT_CASH,
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
  const [catalog, setCatalog] = useState([]);
  const [categories, setCategories] = useState([]);
  const [categoryId, setCategoryId] = useState('');
  const [cart, setCart] = useState([]);
  const [discount, setDiscount] = useState('0');
  const [reference, setReference] = useState('');
  const [paymentMethod, setPaymentMethod] = useState(DEFAULT_PAYMENT_METHOD);
  const [error, setError] = useState('');
  const [saving, setSaving] = useState(false);
  const [loadingItems, setLoadingItems] = useState(true);
  const [createdBill, setCreatedBill] = useState(null);

  const search = async (term = q, cat = categoryId) => {
    setError('');
    setLoadingItems(true);
    try {
      const res = await listItems({
        q: term || undefined,
        category_id: cat || undefined,
        is_active: true,
        per_page: 60,
      });
      setCatalog(res.data || []);
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
    search('');
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const subtotalPreview = useMemo(
    () => cart.reduce((sum, line) => sum + line.price * line.quantity, 0),
    [cart],
  );

  const orderedCategories = useMemo(
    () => sortCategoriesHierarchically(categories),
    [categories],
  );

  const addItem = (item) => {
    setCart((prev) => {
      const existing = prev.find((line) => line.item_id === item.id);
      if (existing) {
        return prev.map((line) =>
          line.item_id === item.id
            ? { ...line, quantity: line.quantity + 1 }
            : line,
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
        },
      ];
    });
  };

  const setQty = (itemId, quantity) => {
    const qty = Number(quantity);
    if (!Number.isFinite(qty) || qty <= 0) {
      setCart((prev) => prev.filter((line) => line.item_id !== itemId));
      return;
    }
    setCart((prev) =>
      prev.map((line) =>
        line.item_id === itemId ? { ...line, quantity: qty } : line,
      ),
    );
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
    setSaving(true);
    setError('');
    try {
      const res = await createBill({
        reference: reference || null,
        discount: Number(discount || 0),
        payment_method: paymentMethod,
        items: cart.map((line) => ({
          item_id: line.item_id,
          quantity: line.quantity,
        })),
      });
      setCreatedBill(res.data);
      clearCart();
    } catch (err) {
      setError(err.response?.data?.error?.message || 'Failed to generate bill');
    } finally {
      setSaving(false);
    }
  };

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

              <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2} sx={{ mb: 2.5 }}>
                <TextField
                  label="Search items"
                  placeholder="Name or SKU…"
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
                        alignItems: 'center',
                        gap: 2,
                        px: 2,
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
                          {item.category_name || 'Item'} · GST {Number(item.gst_percentage).toFixed(1)}%
                        </Typography>
                      </Box>
                      <Typography
                        fontWeight={650}
                        sx={{
                          minWidth: 72,
                          textAlign: 'right',
                          flexShrink: 0,
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
                        sx={{ flexShrink: 0 }}
                      >
                        Add
                      </Button>
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
                  />
                </RadioGroup>
                <Typography variant="caption" color="text.secondary" display="block" sx={{ mt: 0.5 }}>
                  Required · defaults to Cash
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
                  disabled={!cart.length || saving}
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

      <Dialog open={Boolean(createdBill)} onClose={() => setCreatedBill(null)} fullWidth maxWidth="xs">
        <DialogTitle>Bill generated</DialogTitle>
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
          </Stack>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setCreatedBill(null)}>Close</Button>
          <Button
            variant="contained"
            onClick={() => {
              openBillPrint(createdBill.id, { auto: true });
              setCreatedBill(null);
            }}
          >
            Print
          </Button>
        </DialogActions>
      </Dialog>
    </>
  );
}
