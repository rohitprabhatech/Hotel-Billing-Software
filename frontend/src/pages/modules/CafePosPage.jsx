import AddShoppingCartOutlinedIcon from '@mui/icons-material/AddShoppingCartOutlined';
import DeleteOutlineOutlinedIcon from '@mui/icons-material/DeleteOutlineOutlined';
import LocalCafeOutlinedIcon from '@mui/icons-material/LocalCafeOutlined';
import {
  Alert,
  Box,
  Button,
  Card,
  CardActionArea,
  CardContent,
  Chip,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  Divider,
  FormControlLabel,
  Checkbox,
  Grid,
  IconButton,
  Stack,
  TextField,
  Typography,
} from '@mui/material';
import { useEffect, useMemo, useState } from 'react';
import PageShell from '../../components/PageShell';
import { useModuleGate } from '../../context/ModulesContext';
import { fetchPosCatalog } from '../../services/cafeService';
import { createOrder } from '../../services/orderService';
import { settleOrder } from '../../services/orderSettlementService';

function money(value) {
  return `₹${Number(value || 0).toFixed(2)}`;
}

function lineKey(line) {
  return `${line.kind}:${line.item_id || line.combo_id}:${(line.addon_ids || []).join(',')}`;
}

export default function CafePosPage() {
  const moduleEnabled = useModuleGate('addons_combos');
  const [catalog, setCatalog] = useState({ menu_items: [], combos: [], popular_combos: [] });
  const [cart, setCart] = useState([]);
  const [q, setQ] = useState('');
  const [pickerItem, setPickerItem] = useState(null);
  const [selectedAddons, setSelectedAddons] = useState([]);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    if (!moduleEnabled) return;
    fetchPosCatalog()
      .then((res) => setCatalog(res.data || { menu_items: [], combos: [], popular_combos: [] }))
      .catch((err) => {
        setError(err.response?.data?.error?.message || 'Failed to load cafe catalog');
      });
  }, [moduleEnabled]);

  const filteredItems = useMemo(() => {
    const term = q.trim().toLowerCase();
    const items = catalog.menu_items || [];
    if (!term) return items;
    return items.filter((item) => item.name.toLowerCase().includes(term));
  }, [catalog.menu_items, q]);

  const cartTotal = useMemo(
    () => cart.reduce((sum, line) => sum + Number(line.unit_price || 0) * Number(line.quantity || 0), 0),
    [cart]
  );

  const openPicker = (item) => {
    const defaults = (item.addon_groups || []).flatMap((group) =>
      (group.addons || []).filter((addon) => addon.is_default).map((addon) => addon.id)
    );
    setPickerItem(item);
    setSelectedAddons(defaults);
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
    const addonExtra = (pickerItem.addon_groups || [])
      .flatMap((group) => group.addons || [])
      .filter((addon) => selectedAddons.includes(addon.id))
      .reduce((sum, addon) => sum + Number(addon.extra_price || 0), 0);
    const line = {
      kind: 'item',
      item_id: pickerItem.id,
      name: pickerItem.name,
      quantity: 1,
      unit_price: Number(pickerItem.price) + addonExtra,
      addon_ids: [...selectedAddons],
    };
    setCart((prev) => {
      const key = lineKey(line);
      const existing = prev.find((row) => lineKey(row) === key);
      if (existing) {
        return prev.map((row) =>
          lineKey(row) === key ? { ...row, quantity: Number(row.quantity) + 1 } : row
        );
      }
      return [...prev, line];
    });
    setPickerItem(null);
    setSelectedAddons([]);
  };

  const addCombo = (combo) => {
    const line = {
      kind: 'combo',
      combo_id: combo.id,
      name: combo.name,
      quantity: 1,
      unit_price: Number(combo.combo_price),
    };
    setCart((prev) => {
      const key = lineKey(line);
      const existing = prev.find((row) => lineKey(row) === key);
      if (existing) {
        return prev.map((row) =>
          lineKey(row) === key ? { ...row, quantity: Number(row.quantity) + 1 } : row
        );
      }
      return [...prev, line];
    });
  };

  const removeLine = (line) => {
    setCart((prev) => prev.filter((row) => lineKey(row) !== lineKey(line)));
  };

  const checkout = async () => {
    if (!cart.length) {
      setError('Add at least one item to the cart');
      return;
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
        items,
        combos,
      });
      const order = orderRes.data;
      const billRes = await settleOrder(order.id, { payment_method: 'cash' });
      setSuccess(`Bill ${billRes.data.bill_number} created — ${money(billRes.data.grand_total)}`);
      setCart([]);
    } catch (err) {
      setError(err.response?.data?.error?.message || 'Checkout failed');
    } finally {
      setSaving(false);
    }
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
                placeholder="Search menu…"
                value={q}
                onChange={(event) => setQ(event.target.value)}
                fullWidth
              />

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
            </Stack>
          </Grid>

          <Grid item xs={12} md={4}>
            <Card variant="outlined">
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Cart
                </Typography>
                {!cart.length ? (
                  <Typography variant="body2" color="text.secondary">
                    Tap menu items or combos to add lines.
                  </Typography>
                ) : (
                  <Stack spacing={1}>
                    {cart.map((line) => (
                      <Stack
                        key={lineKey(line)}
                        direction="row"
                        alignItems="center"
                        justifyContent="space-between"
                      >
                        <Box>
                          <Typography variant="body2">
                            {line.name} × {line.quantity}
                          </Typography>
                          <Typography variant="caption" color="text.secondary">
                            {money(Number(line.unit_price) * Number(line.quantity))}
                          </Typography>
                        </Box>
                        <IconButton size="small" onClick={() => removeLine(line)}>
                          <DeleteOutlineOutlinedIcon fontSize="small" />
                        </IconButton>
                      </Stack>
                    ))}
                    <Divider />
                    <Stack direction="row" justifyContent="space-between">
                      <Typography fontWeight={600}>Total</Typography>
                      <Typography fontWeight={600}>{money(cartTotal)}</Typography>
                    </Stack>
                    <Button
                      variant="contained"
                      startIcon={<AddShoppingCartOutlinedIcon />}
                      onClick={checkout}
                      disabled={saving}
                      fullWidth
                    >
                      {saving ? 'Processing…' : 'Quick bill'}
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
    </PageShell>
  );
}
