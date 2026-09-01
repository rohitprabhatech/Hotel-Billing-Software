import CheckroomOutlinedIcon from '@mui/icons-material/CheckroomOutlined';
import {
  Alert,
  Autocomplete,
  Box,
  Button,
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
import { Link as RouterLink, useNavigate } from 'react-router-dom';
import EmptyState from '../../components/EmptyState';
import FilterBar from '../../components/FilterBar';
import LoadingBlock from '../../components/LoadingBlock';
import PageShell from '../../components/PageShell';
import TableCard from '../../components/TableCard';
import TruncateText from '../../components/TruncateText';
import StatusBadge from '../../components/ui/StatusBadge';
import { PageActions } from '../../context/PageActionsContext';
import { useModuleGate } from '../../context/ModulesContext';
import { usePermissions } from '../../hooks/usePermissions';
import { filterControlSx } from '../../layouts/shell';
import { PATHS } from '../../routes/paths';
import { listItems } from '../../services/itemService';
import { listTenantVariants } from '../../services/variantService';

export default function VariantsPage() {
  const moduleEnabled = useModuleGate('variants');
  const { canWriteItems } = usePermissions();
  const navigate = useNavigate();
  const [rows, setRows] = useState([]);
  const [catalog, setCatalog] = useState([]);
  const [itemFilter, setItemFilter] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const load = useCallback(async () => {
    setLoading(true);
    setError('');
    try {
      const res = await listTenantVariants({
        item_id: itemFilter?.id || undefined,
        per_page: 100,
      });
      setRows(res.data || []);
    } catch (err) {
      setError(err.response?.data?.error?.message || 'Failed to load variants');
    } finally {
      setLoading(false);
    }
  }, [itemFilter]);

  useEffect(() => {
    if (!moduleEnabled) return;
    load();
  }, [moduleEnabled, load]);

  useEffect(() => {
    if (!moduleEnabled) return;
    listItems({ is_active: true, per_page: 200 })
      .then((res) => setCatalog(res.data || []))
      .catch(() => setCatalog([]));
  }, [moduleEnabled]);

  if (!moduleEnabled) {
    return (
      <PageShell>
        <Alert severity="warning">The Variants module is not enabled for this business type.</Alert>
      </PageShell>
    );
  }

  return (
    <>
      <PageActions>
        {canWriteItems ? (
          <Button
            component={RouterLink}
            to={PATHS.ownerItems}
            variant="contained"
            startIcon={<CheckroomOutlinedIcon />}
          >
            Edit matrix on Items
          </Button>
        ) : null}
      </PageActions>
      <PageShell>
        <FilterBar>
          <Autocomplete
            options={catalog}
            getOptionLabel={(option) => option.name || ''}
            value={itemFilter}
            onChange={(_, value) => setItemFilter(value)}
            renderInput={(params) => <TextField {...params} label="Filter by item" />}
            sx={filterControlSx}
          />
          <Button variant="outlined" onClick={load}>
            Refresh
          </Button>
        </FilterBar>
        {error ? (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        ) : null}
        <TableCard>
          {loading ? (
            <LoadingBlock />
          ) : !rows.length ? (
            <EmptyState
              title="No variants yet"
              description="Open Items and use the size/color matrix to add independent stock for each combination."
              actionLabel={canWriteItems ? 'Go to Items' : undefined}
              onAction={canWriteItems ? () => navigate(PATHS.ownerItems) : undefined}
            />
          ) : (
            <Table size="small">
              <TableHead>
                <TableRow>
                  <TableCell>Item</TableCell>
                  <TableCell>Size</TableCell>
                  <TableCell>Color</TableCell>
                  <TableCell>Brand</TableCell>
                  <TableCell>SKU / Barcode</TableCell>
                  <TableCell align="right">Stock</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {rows.map((row) => (
                  <TableRow key={row.id}>
                    <TableCell>
                      <TruncateText value={row.item_name || '—'} maxWidth={180} />
                    </TableCell>
                    <TableCell>{row.size}</TableCell>
                    <TableCell>{row.color}</TableCell>
                    <TableCell>{row.brand || '—'}</TableCell>
                    <TableCell>
                      <Stack spacing={0.25}>
                        <Typography variant="body2">{row.sku || '—'}</Typography>
                        <Typography variant="caption" color="text.secondary">
                          {row.barcode || '—'}
                        </Typography>
                      </Stack>
                    </TableCell>
                    <TableCell align="right">
                      <StatusBadge
                        label={Number(row.stock_quantity)}
                        variant={Number(row.stock_quantity) <= 0 ? 'cancelled' : 'active'}
                      />
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </TableCard>
        <Box sx={{ mt: 2 }}>
          <Typography variant="body2" color="text.secondary">
            Parent item stock is the sum of active variant quantities. Sell from New Bill by picking
            size and color.
          </Typography>
        </Box>
      </PageShell>
    </>
  );
}
