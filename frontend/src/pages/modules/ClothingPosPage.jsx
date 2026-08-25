import CheckroomOutlinedIcon from '@mui/icons-material/CheckroomOutlined';
import DeleteOutlineOutlinedIcon from '@mui/icons-material/DeleteOutlineOutlined';
import {
  Alert,
  Box,
  Button,
  Card,
  CardActionArea,
  CardContent,
  CardMedia,
  Chip,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  Divider,
  IconButton,
  Stack,
  TextField,
  Typography,
} from '@mui/material';
import { useCallback, useEffect, useMemo, useState } from 'react';
import PageShell from '../../components/PageShell';
import VariantStockGrid from '../../components/VariantStockGrid';
import { useModuleGate } from '../../context/ModulesContext';
import { createBill } from '../../services/billService';
import { fetchClothingPosCatalog } from '../../services/clothingService';
import {
  DEFAULT_PAYMENT_METHOD,
  PAYMENT_CASH,
  PAYMENT_ONLINE,
  paymentMethodLabel,
} from '../../utils/paymentMethod';

function money(value) {
  return `₹${Number(value || 0).toFixed(2)}`;
}

export default function ClothingPosPage() {
  const moduleEnabled = useModuleGate('variants');
  const [items, setItems] = useState([]);
  const [q, setQ] = useState('');
  const [cart, setCart] = useState([]);
  const [picker, setPicker] = useState(null);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [saving, setSaving] = useState(false);
  const [paymentMethod, setPaymentMethod] = useState(DEFAULT_PAYMENT_METHOD);

  const load = useCallback(async () => {
    setError('');
    try {
      const res = await fetchClothingPosCatalog({ q: q || undefined, limit: 200 });
      setItems(res.data?.items || []);
    } catch (err) {
      setError(err.response?.data?.error?.message || 'Failed to load clothing catalog');
    }
  }, [q]);

  useEffect(() => {
    if (!moduleEnabled) return;
    const handle = window.setTimeout(() => {
      load();
    }, 200);
    return () => window.clearTimeout(handle);
  }, [moduleEnabled, load]);

  const total = useMemo(
    () => cart.reduce((sum, line) => sum + Number(line.price) * Number(line.quantity), 0),
    [cart],
  );

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

  const finalize = async () => {
    if (!cart.length) {
      setError('Add at least one size/color.');
      return;
    }
    setSaving(true);
    setError('');
    setSuccess('');
    try {
      const res = await createBill({
        payment_method: paymentMethod,
        items: cart.map((line) => ({
          item_id: line.item_id,
          variant_id: line.variant_id,
          quantity: line.quantity,
        })),
      });
      setSuccess(`Bill ${res.data?.bill_number} created.`);
      setCart([]);
      await load();
    } catch (err) {
      setError(err.response?.data?.error?.message || 'Failed to generate bill');
    } finally {
      setSaving(false);
    }
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
      {error ? (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      ) : null}
      {success ? (
        <Alert severity="success" sx={{ mb: 2 }}>
          {success}
        </Alert>
      ) : null}
      <Stack direction={{ xs: 'column', md: 'row' }} spacing={2} alignItems="stretch">
        <Box sx={{ flex: 1, minWidth: 0 }}>
          <TextField
            label="Search items"
            value={q}
            onChange={(e) => setQ(e.target.value)}
            fullWidth
            sx={{ mb: 2 }}
          />
          <Box
            sx={{
              display: 'grid',
              gap: 1.5,
              gridTemplateColumns: 'repeat(auto-fill, minmax(160px, 1fr))',
            }}
          >
            {items.map((item) => (
              <Card key={item.id} variant="outlined">
                <CardActionArea onClick={() => setPicker(item)}>
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
                  <CardContent sx={{ py: 1.25 }}>
                    <Typography variant="subtitle2" noWrap>
                      {item.name}
                    </Typography>
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
            ))}
          </Box>
        </Box>
        <Box sx={{ width: { xs: '100%', md: 320 }, flexShrink: 0 }}>
          <Typography variant="h6" sx={{ mb: 1 }}>
            Cart
          </Typography>
          <Stack spacing={1} sx={{ mb: 2, minHeight: 80 }}>
            {cart.map((line) => (
              <Stack key={line.line_key} direction="row" alignItems="center" spacing={1}>
                <Box sx={{ flex: 1, minWidth: 0 }}>
                  <Typography variant="body2" noWrap>
                    {line.name}
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    {line.quantity} × {money(line.price)}
                  </Typography>
                </Box>
                <IconButton
                  size="small"
                  aria-label={`Remove ${line.name}`}
                  onClick={() => setCart((prev) => prev.filter((row) => row.line_key !== line.line_key))}
                >
                  <DeleteOutlineOutlinedIcon fontSize="small" />
                </IconButton>
              </Stack>
            ))}
            {!cart.length ? (
              <Typography variant="body2" color="text.secondary">
                Tap a product, then a size/color with stock.
              </Typography>
            ) : null}
          </Stack>
          <Divider sx={{ mb: 2 }} />
          <Typography fontWeight={700} sx={{ mb: 1.5 }}>
            Total {money(total)}
          </Typography>
          <Stack direction="row" spacing={1} sx={{ mb: 1.5 }}>
            <Button
              size="small"
              variant={paymentMethod === PAYMENT_CASH ? 'contained' : 'outlined'}
              onClick={() => setPaymentMethod(PAYMENT_CASH)}
            >
              {paymentMethodLabel(PAYMENT_CASH)}
            </Button>
            <Button
              size="small"
              variant={paymentMethod === PAYMENT_ONLINE ? 'contained' : 'outlined'}
              onClick={() => setPaymentMethod(PAYMENT_ONLINE)}
            >
              {paymentMethodLabel(PAYMENT_ONLINE)}
            </Button>
          </Stack>
          <Button variant="contained" fullWidth disabled={saving || !cart.length} onClick={finalize}>
            {saving ? 'Saving…' : 'Generate bill'}
          </Button>
        </Box>
      </Stack>

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
            <Button variant="contained" onClick={() => {
              setPicker(null);
              setCart((prev) => {
                const lineKey = picker.id;
                const existing = prev.find((line) => line.line_key === lineKey);
                if (existing) {
                  return prev.map((line) =>
                    line.line_key === lineKey ? { ...line, quantity: line.quantity + 1 } : line,
                  );
                }
                return [
                  ...prev,
                  {
                    line_key: lineKey,
                    item_id: picker.id,
                    variant_id: null,
                    name: picker.name,
                    price: Number(picker.price),
                    quantity: 1,
                    stock_quantity: Number(picker.stock_quantity),
                  },
                ];
              });
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
    </PageShell>
  );
}
