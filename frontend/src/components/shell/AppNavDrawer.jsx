import {
  Box,
  Divider,
  List,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Toolbar,
  Tooltip,
  Typography,
} from '@mui/material';
import { useTheme } from '@mui/material/styles';
import { NavLink } from 'react-router-dom';
import { navItemSx, navSectionSx, sidebarTokens } from './navStyles';

/**
 * Professional sidebar navigation shared by Owner, Billing, and Master layouts.
 */
export default function AppNavDrawer({
  brandTitle,
  brandSubtitle,
  brandLogo = null,
  navItems = [],
  onNavigate,
  resolveLabel,
}) {
  const theme = useTheme();
  const tokens = sidebarTokens(theme.palette.mode);

  return (
    <Box
      sx={{
        display: 'flex',
        flexDirection: 'column',
        height: '100%',
        bgcolor: tokens.background,
        color: tokens.text,
      }}
    >
      <Toolbar sx={{ px: 2, minHeight: { xs: 56, sm: 64 } }}>
        {brandLogo ? (
          <Box sx={{ minWidth: 0, width: '100%' }}>{brandLogo}</Box>
        ) : (
          <Box sx={{ minWidth: 0, width: '100%' }}>
            <Tooltip title={brandTitle || ''}>
              <Typography variant="subtitle1" fontWeight={700} noWrap sx={{ color: tokens.text }}>
                {brandTitle}
              </Typography>
            </Tooltip>
            {brandSubtitle ? (
              <Typography variant="caption" sx={{ color: tokens.textMuted }}>
                {brandSubtitle}
              </Typography>
            ) : null}
          </Box>
        )}
      </Toolbar>
      <Divider sx={{ borderColor: tokens.border }} />
      <List
        sx={{
          px: 1,
          pt: 0.75,
          pb: 1.5,
          flexGrow: 1,
          overflowY: 'auto',
          '&::-webkit-scrollbar': { width: 6 },
          '&::-webkit-scrollbar-thumb': {
            bgcolor: 'rgba(255,255,255,0.12)',
            borderRadius: 8,
          },
        }}
      >
        {navItems.map((item, index) => {
          if (item.type === 'section') {
            return (
              <Typography
                key={`section-${item.label}-${index}`}
                variant="caption"
                sx={navSectionSx(tokens, { first: index === 0 })}
              >
                {item.label}
              </Typography>
            );
          }

          const label = resolveLabel ? resolveLabel(item) : item.label;

          return (
            <ListItemButton
              key={`${item.to}-${item.label}`}
              component={NavLink}
              to={item.to}
              end={item.end}
              onClick={() => onNavigate?.()}
              sx={navItemSx(tokens, { emphasize: item.emphasize })}
            >
              <ListItemIcon>{item.icon}</ListItemIcon>
              <ListItemText
                primary={label}
                primaryTypographyProps={{
                  fontSize: '0.875rem',
                  fontWeight: item.emphasize ? 650 : 550,
                  noWrap: true,
                }}
              />
            </ListItemButton>
          );
        })}
      </List>
    </Box>
  );
}
