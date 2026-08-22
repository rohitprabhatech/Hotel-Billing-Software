import {
  Alert,
  Box,
  Button,
  Card,
  CardContent,
  FormControl,
  FormControlLabel,
  InputLabel,
  MenuItem,
  Radio,
  RadioGroup,
  Select,
  Stack,
  TextField,
  Typography,
} from '@mui/material';
import { useEffect, useMemo, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import CustomerPicker from '../../components/CustomerPicker';
import PageShell from '../../components/PageShell';
import { useAuth } from '../../context/AuthContext';
import { useModuleGate } from '../../context/ModulesContext';
import { PATHS } from '../../routes/paths';
import { listItems } from '../../services/itemService';
import { createOrder } from '../../services/orderService';
import { listTables } from '../../services/tableService';

const CHANNELS = [
  { value: 'dine_in', label: 'Dine-in' },
  { value: 'takeaway', label: 'Takeaway' },
  { value: 'delivery', label: 'Delivery' },
];

function money(value) {
  return `₹${Number(value || 0).toFixed(2)}`;
}

export default function NewOrderPage() {
  const navigate = useNavigate();
  const { role } = useAuth();
  const moduleEnabled = useModuleGate('order_channels');
  const ordersPath = role === 'OWNER' ? PATHS.ownerOrders : PATHS.billingOrders;

  const [channel, setChannel] = useState('dine_in');
  const [tables, setTables] = useState([]);
  const [catalog, setCatalog] = useState([]);
  const [diningTableId, setDiningTableId] = useState('');
  const [deliveryAddress, setDeliveryAddress] = useState('');
  const [notes, setNotes] = useState('');
  const [selectedCustomer, setSelectedCustomer] = useState(null);
  const [customerName, setCustomerName] = useState('');
  const [countryCode, setCountryCode] = useState('91');
  const [customerPhone, setCustomerPhone] = useState('');
  const [cart, setCart] = useState([]);
  const [q, setQ] = useState('');
  const [error, setError] = useState('');
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    if (!moduleEnabled) return;
    listTables({ status: 'available' })
      .then((res) => setTables(res.data || []))
      .catch(() => {});
    listItems({ is_active: true, per_page: 100, is_menu: true })
      .then((res) => setCatalog(res.data || []))
      .catch(() => {
        listItems({ is_active: true, per_page: 100 })
          .then((res) => setCatalog(res.data || []))
          .catch(() => {});
      });
  }, [moduleEnabled]);

  const filteredCatalog = useMemo(() => {
    const term = q.trim().toLowerCase();
    if (!term) return catalog;
    return catalog.filter(
      (item) =>
        item.name.toLowerCase().includes(term) ||
        (item.barcode || '').toLowerCase().includes(term),
    );
  }, [catalog, q]);

  const cartTotal = useMemo(
    () => cart.reduce((sum, line) => sum + line.price * line.quantity, 0),
    [cart],
  );

  const addToCart = (item) => {
    setCart((prev) => {
      const existing = prev.find((line) => line.item_id === item.id);
      if (existing) {
        return prev.map((line) =>
          line.item_id === item.id ? { ...line, quantity: line.quantity + 1 } : line,
        );
      }
      return [
        ...prev,
        {
          item_id: item.id,
          name: item.name,
          price: Number(item.price),
          quantity: 1,
        },
      ];
    });
  };

  const onSubmit = async () => {
    setError('');
    if (channel === 'dine_in' && !diningTableId) {
      setError('Select a table for dine-in orders.');
      return;
    }
    if (channel === 'delivery' && !deliveryAddress.trim()) {
      setError('Delivery address is required.');
      return;
    }
    if (cart.length === 0) {
      setError('Add at least one item to the order.');
      return;
    }

    setSaving(true);
    try {
      const payload = {
        channel,
        dining_table_id: channel === 'dine_in' ? diningTableId : null,
        delivery_address: channel === 'delivery' ? deliveryAddress.trim() : null,
        notes: notes.trim() || null,
        customer_id: selectedCustomer?.id || null,
        customer_name: customerName.trim() || null,
        customer_phone_country_code: customerPhone ? countryCode : null,
        customer_phone: customerPhone.trim() || null,
        items: cart.map((line) => ({ item_id: line.item_id, quantity: line.quantity })),
      };
      await createOrder(payload);
      navigate(ordersPath);
    } catch (err) {
      setError(err.response?.data?.error?.message || 'Unable to create order.');
    } finally {
      setSaving(false);
    }
  };

  if (!moduleEnabled) {
    return (
      <PageShell>
        <Alert severity="warning">Order channels are not enabled for this business type.</Alert>
      </PageShell>
    );
  }

  return (
    <PageShell>
      <Stack spacing={2}>
        {error ? <Alert severity="error">{error}</Alert> : null}

        <Card variant="outlined">
          <CardContent>
            <Typography variant="subtitle1" gutterBottom>
              Order channel
            </Typography>
            <FormControl component="fieldset">
              <RadioGroup row value={channel} onChange={(e) => setChannel(e.target.value)}>
                {CHANNELS.map((option) => (
                  <FormControlLabel
                    key={option.value}
                    value={option.value}
                    control={<Radio />}
                    label={option.label}
                  />
                ))}
              </RadioGroup>
            </FormControl>

            {channel === 'dine_in' ? (
              <FormControl fullWidth sx={{ mt: 2 }}>
                <InputLabel id="order-table-label">Table</InputLabel>
                <Select
                  labelId="order-table-label"
                  label="Table"
                  value={diningTableId}
                  onChange={(e) => setDiningTableId(e.target.value)}
                >
                  {tables.map((table) => (
                    <MenuItem key={table.id} value={table.id}>
                      {table.code}
                      {table.section ? ` · ${table.section}` : ''}
                      {table.capacity ? ` (${table.capacity} seats)` : ''}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            ) : null}

            {channel === 'delivery' ? (
              <TextField
                label="Delivery address"
                value={deliveryAddress}
                onChange={(e) => setDeliveryAddress(e.target.value)}
                fullWidth
                multiline
                minRows={2}
                sx={{ mt: 2 }}
              />
            ) : null}

            {channel !== 'dine_in' ? (
              <Stack spacing={2} sx={{ mt: 2 }}>
                <CustomerPicker
                  value={selectedCustomer}
                  onChange={(customer) => {
                    setSelectedCustomer(customer);
                    if (customer) {
                      setCustomerName(customer.name || '');
                      setCountryCode(customer.phone_country_code || '91');
                      setCustomerPhone(customer.phone_national || '');
                    }
                  }}
                />
                <TextField
                  label="Customer name"
                  value={customerName}
                  onChange={(e) => setCustomerName(e.target.value)}
                  fullWidth
                />
              </Stack>
            ) : null}

            <TextField
              label="Notes (optional)"
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              fullWidth
              sx={{ mt: 2 }}
            />
          </CardContent>
        </Card>

        <Box
          sx={{
            display: 'grid',
            gap: 2,
            gridTemplateColumns: { xs: '1fr', md: '1fr 1fr' },
          }}
        >
          <Card variant="outlined">
            <CardContent>
              <TextField
                label="Search menu items"
                value={q}
                onChange={(e) => setQ(e.target.value)}
                fullWidth
                sx={{ mb: 2 }}
              />
              <Stack spacing={1} sx={{ maxHeight: 360, overflow: 'auto' }}>
                {filteredCatalog.map((item) => (
                  <Button
                    key={item.id}
                    variant="outlined"
                    onClick={() => addToCart(item)}
                    sx={{ justifyContent: 'space-between' }}
                  >
                    <span>{item.name}</span>
                    <span>{money(item.price)}</span>
                  </Button>
                ))}
              </Stack>
            </CardContent>
          </Card>

          <Card variant="outlined">
            <CardContent>
              <Typography variant="subtitle1" gutterBottom>
                Order lines
              </Typography>
              {cart.length === 0 ? (
                <Typography variant="body2" color="text.secondary">
                  Tap items to add them to this order.
                </Typography>
              ) : (
                <Stack spacing={1}>
                  {cart.map((line) => (
                    <Stack key={line.item_id} direction="row" justifyContent="space-between">
                      <Typography>
                        {line.name} × {line.quantity}
                      </Typography>
                      <Typography>{money(line.price * line.quantity)}</Typography>
                    </Stack>
                  ))}
                  <Typography variant="subtitle1" align="right" sx={{ pt: 1 }}>
                    Subtotal: {money(cartTotal)}
                  </Typography>
                </Stack>
              )}
              <Button
                variant="contained"
                fullWidth
                sx={{ mt: 2 }}
                disabled={saving}
                onClick={onSubmit}
              >
                {saving ? 'Saving…' : 'Create order'}
              </Button>
            </CardContent>
          </Card>
        </Box>
      </Stack>
    </PageShell>
  );
}
