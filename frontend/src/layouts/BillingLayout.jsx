import CategoryOutlinedIcon from '@mui/icons-material/CategoryOutlined';
import DashboardOutlinedIcon from '@mui/icons-material/DashboardOutlined';
import LockOutlinedIcon from '@mui/icons-material/LockOutlined';
import LogoutOutlinedIcon from '@mui/icons-material/LogoutOutlined';
import MenuIcon from '@mui/icons-material/Menu';
import PersonOutlinedIcon from '@mui/icons-material/PersonOutlined';
import Inventory2OutlinedIcon from '@mui/icons-material/Inventory2Outlined';
import PointOfSaleOutlinedIcon from '@mui/icons-material/PointOfSaleOutlined';
import ReceiptLongOutlinedIcon from '@mui/icons-material/ReceiptLongOutlined';
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
import { useMemo, useState } from 'react';
import { NavLink, Outlet, useLocation, useNavigate } from 'react-router-dom';
import MainContent from '../components/MainContent';
import PageHeader from '../components/PageHeader';
import RouteErrorBoundary from '../components/RouteErrorBoundary';
import ThemeModeToggle from '../components/ThemeModeToggle';
import NotificationBell from '../components/NotificationBell';
import { useAuth } from '../context/AuthContext';
import { PageActionsProvider, PageActionsSlot } from '../context/PageActionsContext';
import { DRAWER_WIDTH } from './shell';
import { logoutRequest } from '../services/authService';
import { PATHS } from '../routes/paths';

const drawerWidth = DRAWER_WIDTH;

const billingNav = [
  { to: PATHS.billingHome, label: 'Dashboard', icon: <PointOfSaleOutlinedIcon />, end: true },
  { to: PATHS.billingNew, label: 'New Bill', icon: <ReceiptLongOutlinedIcon /> },
  { to: PATHS.billingBills, label: 'Bills', icon: <ReceiptLongOutlinedIcon /> },
  { to: PATHS.billingItems, label: 'Items', icon: <Inventory2OutlinedIcon /> },
  { to: PATHS.billingCategories, label: 'Categories', icon: <CategoryOutlinedIcon /> },
  { to: PATHS.billingProfile, label: 'Profile', icon: <PersonOutlinedIcon /> },
];

function pageMeta(pathname) {
  if (pathname === PATHS.billingHome || pathname === `${PATHS.billingHome}/`) {
    return {
      title: 'Billing Dashboard',
      subtitle: "Today's billing overview and quick actions.",
    };
  }
  if (pathname.startsWith(PATHS.billingNew)) {
    return {
      title: 'New Bill',
      subtitle: 'Create and manage the current customer bill.',
    };
  }
  if (pathname.startsWith(PATHS.billingBills)) {
    return {
      title: "Today's Bills",
      subtitle: 'Review bills generated today.',
    };
  }
  if (pathname.startsWith(PATHS.billingItems)) {
    return {
      title: 'Items',
      subtitle: 'Add and manage catalog items for billing.',
    };
  }
  if (pathname.startsWith(PATHS.billingCategories)) {
    return {
      title: 'Categories',
      subtitle: 'Browse categories available for billing items.',
    };
  }
  if (pathname.startsWith(PATHS.billingProfile)) {
    return {
      title: 'Profile',
      subtitle: 'Manage your personal account details.',
    };
  }
  if (pathname.startsWith(PATHS.billingChangePassword)) {
    return {
      title: 'Change Password',
      subtitle: 'Update your account password securely.',
    };
  }
  return { title: 'Billing', subtitle: '' };
}

