import { Autocomplete, Box, TextField, Typography } from '@mui/material';
import { useMemo } from 'react';
import {
  buildHierarchyRows,
  formatCategoryPath,
} from '../utils/categoryHierarchy';

function optionLabel(option) {
  if (!option) return '';
  if (option.isEmpty || option.isRoot) return option.name || '';
  return formatCategoryPath(option.hierarchy_path || option.name || '');
}

/**
 * Searchable category picker with hierarchy indentation.
 * Use for Items assign/filter and Categories parent selection.
 */
export default function CategoryHierarchyAutocomplete({
  categories = [],
  valueId = '',
  onChange,
  label = 'Category',
  helperText,
  required = false,
  disabled = false,
  allowEmpty = false,
  emptyOption = { id: '', name: 'All categories', isEmpty: true },
  excludeIds = [],
  activeOnly = true,
  includeInactiveIds = [],
  sx,
}) {
  const hierarchyRows = useMemo(() => buildHierarchyRows(categories), [categories]);

  const options = useMemo(() => {
    const excluded = new Set(excludeIds.filter(Boolean));
    const keepInactive = new Set(includeInactiveIds.filter(Boolean));
    const list = hierarchyRows
      .map(({ category, depth }) => ({ ...category, depth, isEmpty: false, isRoot: false }))
      .filter((category) => {
        if (excluded.has(category.id)) return false;
        if (activeOnly && !category.is_active && !keepInactive.has(category.id)) {
          return false;
        }
        return true;
      });
    return allowEmpty ? [emptyOption, ...list] : list;
  }, [
    allowEmpty,
    emptyOption,
    excludeIds,
    activeOnly,
    includeInactiveIds,
    hierarchyRows,
  ]);

  const value =
    options.find((option) => option.id === (valueId || '')) ||
    (allowEmpty ? emptyOption : null);

  return (
    <Autocomplete
      options={options}
      value={value}
      disabled={disabled}
      onChange={(_, option) => onChange?.(option?.id || '')}
      getOptionLabel={optionLabel}
      isOptionEqualToValue={(option, selected) => option.id === selected.id}
      filterOptions={(opts, state) => {
        const q = state.inputValue.trim().toLowerCase();
        if (!q) return opts;
        return opts.filter((option) => {
          if (option.isEmpty || option.isRoot) {
            return (option.name || '').toLowerCase().includes(q);
          }
          const hay = [option.name, option.hierarchy_path, option.parent_category_name]
            .filter(Boolean)
            .join(' ')
            .toLowerCase();
          return hay.includes(q);
        });
      }}
      renderOption={(props, option) => {
        const depth = option.isEmpty || option.isRoot ? 0 : option.depth || 0;
        const path = formatCategoryPath(option.hierarchy_path || '');
        return (
          <li {...props} key={option.id || 'empty'}>
            <Box sx={{ pl: depth * 1.5, py: 0.25 }}>
              <Typography
                variant="body2"
                fontWeight={option.isEmpty || option.isRoot || depth === 0 ? 650 : 500}
              >
                {option.isEmpty || option.isRoot
                  ? option.name
                  : depth > 0
                    ? `→ ${option.name}`
                    : option.name}
              </Typography>
              {!option.isEmpty &&
              !option.isRoot &&
              path &&
              path !== option.name ? (
                <Typography variant="caption" color="text.secondary" display="block">
                  {path}
                </Typography>
              ) : null}
            </Box>
          </li>
        );
      }}
      renderInput={(params) => (
        <TextField
          {...params}
          label={label}
          required={required}
          helperText={helperText}
        />
      )}
      sx={sx}
    />
  );
}
