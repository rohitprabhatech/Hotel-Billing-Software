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
import { getRecipe, listRecipes } from '../../services/recipeService';
import { createProduction, listProductions } from '../../services/productionService';

const PAGE_SIZE = 25;

export default function ProductionPage() {
  const moduleEnabled = useModuleGate('production');
  const { hasPermission } = usePermissions();
  const canWrite = hasPermission('production.write');

  const [rows, setRows] = useState([]);
  const [meta, setMeta] = useState({ page: 1, total: 0, per_page: PAGE_SIZE });
  const [fromDate, setFromDate] = useState('');
  const [toDate, setToDate] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [dialogOpen, setDialogOpen] = useState(false);
  const [recipes, setRecipes] = useState([]);
  const [selectedRecipe, setSelectedRecipe] = useState(null);
  const [quantity, setQuantity] = useState('1');
  const [notes, setNotes] = useState('');
  const [runDate, setRunDate] = useState('');
  const [expiryDate, setExpiryDate] = useState('');
  const [batchCode, setBatchCode] = useState('');
  const [saving, setSaving] = useState(false);

  const load = useCallback(async (page = 1) => {
    setLoading(true);
    setError('');
    try {
      const params = { page, per_page: PAGE_SIZE };
      if (fromDate) params.from = fromDate;
      if (toDate) params.to = toDate;
      const res = await listProductions(params);
      setRows(res.data || []);
      setMeta(res.meta || { page: 1, total: 0, per_page: PAGE_SIZE });
    } catch (err) {
      setError(err.response?.data?.error?.message || 'Failed to load production runs');
    } finally {
      setLoading(false);
    }
  }, [fromDate, toDate]);

  useEffect(() => {
    if (!moduleEnabled) return;
    load(1);
  }, [moduleEnabled, load]);

  const openDialog = () => {
    setSelectedRecipe(null);
    setQuantity('1');
    setNotes('');
    setRunDate('');
    setExpiryDate('');
    setBatchCode('');
    setDialogOpen(true);
    listRecipes({ is_active: true, per_page: 200 })
      .then((res) => setRecipes(res.data || []))
      .catch(() => setRecipes([]));
  };

  const submit = async () => {
    if (!selectedRecipe) {
      setError('Select a recipe');
      return;
    }
    setSaving(true);
    setError('');
    try {
      await createProduction({
        recipe_id: selectedRecipe.id,
        quantity,
        notes: notes || undefined,
        run_date: runDate || undefined,
        expiry_date: expiryDate || undefined,
        batch_code: batchCode || undefined,
      });
      setDialogOpen(false);
      load(1);
    } catch (err) {
      setError(err.response?.data?.error?.message || 'Failed to record production');
    } finally {
      setSaving(false);
    }
  };

  if (!moduleEnabled) {
    return (
      <PageShell>
        <Alert severity="info">Production is not enabled for this business type.</Alert>
      </PageShell>
    );
  }

  return (
    <PageShell>
      <PageActions>
        {canWrite ? (
          <Button variant="contained" startIcon={<AddOutlinedIcon />} onClick={openDialog}>
            New production
          </Button>
        ) : null}
      </PageActions>

      {error ? (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError('')}>
          {error}
        </Alert>
      ) : null}

      <FilterBar>
        <TextField
          label="From"
          type="date"
          size="small"
          value={fromDate}
          onChange={(e) => setFromDate(e.target.value)}
          InputLabelProps={{ shrink: true }}
          sx={filterControlWideSx}
        />
        <TextField
          label="To"
          type="date"
          size="small"
          value={toDate}
          onChange={(e) => setToDate(e.target.value)}
          InputLabelProps={{ shrink: true }}
          sx={filterControlWideSx}
        />
        <Button variant="outlined" onClick={() => load(1)}>
          Apply
        </Button>
      </FilterBar>

      {loading ? (
        <LoadingBlock />
      ) : rows.length === 0 ? (
        <EmptyState
          title="No production runs"
          description="Record a bake using a recipe — ingredients deduct and finished goods stock increases."
        />
      ) : (
        <TableCard>
          <Table size="small">
            <TableHead>
              <TableRow>
                <TableCell>Run</TableCell>
                <TableCell>Date</TableCell>
                <TableCell>Finished goods</TableCell>
                <TableCell align="right">Qty</TableCell>
                <TableCell>Ingredients</TableCell>
                <TableCell>Notes</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {rows.map((row) => (
                <TableRow key={row.id} hover>
                  <TableCell>{row.run_number}</TableCell>
                  <TableCell>{row.run_date}</TableCell>
                  <TableCell>
                    <TruncateText text={row.finished_item_name} />
                  </TableCell>
                  <TableCell align="right">{row.quantity}</TableCell>
                  <TableCell>
                    <Typography variant="body2" color="text.secondary">
                      {(row.items || [])
                        .map((line) => `${line.item_name} (−${line.quantity})`)
                        .join(', ') || '—'}
                    </Typography>
                  </TableCell>
                  <TableCell>
                    <TruncateText text={row.notes || '—'} />
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
          <PaginationBar
            page={meta.page}
            total={meta.total}
            perPage={meta.per_page}
            onChange={(p) => load(p)}
          />
        </TableCard>
      )}

      <Dialog open={dialogOpen} onClose={() => !saving && setDialogOpen(false)} fullWidth maxWidth="sm">
        <DialogTitle>New production run</DialogTitle>
        <DialogContent>
          <Stack spacing={2} sx={{ mt: 1 }}>
            <Autocomplete
              options={recipes}
              getOptionLabel={(opt) =>
                opt.name
                  ? `${opt.name} → ${opt.menu_item_name || opt.menu_item_id}`
                  : opt.menu_item_name || opt.menu_item_id || opt.id
              }
              value={selectedRecipe}
              onChange={async (_, value) => {
                if (!value) {
                  setSelectedRecipe(null);
                  return;
                }
                try {
                  const res = await getRecipe(value.id);
                  setSelectedRecipe(res.data || value);
                } catch {
                  setSelectedRecipe(value);
                }
              }}
              renderInput={(params) => <TextField {...params} label="Recipe" required />}
            />
            {selectedRecipe ? (
              <Box>
                <Typography variant="caption" color="text.secondary">
                  Yield {selectedRecipe.yield_quantity} · Ingredients:{' '}
                  {(selectedRecipe.ingredients || [])
                    .map((line) => `${line.ingredient_name} (${line.quantity})`)
                    .join(', ') || 'none'}
                </Typography>
              </Box>
            ) : null}
            <TextField
              label="Quantity produced"
              type="number"
              value={quantity}
              onChange={(e) => setQuantity(e.target.value)}
              required
              inputProps={{ min: 0, step: 'any' }}
            />
            <TextField
              label="Run date"
              type="date"
              value={runDate}
              onChange={(e) => setRunDate(e.target.value)}
              InputLabelProps={{ shrink: true }}
            />
            <TextField
              label="FG expiry date"
              type="date"
              value={expiryDate}
              onChange={(e) => setExpiryDate(e.target.value)}
              InputLabelProps={{ shrink: true }}
              helperText="Required when finished goods uses batch / expiry tracking"
            />
            <TextField
              label="Batch code (optional)"
              value={batchCode}
              onChange={(e) => setBatchCode(e.target.value)}
              helperText="Defaults to the production run number"
            />
            <TextField
              label="Notes"
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              multiline
              minRows={2}
            />
          </Stack>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDialogOpen(false)} disabled={saving}>
            Cancel
          </Button>
          <Button variant="contained" onClick={submit} disabled={saving || !selectedRecipe}>
            {saving ? 'Saving…' : 'Record production'}
          </Button>
        </DialogActions>
      </Dialog>
    </PageShell>
  );
}
