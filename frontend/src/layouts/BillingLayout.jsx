import AssessmentOutlinedIcon from '@mui/icons-material/AssessmentOutlined';
import SwapVertOutlinedIcon from '@mui/icons-material/SwapVertOutlined';
import TableRestaurantOutlinedIcon from '@mui/icons-material/TableRestaurantOutlined';
import RestaurantMenuOutlinedIcon from '@mui/icons-material/RestaurantMenuOutlined';
import KitchenOutlinedIcon from '@mui/icons-material/KitchenOutlined';
import LocalCafeOutlinedIcon from '@mui/icons-material/LocalCafeOutlined';
import ExtensionOutlinedIcon from '@mui/icons-material/ExtensionOutlined';
import LocalOfferOutlinedIcon from '@mui/icons-material/LocalOfferOutlined';
import LunchDiningOutlinedIcon from '@mui/icons-material/LunchDiningOutlined';
import ReceiptLongOutlinedIcon from '@mui/icons-material/ReceiptLongOutlined';
import LocalShippingOutlinedIcon from '@mui/icons-material/LocalShippingOutlined';
import CheckroomOutlinedIcon from '@mui/icons-material/CheckroomOutlined';
import AssignmentReturnOutlinedIcon from '@mui/icons-material/AssignmentReturnOutlined';
import BoltOutlinedIcon from '@mui/icons-material/BoltOutlined';
import PaymentsOutlinedIcon from '@mui/icons-material/PaymentsOutlined';
import PriceChangeOutlinedIcon from '@mui/icons-material/PriceChangeOutlined';
import RequestQuoteOutlinedIcon from '@mui/icons-material/RequestQuoteOutlined';
import ShoppingCartCheckoutOutlinedIcon from '@mui/icons-material/ShoppingCartCheckoutOutlined';
import AssignmentOutlinedIcon from '@mui/icons-material/AssignmentOutlined';
import WarehouseOutlinedIcon from '@mui/icons-material/WarehouseOutlined';
import AccountBalanceWalletOutlinedIcon from '@mui/icons-material/AccountBalanceWalletOutlined';
import ContactsOutlinedIcon from '@mui/icons-material/ContactsOutlined';
import FlightTakeoffOutlinedIcon from '@mui/icons-material/FlightTakeoffOutlined';
import HandshakeOutlinedIcon from '@mui/icons-material/HandshakeOutlined';
import LuggageOutlinedIcon from '@mui/icons-material/LuggageOutlined';
import CategoryOutlinedIcon from '@mui/icons-material/CategoryOutlined';
import DashboardOutlinedIcon from '@mui/icons-material/DashboardOutlined';
import ListAltOutlinedIcon from '@mui/icons-material/ListAltOutlined';
import LockOutlinedIcon from '@mui/icons-material/LockOutlined';
import LogoutOutlinedIcon from '@mui/icons-material/LogoutOutlined';
import PersonOutlinedIcon from '@mui/icons-material/PersonOutlined';
import Inventory2OutlinedIcon from '@mui/icons-material/Inventory2Outlined';
import PointOfSaleOutlinedIcon from '@mui/icons-material/PointOfSaleOutlined';
import ShoppingCartOutlinedIcon from '@mui/icons-material/ShoppingCartOutlined';
import MenuBookOutlinedIcon from '@mui/icons-material/MenuBookOutlined';
import DeleteSweepOutlinedIcon from '@mui/icons-material/DeleteSweepOutlined';
import StraightenOutlinedIcon from '@mui/icons-material/StraightenOutlined';
import {
  Box,
  Divider,
  ListItemIcon,
  Menu,
  MenuItem,
  Toolbar,
  Typography,
  useMediaQuery,
} from '@mui/material';
import { useTheme } from '@mui/material/styles';
import { useEffect, useMemo, useState } from 'react';
import { Outlet, useLocation, useNavigate } from 'react-router-dom';
import MainContent from '../components/MainContent';
import PageHeader from '../components/PageHeader';
import RouteErrorBoundary from '../components/RouteErrorBoundary';
import AppNavDrawer from '../components/shell/AppNavDrawer';
import AppShellDrawers from '../components/shell/AppShellDrawers';
import AppTopBar from '../components/shell/AppTopBar';
import NotificationBell from '../components/NotificationBell';
import SubscriptionLockout from '../components/SubscriptionLockout';
import { useAuth } from '../context/AuthContext';
import { useModules } from '../context/ModulesContext';
import { usePermissions } from '../hooks/usePermissions';
import { PageActionsProvider, PageActionsSlot } from '../context/PageActionsContext';
import { fetchMe, logoutRequest } from '../services/authService';
import { PATHS } from '../routes/paths';
import { layout } from '../theme/tokens';
import { isAccountPath, subscriptionAllowsAccess } from '../utils/subscriptionAccess';

