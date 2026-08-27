import AssessmentOutlinedIcon from '@mui/icons-material/AssessmentOutlined';
import SwapVertOutlinedIcon from '@mui/icons-material/SwapVertOutlined';
import TableRestaurantOutlinedIcon from '@mui/icons-material/TableRestaurantOutlined';
import RestaurantMenuOutlinedIcon from '@mui/icons-material/RestaurantMenuOutlined';
import KitchenOutlinedIcon from '@mui/icons-material/KitchenOutlined';
import LocalCafeOutlinedIcon from '@mui/icons-material/LocalCafeOutlined';
import ReceiptLongOutlinedIcon from '@mui/icons-material/ReceiptLongOutlined';
import LocalShippingOutlinedIcon from '@mui/icons-material/LocalShippingOutlined';
import CheckroomOutlinedIcon from '@mui/icons-material/CheckroomOutlined';
import AssignmentReturnOutlinedIcon from '@mui/icons-material/AssignmentReturnOutlined';
import BoltOutlinedIcon from '@mui/icons-material/BoltOutlined';
import PaymentsOutlinedIcon from '@mui/icons-material/PaymentsOutlined';
import AccountBalanceWalletOutlinedIcon from '@mui/icons-material/AccountBalanceWalletOutlined';
import ContactsOutlinedIcon from '@mui/icons-material/ContactsOutlined';
import CategoryOutlinedIcon from '@mui/icons-material/CategoryOutlined';
import DashboardOutlinedIcon from '@mui/icons-material/DashboardOutlined';
import ListAltOutlinedIcon from '@mui/icons-material/ListAltOutlined';
import LockOutlinedIcon from '@mui/icons-material/LockOutlined';
import LogoutOutlinedIcon from '@mui/icons-material/LogoutOutlined';
import MenuIcon from '@mui/icons-material/Menu';
import PersonOutlinedIcon from '@mui/icons-material/PersonOutlined';
import Inventory2OutlinedIcon from '@mui/icons-material/Inventory2Outlined';
import PointOfSaleOutlinedIcon from '@mui/icons-material/PointOfSaleOutlined';
import ShoppingCartOutlinedIcon from '@mui/icons-material/ShoppingCartOutlined';
import MenuBookOutlinedIcon from '@mui/icons-material/MenuBookOutlined';
import StraightenOutlinedIcon from '@mui/icons-material/StraightenOutlined';
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

/**
 * Billing sidebar order — hotel groups follow desk workflow:
 * Sell → Floor → Menu → Customers → Reports → Account.
 * Other business types keep a flat sell-first list without hotel-only sections.
 */
