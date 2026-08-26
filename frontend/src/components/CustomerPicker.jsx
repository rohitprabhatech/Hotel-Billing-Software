import { Autocomplete, Box, CircularProgress, TextField, Typography } from '@mui/material';
import { useEffect, useMemo, useState } from 'react';
import { listCustomers } from '../services/customerService';

function formatCustomerLabel(customer) {
  if (!customer) return '';
  const parts = [customer.name];
  if (customer.phone_national) {
    parts.push(
      customer.phone_country_code
        ? `+${customer.phone_country_code} ${customer.phone_national}`
        : customer.phone_national,
    );
  } else if (customer.phone_masked) {
    parts.push(customer.phone_masked);
  }
  return parts.join(' · ');
}

export default function CustomerPicker({
  value,
  onChange,
  onClear,
  disabled = false,
  label = 'Select customer (optional)',
}) {
  const [inputValue, setInputValue] = useState('');
  const [options, setOptions] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    let active = true;
    const handle = window.setTimeout(async () => {
      setLoading(true);
      try {
        const res = await listCustomers({
          q: inputValue || undefined,
          is_active: true,
          per_page: 20,
        });
        if (active) setOptions(res.data || []);
      } catch {
        if (active) setOptions([]);
      } finally {
        if (active) setLoading(false);
      }
    }, 250);
    return () => {
      active = false;
      window.clearTimeout(handle);
    };
  }, [inputValue]);

  const selected = useMemo(
    () => options.find((row) => row.id === value?.id) || value || null,
    [options, value],
  );

  return (
    <Autocomplete
      value={selected}
      onChange={(_, next) => {
        if (!next) {
          onClear?.();
          return;
        }
        onChange?.(next);
      }}
      inputValue={inputValue}
      onInputChange={(_, next) => setInputValue(next)}
      options={options}
      loading={loading}
      disabled={disabled}
      getOptionLabel={(option) => formatCustomerLabel(option)}
      isOptionEqualToValue={(option, val) => option?.id === val?.id}
      filterOptions={(x) => x}
      renderOption={(props, option) => {
        const { key, ...liProps } = props;
        return (
          <Box component="li" key={option.id ?? key} {...liProps}>
            <Box sx={{ minWidth: 0 }}>
              <Typography variant="body2" fontWeight={600} noWrap>
                {option.name}
              </Typography>
              <Typography variant="caption" color="text.secondary" noWrap>
                {[option.phone_masked, option.email_masked].filter(Boolean).join(' · ') ||
                  'No contact'}
                {Number(option.balance || 0) > 0
                  ? ` · Due ₹${Number(option.balance).toFixed(2)}`
                  : ''}
              </Typography>
            </Box>
          </Box>
        );
      }}
      renderInput={(params) => {
        // MUI v6+ may omit params.InputProps; never read .endAdornment blindly.
        const inputSlot = params.InputProps ?? params.slotProps?.input ?? {};
        return (
          <TextField
            {...params}
            label={label}
            placeholder="Search by name or phone"
            InputProps={{
              ...inputSlot,
              endAdornment: (
                <>
                  {loading ? <CircularProgress color="inherit" size={18} /> : null}
                  {inputSlot.endAdornment}
                </>
              ),
            }}
          />
        );
      }}
    />
  );
}
