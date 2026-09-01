import AddOutlinedIcon from '@mui/icons-material/AddOutlined';
import {
  Alert,
  Autocomplete,
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  FormControl,
  InputLabel,
  MenuItem,
  Select,
  Stack,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
  TextField,
  Typography,
} from '@mui/material';
import { useCallback, useEffect, useState } from 'react';
import { useSearchParams } from 'react-router-dom';
import EmptyState from '../../components/EmptyState';
import FilterBar from '../../components/FilterBar';
import LoadingBlock from '../../components/LoadingBlock';
import PageShell from '../../components/PageShell';
import TableCard from '../../components/TableCard';
import TruncateText from '../../components/TruncateText';
import SearchInput from '../../components/ui/SearchInput';
import StatusBadge from '../../components/ui/StatusBadge';
import { PageActions } from '../../context/PageActionsContext';
import { useModuleGate } from '../../context/ModulesContext';
import { usePermissions } from '../../hooks/usePermissions';
import { filterControlSx } from '../../layouts/shell';
import { listItems } from '../../services/itemService';
import { listSerialUnits, receiveSerialUnit } from '../../services/serialService';

function statusBadge(status) {
  if (status === 'SOLD') return <StatusBadge label="Sold" variant="cancelled" />;
  if (status === 'QUARANTINE') return <StatusBadge label="Quarantine" variant="pending" />;
  return <StatusBadge label="In stock" variant="active" />;
}

