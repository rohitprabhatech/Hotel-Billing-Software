import CategoryOutlinedIcon from '@mui/icons-material/CategoryOutlined';
import DashboardOutlinedIcon from '@mui/icons-material/DashboardOutlined';
import LockOutlinedIcon from '@mui/icons-material/LockOutlined';
import LogoutOutlinedIcon from '@mui/icons-material/LogoutOutlined';
import MenuIcon from '@mui/icons-material/Menu';
import PersonOutlinedIcon from '@mui/icons-material/PersonOutlined';
import PointOfSaleOutlinedIcon from '@mui/icons-material/PointOfSaleOutlined';
import ReceiptLongOutlinedIcon from '@mui/icons-material/ReceiptLongOutlined';
import RestaurantMenuOutlinedIcon from '@mui/icons-material/RestaurantMenuOutlined';
import {
  AppBar,
  Box,
  Button,
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
import PageHeader from '../components/PageHeader';
import { useAuth } from '../context/AuthContext';
import { PageActionsProvider, PageActionsSlot } from '../context/PageActionsContext';
import { logoutRequest } from '../services/authService';
import { PATHS } from '../routes/paths';

const drawerWidth = 248;

const billingNav = [
  { to: PATHS.billingHome, label: 'Billing Home', icon: <PointOfSaleOutlinedIcon />, end: true },
  { to: PATHS.billingNew, label: 'New Bill', icon: <ReceiptLongOutlinedIcon /> },
  { to: PATHS.billingBills, label: 'Bills', icon: <ReceiptLongOutlinedIcon /> },
  { to: PATHS.billingItems, label: 'Items', icon: <RestaurantMenuOutlinedIcon /> },
  { to: PATHS.billingCategories, label: 'Categories', icon: <CategoryOutlinedIcon /> },
  { to: PATHS.billingProfile, label: 'Profile', icon: <PersonOutlinedIcon /> },
  { to: PATHS.billingChangePassword, label: 'Change Password', icon: <LockOutlinedIcon /> },
];

function pageMeta(pathname) {
  if (pathname === PATHS.billingHome || pathname === `${PATHS.billingHome}/`) {
    return {
      title: 'Billing Home',
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
      subtitle: "Manage your hotel's food and beverage items.",
    };
  }
  if (pathname.startsWith(PATHS.billingCategories)) {
    return {
      title: 'Categories',
      subtitle: 'Browse food and beverage categories.',
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
    // Owners: explicit return path to Owner Main Dashboard (root cause fix)
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

  const navButtonSx = {
    borderRadius: 2,
    mb: 0.5,
    '&.active': {
      bgcolor: 'primary.main',
      color: 'primary.contrastText',
      '& .MuiListItemIcon-root': { color: 'inherit' },
    },
  };

  const drawer = (
    <Box sx={{ width: drawerWidth, display: 'flex', flexDirection: 'column', height: '100%' }}>
      <Toolbar sx={{ px: 2 }}>
        <Box sx={{ minWidth: 0 }}>
          <Typography variant="subtitle1" fontWeight={700} noWrap>
            {user?.tenant?.business_name || 'Billing'}
          </Typography>
          <Typography variant="caption" color="text.secondary">
            {isOwner ? 'Owner · Billing workspace' : 'Billing counter'}
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
            sx={navButtonSx}
          >
            <ListItemIcon sx={{ minWidth: 40 }}>{item.icon}</ListItemIcon>
            <ListItemText primary={item.label} />
          </ListItemButton>
        ))}
      </List>
    </Box>
  );

  const topLinks = isOwner
    ? [
        { to: PATHS.ownerDashboard, label: 'Owner Dashboard', end: true },
        { to: PATHS.billingHome, label: 'Billing Home', end: true },
        { to: PATHS.billingNew, label: 'New Bill' },
        { to: PATHS.billingBills, label: 'Bills' },
      ]
    : [
        { to: PATHS.billingHome, label: 'Dashboard', end: true },
        { to: PATHS.billingNew, label: 'New Bill' },
        { to: PATHS.billingBills, label: 'Bills' },
        { to: PATHS.billingItems, label: 'Items' },
      ];

  return (
    <Box sx={{ display: 'flex', minHeight: '100vh', bgcolor: 'background.default' }}>
      <AppBar
        position="fixed"
        sx={{
          width: { md: `calc(100% - ${drawerWidth}px)` },
          ml: { md: `${drawerWidth}px` },
        }}
      >
        <Toolbar sx={{ gap: 1 }}>
          {isMobile ? (
            <IconButton edge="start" onClick={() => setMobileOpen(true)} aria-label="Open menu">
              <MenuIcon />
            </IconButton>
          ) : null}
          <Box sx={{ flexGrow: 1, minWidth: 0, mr: 1 }}>
            <Tooltip title={user?.tenant?.business_name || 'Hotel Billing'}>
              <Typography variant="subtitle1" fontWeight={700} noWrap>
                {user?.tenant?.business_name || 'Hotel Billing'}
              </Typography>
            </Tooltip>
            <Typography variant="caption" color="text.secondary" noWrap>
              {meta.title}
            </Typography>
          </Box>
          {!isMobile
            ? topLinks.map((item) => (
                <Button
                  key={item.to}
                  color="inherit"
                  component={NavLink}
                  to={item.to}
                  end={item.end}
                  sx={{
                    '&.active': {
                      bgcolor: 'action.selected',
                    },
                  }}
                >
                  {item.label}
                </Button>
              ))
            : null}
          <Chip
            size="small"
            label={isOwner ? 'OWNER' : 'BILLING'}
            color={isOwner ? 'primary' : 'default'}
            variant="outlined"
          />
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
              Profile
            </MenuItem>
            <MenuItem
              onClick={() => {
                setAnchorEl(null);
                navigate(PATHS.billingChangePassword);
              }}
            >
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
  return (
    <Box
      sx={{
        px: { xs: 2, sm: 3, lg: 4 },
        py: { xs: 2.5, md: 3 },
        width: '100%',
        maxWidth: 1400,
        mx: 'auto',
        boxSizing: 'border-box',
      }}
    >
      <PageHeader
        title={meta.title}
        subtitle={meta.subtitle}
        actions={<PageActionsSlot />}
      />
      <Outlet />
    </Box>
  );
}