const billingNav = [
  { to: PATHS.billingHome, label: 'Dashboard', icon: <DashboardOutlinedIcon />, end: true },

  { type: 'section', label: 'Sell', businessTypes: ['hotel_restaurant'] },
  {
    to: PATHS.billingRestaurantBilling,
    label: 'Table Bill',
    icon: <PointOfSaleOutlinedIcon />,
    module: 'table_management',
    businessTypes: ['hotel_restaurant'],
    emphasize: true,
  },
  {
    to: PATHS.billingNew,
    label: 'Quick Bill',
    icon: <BoltOutlinedIcon />,
    businessTypes: ['hotel_restaurant'],
  },
  {
    to: PATHS.billingNew,
    label: 'New Bill',
    icon: <ReceiptLongOutlinedIcon />,
    hideForBusinessTypes: ['hotel_restaurant'],
  },
  {
    to: PATHS.billingBills,
    label: "Today's Bills",
    icon: <ReceiptLongOutlinedIcon />,
    businessTypes: ['hotel_restaurant'],
  },
  {
    to: PATHS.billingBills,
    label: 'Bills',
    icon: <ReceiptLongOutlinedIcon />,
    hideForBusinessTypes: ['hotel_restaurant'],
  },

  { type: 'section', label: 'Floor', businessTypes: ['hotel_restaurant'] },
  {
    to: PATHS.billingTables,
    label: 'Tables',
    icon: <TableRestaurantOutlinedIcon />,
    module: 'table_management',
    businessTypes: ['hotel_restaurant', 'cafe_tea'],
  },
  {
    to: PATHS.billingKitchen,
    label: 'Kitchen',
    icon: <KitchenOutlinedIcon />,
    module: 'kitchen',
    businessTypes: ['hotel_restaurant', 'cafe_tea'],
  },
  {
    to: PATHS.billingOrders,
    label: 'Open Orders',
    icon: <ListAltOutlinedIcon />,
    module: 'order_channels',
    businessTypes: ['hotel_restaurant'],
  },
  {
    to: PATHS.billingOrders,
    label: 'Orders',
    icon: <ListAltOutlinedIcon />,
    module: 'order_channels',
    businessTypes: ['cafe_tea'],
  },

  { type: 'section', label: 'Menu', businessTypes: ['hotel_restaurant'] },
  {
    to: PATHS.billingMenu,
    label: 'Menu Board',
    icon: <RestaurantMenuOutlinedIcon />,
    module: 'restaurant_menu',
    businessTypes: ['hotel_restaurant'],
  },
  {
    to: PATHS.billingMenu,
    label: 'Menu',
    icon: <RestaurantMenuOutlinedIcon />,
    module: 'restaurant_menu',
    businessTypes: ['cafe_tea'],
  },
  {
    to: PATHS.billingItems,
    label: 'Items',
    icon: <Inventory2OutlinedIcon />,
    businessTypes: ['hotel_restaurant'],
  },
  {
    to: PATHS.billingCategories,
    label: 'Categories',
    icon: <CategoryOutlinedIcon />,
    businessTypes: ['hotel_restaurant'],
  },
  {
    to: PATHS.billingItems,
    label: 'Items',
    icon: <Inventory2OutlinedIcon />,
    hideForBusinessTypes: ['hotel_restaurant'],
  },
  {
    to: PATHS.billingCategories,
    label: 'Categories',
    icon: <CategoryOutlinedIcon />,
    hideForBusinessTypes: ['hotel_restaurant'],
  },

  { type: 'section', label: 'Customers', businessTypes: ['hotel_restaurant'] },
  { to: PATHS.billingCustomers, label: 'Customers', icon: <ContactsOutlinedIcon /> },
  {
    to: PATHS.billingCredit,
    label: 'Credit / Udhari',
    icon: <AccountBalanceWalletOutlinedIcon />,
    module: 'customer_credit',
  },
  {
    to: PATHS.billingSuppliers,
    label: 'Suppliers',
    icon: <LocalShippingOutlinedIcon />,
    hideForBusinessTypes: ['hotel_restaurant'],
  },

  {
    to: PATHS.billingCafe,
    label: 'Cafe POS',
    icon: <LocalCafeOutlinedIcon />,
    module: 'addons_combos',
    businessTypes: ['cafe_tea'],
  },
  {
    to: PATHS.billingGrocery,
    label: 'Grocery POS',
    icon: <ShoppingCartOutlinedIcon />,
    module: 'barcode_pos',
    businessTypes: ['grocery_kirana', 'wholesale'],
  },
  {
    to: PATHS.billingStationery,
    label: 'Stationery POS',
    icon: <MenuBookOutlinedIcon />,
    module: 'barcode_pos',
    businessTypes: ['stationery', 'book_store'],
  },
  {
    to: PATHS.billingHardware,
    label: 'Hardware POS',
    icon: <StraightenOutlinedIcon />,
    module: 'uom_measurement',
    businessTypes: ['hardware', 'building_material'],
  },
  {
    to: PATHS.billingClothing,
    label: 'Clothing POS',
    icon: <CheckroomOutlinedIcon />,
    module: 'variants',
    businessTypes: ['clothing'],
  },
  {
    to: PATHS.billingReturns,
    label: 'Returns / Exchange',
    icon: <AssignmentReturnOutlinedIcon />,
    module: 'returns_exchange',
  },

  { type: 'section', label: 'Account' },
  { to: PATHS.billingProfile, label: 'Profile', icon: <PersonOutlinedIcon /> },
];

/** Slim sidebar for hotel Billing Users — primary desk workflow only. */
const hotelBillingUserNav = [
  { to: PATHS.billingHome, label: 'Dashboard', icon: <DashboardOutlinedIcon />, end: true },
  { type: 'section', label: 'Billing' },
  {
    to: PATHS.billingRestaurantBilling,
    label: 'Table Bill',
    icon: <PointOfSaleOutlinedIcon />,
    module: 'table_management',
    emphasize: true,
  },
  {
    to: PATHS.billingNew,
    label: 'Quick Bill',
    icon: <BoltOutlinedIcon />,
  },
  {
    to: PATHS.billingBills,
    label: "Today's Bills",
    icon: <ReceiptLongOutlinedIcon />,
  },
  {
    to: PATHS.billingTables,
    label: 'Tables',
    icon: <TableRestaurantOutlinedIcon />,
    module: 'table_management',
  },
  {
    to: PATHS.billingItems,
    label: 'Items',
    icon: <Inventory2OutlinedIcon />,
  },
  {
    to: PATHS.billingCategories,
    label: 'Categories',
    icon: <CategoryOutlinedIcon />,
  },
  { type: 'section', label: 'Account' },
  { to: PATHS.billingProfile, label: 'Profile', icon: <PersonOutlinedIcon /> },
  {
    to: PATHS.billingChangePassword,
    label: 'Settings',
    icon: <LockOutlinedIcon />,
  },
];