export default function BillingLayout() {
  const { user, role, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  const [mobileOpen, setMobileOpen] = useState(false);
  const [anchorEl, setAnchorEl] = useState(null);
  const isOwner = role === 'OWNER';

  const navItems = useMemo(() => {
    if (!isOwner) {
      return [
        { to: PATHS.billingHome, label: 'Dashboard', icon: <DashboardOutlinedIcon />, end: true },
        ...billingNav.slice(1),
      ];
    }
    return [
      {
        to: PATHS.ownerDashboard,
        label: 'Owner Dashboard',
        icon: <DashboardOutlinedIcon />,
        end: true,
      },
      ...billingNav,
    ];
  }, [isOwner]);

  const meta = pageMeta(location.pathname);

  const onLogout = async () => {
    try {
      await logoutRequest();
    } catch {
      // continue local logout
    }
    logout();
    navigate(PATHS.login, { replace: true });
  };

  const drawer = (
    <Box sx={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
      <Toolbar sx={{ px: 2 }}>
        <Box sx={{ minWidth: 0, width: '100%' }}>
          <Tooltip title={user?.tenant?.business_name || 'Billing'}>
            <Typography variant="subtitle1" fontWeight={700} noWrap>
              {user?.tenant?.business_name || 'Billing'}
            </Typography>
          </Tooltip>
          <Typography variant="caption" color="text.secondary">
            {isOwner ? 'Owner · Billing' : 'Billing'}
          </Typography>
        </Box>
      </Toolbar>
      <Divider />
      <List sx={{ px: 1, pt: 1, flexGrow: 1 }}>
        {navItems.map((item) => (
          <ListItemButton
            key={`${item.to}-${item.label}`}
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
        <Toolbar sx={{ px: { xs: 1, sm: 2 }, gap: 0.5, minHeight: { xs: 56, sm: 64 } }}>
          {isMobile ? (
            <IconButton edge="start" onClick={() => setMobileOpen(true)} sx={{ mr: 0.5 }} aria-label="Open menu">
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
                : meta.title}
            </Typography>
          </Box>
          <Chip
            size="small"
            label={isOwner ? 'OWNER' : 'BILLING'}
            color={isOwner ? 'primary' : 'default'}
            variant="outlined"
            sx={{ mr: 0.5, display: { xs: 'none', sm: 'inline-flex' } }}
          />
          <NotificationBell />
          <ThemeModeToggle sx={{ mr: 0.25 }} />
          <Tooltip title="Account menu">
            <IconButton onClick={(e) => setAnchorEl(e.currentTarget)} aria-label="Account menu">
              <PersonOutlinedIcon />
            </IconButton>
          </Tooltip>
          <Menu anchorEl={anchorEl} open={Boolean(anchorEl)} onClose={() => setAnchorEl(null)}>
            <MenuItem disabled>
              <Box>
                <Typography variant="body2" fontWeight={600}>{user?.name}</Typography>
                <Typography variant="caption" color="text.secondary">{user?.email}</Typography>
              </Box>
            </MenuItem>
            <Divider />
            {isOwner ? (
              <MenuItem
                onClick={() => {
                  setAnchorEl(null);
                  navigate(PATHS.ownerDashboard);
                }}
              >
                <ListItemIcon><DashboardOutlinedIcon fontSize="small" /></ListItemIcon>
                Owner Dashboard
              </MenuItem>
            ) : null}
            <MenuItem
              onClick={() => {
                setAnchorEl(null);
                navigate(PATHS.billingProfile);
              }}
            >
              <ListItemIcon><PersonOutlinedIcon fontSize="small" /></ListItemIcon>
              Profile
            </MenuItem>
            <MenuItem
              onClick={() => {
                setAnchorEl(null);
                navigate(PATHS.billingChangePassword);
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
          <BillingMain meta={meta} />
        </PageActionsProvider>
      </Box>
    </Box>
  );
}

function BillingMain({ meta }) {
  const location = useLocation();
  return (
    <MainContent>
      <PageHeader
        title={meta.title}
        subtitle={meta.subtitle}
        actions={<PageActionsSlot />}
      />
      <RouteErrorBoundary key={location.pathname}>
        <Outlet />
      </RouteErrorBoundary>
    </MainContent>
  );
}
