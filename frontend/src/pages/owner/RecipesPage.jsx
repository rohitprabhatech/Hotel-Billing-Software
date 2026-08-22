import AddOutlinedIcon from '@mui/icons-material/AddOutlined';
import DeleteOutlinedIcon from '@mui/icons-material/DeleteOutlined';
import {
  Alert,
  Autocomplete,
  Box,
  Button,
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
import { listItems } from '../../services/itemService';
import { createRecipe, deleteRecipe, listRecipes } from '../../services/recipeService';

const emptyLine = () => ({ ingredient_item_id: '', quantity: '' });

export default function RecipesPage() {
  const moduleEnabled = useModuleGate('recipe');
  const { canManageRecipes } = usePermissions();
  const [recipes, setRecipes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [open, setOpen] = useState(false);
  const [saving, setSaving] = useState(false);
  const [menuItems, setMenuItems] = useState([]);
  const [ingredients, setIngredients] = useState([]);
  const [form, setForm] = useState({
    menu_item_id: '',
    yield_quantity: '1',
    lines: [emptyLine()],
  });

  const ingredientOptions = useMemo(
    () => ingredients.filter((item) => item.is_active && !item.is_menu),
    [ingredients],
  );

  const load = useCallback(async () => {
    if (!moduleEnabled) return;
    setLoading(true);
    setError('');
    try {
      const [recipeRes, itemRes] = await Promise.all([
        listRecipes({ per_page: 100 }),
        listItems({ per_page: 500 }),
      ]);
      setRecipes(recipeRes.data || []);
      const items = itemRes.data || [];
      setMenuItems(items.filter((item) => item.is_menu && item.is_active));
      setIngredients(items);
    } catch (err) {
      setError(err.response?.data?.error?.message || 'Unable to load recipes.');
    } finally {
      setLoading(false);
    }
  }, [moduleEnabled]);

  useEffect(() => {
    load();
  }, [load]);

  const onCreate = async () => {
    setSaving(true);
    setError('');
    try {
      const payload = {
        menu_item_id: form.menu_item_id,
        yield_quantity: Number(form.yield_quantity || 1),
        ingredients: form.lines
          .filter((line) => line.ingredient_item_id && line.quantity)
          .map((line) => ({
            ingredient_item_id: line.ingredient_item_id,
            quantity: Number(line.quantity),
          })),
      };
      await createRecipe(payload);
      setOpen(false);
      setForm({ menu_item_id: '', yield_quantity: '1', lines: [emptyLine()] });
      await load();
    } catch (err) {
      setError(err.response?.data?.error?.message || 'Unable to save recipe.');
    } finally {
      setSaving(false);
    }
  };

  const onDelete = async (id) => {
    if (!window.confirm('Delete this recipe?')) return;
    try {
      await deleteRecipe(id);
      await load();
    } catch (err) {
      setError(err.response?.data?.error?.message || 'Unable to delete recipe.');
    }
  };

  if (!moduleEnabled) {
    return (
      <PageShell>
        <Alert severity="warning">Recipes module is not enabled for this business type.</Alert>
      </PageShell>
    );
  }

  return (
    <>
      {canManageRecipes ? (
        <PageActions>
          <Button variant="contained" startIcon={<AddOutlinedIcon />} onClick={() => setOpen(true)}>
            New recipe
          </Button>
        </PageActions>
      ) : null}

      <PageShell>
        <Stack spacing={2}>
          <Typography variant="body2" color="text.secondary">
            Ingredients deduct from stock when an order is settled (not when KOT is fired).
          </Typography>
          {error ? <Alert severity="error">{error}</Alert> : null}
          <TableCard>
            {loading ? (
              <LoadingBlock />
            ) : recipes.length === 0 ? (
              <EmptyState
                title="No recipes yet"
                description="Link menu items to ingredient BOMs for automatic stock deduction on settle."
                actionLabel={canManageRecipes ? 'New recipe' : undefined}
                onAction={canManageRecipes ? () => setOpen(true) : undefined}
              />
            ) : (
              <Table size="small">
                <TableHead>
                  <TableRow>
                    <TableCell>Menu item</TableCell>
                    <TableCell>Recipe name</TableCell>
                    <TableCell align="right">Ingredients</TableCell>
                    <TableCell align="right">Yield</TableCell>
                    {canManageRecipes ? <TableCell align="right">Actions</TableCell> : null}
                  </TableRow>
                </TableHead>
                <TableBody>
                  {recipes.map((recipe) => (
                    <TableRow key={recipe.id}>
                      <TableCell>{recipe.menu_item_name}</TableCell>
                      <TableCell>{recipe.name}</TableCell>
                      <TableCell align="right">{recipe.ingredient_count}</TableCell>
                      <TableCell align="right">{recipe.yield_quantity}</TableCell>
                      {canManageRecipes ? (
                        <TableCell align="right">
                          <IconButton size="small" color="error" onClick={() => onDelete(recipe.id)}>
                            <DeleteOutlinedIcon fontSize="small" />
                          </IconButton>
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

      <Dialog open={open} onClose={() => setOpen(false)} fullWidth maxWidth="md">
        <DialogTitle>New recipe (BOM)</DialogTitle>
        <DialogContent>
          <Stack spacing={2} sx={{ mt: 1 }}>
            <Autocomplete
              options={menuItems}
              getOptionLabel={(option) => option.name}
              value={menuItems.find((item) => item.id === form.menu_item_id) || null}
              onChange={(_, value) => setForm((prev) => ({ ...prev, menu_item_id: value?.id || '' }))}
              renderInput={(params) => <TextField {...params} label="Menu item" required />}
            />
            <TextField
              label="Yield quantity (portions)"
              type="number"
              value={form.yield_quantity}
              onChange={(e) => setForm((prev) => ({ ...prev, yield_quantity: e.target.value }))}
              inputProps={{ min: 0.001, step: '0.001' }}
            />
            <Typography variant="subtitle2">Ingredients per yield</Typography>
            {form.lines.map((line, index) => (
              <Stack key={index} direction={{ xs: 'column', sm: 'row' }} spacing={1} alignItems="center">
                <Autocomplete
                  sx={{ flex: 2 }}
                  options={ingredientOptions}
                  getOptionLabel={(option) => `${option.name} (${option.uom || 'pcs'})`}
                  value={ingredientOptions.find((item) => item.id === line.ingredient_item_id) || null}
                  onChange={(_, value) =>
                    setForm((prev) => ({
                      ...prev,
                      lines: prev.lines.map((row, i) =>
                        i === index ? { ...row, ingredient_item_id: value?.id || '' } : row,
                      ),
                    }))
                  }
                  renderInput={(params) => <TextField {...params} label="Ingredient" />}
                />
                <TextField
                  sx={{ flex: 1 }}
                  label="Qty"
                  type="number"
                  value={line.quantity}
                  onChange={(e) =>
                    setForm((prev) => ({
                      ...prev,
                      lines: prev.lines.map((row, i) =>
                        i === index ? { ...row, quantity: e.target.value } : row,
                      ),
                    }))
                  }
                />
                <IconButton
                  color="error"
                  disabled={form.lines.length <= 1}
                  onClick={() =>
                    setForm((prev) => ({
                      ...prev,
                      lines: prev.lines.filter((_, i) => i !== index),
                    }))
                  }
                >
                  <DeleteOutlinedIcon />
                </IconButton>
              </Stack>
            ))}
            <Box>
              <Button onClick={() => setForm((prev) => ({ ...prev, lines: [...prev.lines, emptyLine()] }))}>
                Add ingredient line
              </Button>
            </Box>
          </Stack>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpen(false)}>Cancel</Button>
          <Button variant="contained" disabled={saving} onClick={onCreate}>
            {saving ? 'Saving…' : 'Save recipe'}
          </Button>
        </DialogActions>
      </Dialog>
    </>
  );
}
