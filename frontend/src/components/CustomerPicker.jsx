import { Autocomplete, Box, TextField, Typography } from '@mui/material';
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

/**
 * Customer search for billing. Compatible with MUI v9 Autocomplete:
 * do not touch params.InputProps (may be undefined); rely on built-in `loading`.
 */
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
        if (active) setOptions(Array.isArray(res.data) ? res.data : []);
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

  const selected = useMemo(() => {
    if (!value) return null;
    return options.find((row) => row?.id === value.id) || value;
  }, [options, value]);

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
      onInputChange={(_, next, reason) => {
        if (reason === 'reset' && !next && selected) return;
        setInputValue(next ?? '');
      }}
      options={options}
      loading={loading}
      disabled={disabled}
      clearOnBlur={false}
      handleHomeEndKeys
      getOptionLabel={(option) => {
        if (!option) return '';
        if (typeof option === 'string') return option;
        return formatCustomerLabel(option);
      }}
      isOptionEqualToValue={(option, val) => Boolean(option?.id && val?.id && option.id === val.id)}
      filterOptions={(x) => x}
      noOptionsText={loading ? 'Searching…' : 'No customers found'}
      renderOption={(props, option) => {
        const { key, ...liProps } = props;
        return (
          <Box component="li" key={option?.id ?? key} {...liProps}>
            <Box sx={{ minWidth: 0 }}>
              <Typography variant="body2" fontWeight={600} noWrap>
                {option?.name || 'Customer'}
              </Typography>
              <Typography variant="caption" color="text.secondary" noWrap>
                {[option?.phone_masked, option?.email_masked].filter(Boolean).join(' · ') ||
                  'No contact'}
                {Number(option?.balance || 0) > 0
                  ? ` · Due ₹${Number(option.balance).toFixed(2)}`
                  : ''}
              </Typography>
            </Box>
          </Box>
        );
      }}
      renderInput={(params) => (
        <TextField
          {...params}
          label={label}
          placeholder="Search by name or phone"
        />
      )}
    />
  );
}
