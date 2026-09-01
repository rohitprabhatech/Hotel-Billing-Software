import MenuIcon from '@mui/icons-material/Menu';
import PersonOutlinedIcon from '@mui/icons-material/PersonOutlined';
import {
  AppBar,
  Box,
  Chip,
  IconButton,
  Toolbar,
  Tooltip,
  Typography,
} from '@mui/material';
import { layout } from '../../theme/tokens';
import ThemeModeToggle from '../ThemeModeToggle';

export default function AppTopBar({
  isMobile,
  onMenuOpen,
  title,
  subtitle,
  badge = null,
  notificationSlot = null,
  accountMenu,
}) {
  return (
    <AppBar
      position="fixed"
      sx={{
        width: { md: `calc(100% - ${layout.drawerWidth}px)` },
        ml: { md: `${layout.drawerWidth}px` },
      }}
    >
      <Toolbar sx={{ px: { xs: 1, sm: 2 }, gap: 0.5, minHeight: { xs: layout.headerHeightMobile, sm: layout.headerHeight } }}>
        {isMobile ? (
          <IconButton edge="start" onClick={onMenuOpen} sx={{ mr: 0.5 }} aria-label="Open menu">
            <MenuIcon />
          </IconButton>
        ) : null}
        <Box sx={{ flexGrow: 1, minWidth: 0, mr: 1 }}>
          <Tooltip title={title || ''}>
            <Typography variant="subtitle1" fontWeight={700} noWrap>
              {title}
            </Typography>
          </Tooltip>
          {subtitle ? (
            <Typography variant="caption" color="text.secondary" noWrap>
              {subtitle}
            </Typography>
          ) : null}
        </Box>
        {badge ? (
          <Chip
            size="small"
            label={badge}
            color="primary"
            variant="outlined"
            sx={{ mr: 0.5, display: { xs: 'none', sm: 'inline-flex' } }}
          />
        ) : null}
        {notificationSlot}
        <ThemeModeToggle sx={{ mr: 0.25 }} />
        <Tooltip title="Account menu">
          <IconButton onClick={accountMenu.onOpen} aria-label="Account menu">
            <PersonOutlinedIcon />
          </IconButton>
        </Tooltip>
        {accountMenu.menu}
      </Toolbar>
    </AppBar>
  );
}
