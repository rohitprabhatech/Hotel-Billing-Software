import AssessmentOutlinedIcon from '@mui/icons-material/AssessmentOutlined';
import SwapVertOutlinedIcon from '@mui/icons-material/SwapVertOutlined';
import TableRestaurantOutlinedIcon from '@mui/icons-material/TableRestaurantOutlined';
import RestaurantMenuOutlinedIcon from '@mui/icons-material/RestaurantMenuOutlined';
import KitchenOutlinedIcon from '@mui/icons-material/KitchenOutlined';
import LocalCafeOutlinedIcon from '@mui/icons-material/LocalCafeOutlined';
import ReceiptLongOutlinedIcon from '@mui/icons-material/ReceiptLongOutlined';
import LocalShippingOutlinedIcon from '@mui/icons-material/LocalShippingOutlined';
import ShoppingCartOutlinedIcon from '@mui/icons-material/ShoppingCartOutlined';
import PaymentsOutlinedIcon from '@mui/icons-material/PaymentsOutlined';
import ContactsOutlinedIcon from '@mui/icons-material/ContactsOutlined';
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
import { useEffect, useMemo, useState } from 'react';
import { NavLink, Outlet, useLocation, useNavigate } from 'react-router-dom';
import MainContent from '../components/MainContent';
import PageHeader from '../components/PageHeader';
import RouteErrorBoundary from '../components/RouteErrorBoundary';
import ThemeModeToggle from '../components/ThemeModeToggle';
import NotificationBell from '../components/NotificationBell';
import SubscriptionLockout from '../components/SubscriptionLockout';
import { useAuth } from '../context/AuthContext';
import { useModules } from '../context/ModulesContext';
import { usePermissions } from '../hooks/usePermissions';
import { PageActionsProvider, PageActionsSlot } from '../context/PageActionsContext';
import { DRAWER_WIDTH } from './shell';
import { fetchMe, logoutRequest } from '../services/authService';
import { PATHS } from '../routes/paths';
import { isAccountPath, subscriptionAllowsAccess } from '../utils/subscriptionAccess';

const drawerWidth = DRAWER_WIDTH;

