import AddOutlinedIcon from '@mui/icons-material/AddOutlined';
import WarehouseOutlinedIcon from '@mui/icons-material/WarehouseOutlined';
import DeleteOutlineOutlinedIcon from '@mui/icons-material/DeleteOutlineOutlined';
import {
  Alert,
  Autocomplete,
  Box,
  Button,
  Chip,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  FormControl,
  FormControlLabel,
  IconButton,
  InputLabel,
  MenuItem,
  Select,
  Stack,
  Switch,
  Tab,
  Tabs,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
  TextField,
  Typography,
} from '@mui/material';
import { useCallback, useEffect, useState } from 'react';
import EmptyState from '../../components/EmptyState';
import LoadingBlock from '../../components/LoadingBlock';
import PageShell from '../../components/PageShell';
import TableCard from '../../components/TableCard';
import { PageActions } from '../../context/PageActionsContext';
import { useAuth } from '../../context/AuthContext';
import { useModuleGate } from '../../context/ModulesContext';
import { listItems } from '../../services/itemService';
import {
  createStockTransfer,
  createWarehouse,
  listStockTransfers,
  listWarehouseStocks,
  listWarehouses,
  updateWarehouse,
} from '../../services/warehouseService';

export default function WarehousesPage() {
  const moduleEnabled = useModuleGate('warehouse');
  const { role } = useAuth();
  const canWrite = role === 'OWNER' || role === 'MANAGER';

  const [tab, setTab] = useState('warehouses');
  const [warehouses, setWarehouses] = useState([]);
  const [stocks, setStocks] = useState([]);
  const [transfers, setTransfers] = useState([]);
  const [catalog, setCatalog] = useState([]);
  const [stockFilterWh, setStockFilterWh] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const [whOpen, setWhOpen] = useState(false);
  const [code, setCode] = useState('');
  const [name, setName] = useState('');
  const [address, setAddress] = useState('');
  const [isDefault, setIsDefault] = useState(false);

  const [trOpen, setTrOpen] = useState(false);
  const [fromId, setFromId] = useState('');
  const [toId, setToId] = useState('');
  const [lines, setLines] = useState([{ item: null, quantity: '1' }]);
  const [saving, setSaving] = useState(false);

  const load = useCallback(async () => {
    if (!moduleEnabled) return;
    setLoading(true);
    setError('');
    try {
      const [wh, st, tr, items] = await Promise.all([
        listWarehouses(),
        listWarehouseStocks({ per_page: 100 }),
        listStockTransfers({ per_page: 50 }),
        listItems({ per_page: 200, is_active: true }),
      ]);
      setWarehouses(wh.data || []);
      setStocks(st.data || []);
      setTransfers(tr.data || []);
      setCatalog(items.data || []);
    } catch (err) {
      setError(err.response?.data?.error?.message || 'Failed to load warehouses');
    } finally {
      setLoading(false);
    }
  }, [moduleEnabled]);

  useEffect(() => {
    load();
  }, [load]);

  const onCreateWarehouse = async () => {
    if (!code.trim() || !name.trim()) {
      setError('Code and name are required.');
      return;
    }
    setSaving(true);
    setError('');
    try {
      await createWarehouse({
        code: code.trim(),
        name: name.trim(),
        address: address.trim() || null,
        is_default: isDefault,
      });
      setWhOpen(false);
      setSuccess('Warehouse created');
      await load();
    } catch (err) {
      setError(err.response?.data?.error?.message || 'Could not create warehouse');
    } finally {
      setSaving(false);
    }
  };

  const onMakeDefault = async (row) => {
    try {
      await updateWarehouse(row.id, { is_default: true });
      await load();
    } catch (err) {
      setError(err.response?.data?.error?.message || 'Could not update warehouse');
    }
  };

  const onTransfer = async () => {
    const payloadLines = lines
      .filter((line) => line.item?.id)
      .map((line) => ({ item_id: line.item.id, quantity: Number(line.quantity) }));
    if (!fromId || !toId || !payloadLines.length) {
      setError('Select warehouses and at least one item.');
      return;
    }
    setSaving(true);
    setError('');
    try {
      const res = await createStockTransfer({
        from_warehouse_id: fromId,
        to_warehouse_id: toId,
        items: payloadLines,
      });
      setTrOpen(false);
      setSuccess(`Transfer ${res.data?.transfer_number} completed`);
      setLines([{ item: null, quantity: '1' }]);
      await load();
    } catch (err) {
      setError(err.response?.data?.error?.message || 'Transfer failed');
    } finally {
      setSaving(false);
    }
  };

  const availableAtFrom = (itemId) => {
    if (!fromId || !itemId) return null;
    const row = stocks.find((s) => s.warehouse_id === fromId && s.item_id === itemId);
    return row ? Number(row.quantity) : 0;
  };

  const filteredStocks = stockFilterWh
    ? stocks.filter((row) => row.warehouse_id === stockFilterWh)
    : stocks;

  if (!moduleEnabled) {
    return (
      <PageShell>
        <EmptyState
          icon={<WarehouseOutlinedIcon />}
          title="Warehouses not enabled"
          description="Available for building material and wholesale tenants."
        />
      </PageShell>
    );
  }

  return (
    <PageShell>
      <PageActions>
        {canWrite ? (
          <Stack direction="row" spacing={1}>
            <Button
              variant="outlined"
              onClick={() => {
                setCode('');
                setName('');
                setAddress('');
                setIsDefault(false);
                setWhOpen(true);
              }}
              startIcon={<AddOutlinedIcon />}
            >
              Warehouse
            </Button>
            <Button
              variant="contained"
              onClick={() => {
                setFromId(warehouses.find((w) => w.is_default)?.id || warehouses[0]?.id || '');
                setToId('');
                setLines([{ item: null, quantity: '1' }]);
                setTrOpen(true);
              }}
            >
              Transfer stock
            </Button>
          </Stack>
        ) : null}
      </PageActions>

      {error ? <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert> : null}
      {success ? <Alert severity="success" sx={{ mb: 2 }}>{success}</Alert> : null}

      <Tabs value={tab} onChange={(_, v) => setTab(v)} sx={{ mb: 2 }}>
        <Tab value="warehouses" label="Locations" />
        <Tab value="stocks" label="Balances" />
        <Tab value="transfers" label="Transfers" />
      </Tabs>

      {loading ? (
        <LoadingBlock />
      ) : tab === 'warehouses' ? (
        <TableCard>
          <Table size="small">
            <TableHead>
              <TableRow>
                <TableCell>Code</TableCell>
                <TableCell>Name</TableCell>
                <TableCell>Default</TableCell>
                <TableCell>Status</TableCell>
                <TableCell align="right">Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {warehouses.map((row) => (
                <TableRow key={row.id} hover>
                  <TableCell>{row.code}</TableCell>
                  <TableCell>{row.name}</TableCell>
                  <TableCell>
                    {row.is_default ? <Chip size="small" color="primary" label="Default" /> : '—'}
                  </TableCell>
                  <TableCell>{row.is_active ? 'Active' : 'Inactive'}</TableCell>
                  <TableCell align="right">
                    {canWrite && !row.is_default ? (
                      <Button size="small" onClick={() => onMakeDefault(row)}>
                        Set default
                      </Button>
                    ) : null}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableCard>
      ) : tab === 'stocks' ? (
        <>
          <FormControl size="small" sx={{ mb: 2, minWidth: 220 }}>
            <InputLabel id="stock-wh-filter">Warehouse</InputLabel>
            <Select
              labelId="stock-wh-filter"
              label="Warehouse"
              value={stockFilterWh}
              onChange={(e) => setStockFilterWh(e.target.value)}
            >
              <MenuItem value="">All locations</MenuItem>
              {warehouses.map((w) => (
                <MenuItem key={w.id} value={w.id}>
                  {w.code} · {w.name}
                </MenuItem>
              ))}
            </Select>
          </FormControl>
          {filteredStocks.length === 0 ? (
            <EmptyState title="No warehouse balances" description="Purchase stock or seed the default warehouse." />
          ) : (
            <TableCard>
              <Table size="small">
                <TableHead>
                  <TableRow>
                    <TableCell>Warehouse</TableCell>
                    <TableCell>Item</TableCell>
                    <TableCell align="right">Qty</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {filteredStocks.map((row) => (
                    <TableRow key={row.id} hover>
                      <TableCell>
                        {row.warehouse_code} · {row.warehouse_name}
                      </TableCell>
                      <TableCell>{row.item_name}</TableCell>
                      <TableCell align="right">{row.quantity}</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableCard>
          )}
        </>
      ) : transfers.length === 0 ? (
        <EmptyState title="No transfers yet" description="Move stock between warehouses with Transfer stock." />
      ) : (
        <TableCard>
          <Table size="small">
            <TableHead>
              <TableRow>
                <TableCell>Number</TableCell>
                <TableCell>From</TableCell>
                <TableCell>To</TableCell>
                <TableCell>Lines</TableCell>
                <TableCell>When</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {transfers.map((row) => (
                <TableRow key={row.id} hover>
                  <TableCell>{row.transfer_number}</TableCell>
                  <TableCell>{row.from_warehouse_name}</TableCell>
                  <TableCell>{row.to_warehouse_name}</TableCell>
                  <TableCell>{(row.items || []).length}</TableCell>
                  <TableCell>
                    {row.created_at ? new Date(row.created_at).toLocaleString() : '—'}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableCard>
      )}

      <Dialog open={whOpen} onClose={() => !saving && setWhOpen(false)} fullWidth maxWidth="sm">
        <DialogTitle>New warehouse</DialogTitle>
        <DialogContent>
          <Stack spacing={2} sx={{ mt: 1 }}>
            <TextField label="Code" value={code} onChange={(e) => setCode(e.target.value)} fullWidth />
            <TextField label="Name" value={name} onChange={(e) => setName(e.target.value)} fullWidth />
            <TextField
              label="Address"
              value={address}
              onChange={(e) => setAddress(e.target.value)}
              fullWidth
              multiline
              minRows={2}
            />
            <FormControlLabel
              control={<Switch checked={isDefault} onChange={(e) => setIsDefault(e.target.checked)} />}
              label="Set as default (billing location)"
            />
          </Stack>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setWhOpen(false)} disabled={saving}>
            Cancel
          </Button>
          <Button variant="contained" onClick={onCreateWarehouse} disabled={saving}>
            Save
          </Button>
        </DialogActions>
      </Dialog>

      <Dialog open={trOpen} onClose={() => !saving && setTrOpen(false)} fullWidth maxWidth="md">
        <DialogTitle>Transfer stock</DialogTitle>
        <DialogContent>
          <Stack spacing={2} sx={{ mt: 1 }}>
            <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2}>
              <FormControl fullWidth>
                <InputLabel id="from-wh">From</InputLabel>
                <Select
                  labelId="from-wh"
                  label="From"
                  value={fromId}
                  onChange={(e) => setFromId(e.target.value)}
                >
                  {warehouses.map((w) => (
                    <MenuItem key={w.id} value={w.id}>
                      {w.code} · {w.name}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
              <FormControl fullWidth>
                <InputLabel id="to-wh">To</InputLabel>
                <Select labelId="to-wh" label="To" value={toId} onChange={(e) => setToId(e.target.value)}>
                  {warehouses
                    .filter((w) => w.id !== fromId)
                    .map((w) => (
                      <MenuItem key={w.id} value={w.id}>
                        {w.code} · {w.name}
                      </MenuItem>
                    ))}
                </Select>
              </FormControl>
            </Stack>
            {lines.map((line, index) => {
              const atFrom = line.item?.id != null ? availableAtFrom(line.item.id) : null;
              return (
              <Stack key={index} direction={{ xs: 'column', sm: 'row' }} spacing={1} alignItems="center">
                <Autocomplete
                  options={catalog}
                  getOptionLabel={(opt) => {
                    if (!opt) return '';
                    const avail = availableAtFrom(opt.id);
                    const loc =
                      fromId && avail != null ? ` · at from: ${avail}` : '';
                    return `${opt.name} (total ${opt.stock_quantity ?? '—'}${loc})`;
                  }}
                  value={line.item}
                  onChange={(_, value) => {
                    setLines((prev) =>
                      prev.map((row, i) => (i === index ? { ...row, item: value } : row)),
                    );
                  }}
                  sx={{ flex: 1, minWidth: 220 }}
                  renderInput={(params) => <TextField {...params} label="Item" />}
                />
                <TextField
                  label="Qty"
                  type="number"
                  value={line.quantity}
                  onChange={(e) => {
                    setLines((prev) =>
                      prev.map((row, i) =>
                        i === index ? { ...row, quantity: e.target.value } : row,
                      ),
                    );
                  }}
                  sx={{ width: 120 }}
                  helperText={atFrom != null ? `Available: ${atFrom}` : undefined}
                />
                <IconButton
                  onClick={() => setLines((prev) => prev.filter((_, i) => i !== index))}
                  disabled={lines.length === 1}
                >
                  <DeleteOutlineOutlinedIcon />
                </IconButton>
              </Stack>
              );
            })}
            <Box>
              <Button onClick={() => setLines((prev) => [...prev, { item: null, quantity: '1' }])}>
                Add line
              </Button>
            </Box>
            <Typography variant="caption" color="text.secondary">
              Item totals stay the same; only location balances move.
            </Typography>
          </Stack>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setTrOpen(false)} disabled={saving}>
            Cancel
          </Button>
          <Button variant="contained" onClick={onTransfer} disabled={saving}>
            Transfer
          </Button>
        </DialogActions>
      </Dialog>
    </PageShell>
  );
}