/** Drop section headers that have no visible link items before the next section. */
function pruneEmptySections(items) {
  const result = [];
  for (let i = 0; i < items.length; i += 1) {
    const item = items[i];
    if (item.type !== 'section') {
      result.push(item);
      continue;
    }
    let hasLinks = false;
    for (let j = i + 1; j < items.length; j += 1) {
      if (items[j].type === 'section') break;
      hasLinks = true;
      break;
    }
    if (hasLinks) result.push(item);
  }
  return result;
}

function pageMeta(pathname, businessType) {
  if (pathname === PATHS.billingHome || pathname === `${PATHS.billingHome}/`) {
    if (businessType === 'hotel_restaurant') {
      return {
        title: 'Hotel Billing',
        subtitle: 'Select table → add items → pay → print.',
      };
    }
    return {
      title: 'Billing Dashboard',
      subtitle: "Today's billing overview and quick actions.",
    };
  }
  if (pathname.startsWith(PATHS.billingNew)) {
    if (businessType === 'hotel_restaurant') {
      return {
        title: 'Quick Bill',
        subtitle: 'Bill without a table — search, add, pay, print.',
      };
    }
    return {
      title: 'New Bill',
      subtitle: 'Create and manage the current customer bill.',
    };
  }
  if (pathname.startsWith(PATHS.billingBills)) {
    return {
      title: businessType === 'hotel_restaurant' ? "Today's Bills" : "Today's Bills",
      subtitle:
        businessType === 'hotel_restaurant'
          ? 'Bills generated today — reprint or review.'
          : 'Review bills generated today.',
    };
  }
  if (pathname.startsWith(PATHS.billingItems)) {
    return {
      title: businessType === 'hotel_restaurant' ? 'Menu Items' : 'Items',
      subtitle:
        businessType === 'hotel_restaurant'
          ? 'Add or edit dishes and prices used in billing.'
          : 'Add and manage catalog items for billing.',
    };
  }
  if (pathname.startsWith(PATHS.billingCategories)) {
    return {
      title: 'Categories',
      subtitle:
        businessType === 'hotel_restaurant'
          ? 'Group menu items (Veg, Starters, Drinks…).'
          : 'Browse categories available for billing items.',
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
      subtitle:
        businessType === 'hotel_restaurant'
          ? 'See which tables are free, occupied, or bill pending.'
          : 'Dining table board for restaurants and cafes.',
    };
  }
  if (pathname.startsWith(PATHS.billingRestaurantBilling)) {
    return {
      title: 'Table Bill',
      subtitle: 'Select table → add items → pay → print.',
    };
  }
  if (pathname.startsWith(PATHS.billingKitchen)) {
    return {
      title: 'Kitchen',
      subtitle: 'Live kitchen tickets — queued, preparing, ready.',
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
      subtitle: 'Scan-first billing with barcode lookup, weight quantities, and udhari.',
    };
  }
  if (pathname.startsWith(PATHS.billingStationery)) {
    return {
      title: 'Stationery POS',
      subtitle: 'Search-first billing with barcode, bulk rates, and optional credit.',
    };
  }
  if (pathname.startsWith(PATHS.billingHardware)) {
    return {
      title: 'Hardware POS',
      subtitle: 'Bill by length, weight, or area with clear unit prices.',
    };
  }
  if (pathname.startsWith(PATHS.billingClothing)) {
    return {
      title: 'Clothing POS',
      subtitle: 'Pick size and color from live variant stock.',
    };
  }
  if (pathname.startsWith(PATHS.billingReturns)) {
    return {
      title: 'Returns / Exchange',
      subtitle: 'Look up a bill to see return history. Owner or manager processes new returns.',
    };
  }
  if (pathname.startsWith(PATHS.billingCredit)) {
    return {
      title: 'Credit / Udhari',
      subtitle: 'Outstanding balances, collections, and payment history.',
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
      title: businessType === 'hotel_restaurant' ? 'Open Orders' : 'Orders',
      subtitle:
        businessType === 'hotel_restaurant'
          ? 'All open dine-in, takeaway, and delivery orders.'
          : 'Open dine-in, takeaway, and delivery orders.',
    };
  }
  if (pathname.startsWith(PATHS.billingMenu)) {
    return {
      title: businessType === 'hotel_restaurant' ? 'Menu Board' : 'Menu',
      subtitle:
        businessType === 'hotel_restaurant'
          ? 'Active dishes grouped by category — ready to bill.'
          : 'Active menu items grouped by course/category.',
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
      subtitle:
        businessType === 'hotel_restaurant'
          ? 'Ingredient and stock changes (sale deducts at bill settle).'
          : 'Track inventory changes across items.',
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
    const businessType = user?.tenant?.business_type;
    const isHotel = businessType === 'hotel_restaurant';
    const isBillingUser = role === 'BILLING_USER';
    let items;

    // Hotel Billing User: keep sidebar short and desk-focused.
    if (isHotel && isBillingUser) {
      items = [...hotelBillingUserNav];
      if (canReports) {
        const accountIdx = items.findIndex(
          (row) => row.type === 'section' && row.label === 'Account'
        );
        const reportsBlock = [
          { type: 'section', label: 'Reports' },
          {
            to: PATHS.billingReports,
            label: 'Reports',
            icon: <AssessmentOutlinedIcon />,
          },
        ];
        if (accountIdx >= 0) {
          items = [...items.slice(0, accountIdx), ...reportsBlock, ...items.slice(accountIdx)];
        } else {
          items = [...items, ...reportsBlock];
        }
      }
      return pruneEmptySections(filterByModule(items, businessType));
    }

    if (!isOwner) {
      items = [
        { to: PATHS.billingHome, label: 'Dashboard', icon: <DashboardOutlinedIcon />, end: true },
        ...billingNav.slice(1),
      ];
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

    const extras = [];
    if (!isOwner) {
      if (canReports) {
        extras.push({
          to: PATHS.billingReports,
          label: 'Reports',
          icon: <AssessmentOutlinedIcon />,
        });
      }
      if (canStockMovements) {
        extras.push({
          to: PATHS.billingStockMovements,
          label: 'Stock Movements',
          icon: <SwapVertOutlinedIcon />,
        });
      }
      if (canViewPurchases) {
        extras.push({
          to: PATHS.billingPurchases,
          label: 'Purchases',
          icon: <ShoppingCartOutlinedIcon />,
          hideForBusinessTypes: ['hotel_restaurant'],
        });
      }
      if (canViewExpenses) {
        extras.push({
          to: PATHS.billingExpenses,
          label: 'Expenses',
          icon: <PaymentsOutlinedIcon />,
        });
      }
    }

    if (extras.length) {
      const accountIdx = items.findIndex(
        (row) => row.type === 'section' && row.label === 'Account'
      );
      const block = [
        {
          type: 'section',
          label: isHotel ? 'Reports' : 'More',
        },
        ...extras,
      ];
      if (accountIdx >= 0) {
        items = [...items.slice(0, accountIdx), ...block, ...items.slice(accountIdx)];
      } else {
        items = [...items, ...block];
      }
    }

    return pruneEmptySections(filterByModule(items, businessType));
  }, [
    isOwner,
    role,
    canReports,
    canStockMovements,
    canViewPurchases,
    canViewExpenses,
    filterByModule,
    user?.tenant?.business_type,
  ]);

  const meta = pageMeta(location.pathname, user?.tenant?.business_type);

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
            {user?.tenant?.business_type === 'hotel_restaurant'
              ? 'Hotel Billing'
              : isOwner
                ? 'Owner · Billing'
                : isManager
                  ? 'Manager · Billing'
                  : 'Billing'}
          </Typography>
        </Box>
      </Toolbar>
      <Divider />
      <List
        sx={{
          px: 1,
          pt: 0.75,
          pb: 1.5,
          flexGrow: 1,
          overflowY: 'auto',
        }}
      >
        {navItems.map((item, index) => {
          if (item.type === 'section') {
            return (
              <Typography
                key={`section-${item.label}-${index}`}
                variant="caption"
                color="text.secondary"
                sx={{
                  display: 'block',
                  px: 1.5,
                  pt: index === 0 ? 0.75 : 1.75,
                  pb: 0.5,
                  fontWeight: 700,
                  letterSpacing: '0.08em',
                  textTransform: 'uppercase',
                  fontSize: '0.65rem',
                }}
              >
                {item.label}
              </Typography>
            );
          }
          return (
            <ListItemButton
              key={`${item.to}-${item.label}`}
              component={NavLink}
              to={item.to}
              end={item.end}
              onClick={() => setMobileOpen(false)}
              sx={{
                borderRadius: 1.25,
                mb: 0.35,
                minHeight: 42,
                px: 1.25,
                '&.active': {
                  bgcolor: 'primary.main',
                  color: 'primary.contrastText',
                  '& .MuiListItemIcon-root': { color: 'inherit' },
                },
                ...(item.emphasize
                  ? {
                      border: '1px solid',
                      borderColor: 'divider',
                      bgcolor: 'action.hover',
                      fontWeight: 650,
                      '&.active': {
                        bgcolor: 'primary.main',
                        color: 'primary.contrastText',
                        borderColor: 'primary.main',
                        '& .MuiListItemIcon-root': { color: 'inherit' },
                      },
                    }
                  : null),
              }}
            >
              <ListItemIcon sx={{ minWidth: 36 }}>{item.icon}</ListItemIcon>
              <ListItemText
                primary={item.label}
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
