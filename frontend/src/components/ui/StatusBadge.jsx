import { Chip } from '@mui/material';
import { useTheme } from '@mui/material/styles';
import { statusColors } from '../../theme/tokens';

const VARIANT_MAP = {
  active: 'active',
  paid: 'paid',
  pending: 'pending',
  cancelled: 'cancelled',
  canceled: 'cancelled',
  low: 'low',
  'low stock': 'low',
  available: 'active',
  unavailable: 'cancelled',
  preparing: 'pending',
  ready: 'info',
  completed: 'active',
  info: 'info',
};

function resolveVariant(label) {
  const key = String(label || '')
    .trim()
    .toLowerCase();
  return VARIANT_MAP[key] || 'info';
}

export default function StatusBadge({ label, variant, size = 'small', sx }) {
  const theme = useTheme();
  const isDark = theme.palette.mode === 'dark';
  const resolved = variant || resolveVariant(label);
  const palette = statusColors[resolved] || statusColors.info;

  return (
    <Chip
      label={label}
      size={size}
      sx={{
        height: size === 'small' ? 24 : 28,
        fontWeight: 600,
        fontSize: '0.75rem',
        bgcolor: isDark ? palette.darkBg : palette.bg,
        color: isDark ? palette.darkText : palette.text,
        border: 'none',
        ...sx,
      }}
    />
  );
}
