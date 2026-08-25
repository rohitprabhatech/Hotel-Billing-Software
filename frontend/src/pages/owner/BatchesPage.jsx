import AddOutlinedIcon from '@mui/icons-material/AddOutlined';
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
import EmptyState from '../../components/EmptyState';
import FilterBar from '../../components/FilterBar';
import LoadingBlock from '../../components/LoadingBlock';
import PageShell from '../../components/PageShell';
import TableCard from '../../components/TableCard';
import TruncateText from '../../components/TruncateText';
import { PageActions } from '../../context/PageActionsContext';
import { useModuleGate } from '../../context/ModulesContext';
import { usePermissions } from '../../hooks/usePermissions';
import { adjustBatch, createBatch, fetchExpiryReport, listBatches } from '../../services/batchService';
import { listItems } from '../../services/itemService';
import { filterControlSx } from '../../layouts/shell';
function statusChip(status) {
  if (status === 'expired') return <Chip size="small" color="error" label="Expired" />;
  if (status === 'expiring') return <Chip size="small" color="warning" label="Expiring" />;
  return <Chip size="small" color="success" label="OK" />;
}

export default function BatchesPage() {
  const moduleEnabled = useModuleGate('batch_expiry');
  const { canStockItems } = usePermissions();

  const [tab, setTab] = useState('expiry');
  const [withinDays, setWithinDays] = useState('7');
  const [rows, setRows] = useState([]);
  const [expired, setExpired] = useState([]);
  const [expiring, setExpiring] = useState([]);
  const [summary, setSummary] = useState({ expired_count: 0, expiring_count: 0 });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const [receiveOpen, setReceiveOpen] = useState(false);
  const [catalog, setCatalog] = useState([]);
  const [selectedItem, setSelectedItem] = useState(null);
  const [quantity, setQuantity] = useState('1');
  const [expiryDate, setExpiryDate] = useState('');
  const [batchCode, setBatchCode] = useState('');
  const [reason, setReason] = useState('');
  const [saving, setSaving] = useState(false);

  const [adjustTarget, setAdjustTarget] = useState(null);
  const [adjustDelta, setAdjustDelta] = useState('');
  const [adjustReason, setAdjustReason] = useState('');

  const load = useCallback(async () => {
    setLoading(true);
    setError('');
    try {
      if (tab === 'expiry') {
        const res = await fetchExpiryReport({ within_days: Number(withinDays) || 7 });
        setExpired(res.data?.expired || []);
        setExpiring(res.data?.expiring || []);
        setSummary(res.data?.summary || { expired_count: 0, expiring_count: 0 });
        setRows([]);
      } else {
        const res = await listBatches({ per_page: 100 });
        setRows(res.data || []);
        setExpired([]);
        setExpiring([]);
      }
    } catch (err) {
      setError(err.response?.data?.error?.message || 'Failed to load batches');
    } finally {
      setLoading(false);
    }
  }, [tab, withinDays]);

  useEffect(() => {
    if (!moduleEnabled) return;
    load();
  }, [moduleEnabled, load]);

  const openReceive = async () => {
    setSelectedItem(null);
    setQuantity('1');
    setExpiryDate('');
    setBatchCode('');
    setReason('');
    setReceiveOpen(true);
    setError('');
    try {
      const res = await listItems({ is_active: true, per_page: 200 });
      setCatalog((res.data || []).filter((row) => row.tracks_batches));
    } catch {
      setCatalog([]);
    }
  };

  const submitReceive = async () => {
    if (!selectedItem) {
      setError('Select a batch-tracked item');
      return;
    }
    if (!expiryDate) {
      setError('Expiry date is required');
      return;
    }
    setSaving(true);
    setError('');
    setSuccess('');
    try {
      await createBatch({
        item_id: selectedItem.id,
        quantity: Number(quantity),
        expiry_date: expiryDate,
        batch_code: batchCode.trim() || null,
        reason: reason.trim() || null,
      });
      setSuccess(`Batch received for ${selectedItem.name}`);
      setReceiveOpen(false);
      await load();
    } catch (err) {
      setError(err.response?.data?.error?.message || 'Could not receive batch');
    } finally {
      setSaving(false);
    }
  };

  const submitAdjust = async () => {
    if (!adjustTarget) return;
    if (!adjustReason.trim()) {
      setError('Adjustment reason is required');
      return;
    }
    setSaving(true);
    setError('');
    try {
      await adjustBatch(adjustTarget.id, {
        delta: Number(adjustDelta),
        reason: adjustReason.trim(),
      });
      setSuccess('Batch adjusted');
      setAdjustTarget(null);
      await load();
    } catch (err) {
      setError(err.response?.data?.error?.message || 'Could not adjust batch');
    } finally {
      setSaving(false);
    }
  };

  if (!moduleEnabled) {
    return (
      <PageShell>
        <Alert severity="info">Batch / Expiry is not enabled for this business type.</Alert>
      </PageShell>
    );
  }

  const displayRows = tab === 'expiry' ? [...expired, ...expiring] : rows;

  return (
    <PageShell>
      <PageActions>
        {canStockItems ? (
          <Button startIcon={<AddOutlinedIcon />} variant="contained" onClick={openReceive}>
            Receive batch
          </Button>
        ) : null}
      </PageActions>

      <Stack spacing={2}>
        {error ? <Alert severity="error">{error}</Alert> : null}
        {success ? <Alert severity="success">{success}</Alert> : null}

        <FilterBar>
          <FormControl size="small" sx={filterControlSx}>
            <InputLabel id="batch-view-label">View</InputLabel>
            <Select
              labelId="batch-view-label"
              label="View"
              value={tab}
              onChange={(e) => setTab(e.target.value)}
            >
              <MenuItem value="expiry">Expiry report</MenuItem>
              <MenuItem value="all">All batches</MenuItem>
            </Select>
          </FormControl>
          {tab === 'expiry' ? (
            <TextField
              size="small"
              label="Within days"
              type="number"
              value={withinDays}
              onChange={(e) => setWithinDays(e.target.value)}
              sx={filterControlSx}
              inputProps={{ min: 1 }}
            />
          ) : null}
          <Button variant="outlined" onClick={load}>
            Refresh
          </Button>
        </FilterBar>

        {tab === 'expiry' ? (
          <Typography variant="body2" color="text.secondary">
            Expired: {summary.expired_count} · Expiring within {withinDays || 7} days:{' '}
            {summary.expiring_count}
          </Typography>
        ) : null}

        <TableCard>
          {loading ? (
            <LoadingBlock />
          ) : !displayRows.length ? (
            <EmptyState
              title="No batches found"
              description="Enable tracks batches on an item, then receive stock with an expiry date."
              actionLabel={canStockItems ? 'Receive batch' : undefined}
              onAction={canStockItems ? openReceive : undefined}
            />
          ) : (
            <Box sx={{ overflowX: 'auto' }}>
              <Table size="small">
                <TableHead>
                  <TableRow>
                    <TableCell>Item</TableCell>
                    <TableCell>Batch</TableCell>
                    <TableCell>Expiry</TableCell>
                    <TableCell>Status</TableCell>
                    <TableCell align="right">Qty</TableCell>
                    <TableCell width={120} />
                  </TableRow>
                </TableHead>
                <TableBody>
                  {displayRows.map((row) => (
                    <TableRow key={row.id} hover>
                      <TableCell>
                        <TruncateText value={row.item_name || row.item_id} maxWidth={180} />
                      </TableCell>
                      <TableCell>{row.batch_code || '—'}</TableCell>
                      <TableCell>{row.expiry_date || '—'}</TableCell>
                      <TableCell>{statusChip(row.status)}</TableCell>
                      <TableCell align="right">{row.quantity}</TableCell>
                      <TableCell>
                        {canStockItems ? (
                          <Button
                            size="small"
                            onClick={() => {
                              setAdjustTarget(row);
                              setAdjustDelta('');
                              setAdjustReason('');
                              setError('');
                            }}
                          >
                            Adjust
                          </Button>
                        ) : null}
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </Box>
          )}
        </TableCard>
      </Stack>

      <Dialog open={receiveOpen} onClose={() => setReceiveOpen(false)} fullWidth maxWidth="sm">
        <DialogTitle>Receive batch</DialogTitle>
        <DialogContent>
          <Stack spacing={2} sx={{ mt: 1 }}>
            <Autocomplete
              options={catalog}
              getOptionLabel={(opt) => opt?.name || ''}
              value={selectedItem}
              onChange={(_, value) => setSelectedItem(value)}
              renderInput={(params) => (
                <TextField
                  {...params}
                  label="Batch-tracked item"
                  helperText={
                    catalog.length
                      ? 'Only items with Tracks batches enabled'
                      : 'No batch-tracked items — enable on Items first'
                  }
                />
              )}
            />
                    {!catalog.length ? (
              <Typography variant="caption" color="text.secondary">
                Tip: edit an item on the Items page and enable Tracks batches first.
              </Typography>
            ) : null}
            <TextField
              label="Quantity"
              type="number"
              value={quantity}
              onChange={(e) => setQuantity(e.target.value)}
              inputProps={{ min: 0.001, step: 'any' }}
              fullWidth
            />
            <TextField
              label="Expiry date"
              type="date"
              value={expiryDate}
              onChange={(e) => setExpiryDate(e.target.value)}
              InputLabelProps={{ shrink: true }}
              fullWidth
              required
            />
            <TextField
              label="Batch code (optional)"
              value={batchCode}
              onChange={(e) => setBatchCode(e.target.value)}
              fullWidth
            />
            <TextField
              label="Reason (optional)"
              value={reason}
              onChange={(e) => setReason(e.target.value)}
              fullWidth
            />
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

      <Dialog open={Boolean(adjustTarget)} onClose={() => setAdjustTarget(null)} fullWidth maxWidth="xs">
        <DialogTitle>Adjust batch</DialogTitle>
        <DialogContent>
          <Stack spacing={2} sx={{ mt: 1 }}>
            <Typography variant="body2">
              {adjustTarget?.item_name} · {adjustTarget?.batch_code || adjustTarget?.id?.slice(0, 8)} · qty{' '}
              {adjustTarget?.quantity}
            </Typography>
            <TextField
              label="Delta (+/-)"
              type="number"
              value={adjustDelta}
              onChange={(e) => setAdjustDelta(e.target.value)}
              fullWidth
              autoFocus
            />
            <TextField
              label="Reason (required)"
              value={adjustReason}
              onChange={(e) => setAdjustReason(e.target.value)}
              fullWidth
              required
            />
          </Stack>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setAdjustTarget(null)} disabled={saving}>
            Cancel
          </Button>
          <Button variant="contained" onClick={submitAdjust} disabled={saving || !adjustDelta}>
            {saving ? 'Saving…' : 'Save'}
          </Button>
        </DialogActions>
      </Dialog>
    </PageShell>
  );
}
