import {
  Alert,
  Button,
  Chip,
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
import { useEffect, useMemo, useState } from 'react';
import { useSearchParams } from 'react-router-dom';
import EmptyState from '../../components/EmptyState';
import FilterBar from '../../components/FilterBar';
import LoadingBlock from '../../components/LoadingBlock';
import PageShell from '../../components/PageShell';
import PaginationBar from '../../components/PaginationBar';
import TableCard from '../../components/TableCard';
import TruncateText from '../../components/TruncateText';
import { useAuth } from '../../context/AuthContext';
import { filterControlSx } from '../../layouts/shell';
import { listItems } from '../../services/itemService';
import { listStockMovements } from '../../services/stockMovementService';

/** Backend source codes with hotel-friendly labels. */
const SOURCE_OPTIONS = [
  { value: '', label: 'All types' },
  { value: 'RECEIVE', label: 'Stock In' },
  { value: 'PURCHASE', label: 'Purchase In' },
  { value: 'BILL', label: 'Sale / Consumption' },
  { value: 'RECIPE', label: 'Recipe Consumption' },
  { value: 'WASTAGE', label: 'Wastage' },
  { value: 'ADJUST', label: 'Adjustment' },
  { value: 'CANCEL', label: 'Cancel / Reversal' },
  { value: 'RETURN', label: 'Return' },
  { value: 'EXCHANGE', label: 'Exchange' },
  { value: 'ITEM_UPDATE', label: 'Item Update' },
  { value: 'PRODUCTION', label: 'Production' },
  { value: 'TRANSFER_IN', label: 'Transfer In' },
  { value: 'TRANSFER_OUT', label: 'Transfer Out' },
];

const PAGE_SIZE = 50;

const SOURCE_LABEL = Object.fromEntries(SOURCE_OPTIONS.filter((row) => row.value).map((row) => [row.value, row.label]));

function sourceColor(source) {
  if (source === 'BILL' || source === 'RECIPE') return 'warning';
  if (source === 'CANCEL' || source === 'RETURN') return 'info';
  if (source === 'ADJUST' || source === 'ITEM_UPDATE') return 'default';
  if (source === 'RECEIVE' || source === 'PURCHASE' || source === 'PRODUCTION') return 'success';
  if (source === 'WASTAGE') return 'error';
  return 'primary';
}

function formatDelta(value) {
  const n = Number(value);
  if (Number.isNaN(n)) return '—';
  return `${n > 0 ? '+' : ''}${n}`;
}

export default function StockMovementsPage() {
  const { user } = useAuth();
  const isHotel = user?.tenant?.business_type === 'hotel_restaurant';
  const [searchParams] = useSearchParams();
  const [rows, setRows] = useState([]);
  const [items, setItems] = useState([]);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);
  const [meta, setMeta] = useState({ page: 1, per_page: PAGE_SIZE, total: 0 });
  const [filters, setFilters] = useState({
    item_id: searchParams.get('item_id') || '',
    source: searchParams.get('source') || '',
    from: searchParams.get('from') || '',
    to: searchParams.get('to') || '',
    q: '',
  });

  const hotelSources = useMemo(
    () =>
      SOURCE_OPTIONS.filter((row) =>
        !row.value
          ? true
          : ['RECEIVE', 'BILL', 'RECIPE', 'WASTAGE', 'ADJUST', 'CANCEL', 'RETURN', 'ITEM_UPDATE'].includes(
              row.value
            )
      ),
    []
  );

  const sourceMenu = isHotel ? hotelSources : SOURCE_OPTIONS;

  const load = async (nextPage = page, nextFilters = filters) => {
    setError('');
    setLoading(true);
    try {
      const params = {
        page: nextPage,
        per_page: PAGE_SIZE,
      };
      if (nextFilters.item_id) params.item_id = nextFilters.item_id;
      if (nextFilters.source) params.source = nextFilters.source;
      if (nextFilters.from) params.from = nextFilters.from;
      if (nextFilters.to) params.to = nextFilters.to;
      const response = await listStockMovements(params);
      let data = response.data || [];
      const term = (nextFilters.q || '').trim().toLowerCase();
      if (term) {
        data = data.filter((row) => (row.item_name || '').toLowerCase().includes(term));
      }
      setRows(data);
      setMeta(response.meta || { page: nextPage, per_page: PAGE_SIZE, total: 0 });
      setPage(response.meta?.page || nextPage);
    } catch (err) {
      setError(err.response?.data?.error?.message || 'Unable to load stock movements.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    listItems({ per_page: 100 })
      .then((res) => setItems(res.data || []))
      .catch(() => {});
    load(1);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return (
    <PageShell>
      <Stack spacing={2}>
        {isHotel ? (
          <Alert severity="info">
            Hotel stock movements: sales and recipe consumption post when a bill is settled (not when
            editing an open table order). Wastage and adjustments are recorded separately for audit.
          </Alert>
        ) : null}
        <FilterBar
          actions={
            <Button variant="contained" onClick={() => load(1, filters)} disabled={loading}>
              Apply
            </Button>
          }
        >
          <TextField
            label="Search item"
            value={filters.q}
            onChange={(e) => setFilters((f) => ({ ...f, q: e.target.value }))}
            sx={filterControlSx}
          />
          <FormControl sx={filterControlSx}>
            <InputLabel>Item</InputLabel>
            <Select
              label="Item"
              value={filters.item_id}
              onChange={(e) => setFilters((f) => ({ ...f, item_id: e.target.value }))}
            >
              <MenuItem value="">All items</MenuItem>
              {items.map((item) => (
                <MenuItem key={item.id} value={item.id}>
                  {item.name}
                </MenuItem>
              ))}
            </Select>
          </FormControl>
          <FormControl sx={filterControlSx}>
            <InputLabel>Movement type</InputLabel>
            <Select
              label="Movement type"
              value={filters.source}
              onChange={(e) => setFilters((f) => ({ ...f, source: e.target.value }))}
            >
              {sourceMenu.map((src) => (
                <MenuItem key={src.value || 'all'} value={src.value}>
                  {src.label}
                </MenuItem>
              ))}
            </Select>
          </FormControl>
          <TextField
            label="From"
            type="date"
            value={filters.from}
            onChange={(e) => setFilters((f) => ({ ...f, from: e.target.value }))}
            InputLabelProps={{ shrink: true }}
            sx={filterControlSx}
          />
          <TextField
            label="To"
            type="date"
            value={filters.to}
            onChange={(e) => setFilters((f) => ({ ...f, to: e.target.value }))}
            InputLabelProps={{ shrink: true }}
            sx={filterControlSx}
          />
        </FilterBar>

        {error ? <Alert severity="error">{error}</Alert> : null}

        <TableCard>
          {loading ? (
            <LoadingBlock />
          ) : !rows.length ? (
            <EmptyState title="No stock movements" description="Try a different date or movement type." />
          ) : (
            <Table size="small" sx={{ minWidth: 900 }}>
              <TableHead>
                <TableRow>
                  <TableCell>When</TableCell>
                  <TableCell>Item</TableCell>
                  <TableCell>Type</TableCell>
                  <TableCell align="right">Qty</TableCell>
                  <TableCell align="right">After</TableCell>
                  <TableCell>Reason / Ref</TableCell>
                  <TableCell>By</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {rows.map((row) => (
                  <TableRow key={row.id} hover>
                    <TableCell>
                      <Typography variant="body2">
                        {row.created_at ? new Date(row.created_at).toLocaleString() : '—'}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <TruncateText value={row.item_name || row.item_id} maxWidth={180} />
                    </TableCell>
                    <TableCell>
                      <Chip
                        size="small"
                        label={SOURCE_LABEL[row.source] || row.source}
                        color={sourceColor(row.source)}
                      />
                    </TableCell>
                    <TableCell align="right">{formatDelta(row.delta)}</TableCell>
                    <TableCell align="right">{Number(row.quantity_after)}</TableCell>
                    <TableCell>
                      <TruncateText
                        value={
                          [
                            row.reason,
                            row.reference_type && row.reference_id
                              ? `${row.reference_type} ${String(row.reference_id).slice(0, 8)}…`
                              : null,
                          ]
                            .filter(Boolean)
                            .join(' · ') || '—'
                        }
                        maxWidth={220}
                      />
                    </TableCell>
                    <TableCell>
                      <TruncateText value={row.created_by_name || row.created_by || '—'} maxWidth={120} />
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </TableCard>

        <PaginationBar
          page={meta.page || page}
          perPage={meta.per_page || PAGE_SIZE}
          total={meta.total || 0}
          onPageChange={(next) => load(next, filters)}
        />
      </Stack>
    </PageShell>
  );
}