function billingBrandSubtitle(user, { isOwner, isManager }) {
  const type = user?.tenant?.business_type;
  if (type === 'hotel_restaurant') return 'Hotel Billing';
  if (type === 'cafe_tea') return 'Cafe Billing';
  if (type === 'clothing') return 'Clothing Billing';
  if (type === 'grocery_kirana') return 'Grocery Billing';
  if (type === 'stationery') return 'Stationery Billing';
  if (type === 'hardware' || type === 'building_material') return 'Hardware Billing';
  if (type === 'travel_agency') return 'Travel Billing';
  if (isOwner) return 'Owner · Billing';
  if (isManager) return 'Manager · Billing';
  return 'Billing';
}

/**
 * Billing sidebar order — hotel groups follow desk workflow:
 * Sell → Floor → Menu → Customers → Reports → Account.
 * Other business types keep a flat sell-first list without hotel-only sections.
 */
const billingNav = [
  { to: PATHS.billingHome, label: 'Dashboard', icon: <DashboardOutlinedIcon />, end: true },

  {
    type: 'section',
    label: 'Sell',
    businessTypes: ['hotel_restaurant', 'cafe_tea', 'clothing', 'hardware'],
  },
  {
    to: PATHS.billingRestaurantBilling,
    label: 'Table Bill',
    icon: <PointOfSaleOutlinedIcon />,
    module: 'table_management',
    businessTypes: ['hotel_restaurant'],
    emphasize: true,
  },
  {
    to: PATHS.billingCafe,
    label: 'Cafe POS',
    icon: <LocalCafeOutlinedIcon />,
    module: 'addons_combos',
    businessTypes: ['cafe_tea'],
    emphasize: true,
  },
  {
    to: PATHS.billingClothing,
    label: 'Clothing POS',
    icon: <CheckroomOutlinedIcon />,
    module: 'variants',
    businessTypes: ['clothing'],
    emphasize: true,
  },
  {
    to: PATHS.billingHardware,
    label: 'Hardware POS',
    icon: <StraightenOutlinedIcon />,
    module: 'uom_measurement',
    businessTypes: ['hardware'],
    emphasize: true,
  },
  {
    to: PATHS.billingNew,
    label: 'Quick Bill',
    icon: <BoltOutlinedIcon />,
    businessTypes: ['hotel_restaurant', 'cafe_tea', 'clothing'],
  },
  {
    to: PATHS.billingNew,
    label: 'New Bill',
    icon: <ReceiptLongOutlinedIcon />,
    hideForBusinessTypes: ['hotel_restaurant', 'cafe_tea', 'hardware'],
  },
  {
    to: PATHS.billingBills,
    label: "Today's Bills",
    icon: <ReceiptLongOutlinedIcon />,
    businessTypes: ['hotel_restaurant', 'cafe_tea', 'clothing', 'hardware'],
  },
  {
    to: PATHS.billingBills,
    label: 'Bills',
    icon: <ReceiptLongOutlinedIcon />,
    hideForBusinessTypes: ['hotel_restaurant', 'cafe_tea', 'hardware'],
  },

  { type: 'section', label: 'Floor', businessTypes: ['hotel_restaurant'] },
  {
    to: PATHS.billingTables,
    label: 'Tables',
    icon: <TableRestaurantOutlinedIcon />,
    module: 'table_management',
    businessTypes: ['hotel_restaurant'],
  },
  {
    to: PATHS.billingKitchen,
    label: 'Kitchen',
    icon: <KitchenOutlinedIcon />,
    module: 'kitchen',
    businessTypes: ['hotel_restaurant'],
  },
  {
    to: PATHS.billingOrders,
    label: 'Open Orders',
    icon: <ListAltOutlinedIcon />,
    module: 'order_channels',
    businessTypes: ['hotel_restaurant'],
  },

  { type: 'section', label: 'Menu', businessTypes: ['hotel_restaurant', 'cafe_tea'] },
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
    to: PATHS.billingAddons,
    label: 'Add-ons',
    icon: <ExtensionOutlinedIcon />,
    module: 'addons_combos',
    businessTypes: ['cafe_tea'],
  },
  {
    to: PATHS.billingCombos,
    label: 'Combos',
    icon: <LunchDiningOutlinedIcon />,
    module: 'addons_combos',
    businessTypes: ['cafe_tea'],
  },
  {
    to: PATHS.billingCoupons,
    label: 'Coupons',
    icon: <LocalOfferOutlinedIcon />,
    module: 'addons_combos',
    businessTypes: ['cafe_tea'],
  },
  {
    to: PATHS.billingItems,
    label: 'Items',
    icon: <Inventory2OutlinedIcon />,
    businessTypes: ['hotel_restaurant', 'cafe_tea'],
  },
  {
    to: PATHS.billingIngredients,
    label: 'Ingredients',
    icon: <KitchenOutlinedIcon />,
    module: 'recipe',
    businessTypes: ['cafe_tea'],
  },
  {
    to: PATHS.billingCategories,
    label: 'Categories',
    icon: <CategoryOutlinedIcon />,
    businessTypes: ['hotel_restaurant', 'cafe_tea'],
  },
  {
    to: PATHS.billingItems,
    label: 'Items',
    icon: <Inventory2OutlinedIcon />,
    hideForBusinessTypes: ['hotel_restaurant', 'cafe_tea'],
  },
  {
    to: PATHS.billingCategories,
    label: 'Categories',
    icon: <CategoryOutlinedIcon />,
    hideForBusinessTypes: ['hotel_restaurant', 'cafe_tea'],
  },

  {
    type: 'section',
    label: 'Customers',
    businessTypes: ['hotel_restaurant', 'cafe_tea', 'clothing', 'hardware'],
  },
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
    hideForBusinessTypes: ['hotel_restaurant', 'cafe_tea'],
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
    to: PATHS.billingReturns,
    label: 'Returns / Exchange',
    icon: <AssignmentReturnOutlinedIcon />,
    module: 'returns_exchange',
    businessTypes: ['clothing'],
  },
  {
    to: PATHS.billingReturns,
    label: 'Returns / Exchange',
    icon: <AssignmentReturnOutlinedIcon />,
    module: 'returns_exchange',
    hideForBusinessTypes: ['clothing'],
  },

  { type: 'section', label: 'Account' },
  { to: PATHS.billingProfile, label: 'Profile', icon: <PersonOutlinedIcon /> },
];

