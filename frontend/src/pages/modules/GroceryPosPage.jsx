import DeleteOutlineOutlinedIcon from '@mui/icons-material/DeleteOutlineOutlined';
import QrCodeScannerOutlinedIcon from '@mui/icons-material/QrCodeScannerOutlined';
import {
  Alert,
  Box,
  Button,
  Card,
  CardContent,
  Divider,
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
import { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import PageShell from '../../components/PageShell';
import TruncateText from '../../components/TruncateText';
import { useModuleGate } from '../../context/ModulesContext';
import { createBill } from '../../services/billService';
import { fetchGroceryPosCatalog } from '../../services/groceryService';
import { getItemByBarcode } from '../../services/itemService';
import { DEFAULT_PAYMENT_METHOD } from '../../utils/paymentMethod';
import { defaultScanQty, qtyStepForUom, uomLabel } from '../../utils/uom';

function money(value) {
  return `₹${Number(value || 0).toFixed(2)}`;
}

function lineTotal(line) {
  return Number(line.price || 0) * Number(line.quantity || 0);
}

export default function GroceryPosPage() {
  const moduleEnabled = useModuleGate('barcode_pos');
  const barcodeRef = useRef(null);
  const [barcode, setBarcode] = useState('');
  const [cart, setCart] = useState([]);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [scanning, setScanning] = useState(false);
  const [saving, setSaving] = useState(false);
  const [recentScans, setRecentScans] = useState([]);

  const focusScan = useCallback(() => {
    window.requestAnimationFrame(() => barcodeRef.current?.focus());
  }, []);

  useEffect(() => {
    if (!moduleEnabled) return;
    fetchGroceryPosCatalog({ limit: 50 })
      .then((res) => setRecentScans((res.data?.items || []).slice(0, 8)))
      .catch(() => {});
    focusScan();
  }, [moduleEnabled, focusScan]);

  const cartTotal = useMemo(() => cart.reduce((sum, line) => sum + lineTotal(line), 0), [cart]);
  const lineCount = useMemo(() => cart.reduce((sum, line) => sum + Number(line.quantity || 0), 0), [cart]);

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
          line.item_id === item.id ? { ...line, quantity: nextQty } : line,
        );
      }
      return [
        ...prev,
        {
          item_id: item.id,
          name: item.name,
          barcode: item.barcode,
          price: Number(item.price),
          gst_percentage: Number(item.gst_percentage || 0),
          quantity: Number(increment),
          uom,
          stock_quantity: available,
          stock_tracked: tracked,
        },
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
      return prev.map((row) => (row.item_id === itemId ? { ...row, quantity: parsed } : row));
    });
  };

  const checkout = async () => {
    if (!cart.length) {
      setError('Scan items to build the bill.');
      return;
    }
    setSaving(true);
    setError('');
    setSuccess('');
    try {
      const res = await createBill({
        payment_method: DEFAULT_PAYMENT_METHOD,
        items: cart.map((line) => ({
          item_id: line.item_id,
          quantity: line.quantity,
        })),
      });
      const bill = res.data;
      setSuccess(`Bill ${bill.bill_number} — ${money(bill.grand_total)}`);
      setCart([]);
      focusScan();
    } catch (err) {
      setError(err.response?.data?.error?.message || 'Could not create bill.');
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
        {error ? <Alert severity="error">{error}</Alert> : null}
        {success ? <Alert severity="success">{success}</Alert> : null}

        <Card variant="outlined" sx={{ borderWidth: 2, borderColor: 'primary.main' }}>
          <CardContent>
            <Stack direction={{ xs: 'column', md: 'row' }} spacing={2} alignItems={{ md: 'center' }}>
              <QrCodeScannerOutlinedIcon color="primary" sx={{ fontSize: 40, display: { xs: 'none', md: 'block' } }} />
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
                sx={{ '& .MuiInputBase-root': { fontSize: '1.15rem' } }}
              />
              <Button variant="contained" onClick={scanBarcode} disabled={scanning || !barcode.trim()} sx={{ minWidth: 120 }}>
                {scanning ? '…' : 'Add'}
              </Button>
            </Stack>
            {recentScans.length ? (
              <Stack direction="row" flexWrap="wrap" gap={1} sx={{ mt: 2 }}>
                <Typography variant="caption" color="text.secondary" sx={{ width: '100%' }}>
                  Quick pick
                </Typography>
                {recentScans.map((item) => (
                  <Button
                    key={item.id}
                    size="small"
                    variant="outlined"
                    onClick={() => addToCart(item)}
                  >
                    {item.name}
                  </Button>
                ))}
              </Stack>
            ) : null}
          </CardContent>
        </Card>

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
                Scan barcodes to add items. Weight items (kg/g/l) support decimal quantities.
              </Typography>
            ) : (
              <>
                <Box sx={{ overflowX: 'auto' }}>
                  <Table size="small">
                    <TableHead>
                      <TableRow>
                        <TableCell>Item</TableCell>
                        <TableCell>Barcode</TableCell>
                        <TableCell align="right">Qty</TableCell>
                        <TableCell>UoM</TableCell>
                        <TableCell align="right">Rate</TableCell>
                        <TableCell align="right">Amount</TableCell>
                        <TableCell width={48} />
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {cart.map((line) => (
                        <TableRow key={line.item_id} hover>
                          <TableCell>
                            <TruncateText value={line.name} maxWidth={180} />
                          </TableCell>
                          <TableCell>{line.barcode || '—'}</TableCell>
                          <TableCell align="right" sx={{ minWidth: 100 }}>
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
                              sx={{ width: 96 }}
                            />
                          </TableCell>
                          <TableCell>{uomLabel(line.uom)}</TableCell>
                          <TableCell align="right">{money(line.price)}</TableCell>
                          <TableCell align="right">{money(lineTotal(line))}</TableCell>
                          <TableCell>
                            <IconButton size="small" onClick={() => setLineQty(line.item_id, 0)}>
                              <DeleteOutlineOutlinedIcon fontSize="small" />
                            </IconButton>
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </Box>
                <Divider sx={{ my: 2 }} />
                <Stack direction="row" justifyContent="space-between" alignItems="center">
                  <Typography variant="h6">{money(cartTotal)}</Typography>
                  <Button variant="contained" size="large" onClick={checkout} disabled={saving}>
                    {saving ? 'Billing…' : 'Bill now (Cash)'}
                  </Button>
                </Stack>
              </>
            )}
          </CardContent>
        </Card>
      </Stack>
    </PageShell>
  );
}
