import SearchOutlinedIcon from '@mui/icons-material/SearchOutlined';
import { InputAdornment, TextField } from '@mui/material';

export default function SearchInput({
  value,
  onChange,
  placeholder = 'Search…',
  fullWidth = true,
  size = 'small',
  sx,
  ...rest
}) {
  return (
    <TextField
      value={value}
      onChange={onChange}
      placeholder={placeholder}
      fullWidth={fullWidth}
      size={size}
      sx={{ minWidth: { xs: '100%', sm: 220 }, ...sx }}
      slotProps={{
        input: {
          startAdornment: (
            <InputAdornment position="start">
              <SearchOutlinedIcon fontSize="small" color="action" />
            </InputAdornment>
          ),
        },
      }}
      {...rest}
    />
  );
}
