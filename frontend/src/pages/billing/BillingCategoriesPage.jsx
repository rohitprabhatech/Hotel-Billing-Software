import { Alert, Chip, Stack, Table, TableBody, TableCell, TableHead, TableRow, Typography } from '@mui/material';
import { useEffect, useMemo, useState } from 'react';
import EmptyState from '../../components/EmptyState';
import LoadingBlock from '../../components/LoadingBlock';
import PageShell from '../../components/PageShell';
import TableCard from '../../components/TableCard';
import TruncateText from '../../components/TruncateText';
import { listCategories } from '../../services/categoryService';
import { buildHierarchyRows } from '../../utils/categoryHierarchy';

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
          <LoadingBlock />
        ) : (
          <Table size="small" sx={{ minWidth: 640 }}>
            <TableHead>
              <TableRow>
                <TableCell>Category Name</TableCell>
                <TableCell>Type</TableCell>
                <TableCell>Description</TableCell>
                <TableCell>Parent Category</TableCell>
                <TableCell>Status</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {hierarchyRows.map(({ category, depth }) => {
                const isMain = !category.parent_id;
                return (
                  <TableRow key={category.id} hover>
                    <TableCell>
                      <Typography
                        variant="body2"
                        sx={{
                          pl: depth * 2,
                          fontWeight: isMain ? 650 : 500,
                          color: category.is_active ? 'text.primary' : 'text.secondary',
                        }}
                      >
                        {depth > 0 ? `${'· '.repeat(Math.min(depth, 3))}→ ` : ''}
                        {category.name}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Chip
                        size="small"
                        label={isMain ? 'Main' : 'Sub'}
                        variant={isMain ? 'filled' : 'outlined'}
                        color={isMain ? 'primary' : 'default'}
                        sx={{ fontWeight: 600 }}
                      />
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
                    <TableCell>
                      <Stack direction="row" alignItems="center" spacing={1}>
                        <Chip
                          size="small"
                          label={category.is_active ? 'Active' : 'Inactive'}
                          color={category.is_active ? 'success' : 'default'}
                          variant="outlined"
                        />
                      </Stack>
                    </TableCell>
                  </TableRow>
                );
              })}
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
