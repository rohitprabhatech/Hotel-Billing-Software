import AddOutlinedIcon from '@mui/icons-material/AddOutlined';
import {
  Alert,
  Autocomplete,
  Box,
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
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
import PaginationBar from '../../components/PaginationBar';
import TableCard from '../../components/TableCard';
import TruncateText from '../../components/TruncateText';
import { PageActions } from '../../context/PageActionsContext';
import { useModuleGate } from '../../context/ModulesContext';
import { usePermissions } from '../../hooks/usePermissions';
import { filterControlWideSx } from '../../layouts/shell';
import { listItems } from '../../services/itemService';
import { createWastage, listWastage } from '../../services/wastageService';

const PAGE_SIZE = 25;
const CATEGORY_SUGGESTIONS = ['Spoilage', 'Prep loss', 'Expired', 'Breakage', 'Sample / tasting'];

export default function WastagePage() {
  const moduleEnabled = useModuleGate('wastage');
  const { hasPermission } = usePermissions();
  const canWrite = hasPermission('wastage.write');

  const [rows, setRows] = useState([]);
  const [meta, setMeta] = useState({ page: 1, total: 0, per_page: PAGE_SIZE });
  const [fromDate, setFromDate] = useState('');
  const [toDate, setToDate] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [dialogOpen, setDialogOpen] = useState(false);
  const [catalog, setCatalog] = useState([]);
  const [selectedItem, setSelectedItem] = useState(null);
  const [quantity, setQuantity] = useState('1');
  const [category, setCategory] = useState('');
  const [reason, setReason] = useState('');
  const [wastageDate, setWastageDate] = useState('');
  const [saving, setSaving] = useState(false);

  const load = useCallback(async (page = 1) => {
    setLoading(true);
    setError('');
    try {
      const params = { page, per_page: PAGE_SIZE };
      if (fromDate) params.from = fromDate;
      if (toDate) params.to = toDate;
      const res = await listWastage(params);
      setRows(res.data || []);
      setMeta(res.meta || { page: 1, total: 0, per_page: PAGE_SIZE });
    } catch (err) {
      setError(err.response?.data?.error?.message || 'Failed to load wastage entries');
    } finally {
      setLoading(false);
    }
  }, [fromDate, toDate]);

  useEffect(() => {
    if (!moduleEnabled) return;
    load(1);
  }, [moduleEnabled, load]);

  const openDialog = () => {
    setSelectedItem(null);
    setQuantity('1');
    setCategory('');
    setReason('');
    setWastageDate('');
    setDialogOpen(true);
    listItems({ is_active: true, per_page: 200, stock_status: 'tracked' })
      .then((res) => setCatalog(res.data || []))
      .catch(() => setCatalog([]));
  };

  const submit = async () => {
    if (!selectedItem) {
      setError('Select an item');
      return;
    }
    setSaving(true);
    setError('');
    try {
      await createWastage({
        item_id: selectedItem.id,
        quantity,
        category: category || undefined,
        reason: reason || undefined,
        wastage_date: wastageDate || undefined,
      });
      setDialogOpen(false);
      await load(meta.page || 1);
    } catch (err) {
      setError(err.response?.data?.error?.message || 'Failed to record wastage');
    } finally {
      setSaving(false);
    }
  };

  if (!moduleEnabled) {
    return (
      <PageShell>
        <Alert severity="info">Wastage tracking is not enabled for this business type.</Alert>
      </PageShell>
    );
  }

  return (
    <>
      {canWrite ? (
        <PageActions>
          <Button variant="contained" startIcon={<AddOutlinedIcon />} onClick={openDialog}>
            Log wastage
          </Button>
        </PageActions>
      ) : null}

      <PageShell>
        <FilterBar
          actions={
            <Button variant="outlined" onClick={() => load(1)}>
              Apply
            </Button>
          }
        >
          <TextField
            label="From"
            type="date"
            value={fromDate}
            onChange={(e) => setFromDate(e.target.value)}
            InputLabelProps={{ shrink: true }}
            sx={filterControlWideSx}
          />
          <TextField
            label="To"
            type="date"
            value={toDate}
            onChange={(e) => setToDate(e.target.value)}
            InputLabelProps={{ shrink: true }}
            sx={filterControlWideSx}
          />
        </FilterBar>

        {error ? <Alert severity="error">{error}</Alert> : null}
        {loading ? <LoadingBlock /> : null}

        {!loading ? (
          <TableCard>
            <Table size="small">
              <TableHead>
                <TableRow>
                  <TableCell>Date</TableCell>
                  <TableCell>Item</TableCell>
                  <TableCell align="right">Qty</TableCell>
                  <TableCell>Category</TableCell>
                  <TableCell>Reason</TableCell>
                  <TableCell>Logged by</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {rows.map((row) => (
                  <TableRow key={row.id} hover>
                    <TableCell>{row.wastage_date}</TableCell>
                    <TableCell>
                      <TruncateText value={row.item_name} maxWidth={220} />
                    </TableCell>
                    <TableCell align="right">{row.quantity}</TableCell>
                    <TableCell>{row.category || '—'}</TableCell>
                    <TableCell>
                      <TruncateText value={row.reason || '—'} maxWidth={240} />
                    </TableCell>
                    <TableCell>{row.created_by_name || '—'}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
            {!rows.length ? (
              <EmptyState
                title="No wastage logged"
                description="Record ingredient or stock losses to keep inventory accurate."
              />
            ) : null}
            <PaginationBar
              page={meta.page}
              total={meta.total}
              pageSize={meta.per_page}
              onPageChange={(page) => load(page)}
            />
          </TableCard>
        ) : null}
      </PageShell>

      <Dialog open={dialogOpen} onClose={() => setDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Log food wastage</DialogTitle>
        <DialogContent dividers>
          <Stack spacing={2} sx={{ pt: 1 }}>
            <Autocomplete
              options={catalog}
              getOptionLabel={(option) => option.name}
              value={selectedItem}
              onChange={(_, value) => setSelectedItem(value)}
              renderInput={(params) => (
                <TextField {...params} label="Stock-tracked item" required />
              )}
            />
            <TextField
              label="Quantity"
              type="number"
              value={quantity}
              onChange={(e) => setQuantity(e.target.value)}
              inputProps={{ min: 0.001, step: 0.001 }}
              required
            />
            <Autocomplete
              freeSolo
              options={CATEGORY_SUGGESTIONS}
              value={category}
              onChange={(_, value) => setCategory(value || '')}
              onInputChange={(_, value) => setCategory(value)}
              renderInput={(params) => <TextField {...params} label="Category" />}
            />
            <TextField
              label="Reason"
              value={reason}
              onChange={(e) => setReason(e.target.value)}
              multiline
              minRows={2}
            />
            <TextField
              label="Wastage date"
              type="date"
              value={wastageDate}
              onChange={(e) => setWastageDate(e.target.value)}
              InputLabelProps={{ shrink: true }}
              helperText="Leave empty for today"
            />
          </Stack>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDialogOpen(false)}>Cancel</Button>
          <Button variant="contained" onClick={submit} disabled={saving}>
            {saving ? 'Saving…' : 'Save'}
          </Button>
        </DialogActions>
      </Dialog>
    </>
  );
}
