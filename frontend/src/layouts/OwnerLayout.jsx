import AssessmentOutlinedIcon from '@mui/icons-material/AssessmentOutlined';
import AutoAwesomeOutlinedIcon from '@mui/icons-material/AutoAwesomeOutlined';
import LocalShippingOutlinedIcon from '@mui/icons-material/LocalShippingOutlined';
import ShoppingCartOutlinedIcon from '@mui/icons-material/ShoppingCartOutlined';
import PaymentsOutlinedIcon from '@mui/icons-material/PaymentsOutlined';
import ContactsOutlinedIcon from '@mui/icons-material/ContactsOutlined';
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
import SwapVertOutlinedIcon from '@mui/icons-material/SwapVertOutlined';
import SettingsOutlinedIcon from '@mui/icons-material/SettingsOutlined';
import TableRestaurantOutlinedIcon from '@mui/icons-material/TableRestaurantOutlined';
import RestaurantMenuOutlinedIcon from '@mui/icons-material/RestaurantMenuOutlined';
import KitchenOutlinedIcon from '@mui/icons-material/KitchenOutlined';
import MenuBookOutlinedIcon from '@mui/icons-material/MenuBookOutlined';
import BakeryDiningOutlinedIcon from '@mui/icons-material/BakeryDiningOutlined';
import CakeOutlinedIcon from '@mui/icons-material/CakeOutlined';
import WeekendOutlinedIcon from '@mui/icons-material/WeekendOutlined';
import LocalCafeOutlinedIcon from '@mui/icons-material/LocalCafeOutlined';
import DeleteSweepOutlinedIcon from '@mui/icons-material/DeleteSweepOutlined';
import AccountBalanceWalletOutlinedIcon from '@mui/icons-material/AccountBalanceWalletOutlined';
import EventAvailableOutlinedIcon from '@mui/icons-material/EventAvailableOutlined';
import CheckroomOutlinedIcon from '@mui/icons-material/CheckroomOutlined';
import StraightenOutlinedIcon from '@mui/icons-material/StraightenOutlined';
import PhoneIphoneOutlinedIcon from '@mui/icons-material/PhoneIphoneOutlined';
import AssignmentReturnOutlinedIcon from '@mui/icons-material/AssignmentReturnOutlined';
import BuildOutlinedIcon from '@mui/icons-material/BuildOutlined';
import HandymanOutlinedIcon from '@mui/icons-material/HandymanOutlined';
import DeliveryDiningOutlinedIcon from '@mui/icons-material/DeliveryDiningOutlined';
import RequestQuoteOutlinedIcon from '@mui/icons-material/RequestQuoteOutlined';
import PriceChangeOutlinedIcon from '@mui/icons-material/PriceChangeOutlined';
import ShoppingCartCheckoutOutlinedIcon from '@mui/icons-material/ShoppingCartCheckoutOutlined';
import AssignmentOutlinedIcon from '@mui/icons-material/AssignmentOutlined';
import WarehouseOutlinedIcon from '@mui/icons-material/WarehouseOutlined';
import FlightTakeoffOutlinedIcon from '@mui/icons-material/FlightTakeoffOutlined';
import LuggageOutlinedIcon from '@mui/icons-material/LuggageOutlined';
import HandshakeOutlinedIcon from '@mui/icons-material/HandshakeOutlined';
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
import { PageActionsProvider, PageActionsSlot } from '../context/PageActionsContext';
import { DRAWER_WIDTH } from './shell';
import { fetchMe, logoutRequest } from '../services/authService';
import { PATHS } from '../routes/paths';
import { isAccountPath, subscriptionAllowsAccess } from '../utils/subscriptionAccess';

const drawerWidth = DRAWER_WIDTH;

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

