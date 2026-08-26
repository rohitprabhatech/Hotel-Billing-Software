import AddOutlinedIcon from '@mui/icons-material/AddOutlined';
import DeleteOutlineOutlinedIcon from '@mui/icons-material/DeleteOutlineOutlined';
import PriceChangeOutlinedIcon from '@mui/icons-material/PriceChangeOutlined';
import {
  Alert,
  Autocomplete,
  Box,
  Button,
  Checkbox,
  Chip,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  FormControlLabel,
  IconButton,
  MenuItem,
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
import CustomerPicker from '../../components/CustomerPicker';
import EmptyState from '../../components/EmptyState';
import LoadingBlock from '../../components/LoadingBlock';
import PageShell from '../../components/PageShell';
import TableCard from '../../components/TableCard';
import { PageActions } from '../../context/PageActionsContext';
import { useAuth } from '../../context/AuthContext';
import { useModuleGate } from '../../context/ModulesContext';
import { listItems } from '../../services/itemService';
import {
  assignCustomerPriceList,
  createPriceList,
  getPriceList,
  listCustomerPriceAssignments,
  listPriceLists,
  replacePriceListItems,
  unassignCustomerPriceList,
} from '../../services/priceListService';

const emptyLine = { item: null, unit_price: '' };

export default function PriceListsPage() {
  const moduleEnabled = useModuleGate('price_lists');
  const { role } = useAuth();
  const canWrite = role === 'OWNER' || role === 'MANAGER';

  const [rows, setRows] = useState([]);
  const [assignments, setAssignments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const [createOpen, setCreateOpen] = useState(false);
  const [createForm, setCreateForm] = useState({
    name: '',
    list_type: 'WHOLESALE',
    is_default: false,
    notes: '',
  });

  const [itemsOpen, setItemsOpen] = useState(false);
  const [itemsTarget, setItemsTarget] = useState(null);
  const [itemOptions, setItemOptions] = useState([]);
  const [itemLines, setItemLines] = useState([emptyLine]);
  const [saving, setSaving] = useState(false);

  const [assignOpen, setAssignOpen] = useState(false);
  const [assignCustomer, setAssignCustomer] = useState(null);
  const [assignListId, setAssignListId] = useState('');

  const load = useCallback(async () => {
    if (!moduleEnabled) return;
    setLoading(true);
    setError('');
    try {
      const [listsRes, assignRes] = await Promise.all([
        listPriceLists({ per_page: 100 }),
        listCustomerPriceAssignments(),
      ]);
      setRows(listsRes.data || []);
      setAssignments(assignRes.data || []);
    } catch (err) {
      setError(err.response?.data?.error?.message || 'Failed to load price lists');
    } finally {
      setLoading(false);
    }
  }, [moduleEnabled]);

  useEffect(() => {
    load();
  }, [load]);

  const openItemsEditor = async (row) => {
    setItemsTarget(row);
    setItemsOpen(true);
    setError('');
    setSaving(true);
    try {
      const [detail, itemsRes] = await Promise.all([
        getPriceList(row.id),
        listItems({ per_page: 200, is_active: true }),
      ]);
      setItemOptions(itemsRes.data || []);
      const lines = (detail.data?.items || []).map((line) => ({
        item: (itemsRes.data || []).find((item) => item.id === line.item_id) || {
          id: line.item_id,
          name: line.item_name,
        },
        unit_price: String(line.unit_price),
      }));
      setItemLines(lines.length ? lines : [emptyLine]);
    } catch (err) {
      setError(err.response?.data?.error?.message || 'Failed to load list items');
    } finally {
      setSaving(false);
    }
  };

  const submitCreate = async () => {
    if (!createForm.name.trim()) {
      setError('Name is required');
      return;
    }
    setSaving(true);
    setError('');
    try {
      await createPriceList({
        name: createForm.name.trim(),
        list_type: createForm.list_type,
        is_default: createForm.is_default,
        notes: createForm.notes.trim() || undefined,
      });
      setCreateOpen(false);
      setCreateForm({ name: '', list_type: 'WHOLESALE', is_default: false, notes: '' });
      setSuccess('Price list created');
      await load();
    } catch (err) {
      setError(err.response?.data?.error?.message || 'Could not create price list');
    } finally {
      setSaving(false);
    }
  };

  const submitItems = async () => {
    if (!itemsTarget) return;
    const cleaned = itemLines
      .filter((line) => line.item && line.unit_price !== '')
      .map((line) => ({
        item_id: line.item.id,
        unit_price: line.unit_price,
      }));
    setSaving(true);
    setError('');
    try {
      await replacePriceListItems(itemsTarget.id, cleaned);
      setItemsOpen(false);
      setSuccess(`Updated prices for ${itemsTarget.name}`);
      await load();
    } catch (err) {
      setError(err.response?.data?.error?.message || 'Could not save list items');
    } finally {
      setSaving(false);
    }
  };

  const submitAssign = async () => {
    if (!assignCustomer || !assignListId) {
      setError('Select customer and price list');
      return;
    }
    setSaving(true);
    setError('');
    try {
      await assignCustomerPriceList(assignCustomer.id, assignListId);
      setAssignOpen(false);
      setAssignCustomer(null);
      setAssignListId('');
      setSuccess(`Assigned ${assignCustomer.name}`);
      await load();
    } catch (err) {
      setError(err.response?.data?.error?.message || 'Could not assign price list');
    } finally {
      setSaving(false);
    }
  };

  const removeAssignment = async (customerId) => {
    setSaving(true);
    setError('');
    try {
      await unassignCustomerPriceList(customerId);
      setSuccess('Customer assignment removed');
      await load();
    } catch (err) {
      setError(err.response?.data?.error?.message || 'Could not remove assignment');
    } finally {
      setSaving(false);
    }
  };

  if (!moduleEnabled) {
    return (
      <PageShell>
        <Alert severity="info">Price lists are not enabled for this business type.</Alert>
      </PageShell>
    );
  }

  return (
    <PageShell>
      <PageActions>
        {canWrite ? (
          <>
            <Button variant="outlined" onClick={() => setAssignOpen(true)}>
              Assign customer
            </Button>
            <Button variant="contained" startIcon={<AddOutlinedIcon />} onClick={() => setCreateOpen(true)}>
              New price list
            </Button>
          </>
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

      <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
        Resolution order: customer list → default wholesale list → bulk qty tiers → catalog retail.
      </Typography>

      {loading ? (
        <LoadingBlock />
      ) : rows.length === 0 ? (
        <EmptyState
          title="No price lists"
          description="Create a wholesale matrix and assign it to trade customers."
          icon={<PriceChangeOutlinedIcon />}
        />
      ) : (
        <TableCard>
          <Table size="small">
            <TableHead>
              <TableRow>
                <TableCell>Name</TableCell>
                <TableCell>Type</TableCell>
                <TableCell>Default</TableCell>
                <TableCell>Status</TableCell>
                <TableCell align="right">Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {rows.map((row) => (
                <TableRow key={row.id}>
                  <TableCell>{row.name}</TableCell>
                  <TableCell>{row.list_type}</TableCell>
                  <TableCell>{row.is_default ? <Chip size="small" label="Default" /> : '—'}</TableCell>
                  <TableCell>{row.is_active ? 'Active' : 'Inactive'}</TableCell>
                  <TableCell align="right">
                    {canWrite ? (
                      <Button size="small" onClick={() => openItemsEditor(row)}>
                        Edit prices
                      </Button>
                    ) : null}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableCard>
      )}

      {assignments.length ? (
        <Box sx={{ mt: 3 }}>
          <Typography variant="h6" sx={{ mb: 1 }}>
            Customer assignments
          </Typography>
          <TableCard>
            <Table size="small">
              <TableHead>
                <TableRow>
                  <TableCell>Customer</TableCell>
                  <TableCell>Price list</TableCell>
                  {canWrite ? <TableCell align="right">Actions</TableCell> : null}
                </TableRow>
              </TableHead>
              <TableBody>
                {assignments.map((row) => (
                  <TableRow key={row.id}>
                    <TableCell>{row.customer_name}</TableCell>
                    <TableCell>{row.price_list_name}</TableCell>
                    {canWrite ? (
                      <TableCell align="right">
                        <IconButton
                          size="small"
                          color="error"
                          disabled={saving}
                          onClick={() => removeAssignment(row.customer_id)}
                        >
                          <DeleteOutlineOutlinedIcon fontSize="small" />
                        </IconButton>
                      </TableCell>
                    ) : null}
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableCard>
        </Box>
      ) : null}

      <Dialog open={createOpen} onClose={() => !saving && setCreateOpen(false)} fullWidth maxWidth="sm">
        <DialogTitle>New price list</DialogTitle>
        <DialogContent>
          <Stack spacing={2} sx={{ mt: 1 }}>
            <TextField
              label="Name"
              value={createForm.name}
              onChange={(e) => setCreateForm((f) => ({ ...f, name: e.target.value }))}
              required
            />
            <TextField
              select
              label="Type"
              value={createForm.list_type}
              onChange={(e) => setCreateForm((f) => ({ ...f, list_type: e.target.value }))}
            >
              <MenuItem value="WHOLESALE">Wholesale</MenuItem>
              <MenuItem value="RETAIL">Retail override</MenuItem>
            </TextField>
            <FormControlLabel
              control={
                <Checkbox
                  checked={createForm.is_default}
                  onChange={(e) => setCreateForm((f) => ({ ...f, is_default: e.target.checked }))}
                />
              }
              label="Default for this type"
            />
            <TextField
              label="Notes"
              value={createForm.notes}
              onChange={(e) => setCreateForm((f) => ({ ...f, notes: e.target.value }))}
              multiline
              minRows={2}
            />
          </Stack>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setCreateOpen(false)} disabled={saving}>
            Cancel
          </Button>
          <Button variant="contained" onClick={submitCreate} disabled={saving}>
            Create
          </Button>
        </DialogActions>
      </Dialog>

      <Dialog open={itemsOpen} onClose={() => !saving && setItemsOpen(false)} fullWidth maxWidth="md">
        <DialogTitle>Edit prices — {itemsTarget?.name}</DialogTitle>
        <DialogContent>
          <Stack spacing={2} sx={{ mt: 1 }}>
            {itemLines.map((line, index) => (
              <Stack direction={{ xs: 'column', sm: 'row' }} spacing={1} key={`line-${index}`}>
                <Autocomplete
                  sx={{ flex: 1 }}
                  options={itemOptions}
                  getOptionLabel={(option) => option.name || ''}
                  value={line.item}
                  onChange={(_, value) =>
                    setItemLines((rows) =>
                      rows.map((row, i) => (i === index ? { ...row, item: value } : row)),
                    )
                  }
                  renderInput={(params) => <TextField {...params} label="Item" />}
                />
                <TextField
                  label="Unit price"
                  type="number"
                  value={line.unit_price}
                  onChange={(e) =>
                    setItemLines((rows) =>
                      rows.map((row, i) => (i === index ? { ...row, unit_price: e.target.value } : row)),
                    )
                  }
                  sx={{ width: { sm: 160 } }}
                />
                <IconButton
                  color="error"
                  onClick={() =>
                    setItemLines((rows) => (rows.length === 1 ? [emptyLine] : rows.filter((_, i) => i !== index)))
                  }
                >
                  <DeleteOutlineOutlinedIcon />
                </IconButton>
              </Stack>
            ))}
            <Button onClick={() => setItemLines((rows) => [...rows, emptyLine])}>Add line</Button>
          </Stack>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setItemsOpen(false)} disabled={saving}>
            Cancel
          </Button>
          <Button variant="contained" onClick={submitItems} disabled={saving}>
            Save prices
          </Button>
        </DialogActions>
      </Dialog>

      <Dialog open={assignOpen} onClose={() => !saving && setAssignOpen(false)} fullWidth maxWidth="sm">
        <DialogTitle>Assign customer price list</DialogTitle>
        <DialogContent>
          <Stack spacing={2} sx={{ mt: 1 }}>
            <CustomerPicker value={assignCustomer} onChange={setAssignCustomer} />
            <TextField
              select
              label="Price list"
              value={assignListId}
              onChange={(e) => setAssignListId(e.target.value)}
              required
            >
              {rows.map((row) => (
                <MenuItem key={row.id} value={row.id}>
                  {row.name}
                </MenuItem>
              ))}
            </TextField>
          </Stack>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setAssignOpen(false)} disabled={saving}>
            Cancel
          </Button>
          <Button variant="contained" onClick={submitAssign} disabled={saving || !assignCustomer || !assignListId}>
            Assign
          </Button>
        </DialogActions>
      </Dialog>
    </PageShell>
  );
}
