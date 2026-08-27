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
import { createAddonGroup, deleteAddonGroup, listAddonGroups } from '../../services/cafeService';
import { listItems } from '../../services/itemService';

const emptyAddon = () => ({ name: '', extra_price: '0', is_default: false, linked_item_id: '' });

function money(value) {
  return `₹${Number(value || 0).toFixed(2)}`;
}

export default function AddonsPage() {
  const moduleEnabled = useModuleGate('addons_combos');
  const { canManageAddons } = usePermissions();
  const [groups, setGroups] = useState([]);
  const [menuItems, setMenuItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [open, setOpen] = useState(false);
  const [saving, setSaving] = useState(false);
  const [form, setForm] = useState({
    menu_item_id: '',
    name: '',
    is_required: false,
    max_selections: '',
    addons: [emptyAddon()],
  });

  const dishOptions = useMemo(
    () => menuItems.filter((item) => item.is_active && item.is_menu),
    [menuItems],
  );

  const stockItemOptions = useMemo(
    () => menuItems.filter((item) => item.is_active && !item.is_menu),
    [menuItems],
  );

  const load = useCallback(async () => {
    if (!moduleEnabled) return;
    setLoading(true);
    setError('');
    try {
      const [addonRes, itemRes] = await Promise.all([
        listAddonGroups(),
        listItems({ per_page: 500 }),
      ]);
      setGroups(addonRes.data || []);
      setMenuItems(itemRes.data || []);
    } catch (err) {
      setError(err.response?.data?.error?.message || 'Unable to load add-ons.');
    } finally {
      setLoading(false);
    }
  }, [moduleEnabled]);

  useEffect(() => {
    load();
  }, [load]);

  const resetForm = () => {
    setForm({
      menu_item_id: '',
      name: '',
      is_required: false,
      max_selections: '',
      addons: [emptyAddon()],
    });
  };

  const openCreate = () => {
    resetForm();
    setOpen(true);
  };

  const onSave = async () => {
    if (!form.menu_item_id) {
      setError('Select a menu item.');
      return;
    }
    if (!form.name.trim()) {
      setError('Group name is required.');
      return;
    }
    const addonsPayload = form.addons
      .filter((row) => row.name.trim())
      .map((row) => ({
        name: row.name.trim(),
        extra_price: Number(row.extra_price || 0),
        is_default: Boolean(row.is_default),
        linked_item_id: row.linked_item_id || null,
      }));
    if (!addonsPayload.length) {
      setError('Add at least one add-on option.');
      return;
    }
    setSaving(true);
    setError('');
    setSuccess('');
    try {
      await createAddonGroup({
        menu_item_id: form.menu_item_id,
        name: form.name.trim(),
        is_required: Boolean(form.is_required),
        max_selections: form.max_selections === '' ? null : Number(form.max_selections),
        addons: addonsPayload,
      });
      setSuccess('Add-on group created.');
      setOpen(false);
      resetForm();
      await load();
    } catch (err) {
      setError(err.response?.data?.error?.message || 'Unable to save add-on group.');
    } finally {
      setSaving(false);
    }
  };

  const onDelete = async (id) => {
    if (!window.confirm('Delete this add-on group?')) return;
    setError('');
    try {
      await deleteAddonGroup(id);
      setSuccess('Add-on group deleted.');
      await load();
    } catch (err) {
      setError(err.response?.data?.error?.message || 'Unable to delete add-on group.');
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
            New add-on group
          </Button>
        </PageActions>
      ) : null}

      <PageShell>
        <Stack spacing={2}>
          <Typography variant="body2" color="text.secondary">
            Attach option groups (milk type, size, toppings) to menu items. Optionally link an option
            to an ingredient item so Cafe POS settle deducts that stock.
          </Typography>
          {error ? <Alert severity="error">{error}</Alert> : null}
          {success ? <Alert severity="success">{success}</Alert> : null}
          <TableCard>
            {loading ? (
              <LoadingBlock />
            ) : groups.length === 0 ? (
              <EmptyState
                title="No add-on groups yet"
                description="Create a group on a menu item, then add options with optional extra price."
                actionLabel={canManageAddons ? 'New add-on group' : undefined}
                onAction={canManageAddons ? openCreate : undefined}
              />
            ) : (
              <Table size="small">
                <TableHead>
                  <TableRow>
                    <TableCell>Menu item</TableCell>
                    <TableCell>Group</TableCell>
                    <TableCell>Rules</TableCell>
                    <TableCell>Options</TableCell>
                    {canManageAddons ? <TableCell align="right">Actions</TableCell> : null}
                  </TableRow>
                </TableHead>
                <TableBody>
                  {groups.map((group) => (
                    <TableRow key={group.id}>
                      <TableCell>{group.menu_item_name || '—'}</TableCell>
                      <TableCell>{group.name}</TableCell>
                      <TableCell>
                        {group.is_required ? 'Required' : 'Optional'}
                        {group.max_selections != null ? ` · max ${group.max_selections}` : ''}
                      </TableCell>
                      <TableCell>
                        {(group.addons || [])
                          .map((addon) => {
                            const link = addon.linked_item_name
                              ? ` → ${addon.linked_item_name}`
                              : '';
                            return `${addon.name} (${money(addon.extra_price)})${link}`;
                          })
                          .join(', ') || '—'}
                      </TableCell>
                      {canManageAddons ? (
                        <TableCell align="right">
                          <Tooltip title="Delete group">
                            <IconButton
                              size="small"
                              color="error"
                              aria-label={`Delete ${group.name}`}
                              onClick={() => onDelete(group.id)}
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
        <DialogTitle>New add-on group</DialogTitle>
        <DialogContent>
          <Stack spacing={2} sx={{ mt: 1 }}>
            {!dishOptions.length ? (
              <Alert severity="warning">
                No menu items found. Create items with &quot;Menu dish&quot; enabled first.
              </Alert>
            ) : null}
            <Autocomplete
              options={dishOptions}
              getOptionLabel={(option) => option.name}
              value={dishOptions.find((item) => item.id === form.menu_item_id) || null}
              onChange={(_, value) => setForm((prev) => ({ ...prev, menu_item_id: value?.id || '' }))}
              renderInput={(params) => <TextField {...params} label="Menu item" required />}
            />
            <TextField
              label="Group name"
              value={form.name}
              onChange={(e) => setForm((prev) => ({ ...prev, name: e.target.value }))}
              fullWidth
              required
              helperText="Example: Milk, Size, Toppings"
            />
            <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2} alignItems="center">
              <FormControlLabel
                control={
                  <Checkbox
                    checked={form.is_required}
                    onChange={(e) => setForm((prev) => ({ ...prev, is_required: e.target.checked }))}
                  />
                }
                label="Required"
              />
              <TextField
                label="Max selections"
                type="number"
                value={form.max_selections}
                onChange={(e) => setForm((prev) => ({ ...prev, max_selections: e.target.value }))}
                inputProps={{ min: 1, step: 1 }}
                helperText="Leave blank for unlimited"
                sx={{ minWidth: 180 }}
              />
            </Stack>
            <Typography variant="subtitle2">Options</Typography>
            {form.addons.map((row, index) => (
              <Stack key={index} spacing={1}>
                <Stack direction={{ xs: 'column', sm: 'row' }} spacing={1} alignItems="center">
                  <TextField
                    sx={{ flex: 2 }}
                    label="Option name"
                    value={row.name}
                    onChange={(e) =>
                      setForm((prev) => ({
                        ...prev,
                        addons: prev.addons.map((addon, i) =>
                          i === index ? { ...addon, name: e.target.value } : addon,
                        ),
                      }))
                    }
                  />
                  <TextField
                    sx={{ flex: 1 }}
                    label="Extra ₹"
                    type="number"
                    value={row.extra_price}
                    onChange={(e) =>
                      setForm((prev) => ({
                        ...prev,
                        addons: prev.addons.map((addon, i) =>
                          i === index ? { ...addon, extra_price: e.target.value } : addon,
                        ),
                      }))
                    }
                    inputProps={{ min: 0, step: '0.01' }}
                  />
                  <FormControlLabel
                    control={
                      <Checkbox
                        checked={row.is_default}
                        onChange={(e) =>
                          setForm((prev) => ({
                            ...prev,
                            addons: prev.addons.map((addon, i) =>
                              i === index ? { ...addon, is_default: e.target.checked } : addon,
                            ),
                          }))
                        }
                      />
                    }
                    label="Default"
                  />
                  <IconButton
                    color="error"
                    disabled={form.addons.length <= 1}
                    onClick={() =>
                      setForm((prev) => ({
                        ...prev,
                        addons: prev.addons.filter((_, i) => i !== index),
                      }))
                    }
                  >
                    <DeleteOutlinedIcon />
                  </IconButton>
                </Stack>
                <Autocomplete
                  options={stockItemOptions}
                  getOptionLabel={(option) => option.name || ''}
                  value={stockItemOptions.find((item) => item.id === row.linked_item_id) || null}
                  onChange={(_, value) =>
                    setForm((prev) => ({
                      ...prev,
                      addons: prev.addons.map((addon, i) =>
                        i === index ? { ...addon, linked_item_id: value?.id || '' } : addon,
                      ),
                    }))
                  }
                  renderInput={(params) => (
                    <TextField
                      {...params}
                      label="Linked ingredient (optional)"
                      helperText="When set, settle deducts 1× line qty of this item"
                    />
                  )}
                />
              </Stack>
            ))}
            <Box>
              <Button onClick={() => setForm((prev) => ({ ...prev, addons: [...prev.addons, emptyAddon()] }))}>
                Add option
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
            {saving ? 'Saving…' : 'Save group'}
          </Button>
        </DialogActions>
      </Dialog>
    </>
  );
}