const billingNav = [
  { to: PATHS.billingHome, label: 'Dashboard', icon: <PointOfSaleOutlinedIcon />, end: true },
  { to: PATHS.billingNew, label: 'New Bill', icon: <ReceiptLongOutlinedIcon /> },
  { to: PATHS.billingBills, label: 'Bills', icon: <ReceiptLongOutlinedIcon /> },
  { to: PATHS.billingItems, label: 'Items', icon: <Inventory2OutlinedIcon /> },
  { to: PATHS.billingCategories, label: 'Categories', icon: <CategoryOutlinedIcon /> },
  { to: PATHS.billingCustomers, label: 'Customers', icon: <ContactsOutlinedIcon /> },
  { to: PATHS.billingSuppliers, label: 'Suppliers', icon: <LocalShippingOutlinedIcon /> },
  {
    to: PATHS.billingOrders,
    label: 'Orders',
    icon: <ReceiptLongOutlinedIcon />,
    module: 'order_channels',
  },
  {
    to: PATHS.billingMenu,
    label: 'Menu',
    icon: <RestaurantMenuOutlinedIcon />,
    module: 'restaurant_menu',
  },
  {
    to: PATHS.billingTables,
    label: 'Tables',
    icon: <TableRestaurantOutlinedIcon />,
    module: 'table_management',
  },
  {
    to: PATHS.billingKitchen,
    label: 'Kitchen',
    icon: <KitchenOutlinedIcon />,
    module: 'kitchen',
  },
  {
    to: PATHS.billingCafe,
    label: 'Cafe POS',
    icon: <LocalCafeOutlinedIcon />,
    module: 'addons_combos',
  },
  {
    to: PATHS.billingGrocery,
    label: 'Grocery POS',
    icon: <ShoppingCartOutlinedIcon />,
    module: 'barcode_pos',
  },
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
  if (pathname.startsWith(PATHS.billingCustomers)) {
    return {
      title: 'Customers',
      subtitle: 'Manage customer contacts and purchase history.',
    };
  }
  if (pathname.startsWith(PATHS.billingSuppliers)) {
    return {
      title: 'Suppliers',
      subtitle: 'View supplier contacts for purchase flows.',
    };
  }
  if (pathname.startsWith(PATHS.billingPurchases)) {
    return {
      title: 'Purchases',
      subtitle: 'Record supplier purchases and review stock receipts.',
    };
  }
  if (pathname.startsWith(PATHS.billingExpenses)) {
    return {
      title: 'Expenses',
      subtitle: 'Track daily business expenses and category totals.',
    };
  }
  if (pathname.startsWith(PATHS.billingTables)) {
    return {
      title: 'Tables',
      subtitle: 'Dining table board for restaurants and cafes.',
    };
  }
  if (pathname.startsWith(PATHS.billingKitchen)) {
    return {
      title: 'Kitchen',
      subtitle: 'Live kitchen board — queued, preparing, and ready tickets.',
    };
  }
  if (pathname.startsWith(PATHS.billingCafe)) {
    return {
      title: 'Cafe POS',
      subtitle: 'Quick takeaway billing with add-ons and combos.',
    };
  }
  if (pathname.startsWith(PATHS.billingGrocery)) {
    return {
      title: 'Grocery POS',
      subtitle: 'Scan-first billing with barcode lookup and weight quantities.',
    };
  }
  if (pathname.startsWith(PATHS.billingOrdersNew)) {
    return {
      title: 'New Order',
      subtitle: 'Take an order by channel — table required for dine-in.',
    };
  }
  if (pathname.startsWith(PATHS.billingOrders)) {
    return {
      title: 'Orders',
      subtitle: 'Open dine-in, takeaway, and delivery orders.',
    };
  }
  if (pathname.startsWith(PATHS.billingMenu)) {
    return {
      title: 'Menu',
      subtitle: 'Active menu items grouped by course/category.',
    };
  }
  if (pathname.startsWith(PATHS.billingReports)) {
    return {
      title: 'Sales Reports',
      subtitle: 'Review sales performance and export summaries.',
    };
  }
  if (pathname.startsWith(PATHS.billingStockMovements)) {
    return {
      title: 'Stock Movements',
      subtitle: 'Track inventory changes across items.',
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
  const { user, role, logout, updateUser } = useAuth();
  const { filterByModule } = useModules();
  const { canReports, canStockMovements, canViewPurchases, canViewExpenses } = usePermissions();
  const navigate = useNavigate();
  const location = useLocation();
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  const [mobileOpen, setMobileOpen] = useState(false);
  const [anchorEl, setAnchorEl] = useState(null);
  const isOwner = role === 'OWNER';
  const isManager = role === 'MANAGER';
  const entitled = subscriptionAllowsAccess(user?.tenant?.subscription);

  useEffect(() => {
    let active = true;
    fetchMe()
      .then((payload) => {
        if (active && payload.data) updateUser(payload.data);
      })
      .catch(() => {});
    return () => {
      active = false;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps -- refresh once per layout mount
  }, []);

  const navItems = useMemo(() => {
    let items;
    if (!isOwner) {
      items = [
        { to: PATHS.billingHome, label: 'Dashboard', icon: <DashboardOutlinedIcon />, end: true },
        ...billingNav.slice(1),
      ];
      if (canReports) {
        items.push({
          to: PATHS.billingReports,
          label: 'Reports',
          icon: <AssessmentOutlinedIcon />,
        });
      }
      if (canStockMovements) {
        items.push({
          to: PATHS.billingStockMovements,
          label: 'Stock Movements',
          icon: <SwapVertOutlinedIcon />,
        });
      }
      if (canViewPurchases) {
        items.push({
          to: PATHS.billingPurchases,
          label: 'Purchases',
          icon: <ShoppingCartOutlinedIcon />,
        });
      }
      if (canViewExpenses) {
        items.push({
          to: PATHS.billingExpenses,
          label: 'Expenses',
          icon: <PaymentsOutlinedIcon />,
        });
      }
    } else {
      items = [
        {
          to: PATHS.ownerDashboard,
          label: 'Owner Dashboard',
          icon: <DashboardOutlinedIcon />,
          end: true,
        },
        ...billingNav,
      ];
    }
    return filterByModule(items);
  }, [isOwner, canReports, canStockMovements, filterByModule]);

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
            {isOwner ? 'Owner · Billing' : isManager ? 'Manager · Billing' : 'Billing'}
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
            label={isOwner ? 'OWNER' : isManager ? 'MANAGER' : 'BILLING'}
            color={isOwner ? 'primary' : isManager ? 'secondary' : 'default'}
            variant="outlined"
            sx={{ mr: 0.5, display: { xs: 'none', sm: 'inline-flex' } }}
          />
          {entitled ? <NotificationBell /> : null}
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
  const { user } = useAuth();
  const entitled = subscriptionAllowsAccess(user?.tenant?.subscription);
  const showApp = entitled || isAccountPath(location.pathname);
  return (
    <MainContent>
      <PageHeader
        title={meta.title}
        subtitle={meta.subtitle}
        actions={<PageActionsSlot />}
      />
      {!entitled ? <SubscriptionLockout user={user} accountPath={PATHS.billingProfile} /> : null}
      {showApp ? (
        <RouteErrorBoundary key={location.pathname}>
          <Outlet />
        </RouteErrorBoundary>
      ) : null}
    </MainContent>
  );
}
