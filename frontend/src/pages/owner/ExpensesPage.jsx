import AddOutlinedIcon from '@mui/icons-material/AddOutlined';
import DeleteOutlinedIcon from '@mui/icons-material/DeleteOutlined';
import EditOutlinedIcon from '@mui/icons-material/EditOutlined';
import {
  Alert,
  Autocomplete,
  Box,
  Button,
  Card,
  CardContent,
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
  Tooltip,
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
import { usePermissions } from '../../hooks/usePermissions';
import { filterControlWideSx } from '../../layouts/shell';
import {
  createExpense,
  deleteExpense,
  getExpenseSummary,
  listExpenses,
  updateExpense,
} from '../../services/expenseService';

const PAGE_SIZE = 25;

const CATEGORY_SUGGESTIONS = [
  'Rent',
  'Utilities',
  'Salaries',
  'Supplies',
  'Transport',
  'Marketing',
  'Maintenance',
  'Other',
];

function todayIso() {
  return new Date().toISOString().slice(0, 10);
}

function formatMoney(value) {
  if (value == null || Number.isNaN(Number(value))) return '—';
  return `₹${Number(value).toFixed(2)}`;
}

const emptyForm = () => ({
  category: '',
  amount: '',
  expense_date: todayIso(),
  notes: '',
});

export default function ExpensesPage() {
  const { canManageExpenses, canViewExpenses } = usePermissions();
  const [expenses, setExpenses] = useState([]);
  const [summary, setSummary] = useState({ total: 0, by_category: [] });
  const [meta, setMeta] = useState({ page: 1, per_page: PAGE_SIZE, total: 0 });
  const [q, setQ] = useState('');
  const [fromDate, setFromDate] = useState('');
  const [toDate, setToDate] = useState('');
  const [page, setPage] = useState(1);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [open, setOpen] = useState(false);
  const [editing, setEditing] = useState(null);
  const [form, setForm] = useState(emptyForm());

  const load = useCallback(
    async (nextPage = page, search = q, from = fromDate, to = toDate) => {
      setError('');
      setLoading(true);
      try {
        const params = {
          q: search || undefined,
          from: from || undefined,
          to: to || undefined,
          page: nextPage,
          per_page: PAGE_SIZE,
        };
        const [listRes, summaryRes] = await Promise.all([
          listExpenses(params),
          getExpenseSummary({ from: from || undefined, to: to || undefined }),
        ]);
        setExpenses(listRes.data || []);
        setMeta(listRes.meta || { page: nextPage, per_page: PAGE_SIZE, total: 0 });
        setSummary(summaryRes.data || { total: 0, by_category: [] });
        setPage(listRes.meta?.page || nextPage);
      } catch (err) {
        setError(err.response?.data?.error?.message || 'Unable to load expenses.');
      } finally {
        setLoading(false);
      }
    },
    [page, q, fromDate, toDate],
  );

  useEffect(() => {
    if (canViewExpenses) load(1);
  }, [canViewExpenses, load]);

  const openCreate = () => {
    setEditing(null);
    setForm(emptyForm());
    setOpen(true);
  };

  const openEdit = (expense) => {
    setEditing(expense);
    setForm({
      category: expense.category || '',
      amount: String(expense.amount ?? ''),
      expense_date: expense.expense_date || todayIso(),
      notes: expense.notes || '',
    });
    setOpen(true);
  };

  const onSave = async () => {
    if (!form.amount || Number(form.amount) <= 0) {
      setError('Amount must be greater than zero.');
      return;
    }
    if (!form.expense_date) {
      setError('Expense date is required.');
      return;
    }
    setSaving(true);
    setError('');
    setSuccess('');
    const payload = {
      category: form.category.trim() || null,
      amount: form.amount,
      expense_date: form.expense_date,
      notes: form.notes.trim() || null,
    };
    try {
      if (editing) {
        await updateExpense(editing.id, payload);
        setSuccess('Expense updated successfully.');
      } else {
        await createExpense(payload);
        setSuccess('Expense recorded successfully.');
      }
      setOpen(false);
      await load(editing ? page : 1, q, fromDate, toDate);
    } catch (err) {
      setError(err.response?.data?.error?.message || 'Failed to save expense.');
    } finally {
      setSaving(false);
    }
  };

  const onDelete = async (expense) => {
    if (!canManageExpenses) return;
    if (!window.confirm(`Delete expense ${formatMoney(expense.amount)} on ${expense.expense_date}?`)) {
      return;
    }
    setError('');
    try {
      await deleteExpense(expense.id);
      setSuccess('Expense deleted.');
      await load(page, q, fromDate, toDate);
    } catch (err) {
      setError(err.response?.data?.error?.message || 'Failed to delete expense.');
    }
  };

  if (!canViewExpenses) {
    return (
      <PageShell>
        <Alert severity="warning">You do not have permission to view expenses.</Alert>
      </PageShell>
    );
  }

  return (
    <>
      {canManageExpenses ? (
        <PageActions>
          <Button variant="contained" startIcon={<AddOutlinedIcon />} onClick={openCreate}>
            Add Expense
          </Button>
        </PageActions>
      ) : null}

      <PageShell>
        <FilterBar
          actions={
            <Button variant="outlined" onClick={() => load(1, q, fromDate, toDate)}>
              Apply
            </Button>
          }
        >
          <TextField
            label="Search category or notes"
            value={q}
            onChange={(e) => setQ(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Enter') load(1, q, fromDate, toDate);
            }}
            sx={{ ...filterControlWideSx, flex: 1 }}
          />
          <TextField
            label="From"
            type="date"
            value={fromDate}
            onChange={(e) => setFromDate(e.target.value)}
            InputLabelProps={{ shrink: true }}
            sx={{ width: { xs: '100%', sm: 160 } }}
          />
          <TextField
            label="To"
            type="date"
            value={toDate}
            onChange={(e) => setToDate(e.target.value)}
            InputLabelProps={{ shrink: true }}
            sx={{ width: { xs: '100%', sm: 160 } }}
          />
        </FilterBar>

        {error ? <Alert severity="error">{error}</Alert> : null}
        {success ? <Alert severity="success">{success}</Alert> : null}

        <Card variant="outlined">
          <CardContent>
            <Stack
              direction={{ xs: 'column', md: 'row' }}
              spacing={3}
              justifyContent="space-between"
              alignItems={{ md: 'center' }}
            >
              <Box>
                <Typography variant="overline" color="text.secondary">
                  Total expenses
                </Typography>
                <Typography variant="h5">{formatMoney(summary.total)}</Typography>
              </Box>
              <Stack direction="row" spacing={1} flexWrap="wrap" useFlexGap>
                {(summary.by_category || []).map((row) => (
                  <Typography key={row.category} variant="body2" color="text.secondary">
                    {row.category}: {formatMoney(row.total)}
                  </Typography>
                ))}
              </Stack>
            </Stack>
          </CardContent>
        </Card>

        <TableCard>
          {loading ? (
            <LoadingBlock />
          ) : (
            <Table size="small" sx={{ minWidth: 900 }}>
              <TableHead>
                <TableRow>
                  <TableCell>Date</TableCell>
                  <TableCell>Category</TableCell>
                  <TableCell>Notes</TableCell>
                  <TableCell align="right">Amount</TableCell>
                  <TableCell>Recorded by</TableCell>
                  <TableCell align="right">Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {expenses.map((expense) => (
                  <TableRow key={expense.id} hover>
                    <TableCell>{expense.expense_date}</TableCell>
                    <TableCell>{expense.category || 'Uncategorized'}</TableCell>
                    <TableCell>
                      <TruncateText value={expense.notes || '—'} maxWidth={220} />
                    </TableCell>
                    <TableCell align="right">{formatMoney(expense.amount)}</TableCell>
                    <TableCell>
                      <Typography variant="body2" color="text.secondary">
                        {expense.created_by_name || '—'}
                      </Typography>
                    </TableCell>
                    <TableCell align="right">
                      {canManageExpenses ? (
                        <Stack direction="row" spacing={0.5} justifyContent="flex-end">
                          <Tooltip title="Edit">
                            <IconButton
                              size="small"
                              aria-label="Edit expense"
                              onClick={() => openEdit(expense)}
                            >
                              <EditOutlinedIcon fontSize="small" />
                            </IconButton>
                          </Tooltip>
                          <Tooltip title="Delete">
                            <IconButton
                              size="small"
                              aria-label="Delete expense"
                              onClick={() => onDelete(expense)}
                            >
                              <DeleteOutlinedIcon fontSize="small" />
                            </IconButton>
                          </Tooltip>
                        </Stack>
                      ) : (
                        <Typography variant="caption" color="text.secondary">
                          —
                        </Typography>
                      )}
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
          {!loading && !expenses.length ? (
            <EmptyState
              title="No expenses found"
              description="Record daily business expenses to prepare for P&L reporting."
              actionLabel={canManageExpenses ? 'Add Expense' : undefined}
              onAction={canManageExpenses ? openCreate : undefined}
            />
          ) : null}
        </TableCard>

        {!loading && expenses.length ? (
          <PaginationBar
            page={page}
            total={meta.total}
            pageSize={PAGE_SIZE}
            onPageChange={(next) => load(next, q, fromDate, toDate)}
          />
        ) : null}
      </PageShell>

      <Dialog open={open} onClose={() => setOpen(false)} fullWidth maxWidth="sm">
        <DialogTitle>{editing ? 'Edit Expense' : 'Add Expense'}</DialogTitle>
        <DialogContent>
          <Stack spacing={2.5} sx={{ mt: 1 }}>
            <Autocomplete
              freeSolo
              options={CATEGORY_SUGGESTIONS}
              value={form.category}
              onChange={(_, value) => setForm((f) => ({ ...f, category: value || '' }))}
              onInputChange={(_, value) => setForm((f) => ({ ...f, category: value }))}
              renderInput={(params) => (
                <TextField {...params} label="Category (optional)" fullWidth />
              )}
            />
            <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2}>
              <TextField
                label="Amount"
                type="number"
                inputProps={{ min: 0.01, step: '0.01' }}
                value={form.amount}
                onChange={(e) => setForm((f) => ({ ...f, amount: e.target.value }))}
                fullWidth
                required
              />
              <TextField
                label="Date"
                type="date"
                value={form.expense_date}
                onChange={(e) => setForm((f) => ({ ...f, expense_date: e.target.value }))}
                InputLabelProps={{ shrink: true }}
                fullWidth
                required
              />
            </Stack>
            <TextField
              label="Notes"
              value={form.notes}
              onChange={(e) => setForm((f) => ({ ...f, notes: e.target.value }))}
              fullWidth
              multiline
              minRows={2}
            />
          </Stack>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpen(false)}>Cancel</Button>
          <Button variant="contained" onClick={onSave} disabled={saving}>
            {saving ? 'Saving...' : 'Save'}
          </Button>
        </DialogActions>
      </Dialog>
    </>
  );
}
