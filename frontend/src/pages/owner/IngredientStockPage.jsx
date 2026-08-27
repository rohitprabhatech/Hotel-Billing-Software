import KitchenOutlinedIcon from '@mui/icons-material/KitchenOutlined';
import {
  Alert,
  Chip,
  Stack,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
  Typography,
} from '@mui/material';
import { useCallback, useEffect, useMemo, useState } from 'react';
import { Link as RouterLink, useNavigate } from 'react-router-dom';
import EmptyState from '../../components/EmptyState';
import LoadingBlock from '../../components/LoadingBlock';
import PageShell from '../../components/PageShell';
import TableCard from '../../components/TableCard';
import { useAuth } from '../../context/AuthContext';
import { useModuleGate } from '../../context/ModulesContext';
import { listItems } from '../../services/itemService';
import { PATHS } from '../../routes/paths';

function stockLabel(item) {
  if (item.stock_quantity == null) return 'Not tracked';
  return String(item.stock_quantity);
}

function isLow(item) {
  if (item.stock_quantity == null || item.minimum_stock_level == null) return false;
  return Number(item.stock_quantity) <= Number(item.minimum_stock_level);
}

/**
 * Cafe-focused view of raw ingredient stock (non-menu items).
 * Sprint 6 — complements Recipes + dashboard low-ingredient alerts.
 */
export default function IngredientStockPage() {
  const navigate = useNavigate();
  const moduleEnabled = useModuleGate('recipe');
  const { user } = useAuth();
  const businessType = user?.tenant?.business_type;
  const isCafe = businessType === 'cafe_tea';
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const load = useCallback(async () => {
    if (!moduleEnabled) return;
    setLoading(true);
    setError('');
    try {
      const res = await listItems({ is_active: true, per_page: 500 });
      setItems(res.data || []);
    } catch (err) {
      setError(err.response?.data?.error?.message || 'Unable to load ingredients.');
    } finally {
      setLoading(false);
    }
  }, [moduleEnabled]);

  useEffect(() => {
    load();
  }, [load]);

  const ingredients = useMemo(
    () =>
      (items || [])
        .filter((item) => item.is_active && !item.is_menu)
        .sort((a, b) => {
          const lowA = isLow(a) ? 0 : 1;
          const lowB = isLow(b) ? 0 : 1;
          if (lowA !== lowB) return lowA - lowB;
          return String(a.name || '').localeCompare(String(b.name || ''));
        }),
    [items],
  );

  const lowCount = ingredients.filter(isLow).length;
  const itemsPath = window.location.pathname.startsWith('/billing')
    ? PATHS.billingItems
    : PATHS.ownerItems;

  if (!moduleEnabled) {
    return (
      <PageShell>
        <Alert severity="warning">Recipes / ingredient stock is not enabled for this business.</Alert>
      </PageShell>
    );
  }

  return (
    <PageShell>
      <Stack spacing={2}>
        <Typography variant="body2" color="text.secondary">
          {isCafe
            ? 'Raw ingredients used by recipes and linked add-ons. Stock drops when Cafe POS bills settle.'
            : 'Raw ingredients used by recipes. Stock drops when bills settle.'}{' '}
          Manage catalog in{' '}
          <Typography component={RouterLink} to={itemsPath} variant="body2" color="primary">
            Items
          </Typography>
          .
        </Typography>
        {lowCount > 0 ? (
          <Alert severity="warning">
            {lowCount} ingredient{lowCount === 1 ? '' : 's'} at or below minimum stock.
          </Alert>
        ) : null}
        {error ? <Alert severity="error">{error}</Alert> : null}
        {loading ? (
          <LoadingBlock />
        ) : ingredients.length === 0 ? (
          <EmptyState
            icon={<KitchenOutlinedIcon />}
            title="No ingredients yet"
            description='Create items with “Menu dish” turned OFF — those appear here as ingredients.'
            actionLabel="Go to Items"
            onAction={() => navigate(itemsPath)}
          />
        ) : (
          <TableCard>
            <Table size="small">
              <TableHead>
                <TableRow>
                  <TableCell>Ingredient</TableCell>
                  <TableCell>Unit</TableCell>
                  <TableCell align="right">Stock</TableCell>
                  <TableCell align="right">Min</TableCell>
                  <TableCell>Status</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {ingredients.map((item) => (
                  <TableRow key={item.id} hover>
                    <TableCell>{item.name}</TableCell>
                    <TableCell>{item.uom || '—'}</TableCell>
                    <TableCell align="right">{stockLabel(item)}</TableCell>
                    <TableCell align="right">
                      {item.minimum_stock_level != null ? item.minimum_stock_level : '—'}
                    </TableCell>
                    <TableCell>
                      {item.stock_quantity == null ? (
                        <Chip size="small" label="Untracked" variant="outlined" />
                      ) : isLow(item) ? (
                        <Chip size="small" color="warning" label="Low" />
                      ) : (
                        <Chip size="small" color="success" variant="outlined" label="OK" />
                      )}
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableCard>
        )}
      </Stack>
    </PageShell>
  );
}
