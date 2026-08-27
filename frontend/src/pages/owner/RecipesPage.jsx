import AddOutlinedIcon from '@mui/icons-material/AddOutlined';
import DeleteOutlinedIcon from '@mui/icons-material/DeleteOutlined';
import EditOutlinedIcon from '@mui/icons-material/EditOutlined';
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
  Tooltip,
  Typography,
} from '@mui/material';
import { useCallback, useEffect, useMemo, useState } from 'react';
import EmptyState from '../../components/EmptyState';
import LoadingBlock from '../../components/LoadingBlock';
import PageShell from '../../components/PageShell';
import TableCard from '../../components/TableCard';
import { PageActions } from '../../context/PageActionsContext';
import { useAuth } from '../../context/AuthContext';
import { useModuleGate } from '../../context/ModulesContext';
import { usePermissions } from '../../hooks/usePermissions';
import { listItems } from '../../services/itemService';
import {
  createRecipe,
  deleteRecipe,
  getRecipe,
  listRecipes,
  updateRecipe,
} from '../../services/recipeService';

const emptyLine = () => ({ ingredient_item_id: '', quantity: '' });

export default function RecipesPage() {
  const { user } = useAuth();
  const isHotel = user?.tenant?.business_type === 'hotel_restaurant';
  const moduleEnabled = useModuleGate('recipe');
  const { canManageRecipes } = usePermissions();
  const [recipes, setRecipes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [open, setOpen] = useState(false);
  const [editing, setEditing] = useState(null);
  const [saving, setSaving] = useState(false);
  const [menuItems, setMenuItems] = useState([]);
  const [ingredients, setIngredients] = useState([]);
  const [form, setForm] = useState({
    menu_item_id: '',
    name: '',
    yield_quantity: '1',
    lines: [emptyLine()],
  });

  const ingredientOptions = useMemo(
    () =>
      ingredients.filter(
        (item) =>
          item.is_active &&
          !item.is_menu &&
          item.id !== form.menu_item_id,
      ),
    [ingredients, form.menu_item_id],
  );

  const dishOptions = useMemo(() => {
    // Prefer menu dishes; for hotel also allow any active item so older catalog works.
    const menu = menuItems.filter((item) => item.is_active);
    if (menu.length) return menu;
    if (isHotel) {
      return ingredients.filter((item) => item.is_active);
    }
    return [];
  }, [menuItems, ingredients, isHotel]);

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

  const resetForm = () => {
    setEditing(null);
    setForm({ menu_item_id: '', name: '', yield_quantity: '1', lines: [emptyLine()] });
  };

  const openCreate = () => {
    resetForm();
    setOpen(true);
  };

  const openEdit = async (recipe) => {
    setError('');
    try {
      const res = await getRecipe(recipe.id);
      const detail = res.data || recipe;
      setEditing(detail);
      setForm({
        menu_item_id: detail.menu_item_id || '',
        name: detail.name || '',
        yield_quantity: String(detail.yield_quantity ?? 1),
        lines:
          (detail.ingredients || []).length > 0
            ? detail.ingredients.map((line) => ({
                ingredient_item_id: line.ingredient_item_id,
                quantity: String(line.quantity),
              }))
            : [emptyLine()],
      });
      setOpen(true);
    } catch (err) {
      setError(err.response?.data?.error?.message || 'Unable to load recipe.');
    }
  };

  const onSave = async () => {
    if (!form.menu_item_id) {
      setError('Select a menu dish.');
      return;
    }
    const ingredientsPayload = form.lines
      .filter((line) => line.ingredient_item_id && line.quantity)
      .map((line) => ({
        ingredient_item_id: line.ingredient_item_id,
        quantity: Number(line.quantity),
      }));
    if (!ingredientsPayload.length) {
      setError('Add at least one ingredient with quantity.');
      return;
    }
    setSaving(true);
    setError('');
    setSuccess('');
    try {
      if (editing) {
        await updateRecipe(editing.id, {
          name: form.name.trim() || undefined,
          yield_quantity: Number(form.yield_quantity || 1),
          ingredients: ingredientsPayload,
        });
        setSuccess('Recipe updated.');
      } else {
        await createRecipe({
          menu_item_id: form.menu_item_id,
          name: form.name.trim() || undefined,
          yield_quantity: Number(form.yield_quantity || 1),
          ingredients: ingredientsPayload,
        });
        setSuccess('Recipe created.');
      }
      setOpen(false);
      resetForm();
      await load();
    } catch (err) {
      setError(err.response?.data?.error?.message || 'Unable to save recipe.');
    } finally {
      setSaving(false);
    }
  };

  const onDelete = async (id) => {
    if (!window.confirm('Delete this recipe?')) return;
    setError('');
    try {
      await deleteRecipe(id);
      setSuccess('Recipe deleted.');
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
          <Button variant="contained" startIcon={<AddOutlinedIcon />} onClick={openCreate}>
            New recipe
          </Button>
        </PageActions>
      ) : null}

      <PageShell>
        <Stack spacing={2}>
          <Typography variant="body2" color="text.secondary">
            {isHotel
              ? 'Link each dish to raw ingredients. When you generate a bill, ingredient stock is deducted automatically (not the finished dish stock).'
              : 'Ingredients deduct from stock when an order is settled (not when KOT is fired).'}
          </Typography>
          <Alert severity="info">
            Create dishes as <strong>Menu dish</strong> items, and raw materials (rice, oil, veggies)
            as items with Menu dish turned OFF. Then map them here.
          </Alert>
          {error ? <Alert severity="error">{error}</Alert> : null}
          {success ? <Alert severity="success">{success}</Alert> : null}
          <TableCard>
            {loading ? (
              <LoadingBlock />
            ) : recipes.length === 0 ? (
              <EmptyState
                title="No recipes yet"
                description="Add a recipe so billing deducts ingredients when a dish is sold."
                actionLabel={canManageRecipes ? 'New recipe' : undefined}
                onAction={canManageRecipes ? openCreate : undefined}
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
                          <Stack direction="row" spacing={0.5} justifyContent="flex-end">
                            <Tooltip title="Edit Recipe">
                              <IconButton
                                size="small"
                                aria-label={`Edit ${recipe.name}`}
                                onClick={() => openEdit(recipe)}
                              >
                                <EditOutlinedIcon fontSize="small" />
                              </IconButton>
                            </Tooltip>
                            <Tooltip title="Delete Recipe">
                              <IconButton
                                size="small"
                                color="error"
                                aria-label={`Delete ${recipe.name}`}
                                onClick={() => onDelete(recipe.id)}
                              >
                                <DeleteOutlinedIcon fontSize="small" />
                              </IconButton>
                            </Tooltip>
                          </Stack>
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

      <Dialog
        open={open}
        onClose={() => {
          setOpen(false);
          resetForm();
        }}
        fullWidth
        maxWidth="md"
      >
        <DialogTitle>{editing ? 'Edit recipe' : 'New recipe (BOM)'}</DialogTitle>
        <DialogContent>
          <Stack spacing={2} sx={{ mt: 1 }}>
            {!dishOptions.length ? (
              <Alert severity="warning">
                No dishes found. Go to Items, create a dish, and enable &quot;Menu dish&quot;.
              </Alert>
            ) : null}
            {!ingredientOptions.length ? (
              <Alert severity="warning">
                No ingredient items found. Create raw items in Items with &quot;Menu dish&quot; turned
                OFF (example: Rice, Oil, Chicken).
              </Alert>
            ) : null}
            <Autocomplete
              options={dishOptions}
              getOptionLabel={(option) => option.name}
              disabled={Boolean(editing)}
              value={dishOptions.find((item) => item.id === form.menu_item_id) || null}
              onChange={(_, value) => setForm((prev) => ({ ...prev, menu_item_id: value?.id || '' }))}
              renderInput={(params) => <TextField {...params} label="Menu dish" required />}
            />
            <TextField
              label="Recipe name (optional)"
              value={form.name}
              onChange={(e) => setForm((prev) => ({ ...prev, name: e.target.value }))}
              fullWidth
            />
            <TextField
              label="Yield quantity (portions)"
              type="number"
              value={form.yield_quantity}
              onChange={(e) => setForm((prev) => ({ ...prev, yield_quantity: e.target.value }))}
              inputProps={{ min: 0.001, step: '0.001' }}
              helperText="For 1 plate sold, ingredients below are used once when yield = 1"
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
          <Button
            onClick={() => {
              setOpen(false);
              resetForm();
            }}
          >
            Cancel
          </Button>
          <Button variant="contained" disabled={saving} onClick={onSave}>
            {saving ? 'Saving…' : editing ? 'Save Changes' : 'Save recipe'}
          </Button>
        </DialogActions>
      </Dialog>
    </>
  );
}
