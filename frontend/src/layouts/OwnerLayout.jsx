import AssessmentOutlinedIcon from '@mui/icons-material/AssessmentOutlined';
import AutoAwesomeOutlinedIcon from '@mui/icons-material/AutoAwesomeOutlined';
import CategoryOutlinedIcon from '@mui/icons-material/CategoryOutlined';
import DashboardOutlinedIcon from '@mui/icons-material/DashboardOutlined';
import HistoryOutlinedIcon from '@mui/icons-material/HistoryOutlined';
import LockOutlinedIcon from '@mui/icons-material/LockOutlined';
import LogoutOutlinedIcon from '@mui/icons-material/LogoutOutlined';
import MenuIcon from '@mui/icons-material/Menu';
import PeopleOutlinedIcon from '@mui/icons-material/PeopleOutlined';
import PersonOutlinedIcon from '@mui/icons-material/PersonOutlined';
import PointOfSaleOutlinedIcon from '@mui/icons-material/PointOfSaleOutlined';
import ReceiptLongOutlinedIcon from '@mui/icons-material/ReceiptLongOutlined';
import Inventory2OutlinedIcon from '@mui/icons-material/Inventory2Outlined';
import SettingsOutlinedIcon from '@mui/icons-material/SettingsOutlined';
import {
  AppBar,
  Box,
  Chip,
  Divider,
  Drawer,
  IconButton,
  List,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Menu,
  MenuItem,
  Toolbar,
  Tooltip,
  Typography,
  useMediaQuery,
} from '@mui/material';
import { useTheme } from '@mui/material/styles';
import { useState } from 'react';
import { NavLink, Outlet, useLocation, useNavigate } from 'react-router-dom';
import MainContent from '../components/MainContent';
import PageHeader from '../components/PageHeader';
import ThemeModeToggle from '../components/ThemeModeToggle';
import { useAuth } from '../context/AuthContext';
import { PageActionsProvider, PageActionsSlot } from '../context/PageActionsContext';
import { DRAWER_WIDTH } from './shell';
import { logoutRequest } from '../services/authService';
import { PATHS } from '../routes/paths';

const drawerWidth = DRAWER_WIDTH;

const navItems = [
  { to: PATHS.ownerDashboard, label: 'Dashboard', icon: <DashboardOutlinedIcon />, end: true },
  { to: PATHS.billingHome, label: 'Billing', icon: <PointOfSaleOutlinedIcon /> },
  { to: PATHS.ownerBills, label: 'Bills', icon: <ReceiptLongOutlinedIcon /> },
  { to: PATHS.ownerItems, label: 'Items', icon: <Inventory2OutlinedIcon /> },
  { to: PATHS.ownerItemActivity, label: 'Item Activity', icon: <HistoryOutlinedIcon /> },
  { to: PATHS.ownerCategories, label: 'Categories', icon: <CategoryOutlinedIcon /> },
  { to: PATHS.ownerReports, label: 'Sales Reports', icon: <AssessmentOutlinedIcon /> },
  { to: PATHS.ownerAi, label: 'AI Assistant', icon: <AutoAwesomeOutlinedIcon /> },
  { to: PATHS.ownerAudit, label: 'Audit & Activity', icon: <HistoryOutlinedIcon /> },
  { to: PATHS.ownerUsers, label: 'Users', icon: <PeopleOutlinedIcon /> },
  { to: PATHS.ownerSettings, label: 'Settings', icon: <SettingsOutlinedIcon /> },
  { to: PATHS.ownerProfile, label: 'Profile', icon: <PersonOutlinedIcon /> },
];

const titles = {
  [PATHS.ownerDashboard]: {
    title: 'Owner Dashboard',
    hidePageHeader: true,
  },
  [PATHS.ownerBills]: {
    title: 'Bills',
    subtitle: 'Review billing history for your business.',
  },
  [PATHS.ownerItems]: {
    title: 'Items',
    subtitle: 'Manage catalog items, pricing, GST, SKU, and stock.',
  },
  [PATHS.ownerItemActivity]: {
    title: 'Item Activity',
    subtitle: 'See who created, edited, or deactivated items.',
  },
  [PATHS.ownerCategories]: {
    title: 'Categories',
    subtitle: 'Organize business items with main and child categories.',
  },
  [PATHS.ownerReports]: {
    title: 'Sales Reports',
    subtitle: 'Review your business sales performance.',
  },
  [PATHS.ownerAi]: {
    title: 'AI Business Assistant',
    subtitle:
      'Sales analysis and decision support from real billing history — never invents numbers.',
  },
  [PATHS.ownerAudit]: {
    title: 'Audit Activity',
    subtitle: 'Track important activities across your business account.',
  },
  [PATHS.ownerUsers]: {
    title: 'Users',
    subtitle: 'Manage users who can access this billing system.',
  },
  [PATHS.ownerSettings]: {
    title: 'Settings',
    subtitle: 'Manage profile, business information, subscription, appearance, security, and account email.',
  },
  [PATHS.ownerProfile]: {
    title: 'Profile',
    subtitle: 'Manage your personal account details.',
  },
  [PATHS.ownerChangePassword]: {
    title: 'Change Password',
    subtitle: 'Update your account password securely.',
  },
};

