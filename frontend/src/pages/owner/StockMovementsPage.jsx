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
import { useEffect, useState } from 'react';
import { useSearchParams } from 'react-router-dom';
import EmptyState from '../../components/EmptyState';
import FilterBar from '../../components/FilterBar';
import LoadingBlock from '../../components/LoadingBlock';
import PageShell from '../../components/PageShell';
import PaginationBar from '../../components/PaginationBar';
import TableCard from '../../components/TableCard';
import TruncateText from '../../components/TruncateText';
import { filterControlSx } from '../../layouts/shell';
import { listItems } from '../../services/itemService';
import { listStockMovements } from '../../services/stockMovementService';

const SOURCES = ['', 'BILL', 'CANCEL', 'ADJUST', 'RECEIVE', 'ITEM_UPDATE'];
const PAGE_SIZE = 50;

function sourceColor(source) {
  if (source === 'BILL') return 'warning';
  if (source === 'CANCEL') return 'info';
  if (source === 'ADJUST') return 'success';
  if (source === 'RECEIVE') return 'primary';
  return 'default';
}

function formatDelta(value) {
  const n = Number(value);
  if (Number.isNaN(n)) return '—';
  return `${n > 0 ? '+' : ''}${n}`;
}

export default function StockMovementsPage() {
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
  });

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
      setRows(response.data || []);
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
        <FilterBar
          actions={
            <Button variant="contained" onClick={() => load(1)} disabled={loading}>
              Apply
            </Button>
          }
        >
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
            <InputLabel>Source</InputLabel>
            <Select
              label="Source"
              value={filters.source}
              onChange={(e) => setFilters((f) => ({ ...f, source: e.target.value }))}
            >
              {SOURCES.map((src) => (
                <MenuItem key={src || 'all'} value={src}>
                  {src || 'All sources'}
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
          ) : (
            <Table size="small" sx={{ minWidth: 900 }}>
              <TableHead>
                <TableRow>
                  <TableCell>When</TableCell>
                  <TableCell>Item</TableCell>
                  <TableCell>Source</TableCell>
                  <TableCell align="right">Delta</TableCell>
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
                      <Chip size="small" label={row.source} color={sourceColor(row.source)} />
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
                      <TruncateText value={row.created_by_name || '—'} maxWidth={120} />
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
          {!loading && !rows.length ? (
            <EmptyState
              title="No stock movements yet"
              description="Movements appear when bills deduct stock, cancels restore it, or you adjust stock."
            />
          ) : null}
          {!loading && rows.length ? (
            <PaginationBar
              page={meta.page}
              perPage={meta.per_page}
              total={meta.total}
              onPageChange={(next) => load(next)}
            />
          ) : null}
        </TableCard>
      </Stack>
    </PageShell>
  );
}