/** Slim sidebar for hotel Billing Users — desk workflow + operational modules. */
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
    to: PATHS.billingKitchen,
    label: 'Kitchen',
    icon: <KitchenOutlinedIcon />,
    module: 'kitchen',
  },
  {
    to: PATHS.billingOrders,
    label: 'Open Orders',
    icon: <ListAltOutlinedIcon />,
    module: 'order_channels',
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
  {
    to: PATHS.billingMenu,
    label: 'Menu Board',
    icon: <RestaurantMenuOutlinedIcon />,
    module: 'restaurant_menu',
  },
  {
    to: PATHS.billingCustomers,
    label: 'Customers',
    icon: <ContactsOutlinedIcon />,
  },
  {
    to: PATHS.billingExpenses,
    label: 'Expenses',
    icon: <PaymentsOutlinedIcon />,
  },
  {
    to: PATHS.billingWastage,
    label: 'Wastage',
    icon: <DeleteSweepOutlinedIcon />,
    module: 'wastage',
  },
  { type: 'section', label: 'Account' },
  { to: PATHS.billingProfile, label: 'Profile', icon: <PersonOutlinedIcon /> },
  {
    to: PATHS.billingChangePassword,
    label: 'Settings',
    icon: <LockOutlinedIcon />,
  },
];