export default function OwnerLayout() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  const [mobileOpen, setMobileOpen] = useState(false);
  const [anchorEl, setAnchorEl] = useState(null);

  const meta = titles[location.pathname] || {
    title: 'Owner Console',
    subtitle: '',
  };

  const onLogout = async () => {
    try {
      await logoutRequest();
    } catch {
      // Client logout proceeds even if API logout fails
    }
    logout();
    navigate(PATHS.login, { replace: true });
  };

  const drawer = (
    <Box sx={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
      <Toolbar sx={{ px: 2 }}>
        <Box sx={{ minWidth: 0, width: '100%' }}>
          <Tooltip title={user?.tenant?.business_name || 'Owner Dashboard'}>
            <Typography variant="subtitle1" fontWeight={700} noWrap>
              {user?.tenant?.business_name || 'Owner Dashboard'}
            </Typography>
          </Tooltip>
          <Typography variant="caption" color="text.secondary">
            Owner · Console
          </Typography>
        </Box>
      </Toolbar>
      <Divider />
      <List sx={{ px: 1, pt: 1, flexGrow: 1 }}>
        {navItems.map((item) => (
          <ListItemButton
            key={item.to}
            component={NavLink}
            to={item.to}
            end={item.end}
            onClick={() => setMobileOpen(false)}
            sx={{
              '&.active': {
                bgcolor: 'primary.main',
                color: 'primary.contrastText',
                '& .MuiListItemIcon-root': { color: 'inherit' },
              },
            }}
          >
            <ListItemIcon sx={{ minWidth: 40 }}>{item.icon}</ListItemIcon>
            <ListItemText primary={item.label} />
          </ListItemButton>
        ))}
      </List>
    </Box>
  );

  return (
    <Box sx={{ display: 'flex', minHeight: '100vh', bgcolor: 'background.default' }}>
      <AppBar
        position="fixed"
        sx={{
          width: { md: `calc(100% - ${drawerWidth}px)` },
          ml: { md: `${drawerWidth}px` },
        }}
      >
        <Toolbar>
          {isMobile ? (
            <IconButton edge="start" onClick={() => setMobileOpen(true)} sx={{ mr: 1 }} aria-label="Open menu">
              <MenuIcon />
            </IconButton>
          ) : null}
          <Box sx={{ flexGrow: 1, minWidth: 0, mr: 1 }}>
            <Tooltip title={user?.tenant?.business_name || 'Business Billing'}>
              <Typography variant="subtitle1" fontWeight={700} noWrap>
                {user?.tenant?.business_name || 'Business Billing'}
              </Typography>
            </Tooltip>
            <Typography variant="caption" color="text.secondary" noWrap>
              {user?.tenant?.business_type_label
                ? `${user.tenant.business_type_label} · ${meta.title}`
                : `Business Dashboard · ${meta.title}`}
            </Typography>
          </Box>
          <Chip size="small" label="OWNER" color="primary" variant="outlined" sx={{ mr: 1 }} />
          <ThemeModeToggle sx={{ mr: 0.5 }} />
          <Tooltip title="Account menu">
            <IconButton onClick={(e) => setAnchorEl(e.currentTarget)} aria-label="Account menu">
              <PersonOutlinedIcon />
            </IconButton>
          </Tooltip>
          <Menu
            anchorEl={anchorEl}
            open={Boolean(anchorEl)}
            onClose={() => setAnchorEl(null)}
          >
            <MenuItem disabled>
              <Box>
                <Typography variant="body2" fontWeight={600}>{user?.name}</Typography>
                <Typography variant="caption" color="text.secondary">{user?.email}</Typography>
              </Box>
            </MenuItem>
            <Divider />
            <MenuItem
              onClick={() => {
                setAnchorEl(null);
                navigate(PATHS.ownerProfile);
              }}
            >
              <ListItemIcon><PersonOutlinedIcon fontSize="small" /></ListItemIcon>
              Profile
            </MenuItem>
            <MenuItem
              onClick={() => {
                setAnchorEl(null);
                navigate(PATHS.ownerChangePassword);
              }}
            >
              <ListItemIcon><LockOutlinedIcon fontSize="small" /></ListItemIcon>
              Change Password
            </MenuItem>
            <MenuItem
              onClick={() => {
                setAnchorEl(null);
                onLogout();
              }}
            >
              <ListItemIcon><LogoutOutlinedIcon fontSize="small" /></ListItemIcon>
              Logout
            </MenuItem>
          </Menu>
        </Toolbar>
      </AppBar>

      <Box component="nav" sx={{ width: { md: drawerWidth }, flexShrink: { md: 0 } }}>
        <Drawer
          variant="temporary"
          open={mobileOpen}
          onClose={() => setMobileOpen(false)}
          ModalProps={{ keepMounted: true }}
          sx={{
            display: { xs: 'block', md: 'none' },
            [`& .MuiDrawer-paper`]: { width: drawerWidth, boxSizing: 'border-box' },
          }}
        >
          {drawer}
        </Drawer>
        <Drawer
          variant="permanent"
          open
          sx={{
            display: { xs: 'none', md: 'block' },
            [`& .MuiDrawer-paper`]: { width: drawerWidth, boxSizing: 'border-box' },
          }}
        >
          {drawer}
        </Drawer>
      </Box>

      <Box
        component="main"
        sx={{
          flexGrow: 1,
          width: { md: `calc(100% - ${drawerWidth}px)` },
          minWidth: 0,
          bgcolor: 'background.default',
        }}
      >
        <Toolbar />
        <PageActionsProvider>
          <OwnerMain meta={meta} />
        </PageActionsProvider>
      </Box>
    </Box>
  );
}

function OwnerMain({ meta }) {
  return (
    <MainContent>
      {!meta.hidePageHeader ? (
        <PageHeader
          title={meta.title}
          subtitle={meta.subtitle}
          actions={<PageActionsSlot />}
        />
      ) : null}
      <Outlet />
    </MainContent>
  );
}