const navItems = [
  { to: PATHS.ownerDashboard, label: 'Dashboard', icon: <DashboardOutlinedIcon />, end: true },
  { type: 'section', label: 'Sell', businessTypes: ['hotel_restaurant'] },
  {
    to: PATHS.ownerRestaurantBilling,
    label: 'Table Billing',
    icon: <PointOfSaleOutlinedIcon />,
    module: 'table_management',
    businessTypes: ['hotel_restaurant'],
    emphasize: true,
  },
  {
    to: PATHS.billingHome,
    label: 'Billing Desk',
    icon: <PointOfSaleOutlinedIcon />,
    businessTypes: ['hotel_restaurant'],
  },
  {
    to: PATHS.billingHome,
    label: 'Billing',
    icon: <PointOfSaleOutlinedIcon />,
    hideForBusinessTypes: ['hotel_restaurant'],
  },
  {
    to: PATHS.ownerBills,
    label: "Today's Bills",
    icon: <ReceiptLongOutlinedIcon />,
    businessTypes: ['hotel_restaurant'],
  },
  {
    to: PATHS.ownerBills,
    label: 'Bills',
    icon: <ReceiptLongOutlinedIcon />,
    hideForBusinessTypes: ['hotel_restaurant'],
  },
  { type: 'section', label: 'Floor', businessTypes: ['hotel_restaurant'] },
  {
    to: PATHS.ownerTables,
    label: 'Tables',
    icon: <TableRestaurantOutlinedIcon />,
    module: 'table_management',
    businessTypes: ['hotel_restaurant', 'cafe_tea'],
  },
  {
    to: PATHS.ownerKitchen,
    label: 'Kitchen',
    icon: <KitchenOutlinedIcon />,
    module: 'kitchen',
    businessTypes: ['hotel_restaurant', 'cafe_tea'],
  },
  {
    to: PATHS.ownerOrders,
    label: 'Open Orders',
    icon: <ReceiptLongOutlinedIcon />,
    module: 'order_channels',
    businessTypes: ['hotel_restaurant'],
  },
  {
    to: PATHS.ownerOrders,
    label: 'Orders',
    icon: <ReceiptLongOutlinedIcon />,
    module: 'order_channels',
    businessTypes: ['cafe_tea'],
  },
  { type: 'section', label: 'Menu', businessTypes: ['hotel_restaurant'] },
  {
    to: PATHS.ownerMenu,
    label: 'Menu Board',
    icon: <RestaurantMenuOutlinedIcon />,
    module: 'restaurant_menu',
    businessTypes: ['hotel_restaurant'],
  },
  {
    to: PATHS.ownerMenu,
    label: 'Menu',
    icon: <RestaurantMenuOutlinedIcon />,
    module: 'restaurant_menu',
    businessTypes: ['cafe_tea'],
  },
  { to: PATHS.ownerItems, label: 'Items', icon: <Inventory2OutlinedIcon /> },
  { to: PATHS.ownerCategories, label: 'Categories', icon: <CategoryOutlinedIcon /> },
  { to: PATHS.ownerItemActivity, label: 'Item Activity', icon: <HistoryOutlinedIcon /> },
  { to: PATHS.ownerStockMovements, label: 'Stock Movements', icon: <SwapVertOutlinedIcon /> },
  { to: PATHS.ownerCustomers, label: 'Customers', icon: <ContactsOutlinedIcon /> },
  {
    to: PATHS.ownerSuppliers,
    label: 'Suppliers',
    icon: <LocalShippingOutlinedIcon />,
    hideForBusinessTypes: ['hotel_restaurant'],
  },
  {
    to: PATHS.ownerPurchases,
    label: 'Purchases',
    icon: <ShoppingCartOutlinedIcon />,
    hideForBusinessTypes: ['hotel_restaurant'],
  },
  { to: PATHS.ownerExpenses, label: 'Expenses', icon: <PaymentsOutlinedIcon /> },
  {
    to: PATHS.ownerCafe,
    label: 'Cafe POS',
    icon: <LocalCafeOutlinedIcon />,
    module: 'addons_combos',
    businessTypes: ['cafe_tea'],
  },
  {
    to: PATHS.ownerGrocery,
    label: 'Grocery POS',
    icon: <ShoppingCartOutlinedIcon />,
    module: 'barcode_pos',
    businessTypes: ['grocery_kirana', 'wholesale'],
  },
  {
    to: PATHS.ownerStationery,
    label: 'Stationery POS',
    icon: <MenuBookOutlinedIcon />,
    module: 'barcode_pos',
    businessTypes: ['stationery', 'book_store'],
  },
  {
    to: PATHS.ownerHardware,
    label: 'Hardware POS',
    icon: <StraightenOutlinedIcon />,
    module: 'uom_measurement',
    businessTypes: ['hardware', 'building_material'],
  },
  {
    to: PATHS.ownerClothing,
    label: 'Clothing POS',
    icon: <CheckroomOutlinedIcon />,
    module: 'variants',
    businessTypes: ['clothing'],
  },
  {
    to: PATHS.ownerReturns,
    label: 'Returns / Exchange',
    icon: <AssignmentReturnOutlinedIcon />,
    module: 'returns_exchange',
  },
  {
    to: PATHS.ownerRepairs,
    label: 'Repairs',
    icon: <BuildOutlinedIcon />,
    module: 'repair_service',
  },
  {
    to: PATHS.ownerInstallations,
    label: 'Installations',
    icon: <HandymanOutlinedIcon />,
    module: 'installation',
  },
  {
    to: PATHS.ownerQuotations,
    label: 'Quotations',
    icon: <RequestQuoteOutlinedIcon />,
    module: 'quotation',
  },
  {
    to: PATHS.ownerPriceLists,
    label: 'Price Lists',
    icon: <PriceChangeOutlinedIcon />,
    module: 'price_lists',
    businessTypes: ['wholesale'],
  },
  {
    to: PATHS.ownerSalesOrders,
    label: 'Sales Orders',
    icon: <ShoppingCartCheckoutOutlinedIcon />,
    module: 'sales_orders',
    businessTypes: ['wholesale'],
  },
  {
    to: PATHS.ownerPurchaseOrders,
    label: 'Purchase Orders',
    icon: <AssignmentOutlinedIcon />,
    module: 'purchase_orders',
    businessTypes: ['wholesale'],
  },
  {
    to: PATHS.ownerChallans,
    label: 'Delivery Challans',
    icon: <LocalShippingOutlinedIcon />,
    module: 'delivery_challan',
  },
  {
    to: PATHS.ownerWarehouses,
    label: 'Warehouses',
    icon: <WarehouseOutlinedIcon />,
    module: 'warehouse',
  },
  {
    to: PATHS.ownerTourPackages,
    label: 'Tour Packages',
    icon: <FlightTakeoffOutlinedIcon />,
    module: 'tour_packages',
    businessTypes: ['travel_agency'],
  },
  {
    to: PATHS.ownerTravelBookings,
    label: 'Travel Bookings',
    icon: <LuggageOutlinedIcon />,
    module: 'travel_bookings',
    businessTypes: ['travel_agency'],
  },
  {
    to: PATHS.ownerTravelAgents,
    label: 'Travel Agents',
    icon: <HandshakeOutlinedIcon />,
    module: 'travel_commission',
    businessTypes: ['travel_agency'],
  },
  {
    to: PATHS.ownerCredit,
    label: 'Credit / Udhari',
    icon: <AccountBalanceWalletOutlinedIcon />,
    module: 'customer_credit',
  },
  {
    to: PATHS.ownerOutstanding,
    label: 'Outstanding Report',
    icon: <AssessmentOutlinedIcon />,
    module: 'customer_credit',
  },
  {
    to: PATHS.ownerBatches,
    label: 'Batches / Expiry',
    icon: <EventAvailableOutlinedIcon />,
    module: 'batch_expiry',
  },
  {
    to: PATHS.ownerRecipes,
    label: 'Recipes',
    icon: <MenuBookOutlinedIcon />,
    module: 'recipe',
  },
  {
    to: PATHS.ownerProduction,
    label: 'Production',
    icon: <BakeryDiningOutlinedIcon />,
    module: 'production',
  },
  {
    to: PATHS.ownerCakeOrders,
    label: 'Cake Orders',
    icon: <CakeOutlinedIcon />,
    module: 'custom_orders',
    businessTypes: ['bakery_sweet'],
  },
  {
    to: PATHS.ownerFurnitureOrders,
    label: 'Furniture Orders',
    icon: <WeekendOutlinedIcon />,
    module: 'custom_orders',
    businessTypes: ['furniture'],
  },
  {
    to: PATHS.ownerDeliveries,
    label: 'Deliveries',
    icon: <DeliveryDiningOutlinedIcon />,
    module: 'delivery_tracking',
    businessTypes: ['furniture'],
  },
  {
    to: PATHS.ownerWastage,
    label: 'Wastage',
    icon: <DeleteSweepOutlinedIcon />,
    module: 'wastage',
  },
  {
    to: PATHS.ownerVariants,
    label: 'Variants',
    icon: <CheckroomOutlinedIcon />,
    module: 'variants',
  },
  {
    to: PATHS.ownerSerials,
    label: 'Serial / IMEI',
    icon: <PhoneIphoneOutlinedIcon />,
    module: 'serial_imei',
  },
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
  [PATHS.ownerStockMovements]: {
    title: 'Stock Movements',
    subtitle: 'Track every inventory change from bills, cancels, and adjustments.',
  },
  [PATHS.ownerItemActivity]: {
    title: 'Item Activity',
    subtitle: 'See who created, edited, or deactivated items.',
  },
  [PATHS.ownerCategories]: {
    title: 'Categories',
    subtitle: 'Organize business items with main and child categories.',
  },
  [PATHS.ownerCustomers]: {
    title: 'Customers',
    subtitle: 'Manage customer contacts and view purchase history.',
  },
  [PATHS.ownerSuppliers]: {
    title: 'Suppliers',
    subtitle: 'Manage vendor contacts for purchase and stock receive flows.',
  },
  [PATHS.ownerPurchases]: {
    title: 'Purchases',
    subtitle: 'Record supplier purchases that increase stock and update cost price.',
  },
  [PATHS.ownerExpenses]: {
    title: 'Expenses',
    subtitle: 'Track daily business expenses for P&L-style reporting.',
  },
  [PATHS.ownerOrders]: {
    title: 'Orders',
    subtitle: 'Open dine-in, takeaway, and delivery orders before billing.',
  },
  [PATHS.ownerOrdersNew]: {
    title: 'New Order',
    subtitle: 'Take an order by channel — table required for dine-in.',
  },
  [PATHS.ownerMenu]: {
    title: 'Menu',
    subtitle: 'Active menu items grouped by course/category for F&B service.',
  },
  [PATHS.ownerTables]: {
    title: 'Tables',
    subtitle: 'Dining table board for restaurants and cafes.',
  },
  [PATHS.ownerRestaurantBilling]: {
    title: 'Restaurant Billing',
    subtitle: 'Table-first POS — tap a table, add items, pay.',
  },
  [PATHS.ownerKitchen]: {
    title: 'Kitchen',
    subtitle: 'Live kitchen board — queued, preparing, and ready tickets.',
  },
  [PATHS.ownerCafe]: {
    title: 'Cafe POS',
    subtitle: 'Quick takeaway billing with add-ons and combos.',
  },
  [PATHS.ownerGrocery]: {
    title: 'Grocery POS',
    subtitle: 'Scan-first billing with barcode lookup, weight quantities, and udhari.',
  },
  [PATHS.ownerStationery]: {
    title: 'Stationery POS',
    subtitle: 'Search-first billing with barcode, bulk rates, and optional credit.',
  },
  [PATHS.ownerHardware]: {
    title: 'Hardware POS',
    subtitle: 'Bill pipes, cement, and tiles by length, weight, or area with clear unit prices.',
  },
  [PATHS.ownerClothing]: {
    title: 'Clothing POS',
    subtitle: 'Pick size and color from live variant stock. Product images appear as thumbnails.',
  },
  [PATHS.ownerReturns]: {
    title: 'Returns / Exchange',
    subtitle: 'Restock the original size/color or swap into another variant against a finalized bill.',
  },
  [PATHS.ownerRepairs]: {
    title: 'Repairs',
    subtitle: 'Track service tickets from drop-off through ready for pickup.',
  },
  [PATHS.ownerInstallations]: {
    title: 'Installations',
    subtitle: 'Schedule and track on-site installs linked to sold serial units.',
  },
  [PATHS.ownerQuotations]: {
    title: 'Quotations',
    subtitle: 'Build customer quotes and convert accepted lines into bills.',
  },
  [PATHS.ownerPriceLists]: {
    title: 'Price Lists',
    subtitle: 'Wholesale, retail, and customer-wise pricing matrices.',
  },
  [PATHS.ownerSalesOrders]: {
    title: 'Sales Orders',
    subtitle: 'Customer SOs that convert to bills when fulfilled.',
  },
  [PATHS.ownerPurchaseOrders]: {
    title: 'Purchase Orders',
    subtitle: 'Supplier POs that convert to purchases when stock arrives.',
  },
  [PATHS.ownerChallans]: {
    title: 'Delivery Challans',
    subtitle: 'Dispatch documents with printable PDFs; convert to bills when ready.',
  },
  [PATHS.ownerWarehouses]: {
    title: 'Warehouses',
    subtitle: 'Locations, balances, and stock transfers between warehouses.',
  },
  [PATHS.ownerTourPackages]: {
    title: 'Tour Packages',
    subtitle: 'Service packages with pricing — billed without inventory stock.',
  },
  [PATHS.ownerTravelBookings]: {
    title: 'Travel Bookings',
    subtitle: 'Booking board with advances, remaining payments, and trip status.',
  },
  [PATHS.ownerTravelAgents]: {
    title: 'Travel Agents',
    subtitle: 'Agent directory and commission report by booking.',
  },
  [PATHS.ownerCredit]: {
    title: 'Credit / Udhari',
    subtitle: 'Customer and supplier outstanding balances, collections, and ledger history.',
  },
  [PATHS.ownerOutstanding]: {
    title: 'Outstanding Report',
    subtitle: 'Aged customer and supplier dues (0–30, 31–60, 61–90, 90+ days).',
  },
  [PATHS.ownerBatches]: {
    title: 'Batches / Expiry',
    subtitle: 'Receive dated batches and review near-expiry stock.',
  },
  [PATHS.ownerRecipes]: {
    title: 'Recipes',
    subtitle: 'Bill of materials — menu items mapped to ingredient stock.',
  },
  [PATHS.ownerProduction]: {
    title: 'Production',
    subtitle: 'Bake runs that consume ingredients and increase finished goods stock.',
  },
  [PATHS.ownerCakeOrders]: {
    title: 'Cake Orders',
    subtitle: 'Custom cakes with size, flavor, advances, delivery time, and status board.',
  },
  [PATHS.ownerFurnitureOrders]: {
    title: 'Furniture Orders',
    subtitle: 'Custom pieces with dimensions, material, advances, delivery time, and status board.',
  },
  [PATHS.ownerDeliveries]: {
    title: 'Deliveries',
    subtitle: 'Schedule and track last-mile delivery for ready furniture orders.',
  },
  [PATHS.ownerWastage]: {
    title: 'Wastage',
    subtitle: 'Log spoilage and prep loss — stock deducts automatically.',
  },
  [PATHS.ownerVariants]: {
    title: 'Variants',
    subtitle: 'Size, color, and variant stock for clothing and related shops.',
  },
  [PATHS.ownerSerials]: {
    title: 'Serial / IMEI',
    subtitle: 'Receive unique units and see which IMEIs are still in stock.',
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
  const { user, logout, updateUser } = useAuth();
  const { filterByModule } = useModules();
  const navigate = useNavigate();
  const location = useLocation();
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  const [mobileOpen, setMobileOpen] = useState(false);
  const [anchorEl, setAnchorEl] = useState(null);
  const entitled = subscriptionAllowsAccess(user?.tenant?.subscription);
  const visibleNav = useMemo(
    () => pruneEmptySections(filterByModule(navItems, user?.tenant?.business_type)),
    [filterByModule, user?.tenant?.business_type],
  );

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

  const meta = useMemo(() => {
    const base = titles[location.pathname] || {
      title: 'Owner Console',
      subtitle: '',
    };
    if (
      user?.tenant?.business_type === 'hotel_restaurant' &&
      location.pathname === PATHS.ownerUsers
    ) {
      return {
        title: 'Billing Users',
        subtitle: 'View, add, edit, and deactivate billing counter users.',
      };
    }
    return base;
  }, [location.pathname, user?.tenant?.business_type]);

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
            {user?.tenant?.business_type === 'hotel_restaurant'
              ? 'Owner · Hotel'
              : 'Owner · Console'}
          </Typography>
        </Box>
      </Toolbar>
      <Divider />
      <List sx={{ px: 1, pt: 0.75, pb: 1.5, flexGrow: 1, overflowY: 'auto' }}>
        {visibleNav.map((item, index) => {
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
                primary={
                  user?.tenant?.business_type === 'hotel_restaurant' &&
                  item.to === PATHS.ownerUsers
                    ? 'Billing Users'
                    : item.label
                }
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
                : `Business Dashboard · ${meta.title}`}
            </Typography>
          </Box>
          <Chip
            size="small"
            label="OWNER"
            color="primary"
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
  const location = useLocation();
  const { user } = useAuth();
  const entitled = subscriptionAllowsAccess(user?.tenant?.subscription);
  const showApp = entitled || isAccountPath(location.pathname);
  return (
    <MainContent>
      {!meta.hidePageHeader ? (
        <PageHeader
          title={meta.title}
          subtitle={meta.subtitle}
          actions={<PageActionsSlot />}
        />
      ) : null}
      {!entitled ? <SubscriptionLockout user={user} accountPath={PATHS.ownerProfile} /> : null}
      {showApp ? (
        <RouteErrorBoundary key={location.pathname}>
          <Outlet />
        </RouteErrorBoundary>
      ) : null}
    </MainContent>
  );
}