/** Slim sidebar for cafe Billing Users — Cafe POS first, no Hotel table desk. */
const cafeBillingUserNav = [
  { to: PATHS.billingHome, label: 'Dashboard', icon: <DashboardOutlinedIcon />, end: true },
  { type: 'section', label: 'Billing' },
  {
    to: PATHS.billingCafe,
    label: 'Cafe POS',
    icon: <LocalCafeOutlinedIcon />,
    module: 'addons_combos',
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
    to: PATHS.billingMenu,
    label: 'Menu',
    icon: <RestaurantMenuOutlinedIcon />,
    module: 'restaurant_menu',
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
  {
    to: PATHS.billingCustomers,
    label: 'Customers',
    icon: <ContactsOutlinedIcon />,
  },
  {
    to: PATHS.billingCredit,
    label: 'Credit / Udhari',
    icon: <AccountBalanceWalletOutlinedIcon />,
    module: 'customer_credit',
  },
  {
    to: PATHS.billingExpenses,
    label: 'Expenses',
    icon: <PaymentsOutlinedIcon />,
  },
  {
    to: PATHS.billingWastage,
    label: 'Wastage',
    icon: <DeleteSweepOutlinedIcon />,
    module: 'wastage',
  },
  { type: 'section', label: 'Account' },
  { to: PATHS.billingProfile, label: 'Profile', icon: <PersonOutlinedIcon /> },
  {
    to: PATHS.billingChangePassword,
    label: 'Settings',
    icon: <LockOutlinedIcon />,
  },
];

/** Travel agency billing desk — bookings first, then packages and commission. */
const travelAgencyBillingNav = [
  { type: 'section', label: 'Travel desk' },
  {
    to: PATHS.billingTravelBookings,
    label: 'Travel Bookings',
    icon: <LuggageOutlinedIcon />,
    module: 'travel_bookings',
    emphasize: true,
  },
  {
    to: PATHS.billingTourPackages,
    label: 'Tour Packages',
    icon: <FlightTakeoffOutlinedIcon />,
    module: 'tour_packages',
  },
  {
    to: PATHS.billingTravelAgents,
    label: 'Travel Agents',
    icon: <HandshakeOutlinedIcon />,
    module: 'travel_commission',
  },
  { type: 'section', label: 'Billing' },
  { to: PATHS.billingNew, label: 'New Bill', icon: <ReceiptLongOutlinedIcon /> },
  { to: PATHS.billingBills, label: 'Bills', icon: <ReceiptLongOutlinedIcon /> },
  { type: 'section', label: 'Customers' },
  { to: PATHS.billingCustomers, label: 'Customers', icon: <ContactsOutlinedIcon /> },
  { to: PATHS.billingExpenses, label: 'Expenses', icon: <PaymentsOutlinedIcon /> },
];

/** Slim sidebar for travel agency Billing Users — desk workflow only. */
const travelAgencyBillingUserNav = [
  { to: PATHS.billingHome, label: 'Dashboard', icon: <DashboardOutlinedIcon />, end: true },
  { type: 'section', label: 'Travel desk' },
  {
    to: PATHS.billingTravelBookings,
    label: 'Travel Bookings',
    icon: <LuggageOutlinedIcon />,
    module: 'travel_bookings',
    emphasize: true,
  },
  {
    to: PATHS.billingTourPackages,
    label: 'Tour Packages',
    icon: <FlightTakeoffOutlinedIcon />,
    module: 'tour_packages',
  },
  {
    to: PATHS.billingTravelAgents,
    label: 'Travel Agents',
    icon: <HandshakeOutlinedIcon />,
    module: 'travel_commission',
  },
  { type: 'section', label: 'Billing' },
  { to: PATHS.billingNew, label: 'New Bill', icon: <ReceiptLongOutlinedIcon /> },
  { to: PATHS.billingBills, label: 'Bills', icon: <ReceiptLongOutlinedIcon /> },
  { to: PATHS.billingCustomers, label: 'Customers', icon: <ContactsOutlinedIcon /> },
  { type: 'section', label: 'Account' },
  { to: PATHS.billingProfile, label: 'Profile', icon: <PersonOutlinedIcon /> },
  {
    to: PATHS.billingChangePassword,
    label: 'Settings',
    icon: <LockOutlinedIcon />,
  },
];

/** Wholesale trade documents — SO, PO, challans, warehouses (shared owner + billing user nav). */
const wholesaleTradeDocsNav = [
  { type: 'section', label: 'Trade documents' },
  {
    to: PATHS.billingSalesOrders,
    label: 'Sales Orders',
    icon: <ShoppingCartCheckoutOutlinedIcon />,
    module: 'sales_orders',
  },
  {
    to: PATHS.billingPurchaseOrders,
    label: 'Purchase Orders',
    icon: <AssignmentOutlinedIcon />,
    module: 'purchase_orders',
  },
  {
    to: PATHS.billingQuotations,
    label: 'Quotations',
    icon: <RequestQuoteOutlinedIcon />,
    module: 'quotation',
  },
  {
    to: PATHS.billingChallans,
    label: 'Delivery Challans',
    icon: <LocalShippingOutlinedIcon />,
    module: 'delivery_challan',
  },
  {
    to: PATHS.billingWarehouses,
    label: 'Warehouses',
    icon: <WarehouseOutlinedIcon />,
    module: 'warehouse',
  },
];

/** Wholesale billing desk — barcode POS first, then credit and catalog. */
const wholesaleBillingNav = [
  { type: 'section', label: 'Counter' },
  {
    to: PATHS.billingGrocery,
    label: 'Wholesale POS',
    icon: <ShoppingCartOutlinedIcon />,
    module: 'barcode_pos',
    emphasize: true,
  },
  { to: PATHS.billingNew, label: 'Manual Bill', icon: <PointOfSaleOutlinedIcon /> },
  { to: PATHS.billingBills, label: 'Bills', icon: <ReceiptLongOutlinedIcon /> },
  { type: 'section', label: 'Trade pricing' },
  {
    to: PATHS.billingPriceLists,
    label: 'Price Lists',
    icon: <PriceChangeOutlinedIcon />,
    module: 'price_lists',
  },
  ...wholesaleTradeDocsNav,
  { type: 'section', label: 'Udhari (Credit)' },
  {
    to: PATHS.billingCredit,
    label: 'Credit / Udhari',
    icon: <AccountBalanceWalletOutlinedIcon />,
    module: 'customer_credit',
  },
  { type: 'section', label: 'Catalog setup' },
  { to: PATHS.billingCategories, label: 'Categories', icon: <CategoryOutlinedIcon /> },
  { to: PATHS.billingItems, label: 'Items', icon: <Inventory2OutlinedIcon /> },
  { type: 'section', label: 'Stock in' },
  { to: PATHS.billingSuppliers, label: 'Suppliers', icon: <LocalShippingOutlinedIcon /> },
  { to: PATHS.billingPurchases, label: 'Purchases', icon: <ShoppingCartOutlinedIcon /> },
  { type: 'section', label: 'Customers & money' },
  { to: PATHS.billingCustomers, label: 'Customers', icon: <ContactsOutlinedIcon /> },
  { to: PATHS.billingExpenses, label: 'Expenses', icon: <PaymentsOutlinedIcon /> },
];

/** Slim sidebar for wholesale Billing Users — POS + udhari only. */
const wholesaleBillingUserNav = [
  { to: PATHS.billingHome, label: 'Dashboard', icon: <DashboardOutlinedIcon />, end: true },
  { type: 'section', label: 'Counter' },
  {
    to: PATHS.billingGrocery,
    label: 'Wholesale POS',
    icon: <ShoppingCartOutlinedIcon />,
    module: 'barcode_pos',
    emphasize: true,
  },
  { to: PATHS.billingBills, label: 'Bills', icon: <ReceiptLongOutlinedIcon /> },
  { type: 'section', label: 'Trade pricing' },
  {
    to: PATHS.billingPriceLists,
    label: 'Price Lists',
    icon: <PriceChangeOutlinedIcon />,
    module: 'price_lists',
  },
  ...wholesaleTradeDocsNav,
  { to: PATHS.billingCustomers, label: 'Customers', icon: <ContactsOutlinedIcon /> },
  { type: 'section', label: 'Udhari (Credit)' },
  {
    to: PATHS.billingCredit,
    label: 'Credit / Udhari',
    icon: <AccountBalanceWalletOutlinedIcon />,
    module: 'customer_credit',
  },
  { type: 'section', label: 'Account' },
  { to: PATHS.billingProfile, label: 'Profile', icon: <PersonOutlinedIcon /> },
  {
    to: PATHS.billingChangePassword,
    label: 'Settings',
    icon: <LockOutlinedIcon />,
  },
];

/** Grocery / Kirana billing desk — counter first, then udhari and catalog. */
const groceryBillingNav = [
  { type: 'section', label: 'Counter' },
  {
    to: PATHS.billingGrocery,
    label: 'Grocery POS',
    icon: <ShoppingCartOutlinedIcon />,
    module: 'barcode_pos',
    emphasize: true,
  },
  { to: PATHS.billingBills, label: 'Bills', icon: <ReceiptLongOutlinedIcon /> },
  { type: 'section', label: 'Udhari (Credit)' },
  {
    to: PATHS.billingCredit,
    label: 'Credit / Udhari',
    icon: <AccountBalanceWalletOutlinedIcon />,
    module: 'customer_credit',
  },
  { type: 'section', label: 'Catalog setup' },
  { to: PATHS.billingCategories, label: 'Categories', icon: <CategoryOutlinedIcon /> },
  { to: PATHS.billingItems, label: 'Items', icon: <Inventory2OutlinedIcon /> },
  { type: 'section', label: 'Stock in' },
  { to: PATHS.billingSuppliers, label: 'Suppliers', icon: <LocalShippingOutlinedIcon /> },
  { to: PATHS.billingPurchases, label: 'Purchases', icon: <ShoppingCartOutlinedIcon /> },
  { type: 'section', label: 'Customers & money' },
  { to: PATHS.billingCustomers, label: 'Customers', icon: <ContactsOutlinedIcon /> },
  { to: PATHS.billingExpenses, label: 'Expenses', icon: <PaymentsOutlinedIcon /> },
];

/** Stationery billing desk — search POS first, then udhari and catalog. */
const stationeryBillingNav = [
  { type: 'section', label: 'Counter' },
  {
    to: PATHS.billingStationery,
    label: 'Stationery POS',
    icon: <MenuBookOutlinedIcon />,
    module: 'barcode_pos',
    emphasize: true,
  },
  { to: PATHS.billingBills, label: 'Bills', icon: <ReceiptLongOutlinedIcon /> },
  { type: 'section', label: 'Udhari (Credit)' },
  {
    to: PATHS.billingCredit,
    label: 'Credit / Udhari',
    icon: <AccountBalanceWalletOutlinedIcon />,
    module: 'customer_credit',
  },
  { type: 'section', label: 'Catalog setup' },
  { to: PATHS.billingCategories, label: 'Categories', icon: <CategoryOutlinedIcon /> },
  { to: PATHS.billingItems, label: 'Items', icon: <Inventory2OutlinedIcon /> },
  { type: 'section', label: 'Stock in' },
  { to: PATHS.billingSuppliers, label: 'Suppliers', icon: <LocalShippingOutlinedIcon /> },
  { to: PATHS.billingPurchases, label: 'Purchases', icon: <ShoppingCartOutlinedIcon /> },
  { type: 'section', label: 'Customers & money' },
  { to: PATHS.billingCustomers, label: 'Customers', icon: <ContactsOutlinedIcon /> },
  { to: PATHS.billingExpenses, label: 'Expenses', icon: <PaymentsOutlinedIcon /> },
];

/** Slim sidebar for stationery Billing Users — POS + udhari only. */
const stationeryBillingUserNav = [
  { to: PATHS.billingHome, label: 'Dashboard', icon: <DashboardOutlinedIcon />, end: true },
  { type: 'section', label: 'Counter' },
  {
    to: PATHS.billingStationery,
    label: 'Stationery POS',
    icon: <MenuBookOutlinedIcon />,
    module: 'barcode_pos',
    emphasize: true,
  },
  { to: PATHS.billingBills, label: 'Bills', icon: <ReceiptLongOutlinedIcon /> },
  { type: 'section', label: 'Udhari (Credit)' },
  {
    to: PATHS.billingCredit,
    label: 'Credit / Udhari',
    icon: <AccountBalanceWalletOutlinedIcon />,
    module: 'customer_credit',
  },
  { type: 'section', label: 'Account' },
  { to: PATHS.billingProfile, label: 'Profile', icon: <PersonOutlinedIcon /> },
  {
    to: PATHS.billingChangePassword,
    label: 'Settings',
    icon: <LockOutlinedIcon />,
  },
];

/** Slim sidebar for grocery Billing Users — POS + udhari only. */
const groceryBillingUserNav = [
  { to: PATHS.billingHome, label: 'Dashboard', icon: <DashboardOutlinedIcon />, end: true },
  { type: 'section', label: 'Counter' },
  {
    to: PATHS.billingGrocery,
    label: 'Grocery POS',
    icon: <ShoppingCartOutlinedIcon />,
    module: 'barcode_pos',
    emphasize: true,
  },
  { to: PATHS.billingBills, label: 'Bills', icon: <ReceiptLongOutlinedIcon /> },
  { type: 'section', label: 'Udhari (Credit)' },
  {
    to: PATHS.billingCredit,
    label: 'Credit / Udhari',
    icon: <AccountBalanceWalletOutlinedIcon />,
    module: 'customer_credit',
  },
  { type: 'section', label: 'Account' },
  { to: PATHS.billingProfile, label: 'Profile', icon: <PersonOutlinedIcon /> },
  {
    to: PATHS.billingChangePassword,
    label: 'Settings',
    icon: <LockOutlinedIcon />,
  },
];

/** Slim sidebar for clothing Billing Users — Clothing POS first, no F&B floor. */
const clothingBillingUserNav = [
  { to: PATHS.billingHome, label: 'Dashboard', icon: <DashboardOutlinedIcon />, end: true },
  { type: 'section', label: 'Billing' },
  {
    to: PATHS.billingClothing,
    label: 'Clothing POS',
    icon: <CheckroomOutlinedIcon />,
    module: 'variants',
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
    to: PATHS.billingReturns,
    label: 'Returns / Exchange',
    icon: <AssignmentReturnOutlinedIcon />,
    module: 'returns_exchange',
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
  {
    to: PATHS.billingCustomers,
    label: 'Customers',
    icon: <ContactsOutlinedIcon />,
  },
  { type: 'section', label: 'Account' },
  { to: PATHS.billingProfile, label: 'Profile', icon: <PersonOutlinedIcon /> },
  {
    to: PATHS.billingChangePassword,
    label: 'Settings',
    icon: <LockOutlinedIcon />,
  },
];

/** Slim sidebar for hardware / building-material Billing Users — UoM POS first. */
const hardwareBillingUserNav = [
  { to: PATHS.billingHome, label: 'Dashboard', icon: <DashboardOutlinedIcon />, end: true },
  { type: 'section', label: 'Billing' },
  {
    to: PATHS.billingHardware,
    label: 'Hardware POS',
    icon: <StraightenOutlinedIcon />,
    module: 'uom_measurement',
    businessTypes: ['hardware'],
    emphasize: true,
  },
  {
    to: PATHS.billingBills,
    label: "Today's Bills",
    icon: <ReceiptLongOutlinedIcon />,
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
  {
    to: PATHS.billingCustomers,
    label: 'Customers',
    icon: <ContactsOutlinedIcon />,
  },
  {
    to: PATHS.billingCredit,
    label: 'Credit / Udhari',
    icon: <AccountBalanceWalletOutlinedIcon />,
    module: 'customer_credit',
  },
  {
    to: PATHS.billingExpenses,
    label: 'Expenses',
    icon: <PaymentsOutlinedIcon />,
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
    if (businessType === 'cafe_tea') {
      return {
        title: 'Cafe Billing',
        subtitle: 'Cafe POS → add-ons & combos → pay → print.',
      };
    }
    if (businessType === 'clothing') {
      return {
        title: 'Clothing Billing',
        subtitle: 'Clothing POS → pick size & color → pay → print.',
      };
    }
    if (businessType === 'hardware') {
      return {
        title: 'Hardware / Building Material Billing',
        subtitle: 'Hardware POS → length / weight / area → pay → print.',
      };
    }
    if (businessType === 'travel_agency') {
      return {
        title: 'Travel Billing',
        subtitle: 'Bookings, package bills, and commission — today’s overview.',
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
  if (pathname.startsWith(PATHS.billingRecipes)) {
    return {
      title: 'Recipes',
      subtitle: 'Link menu dishes to ingredient quantities for stock deduction.',
    };
  }
  if (pathname.startsWith(PATHS.billingIngredients)) {
    return {
      title: 'Ingredients',
      subtitle: 'Raw ingredient stock for Cafe recipes and linked add-ons.',
    };
  }
  if (pathname.startsWith(PATHS.billingWastage)) {
    return {
      title: 'Wastage',
      subtitle: 'Record food or ingredient wastage and keep stock accurate.',
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
  if (pathname.startsWith(PATHS.billingAddons)) {
    return {
      title: 'Add-ons',
      subtitle: 'Option groups for cafe menu items — milk, size, toppings, and more.',
    };
  }
  if (pathname.startsWith(PATHS.billingCombos)) {
    return {
      title: 'Combos',
      subtitle: 'Fixed-price bundles of menu items for Cafe POS.',
    };
  }
  if (pathname.startsWith(PATHS.billingCoupons)) {
    return {
      title: 'Coupons',
      subtitle: 'Promo codes for Cafe POS — percent or flat discounts.',
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
      title: businessType === 'wholesale' ? 'Wholesale POS' : 'Grocery POS',
      subtitle:
        businessType === 'wholesale'
          ? 'Scan-first trade billing with customer price lists, bulk tiers, and udhari.'
          : 'Scan-first billing with barcode lookup, weight quantities, and udhari.',
    };
  }
  if (pathname.startsWith(PATHS.billingPriceLists)) {
    return {
      title: 'Price Lists',
      subtitle: 'View wholesale and VIP trade rates. Billing users can read prices; owner/manager can edit.',
    };
  }
  if (pathname.startsWith(PATHS.billingSalesOrders)) {
    return {
      title: 'Sales Orders',
      subtitle: 'Track dealer SOs (SO-#####). Billing users can view; owner/manager confirms and converts to bill.',
    };
  }
  if (pathname.startsWith(PATHS.billingPurchaseOrders)) {
    return {
      title: 'Purchase Orders',
      subtitle: 'Track supplier POs (PO-#####). Billing users can view; owner/manager confirms and converts to purchase.',
    };
  }
  if (pathname.startsWith(PATHS.billingQuotations)) {
    return {
      title: 'Quotations',
      subtitle: 'Trade quotes for customers. Billing users can view and download; owner/manager creates and converts.',
    };
  }
  if (pathname.startsWith(PATHS.billingChallans)) {
    return {
      title: 'Delivery Challans',
      subtitle: 'Dispatch documents before invoicing. Billing users can view and print PDFs.',
    };
  }
  if (pathname.startsWith(PATHS.billingWarehouses)) {
    return {
      title: 'Warehouses',
      subtitle: 'Godown stock by location. Billing users can view balances; owner/manager manages transfers.',
    };
  }
  if (pathname.startsWith(PATHS.billingTourPackages)) {
    return {
      title: 'Tour Packages',
      subtitle: 'View packages and create service bills. Owner/manager creates and edits packages.',
    };
  }
  if (pathname.startsWith(PATHS.billingTravelBookings)) {
    return {
      title: 'Travel Bookings',
      subtitle: 'Create bookings, record payments, and track status. Owner/manager confirms trips.',
    };
  }
  if (pathname.startsWith(PATHS.billingTravelAgents)) {
    return {
      title: 'Travel Agents',
      subtitle: 'Agent commission report. Billing users can view; owner/manager manages agents and payouts.',
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
      subtitle: 'Scan variant barcodes or pick size and color from live stock.',
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
    const isCafe = businessType === 'cafe_tea';
    const isClothing = businessType === 'clothing';
    const isGrocery = businessType === 'grocery_kirana';
    const isWholesale = businessType === 'wholesale';
    const isStationery = businessType === 'stationery';
    const isHardware = businessType === 'hardware' || businessType === 'building_material';
    const isTravelAgency = businessType === 'travel_agency';
    const isBillingUser = role === 'BILLING_USER';
    let items;

    const withOptionalReports = (baseItems) => {
      let next = [...baseItems];
      if (!canReports) return next;
      const accountIdx = next.findIndex(
        (row) => row.type === 'section' && row.label === 'Account',
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
        next = [...next.slice(0, accountIdx), ...reportsBlock, ...next.slice(accountIdx)];
      } else {
        next = [...next, ...reportsBlock];
      }
      return next;
    };

    // Hotel / Cafe Billing User: keep sidebar short and desk-focused.
    if (isHotel && isBillingUser) {
      return pruneEmptySections(filterByModule(withOptionalReports(hotelBillingUserNav), businessType));
    }
    if (isCafe && isBillingUser) {
      return pruneEmptySections(filterByModule(withOptionalReports(cafeBillingUserNav), businessType));
    }
    if (isGrocery && isBillingUser) {
      return pruneEmptySections(filterByModule(withOptionalReports(groceryBillingUserNav), businessType));
    }
    if (isWholesale && isBillingUser) {
      return pruneEmptySections(filterByModule(withOptionalReports(wholesaleBillingUserNav), businessType));
    }
    if (isStationery && isBillingUser) {
      return pruneEmptySections(filterByModule(withOptionalReports(stationeryBillingUserNav), businessType));
    }
    if (isClothing && isBillingUser) {
      return pruneEmptySections(filterByModule(clothingBillingUserNav, businessType));
    }
    if (isHardware && isBillingUser) {
      return pruneEmptySections(filterByModule(withOptionalReports(hardwareBillingUserNav), businessType));
    }
    if (isTravelAgency && isBillingUser) {
      return pruneEmptySections(filterByModule(withOptionalReports(travelAgencyBillingUserNav), businessType));
    }

    if (!isOwner) {
      items = [
        { to: PATHS.billingHome, label: 'Dashboard', icon: <DashboardOutlinedIcon />, end: true },
        ...(isWholesale
          ? wholesaleBillingNav
          : isTravelAgency
            ? travelAgencyBillingNav
            : isGrocery
              ? groceryBillingNav
              : isStationery
                ? stationeryBillingNav
                : billingNav.slice(1)),
      ];
    } else {
      items = [
        {
          to: PATHS.ownerDashboard,
          label: 'Owner Dashboard',
          icon: <DashboardOutlinedIcon />,
          end: true,
        },
        ...(isWholesale
          ? wholesaleBillingNav
          : isTravelAgency
            ? travelAgencyBillingNav
            : isGrocery
              ? groceryBillingNav
              : isStationery
                ? stationeryBillingNav
                : billingNav),
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
          hideForBusinessTypes: ['hotel_restaurant', 'cafe_tea'],
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
          label: isHotel || isCafe ? 'Reports' : 'More',
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

  const roleBadge = isOwner ? 'OWNER' : isManager ? 'MANAGER' : 'BILLING';

  return (
    <Box sx={{ display: 'flex', minHeight: '100vh', bgcolor: 'background.default' }}>
      <AppTopBar
        isMobile={isMobile}
        onMenuOpen={() => setMobileOpen(true)}
        title={user?.tenant?.business_name || 'Business Billing'}
        subtitle={
          user?.tenant?.business_type_label
            ? `${user.tenant.business_type_label} · ${meta.title}`
            : meta.title
        }
        badge={roleBadge}
        notificationSlot={entitled ? <NotificationBell /> : null}
        accountMenu={{
          onOpen: (e) => setAnchorEl(e.currentTarget),
          menu: (
            <Menu anchorEl={anchorEl} open={Boolean(anchorEl)} onClose={() => setAnchorEl(null)}>
              <MenuItem disabled>
                <Box>
                  <Typography variant="body2" fontWeight={600}>
                    {user?.name}
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    {user?.email}
                  </Typography>
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
                  <ListItemIcon>
                    <DashboardOutlinedIcon fontSize="small" />
                  </ListItemIcon>
                  Owner Dashboard
                </MenuItem>
              ) : null}
              <MenuItem
                onClick={() => {
                  setAnchorEl(null);
                  navigate(PATHS.billingProfile);
                }}
              >
                <ListItemIcon>
                  <PersonOutlinedIcon fontSize="small" />
                </ListItemIcon>
                Profile
              </MenuItem>
              <MenuItem
                onClick={() => {
                  setAnchorEl(null);
                  navigate(PATHS.billingChangePassword);
                }}
              >
                <ListItemIcon>
                  <LockOutlinedIcon fontSize="small" />
                </ListItemIcon>
                Change Password
              </MenuItem>
              <MenuItem
                onClick={() => {
                  setAnchorEl(null);
                  onLogout();
                }}
              >
                <ListItemIcon>
                  <LogoutOutlinedIcon fontSize="small" />
                </ListItemIcon>
                Logout
              </MenuItem>
            </Menu>
          ),
        }}
      />

      <AppShellDrawers mobileOpen={mobileOpen} onMobileClose={() => setMobileOpen(false)}>
        <AppNavDrawer
          brandTitle={user?.tenant?.business_name || 'Billing'}
          brandSubtitle={billingBrandSubtitle(user, { isOwner, isManager })}
          navItems={navItems}
          onNavigate={() => setMobileOpen(false)}
        />
      </AppShellDrawers>

      <Box
        component="main"
        sx={{
          flexGrow: 1,
          width: { md: `calc(100% - ${layout.drawerWidth}px)` },
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
