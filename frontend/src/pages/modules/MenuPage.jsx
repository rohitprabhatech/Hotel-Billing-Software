import RestaurantMenuOutlinedIcon from '@mui/icons-material/RestaurantMenuOutlined';
import TableRestaurantOutlinedIcon from '@mui/icons-material/TableRestaurantOutlined';
import Inventory2OutlinedIcon from '@mui/icons-material/Inventory2Outlined';
import {
  Alert,
  Box,
  Button,
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
  Typography,
} from '@mui/material';
import { useEffect, useState } from 'react';
import { Link as RouterLink } from 'react-router-dom';
import EmptyState from '../../components/EmptyState';
import LoadingBlock from '../../components/LoadingBlock';
import PageShell from '../../components/PageShell';
import Section from '../../components/Section';
import TableCard from '../../components/TableCard';
import TruncateText from '../../components/TruncateText';
import StatusBadge from '../../components/ui/StatusBadge';
import { useAuth } from '../../context/AuthContext';
import { useModuleGate } from '../../context/ModulesContext';
import { PATHS } from '../../routes/paths';
import { fetchMenu } from '../../services/menuService';
import { formatCategoryPath } from '../../utils/categoryHierarchy';

function money(value) {
  return `₹${Number(value || 0).toLocaleString('en-IN', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  })}`;
}

function vegLabel(isVeg) {
  if (isVeg === true) return 'Veg';
  if (isVeg === false) return 'Non-veg';
  return '—';
}

export default function MenuPage() {
  const { role } = useAuth();
  const moduleEnabled = useModuleGate('restaurant_menu');
  const itemsPath = role === 'OWNER' ? PATHS.ownerItems : PATHS.billingItems;
  const [sections, setSections] = useState([]);
  const [meta, setMeta] = useState({ total_sections: 0, total_items: 0 });
  const [vegFilter, setVegFilter] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const load = async () => {
    setLoading(true);
    setError('');
    try {
      const params = {};
      if (vegFilter === 'veg') params.is_veg = true;
      if (vegFilter === 'nonveg') params.is_veg = false;
      const response = await fetchMenu(params);
      setSections(response.data || []);
      setMeta(response.meta || { total_sections: 0, total_items: 0 });
    } catch (err) {
      setError(err.response?.data?.error?.message || 'Unable to load menu.');
      setSections([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (moduleEnabled) load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [moduleEnabled, vegFilter]);

  if (!moduleEnabled) {
    return (
      <PageShell>
        <Alert severity="warning">
          Restaurant menu is not enabled for this business type.
        </Alert>
      </PageShell>
    );
  }

  return (
    <PageShell>
      <Stack spacing={2}>
        {error ? <Alert severity="error">{error}</Alert> : null}

        <Stack
          direction={{ xs: 'column', sm: 'row' }}
          spacing={1.5}
          alignItems={{ sm: 'center' }}
          justifyContent="space-between"
        >
          <Typography variant="body2" color="text.secondary">
            {meta.total_items} menu item{meta.total_items === 1 ? '' : 's'} across{' '}
            {meta.total_sections} course{meta.total_sections === 1 ? '' : 's'}
          </Typography>
          <Stack direction="row" spacing={1} flexWrap="wrap" useFlexGap>
            <FormControl size="small" sx={{ minWidth: 160 }}>
              <InputLabel id="menu-veg-filter">Diet filter</InputLabel>
              <Select
                labelId="menu-veg-filter"
                label="Diet filter"
                value={vegFilter}
                onChange={(e) => setVegFilter(e.target.value)}
              >
                <MenuItem value="">All items</MenuItem>
                <MenuItem value="veg">Veg only</MenuItem>
                <MenuItem value="nonveg">Non-veg only</MenuItem>
              </Select>
            </FormControl>
            <Button component={RouterLink} to={itemsPath} variant="outlined" size="small">
              Manage items
            </Button>
          </Stack>
        </Stack>

        {loading ? (
          <LoadingBlock />
        ) : sections.length === 0 ? (
          <EmptyState
            title="No menu items yet"
            description="Mark catalog items as menu items on the Items page to show them here."
            action={
              <Button component={RouterLink} to={itemsPath} variant="contained">
                Go to Items
              </Button>
            }
          />
        ) : (
          sections.map((section) => (
            <Section
              key={section.category_id}
              title={formatCategoryPath(section.category_hierarchy_path || section.category_name)}
            >
              <TableCard>
                <Table size="small">
                  <TableHead>
                    <TableRow>
                      <TableCell>Item</TableCell>
                      <TableCell>Diet</TableCell>
                      <TableCell align="right">Price</TableCell>
                      <TableCell align="right">GST</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {section.items.map((item) => (
                      <TableRow key={item.id} hover>
                        <TableCell>
                          <TruncateText value={item.name} maxWidth={240} />
                          {item.description ? (
                            <Typography variant="caption" color="text.secondary" display="block">
                              {item.description}
                            </Typography>
                          ) : null}
                        </TableCell>
                        <TableCell>
                          <StatusBadge
                            label={vegLabel(item.is_veg)}
                            variant={
                              item.is_veg === true ? 'active' : item.is_veg === false ? 'pending' : 'info'
                            }
                          />
                        </TableCell>
                        <TableCell align="right">{money(item.price)}</TableCell>
                        <TableCell align="right">{Number(item.gst_percentage).toFixed(2)}%</TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableCard>
            </Section>
          ))
        )}
      </Stack>
    </PageShell>
  );
}

export function RestaurantDashboardWidgets() {
  const moduleEnabled = useModuleGate('restaurant_menu');
  if (!moduleEnabled) return null;

  return (
    <Section title="Restaurant">
      <Stack direction={{ xs: 'column', sm: 'row' }} spacing={1.5} flexWrap="wrap" useFlexGap>
        <Button
          component={RouterLink}
          to={PATHS.ownerMenu}
          variant="outlined"
          startIcon={<RestaurantMenuOutlinedIcon />}
        >
          Menu
        </Button>
        <Button
          component={RouterLink}
          to={PATHS.ownerTables}
          variant="outlined"
          startIcon={<TableRestaurantOutlinedIcon />}
        >
          Tables
        </Button>
        <Button
          component={RouterLink}
          to={PATHS.ownerItems}
          variant="outlined"
          startIcon={<Inventory2OutlinedIcon />}
        >
          Items
        </Button>
      </Stack>
      <Box sx={{ mt: 1.5 }}>
        <Typography variant="body2" color="text.secondary">
          Configure menu items with course categories (Starters, Main Course, Beverages) and veg flags.
        </Typography>
      </Box>
    </Section>
  );
}
