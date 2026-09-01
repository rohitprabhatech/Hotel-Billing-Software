import { sidebar } from '../../theme/tokens';

export function sidebarTokens(mode = 'light') {
  return mode === 'dark' ? sidebar.dark : sidebar.light;
}

export function navItemSx(tokens, { emphasize = false } = {}) {
  return {
    borderRadius: `${8}px`,
    mb: 0.35,
    minHeight: 42,
    px: 1.25,
    color: tokens.text,
    transition: 'background-color 0.15s ease, color 0.15s ease',
    '& .MuiListItemIcon-root': {
      color: tokens.icon,
      minWidth: 36,
    },
    '&:hover': {
      bgcolor: tokens.hover,
    },
    '&.active': {
      bgcolor: tokens.active,
      color: tokens.activeText,
      '& .MuiListItemIcon-root': { color: 'inherit' },
    },
    ...(emphasize
      ? {
          border: '1px solid',
          borderColor: tokens.border,
          bgcolor: 'rgba(255, 255, 255, 0.04)',
          '&.active': {
            bgcolor: tokens.active,
            color: tokens.activeText,
            borderColor: tokens.active,
            '& .MuiListItemIcon-root': { color: 'inherit' },
          },
        }
      : null),
  };
}

export function navSectionSx(tokens, { first = false } = {}) {
  return {
    display: 'block',
    px: 1.5,
    pt: first ? 0.75 : 1.75,
    pb: 0.5,
    fontWeight: 700,
    letterSpacing: '0.08em',
    textTransform: 'uppercase',
    fontSize: '0.65rem',
    color: tokens.section,
  };
}
