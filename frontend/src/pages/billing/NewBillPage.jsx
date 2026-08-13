import DeleteOutlinedIcon from '@mui/icons-material/DeleteOutlined';
import {
  Alert,
  Box,
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  IconButton,
  Stack,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
  TextField,
  Typography,
} from '@mui/material';
import { useEffect, useMemo, useState } from 'react';
import { createBill, openBillPrint } from '../../services/billService';
import { listItems } from '../../services/itemService';

export default function NewBillPage() {
  const [q, setQ] = useState('');
  const [catalog, setCatalog] = useState([]);
  const [cart, setCart] = useState([]);
  const [discount, setDiscount] = useState('0');
  const [tableNumber, setTableNumber] = useState('');
  const [error, setError] = useState('');
  const [saving, setSaving] = useState(false);
  const [createdBill, setCreatedBill] = useState(null);

  const search = async (term = q) => {
    setError('');
    try {
      const res = await listItems({ q: term || undefined, per_page: 40 });
      setCatalog(res.data || []);
    } catch (err) {
      setError(err.response?.data?.error?.message || 'Failed to search items');
    }
  };

  useEffect(() => {
    search('');
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const subtotalPreview = useMemo(
    () => cart.reduce((sum, line) => sum + line.price * line.quantity, 0),
    [cart],
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
    setTableNumber('');
  };

  const finalize = async () => {
    setSaving(true);
    setError('');
    try {
      const res = await createBill({
        table_number: tableNumber || null,
        discount: Number(discount || 0),
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
      <Typography variant="h5" gutterBottom>
        New Bill
      </Typography>

      {error ? <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert> : null}

      <Box
        sx={{
          display: 'grid',
          gap: 2,
          gridTemplateColumns: { xs: '1fr', md: '1.1fr 0.9fr' },
        }}
      >
        <Box sx={{ bgcolor: 'background.paper', borderRadius: 2, p: 2 }}>
          <TextField
            label="Search food item"
            value={q}
            onChange={(e) => setQ(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Enter') search();
            }}
            fullWidth
            autoFocus
            sx={{ mb: 2 }}
          />
          <Table size="small">
            <TableHead>
              <TableRow>
                <TableCell>Item</TableCell>
                <TableCell align="right">Price</TableCell>
                <TableCell align="right" />
              </TableRow>
            </TableHead>
            <TableBody>
              {catalog.map((item) => (
                <TableRow key={item.id} hover>
                  <TableCell>
                    <Typography fontWeight={600}>{item.name}</Typography>
                    <Typography variant="caption" color="text.secondary">
                      {item.category_name} · GST {Number(item.gst_percentage).toFixed(2)}%
                    </Typography>
                  </TableCell>
                  <TableCell align="right">₹{Number(item.price).toFixed(2)}</TableCell>
                  <TableCell align="right">
                    <Button size="small" variant="contained" onClick={() => addItem(item)}>
                      Add
                    </Button>
                  </TableCell>
                </TableRow>
              ))}
              {!catalog.length ? (
                <TableRow>
                  <TableCell colSpan={3}>
                    <Typography color="text.secondary">No active items found.</Typography>
                  </TableCell>
                </TableRow>
              ) : null}
            </TableBody>
          </Table>
        </Box>

        <Box sx={{ bgcolor: 'background.paper', borderRadius: 2, p: 2 }}>
          <Stack direction="row" justifyContent="space-between" alignItems="center" mb={2}>
            <Typography variant="h6">Current Bill</Typography>
            <Button color="inherit" onClick={clearCart} disabled={!cart.length}>
              Clear
            </Button>
          </Stack>

          <Stack direction="row" spacing={2} mb={2}>
            <TextField
              label="Table No."
              value={tableNumber}
              onChange={(e) => setTableNumber(e.target.value)}
              fullWidth
            />
            <TextField
              label="Discount ₹"
              type="number"
              value={discount}
              onChange={(e) => setDiscount(e.target.value)}
              fullWidth
              inputProps={{ min: 0, step: '0.01' }}
            />
          </Stack>

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
                    {line.name}
                    <Typography variant="caption" display="block" color="text.secondary">
                      ₹{line.price.toFixed(2)}
                    </Typography>
                  </TableCell>
                  <TableCell align="right" sx={{ width: 100 }}>
                    <TextField
                      type="number"
                      size="small"
                      value={line.quantity}
                      onChange={(e) => setQty(line.item_id, e.target.value)}
                      inputProps={{ min: 1, step: 1 }}
                    />
                  </TableCell>
                  <TableCell align="right">
                    ₹{(line.price * line.quantity).toFixed(2)}
                  </TableCell>
                  <TableCell align="right">
                    <IconButton size="small" onClick={() => removeLine(line.item_id)}>
                      <DeleteOutlinedIcon fontSize="small" />
                    </IconButton>
                  </TableCell>
                </TableRow>
              ))}
              {!cart.length ? (
                <TableRow>
                  <TableCell colSpan={4}>
                    <Typography color="text.secondary">Cart is empty.</Typography>
                  </TableCell>
                </TableRow>
              ) : null}
            </TableBody>
          </Table>

          <Stack spacing={1} mt={2}>
            <Typography>Subtotal (preview): ₹{subtotalPreview.toFixed(2)}</Typography>
            <Typography variant="caption" color="text.secondary">
              Final GST/total is calculated by the server on Generate Bill.
            </Typography>
            <Button
              variant="contained"
              size="large"
              disabled={!cart.length || saving}
              onClick={finalize}
            >
              Generate Bill
            </Button>
          </Stack>
        </Box>
      </Box>

      <Dialog open={Boolean(createdBill)} onClose={() => setCreatedBill(null)} fullWidth maxWidth="sm">
        <DialogTitle>Bill Generated</DialogTitle>
        <DialogContent>
          {createdBill ? (
            <Stack spacing={1} sx={{ mt: 1 }}>
              <Typography>Bill No: {createdBill.bill_number}</Typography>
              <Typography>Status: {createdBill.status}</Typography>
              <Typography>Subtotal: ₹{Number(createdBill.subtotal).toFixed(2)}</Typography>
              <Typography>Discount: ₹{Number(createdBill.discount).toFixed(2)}</Typography>
              <Typography>CGST: ₹{Number(createdBill.cgst_amount).toFixed(2)}</Typography>
              <Typography>SGST: ₹{Number(createdBill.sgst_amount).toFixed(2)}</Typography>
              <Typography fontWeight={700}>
                Grand Total: ₹{Number(createdBill.grand_total).toFixed(2)}
              </Typography>
            </Stack>
          ) : null}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setCreatedBill(null)}>Done</Button>
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