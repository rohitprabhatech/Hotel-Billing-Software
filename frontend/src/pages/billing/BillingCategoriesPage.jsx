import {
  Alert,
  Box,
  CircularProgress,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
  Typography,
} from '@mui/material';
import { useEffect, useMemo, useState } from 'react';
import EmptyState from '../../components/EmptyState';
import PageShell from '../../components/PageShell';
import TableCard from '../../components/TableCard';
import TruncateText from '../../components/TruncateText';
import { listCategories } from '../../services/categoryService';

function buildHierarchyRows(categories) {
  const byParent = new Map();
  categories.forEach((category) => {
    const key = category.parent_id || 'root';
    if (!byParent.has(key)) byParent.set(key, []);
    byParent.get(key).push(category);
  });
  byParent.forEach((list) => list.sort((a, b) => a.name.localeCompare(b.name)));

  const rows = [];
  const walk = (parentKey, depth) => {
    (byParent.get(parentKey) || []).forEach((category) => {
      rows.push({ category, depth });
      walk(category.id, depth + 1);
    });
  };
  walk('root', 0);
  return rows;
}

/**
 * Read-only category list for Billing Users (needed when assigning items to categories).
 * Category create/edit remains Owner-only.
 */
export default function BillingCategoriesPage() {
  const [categories, setCategories] = useState([]);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    listCategories()
      .then((res) => setCategories(res.data || []))
      .catch((err) => {
        setError(err.response?.data?.error?.message || 'Failed to load categories');
      })
      .finally(() => setLoading(false));
  }, []);

  const hierarchyRows = useMemo(() => buildHierarchyRows(categories), [categories]);

  return (
    <PageShell>
      {error ? <Alert severity="error">{error}</Alert> : null}

      <TableCard>
        {loading ? (
          <Box sx={{ py: 8, display: 'grid', placeItems: 'center' }}>
            <CircularProgress size={28} />
          </Box>
        ) : (
          <Table size="small" sx={{ minWidth: 640 }}>
            <TableHead>
              <TableRow>
                <TableCell>Name</TableCell>
                <TableCell>Description</TableCell>
                <TableCell>Parent Category</TableCell>
                <TableCell>Status</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {hierarchyRows.map(({ category, depth }) => (
                <TableRow key={category.id} hover>
                  <TableCell>
                    <Typography
                      variant="body2"
                      sx={{ pl: depth * 2, fontWeight: depth === 0 ? 650 : 500 }}
                    >
                      {depth > 0 ? '└ ' : ''}
                      {category.name}
                    </Typography>
                  </TableCell>
                  <TableCell>
                    <TruncateText value={category.description || '—'} maxWidth={220} />
                  </TableCell>
                  <TableCell>
                    <TruncateText
                      value={category.parent_category_name || 'No Parent / Main Category'}
                      maxWidth={140}
                    />
                  </TableCell>
                  <TableCell>{category.is_active ? 'Active' : 'Inactive'}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        )}
        {!loading && !categories.length ? (
          <EmptyState
            title="No categories found"
            description="Ask the business owner to add categories for this workspace."
          />
        ) : null}
      </TableCard>
    </PageShell>
  );
}