export default function SerialUnitsPage() {
  const moduleEnabled = useModuleGate('serial_imei');
  const { canStockItems } = usePermissions();
  const [searchParams] = useSearchParams();
  const presetItemId = searchParams.get('item_id') || '';

  const [rows, setRows] = useState([]);
  const [status, setStatus] = useState('');
  const [q, setQ] = useState('');
  const [itemId, setItemId] = useState(presetItemId);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const [receiveOpen, setReceiveOpen] = useState(false);
  const [catalog, setCatalog] = useState([]);
  const [selectedItem, setSelectedItem] = useState(null);
  const [serial, setSerial] = useState('');
  const [warrantyMonths, setWarrantyMonths] = useState('');
  const [saving, setSaving] = useState(false);

  const load = useCallback(async () => {
    setLoading(true);
    setError('');
    try {
      const res = await listSerialUnits({
        per_page: 100,
        status: status || undefined,
        q: q || undefined,
        item_id: itemId || undefined,
      });
      setRows(res.data || []);
    } catch (err) {
      setError(err.response?.data?.error?.message || 'Failed to load serial units');
    } finally {
      setLoading(false);
    }
  }, [status, q, itemId]);

  useEffect(() => {
    if (!moduleEnabled) return;
    load();
  }, [moduleEnabled, load]);

  const openReceive = async () => {
    setSelectedItem(null);
    setSerial('');
    setWarrantyMonths('');
    setReceiveOpen(true);
    setError('');
    try {
      const res = await listItems({ is_active: true, per_page: 200 });
      const items = res.data || [];
      setCatalog(items.filter((row) => !row.tracks_variants));
      if (itemId) {
        setSelectedItem(items.find((row) => row.id === itemId) || null);
      }
    } catch {
      setCatalog([]);
    }
  };

  const submitReceive = async () => {
    if (!selectedItem) {
      setError('Select an item');
      return;
    }
    if (!serial.trim()) {
      setError('Enter a serial / IMEI');
      return;
    }
    setSaving(true);
    setError('');
    setSuccess('');
    try {
      await receiveSerialUnit({
        item_id: selectedItem.id,
        serial: serial.trim(),
        warranty_months: warrantyMonths === '' ? null : Number(warrantyMonths),
      });
      setSuccess(`Received ${serial.trim().toUpperCase()} for ${selectedItem.name}.`);
      setReceiveOpen(false);
      await load();
    } catch (err) {
      setError(err.response?.data?.error?.message || 'Could not receive serial / IMEI');
    } finally {
      setSaving(false);
    }
  };

  if (!moduleEnabled) {
    return (
      <PageShell>
        <EmptyState
          title="Serial / IMEI stock is not enabled"
          description="Switch the business type to Mobile or Electronics to receive and sell serialized units."
        />
      </PageShell>
    );
  }

  return (
    <PageShell>
      <PageActions>
        {canStockItems ? (
          <Button variant="contained" startIcon={<AddOutlinedIcon />} onClick={openReceive}>
            Receive IMEI
          </Button>
        ) : null}
      </PageActions>
      {error ? (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError('')}>
          {error}
        </Alert>
      ) : null}
      {success ? (
        <Alert severity="success" sx={{ mb: 2 }} onClose={() => setSuccess('')}>
          {success}
        </Alert>
      ) : null}
      <FilterBar>
        <SearchInput
          placeholder="Search IMEI…"
          value={q}
          onChange={(e) => setQ(e.target.value)}
          sx={filterControlSx}
        />
        <FormControl size="small" sx={filterControlSx}>
          <InputLabel id="serial-status-label">Status</InputLabel>
          <Select
            labelId="serial-status-label"
            label="Status"
            value={status}
            onChange={(e) => setStatus(e.target.value)}
          >
            <MenuItem value="">All</MenuItem>
            <MenuItem value="IN_STOCK">In stock</MenuItem>
            <MenuItem value="SOLD">Sold</MenuItem>
          </Select>
        </FormControl>
      </FilterBar>
      {loading ? (
        <LoadingBlock />
      ) : rows.length === 0 ? (
        <EmptyState
          title="No serial units yet"
          description="Receive an IMEI or serial number against a phone or electronics item, then sell that exact unit on New Bill."
        />
      ) : (
        <TableCard>
          <Table size="small">
            <TableHead>
              <TableRow>
                <TableCell>Serial / IMEI</TableCell>
                <TableCell>Item</TableCell>
                <TableCell>Status</TableCell>
                <TableCell>Received</TableCell>
                <TableCell>Sold</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {rows.map((row) => (
                <TableRow key={row.id}>
                  <TableCell>
                    <Typography fontFamily="monospace" fontWeight={650}>
                      {row.serial}
                    </Typography>
                  </TableCell>
                  <TableCell>
                    <TruncateText value={row.item_name || '—'} maxWidth={220} />
                  </TableCell>
                  <TableCell>{statusBadge(row.status)}</TableCell>
                  <TableCell>{row.received_at ? row.received_at.slice(0, 10) : '—'}</TableCell>
                  <TableCell>{row.sold_at ? row.sold_at.slice(0, 10) : '—'}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableCard>
      )}

      <Dialog open={receiveOpen} onClose={() => (!saving ? setReceiveOpen(false) : null)} fullWidth maxWidth="sm">
        <DialogTitle>Receive serial / IMEI</DialogTitle>
        <DialogContent>
          <Stack spacing={2} sx={{ mt: 1 }}>
            <Autocomplete
              options={catalog}
              getOptionLabel={(option) => option.name || ''}
              value={selectedItem}
              onChange={(_, value) => setSelectedItem(value)}
              renderInput={(params) => <TextField {...params} label="Item" />}
            />
            <TextField
              label="Serial / IMEI"
              value={serial}
              onChange={(e) => setSerial(e.target.value)}
              autoFocus
              inputProps={{ style: { textTransform: 'uppercase' } }}
            />
            <TextField
              label="Warranty override (months, optional)"
              type="number"
              value={warrantyMonths}
              onChange={(e) => setWarrantyMonths(e.target.value)}
              inputProps={{ min: 0, max: 120, step: 1 }}
              helperText="Uses item default when blank"
            />
            <Typography variant="caption" color="text.secondary">
              Letters and digits only. Duplicate IMEIs are blocked for this business.
            </Typography>
          </Stack>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setReceiveOpen(false)} disabled={saving}>
            Cancel
          </Button>
          <Button variant="contained" onClick={submitReceive} disabled={saving}>
            {saving ? 'Saving…' : 'Receive'}
          </Button>
        </DialogActions>
      </Dialog>
    </PageShell>
  );
}
