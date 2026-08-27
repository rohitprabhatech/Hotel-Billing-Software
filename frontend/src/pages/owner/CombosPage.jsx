import AddOutlinedIcon from '@mui/icons-material/AddOutlined';
import DeleteOutlinedIcon from '@mui/icons-material/DeleteOutlined';
import {
  Alert,
  Autocomplete,
  Box,
  Button,
  Checkbox,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  FormControlLabel,
  IconButton,
  Stack,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
  TextField,
  Tooltip,
  Typography,
} from '@mui/material';
import { useCallback, useEffect, useMemo, useState } from 'react';
import EmptyState from '../../components/EmptyState';
import LoadingBlock from '../../components/LoadingBlock';
import PageShell from '../../components/PageShell';
import TableCard from '../../components/TableCard';
import { PageActions } from '../../context/PageActionsContext';
import { useModuleGate } from '../../context/ModulesContext';
import { usePermissions } from '../../hooks/usePermissions';
import { createCombo, deleteCombo, listCombos } from '../../services/cafeService';
import { listItems } from '../../services/itemService';

const emptyLine = () => ({ item_id: '', quantity: '1' });

function money(value) {
  return `₹${Number(value || 0).toFixed(2)}`;
}

export default function CombosPage() {
  const moduleEnabled = useModuleGate('addons_combos');
  const { canManageAddons } = usePermissions();
  const [combos, setCombos] = useState([]);
  const [menuItems, setMenuItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [open, setOpen] = useState(false);
  const [saving, setSaving] = useState(false);
  const [form, setForm] = useState({
    name: '',
    description: '',
    combo_price: '',
    is_popular: false,
    items: [emptyLine()],
  });

  const dishOptions = useMemo(
    () => menuItems.filter((item) => item.is_active && item.is_menu),
    [menuItems],
  );

  const load = useCallback(async () => {
    if (!moduleEnabled) return;
    setLoading(true);
    setError('');
    try {
      const [comboRes, itemRes] = await Promise.all([
        listCombos(),
        listItems({ per_page: 500 }),
      ]);
      setCombos(comboRes.data || []);
      setMenuItems(itemRes.data || []);
    } catch (err) {
      setError(err.response?.data?.error?.message || 'Unable to load combos.');
    } finally {
      setLoading(false);
    }
  }, [moduleEnabled]);

  useEffect(() => {
    load();
  }, [load]);

  const resetForm = () => {
    setForm({
      name: '',
      description: '',
      combo_price: '',
      is_popular: false,
      items: [emptyLine()],
    });
  };

  const openCreate = () => {
    resetForm();
    setOpen(true);
  };

  const catalogEstimate = useMemo(() => {
    return form.items.reduce((sum, line) => {
      const item = dishOptions.find((row) => row.id === line.item_id);
      if (!item) return sum;
      return sum + Number(item.price || 0) * Number(line.quantity || 0);
    }, 0);
  }, [form.items, dishOptions]);

  const onSave = async () => {
    if (!form.name.trim()) {
      setError('Combo name is required.');
      return;
    }
    if (form.combo_price === '' || Number(form.combo_price) < 0) {
      setError('Enter a valid combo price.');
      return;
    }
    const itemsPayload = form.items
      .filter((line) => line.item_id && line.quantity)
      .map((line) => ({
        item_id: line.item_id,
        quantity: Number(line.quantity),
      }));
    if (!itemsPayload.length) {
      setError('Add at least one menu item to the combo.');
      return;
    }
    setSaving(true);
    setError('');
    setSuccess('');
    try {
      await createCombo({
        name: form.name.trim(),
        description: form.description.trim() || null,
        combo_price: Number(form.combo_price),
        is_popular: Boolean(form.is_popular),
        items: itemsPayload,
      });
      setSuccess('Combo created.');
      setOpen(false);
      resetForm();
      await load();
    } catch (err) {
      setError(err.response?.data?.error?.message || 'Unable to save combo.');
    } finally {
      setSaving(false);
    }
  };

  const onDelete = async (id) => {
    if (!window.confirm('Delete this combo?')) return;
    setError('');
    try {
      await deleteCombo(id);
      setSuccess('Combo deleted.');
      await load();
    } catch (err) {
      setError(err.response?.data?.error?.message || 'Unable to delete combo.');
    }
  };

  if (!moduleEnabled) {
    return (
      <PageShell>
        <Alert severity="warning">Add-ons &amp; Combos module is not enabled for this business type.</Alert>
      </PageShell>
    );
  }

  return (
    <>
      {canManageAddons ? (
        <PageActions>
          <Button variant="contained" startIcon={<AddOutlinedIcon />} onClick={openCreate}>
            New combo
          </Button>
        </PageActions>
      ) : null}

      <PageShell>
        <Stack spacing={2}>
          <Typography variant="body2" color="text.secondary">
            Bundle menu items at a fixed combo price. Popular combos surface first on Cafe POS.
          </Typography>
          {error ? <Alert severity="error">{error}</Alert> : null}
          {success ? <Alert severity="success">{success}</Alert> : null}
          <TableCard>
            {loading ? (
              <LoadingBlock />
            ) : combos.length === 0 ? (
              <EmptyState
                title="No combos yet"
                description="Create a combo with two or more menu items and a package price."
                actionLabel={canManageAddons ? 'New combo' : undefined}
                onAction={canManageAddons ? openCreate : undefined}
              />
            ) : (
              <Table size="small">
                <TableHead>
                  <TableRow>
                    <TableCell>Name</TableCell>
                    <TableCell>Items</TableCell>
                    <TableCell align="right">Catalog</TableCell>
                    <TableCell align="right">Combo price</TableCell>
                    <TableCell align="right">Savings</TableCell>
                    <TableCell>Popular</TableCell>
                    {canManageAddons ? <TableCell align="right">Actions</TableCell> : null}
                  </TableRow>
                </TableHead>
                <TableBody>
                  {combos.map((combo) => (
                    <TableRow key={combo.id}>
                      <TableCell>
                        <Typography variant="body2">{combo.name}</Typography>
                        {combo.description ? (
                          <Typography variant="caption" color="text.secondary">
                            {combo.description}
                          </Typography>
                        ) : null}
                      </TableCell>
                      <TableCell>
                        {(combo.items || [])
                          .map((row) => `${row.item_name} ×${row.quantity}`)
                          .join(', ') || '—'}
                      </TableCell>
                      <TableCell align="right">{money(combo.catalog_total)}</TableCell>
                      <TableCell align="right">{money(combo.combo_price)}</TableCell>
                      <TableCell align="right">{money(combo.savings)}</TableCell>
                      <TableCell>{combo.is_popular ? 'Yes' : '—'}</TableCell>
                      {canManageAddons ? (
                        <TableCell align="right">
                          <Tooltip title="Delete combo">
                            <IconButton
                              size="small"
                              color="error"
                              aria-label={`Delete ${combo.name}`}
                              onClick={() => onDelete(combo.id)}
                            >
                              <DeleteOutlinedIcon fontSize="small" />
                            </IconButton>
                          </Tooltip>
                        </TableCell>
                      ) : null}
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            )}
          </TableCard>
        </Stack>
      </PageShell>

      <Dialog
        open={open}
        onClose={() => {
          setOpen(false);
          resetForm();
        }}
        fullWidth
        maxWidth="md"
      >
        <DialogTitle>New combo</DialogTitle>
        <DialogContent>
          <Stack spacing={2} sx={{ mt: 1 }}>
            {!dishOptions.length ? (
              <Alert severity="warning">
                No menu items found. Create items with &quot;Menu dish&quot; enabled first.
              </Alert>
            ) : null}
            <TextField
              label="Combo name"
              value={form.name}
              onChange={(e) => setForm((prev) => ({ ...prev, name: e.target.value }))}
              fullWidth
              required
            />
            <TextField
              label="Description (optional)"
              value={form.description}
              onChange={(e) => setForm((prev) => ({ ...prev, description: e.target.value }))}
              fullWidth
              multiline
              minRows={2}
            />
            <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2} alignItems="center">
              <TextField
                label="Combo price ₹"
                type="number"
                value={form.combo_price}
                onChange={(e) => setForm((prev) => ({ ...prev, combo_price: e.target.value }))}
                inputProps={{ min: 0, step: '0.01' }}
                required
                sx={{ minWidth: 180 }}
              />
              <FormControlLabel
                control={
                  <Checkbox
                    checked={form.is_popular}
                    onChange={(e) => setForm((prev) => ({ ...prev, is_popular: e.target.checked }))}
                  />
                }
                label="Mark as popular"
              />
              <Typography variant="body2" color="text.secondary">
                Catalog estimate: {money(catalogEstimate)}
              </Typography>
            </Stack>
            <Typography variant="subtitle2">Included items</Typography>
            {form.items.map((line, index) => (
              <Stack key={index} direction={{ xs: 'column', sm: 'row' }} spacing={1} alignItems="center">
                <Autocomplete
                  sx={{ flex: 2 }}
                  options={dishOptions}
                  getOptionLabel={(option) => `${option.name} (${money(option.price)})`}
                  value={dishOptions.find((item) => item.id === line.item_id) || null}
                  onChange={(_, value) =>
                    setForm((prev) => ({
                      ...prev,
                      items: prev.items.map((row, i) =>
                        i === index ? { ...row, item_id: value?.id || '' } : row,
                      ),
                    }))
                  }
                  renderInput={(params) => <TextField {...params} label="Menu item" />}
                />
                <TextField
                  sx={{ flex: 1 }}
                  label="Qty"
                  type="number"
                  value={line.quantity}
                  onChange={(e) =>
                    setForm((prev) => ({
                      ...prev,
                      items: prev.items.map((row, i) =>
                        i === index ? { ...row, quantity: e.target.value } : row,
                      ),
                    }))
                  }
                  inputProps={{ min: 0.001, step: '0.001' }}
                />
                <IconButton
                  color="error"
                  disabled={form.items.length <= 1}
                  onClick={() =>
                    setForm((prev) => ({
                      ...prev,
                      items: prev.items.filter((_, i) => i !== index),
                    }))
                  }
                >
                  <DeleteOutlinedIcon />
                </IconButton>
              </Stack>
            ))}
            <Box>
              <Button onClick={() => setForm((prev) => ({ ...prev, items: [...prev.items, emptyLine()] }))}>
                Add item
              </Button>
            </Box>
          </Stack>
        </DialogContent>
        <DialogActions>
          <Button
            onClick={() => {
              setOpen(false);
              resetForm();
            }}
          >
            Cancel
          </Button>
          <Button variant="contained" disabled={saving} onClick={onSave}>
            {saving ? 'Saving…' : 'Save combo'}
          </Button>
        </DialogActions>
      </Dialog>
    </>
  );
}
