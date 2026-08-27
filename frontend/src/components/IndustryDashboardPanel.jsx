import BakeryDiningOutlinedIcon from '@mui/icons-material/BakeryDiningOutlined';
import BuildOutlinedIcon from '@mui/icons-material/BuildOutlined';
import HandymanOutlinedIcon from '@mui/icons-material/HandymanOutlined';
import Inventory2OutlinedIcon from '@mui/icons-material/Inventory2Outlined';
import KitchenOutlinedIcon from '@mui/icons-material/KitchenOutlined';
import LocalMallOutlinedIcon from '@mui/icons-material/LocalMallOutlined';
import MenuBookOutlinedIcon from '@mui/icons-material/MenuBookOutlined';
import PhoneIphoneOutlinedIcon from '@mui/icons-material/PhoneIphoneOutlined';
import PointOfSaleOutlinedIcon from '@mui/icons-material/PointOfSaleOutlined';
import ReceiptLongOutlinedIcon from '@mui/icons-material/ReceiptLongOutlined';
import RestaurantMenuOutlinedIcon from '@mui/icons-material/RestaurantMenuOutlined';
import StorefrontOutlinedIcon from '@mui/icons-material/StorefrontOutlined';
import TableRestaurantOutlinedIcon from '@mui/icons-material/TableRestaurantOutlined';
import TravelExploreOutlinedIcon from '@mui/icons-material/TravelExploreOutlined';
import WarehouseOutlinedIcon from '@mui/icons-material/WarehouseOutlined';
import { Box, Button, Stack, Typography } from '@mui/material';
import { Link as RouterLink } from 'react-router-dom';
import Section from './Section';
import { useAuth } from '../context/AuthContext';
import { useModules } from '../context/ModulesContext';
import { PATHS } from '../routes/paths';

/**
 * Quick actions + copy that change with tenant business_type / enabled modules.
 * UI-only — no API changes.
 */
const INDUSTRY_PANELS = {
  hotel_restaurant: {
    title: 'Restaurant & hotel',
    blurb: 'Table-first billing, kitchen tickets, and dine-in flow.',
    accent: '#1F4E5F',
    actions: [
      {
        to: PATHS.ownerRestaurantBilling,
        label: 'Table Billing',
        icon: PointOfSaleOutlinedIcon,
        module: 'table_management',
      },
      { to: PATHS.ownerTables, label: 'Tables', icon: TableRestaurantOutlinedIcon, module: 'table_management' },
      { to: PATHS.ownerKitchen, label: 'Kitchen', icon: KitchenOutlinedIcon, module: 'kitchen' },
      { to: PATHS.ownerMenu, label: 'Menu', icon: RestaurantMenuOutlinedIcon, module: 'restaurant_menu' },
      { to: PATHS.ownerWastage, label: 'Wastage', icon: Inventory2OutlinedIcon, module: 'wastage' },
      { to: PATHS.billingStockMovements, label: 'Stock Movements', icon: Inventory2OutlinedIcon },
    ],
  },
  cafe_tea: {
    title: 'Cafe / tea shop',
    blurb: 'Fast Cafe POS with add-ons, combos, recipes, and wastage.',
    accent: '#2F6B80',
    actions: [
      { to: PATHS.ownerCafe, label: 'Cafe POS', icon: PointOfSaleOutlinedIcon, module: 'addons_combos' },
      { to: PATHS.ownerAddons, label: 'Add-ons', icon: RestaurantMenuOutlinedIcon, module: 'addons_combos' },
      { to: PATHS.ownerCombos, label: 'Combos', icon: LocalMallOutlinedIcon, module: 'addons_combos' },
      { to: PATHS.ownerRecipes, label: 'Recipes', icon: MenuBookOutlinedIcon, module: 'recipe' },
      { to: PATHS.ownerWastage, label: 'Wastage', icon: Inventory2OutlinedIcon, module: 'wastage' },
    ],
  },
  grocery_kirana: {
    title: 'Grocery / kirana',
    blurb: 'Barcode POS, batches, and customer credit.',
    accent: '#2E7D4F',
    actions: [
      { to: PATHS.ownerGrocery, label: 'Grocery POS', icon: LocalMallOutlinedIcon, module: 'barcode_pos' },
      { to: PATHS.ownerBatches, label: 'Batches', icon: Inventory2OutlinedIcon, module: 'batch_expiry' },
      { to: PATHS.ownerCredit, label: 'Credit', icon: ReceiptLongOutlinedIcon, module: 'customer_credit' },
    ],
  },
  clothing: {
    title: 'Clothing',
    blurb: 'Size/color variants, POS, and returns.',
    accent: '#6B4F7A',
    actions: [
      { to: PATHS.ownerClothing, label: 'Clothing POS', icon: LocalMallOutlinedIcon, module: 'variants' },
      { to: PATHS.ownerVariants, label: 'Variants', icon: Inventory2OutlinedIcon, module: 'variants' },
      { to: PATHS.ownerReturns, label: 'Returns', icon: ReceiptLongOutlinedIcon, module: 'returns_exchange' },
    ],
  },
  mobile: {
    title: 'Mobile shop',
    blurb: 'IMEI serials, repairs, and warranty.',
    accent: '#1B4F72',
    actions: [
      { to: PATHS.ownerSerials, label: 'Serials / IMEI', icon: PhoneIphoneOutlinedIcon, module: 'serial_imei' },
      { to: PATHS.ownerRepairs, label: 'Repairs', icon: BuildOutlinedIcon, module: 'repair_service' },
      { to: PATHS.ownerReturns, label: 'Returns', icon: ReceiptLongOutlinedIcon, module: 'returns_exchange' },
    ],
  },
  electronics: {
    title: 'Electronics',
    blurb: 'Serial tracking, repairs, and installation jobs.',
    accent: '#154360',
    actions: [
      { to: PATHS.ownerSerials, label: 'Serials', icon: PhoneIphoneOutlinedIcon, module: 'serial_imei' },
      { to: PATHS.ownerRepairs, label: 'Repairs', icon: BuildOutlinedIcon, module: 'repair_service' },
      { to: PATHS.ownerInstallations, label: 'Installations', icon: HandymanOutlinedIcon, module: 'installation' },
    ],
  },
  hardware: {
    title: 'Hardware',
    blurb: 'Length/weight UOM POS, quotations, and challans.',
    accent: '#7D6608',
    actions: [
      { to: PATHS.ownerHardware, label: 'Hardware POS', icon: HandymanOutlinedIcon, module: 'uom_measurement' },
      { to: PATHS.ownerQuotations, label: 'Quotations', icon: ReceiptLongOutlinedIcon, module: 'quotation' },
      { to: PATHS.ownerChallans, label: 'Challans', icon: ReceiptLongOutlinedIcon, module: 'delivery_challan' },
    ],
  },
  building_material: {
    title: 'Building material',
    blurb: 'Trade credit, warehouses, and material POS.',
    accent: '#6E2C00',
    actions: [
      { to: PATHS.ownerHardware, label: 'Material POS', icon: HandymanOutlinedIcon, module: 'uom_measurement' },
      { to: PATHS.ownerWarehouses, label: 'Warehouses', icon: WarehouseOutlinedIcon, module: 'warehouse' },
      { to: PATHS.ownerCredit, label: 'Trade credit', icon: ReceiptLongOutlinedIcon, module: 'customer_credit' },
    ],
  },
  bakery_sweet: {
    title: 'Bakery / sweets',
    blurb: 'Production runs, cake orders, and batch expiry.',
    accent: '#A04000',
    actions: [
      { to: PATHS.ownerProduction, label: 'Production', icon: BakeryDiningOutlinedIcon, module: 'production' },
      { to: PATHS.ownerCakeOrders, label: 'Cake orders', icon: BakeryDiningOutlinedIcon, module: 'custom_orders' },
      { to: PATHS.ownerBatches, label: 'Batches', icon: Inventory2OutlinedIcon, module: 'batch_expiry' },
    ],
  },
  stationery: {
    title: 'Stationery',
    blurb: 'Pack/UOM POS for stationery counters.',
    accent: '#1A5276',
    actions: [
      { to: PATHS.ownerStationery, label: 'Stationery POS', icon: PointOfSaleOutlinedIcon, module: 'barcode_pos' },
      { to: PATHS.ownerItems, label: 'Items', icon: Inventory2OutlinedIcon, module: 'core_catalog' },
      { to: PATHS.ownerCredit, label: 'Credit', icon: ReceiptLongOutlinedIcon, module: 'customer_credit' },
    ],
  },
  book_store: {
    title: 'Book store',
    blurb: 'ISBN catalog and search-first POS.',
    accent: '#4A235A',
    actions: [
      { to: PATHS.ownerStationery, label: 'Books POS', icon: MenuBookOutlinedIcon, module: 'barcode_pos' },
      { to: PATHS.ownerItems, label: 'Catalog', icon: Inventory2OutlinedIcon, module: 'book_metadata' },
      { to: PATHS.ownerCustomers, label: 'Customers', icon: StorefrontOutlinedIcon },
    ],
  },
  furniture: {
    title: 'Furniture',
    blurb: 'Custom orders, delivery board, and quotations.',
    accent: '#5D4E37',
    actions: [
      { to: PATHS.ownerFurnitureOrders, label: 'Orders', icon: Inventory2OutlinedIcon, module: 'custom_orders' },
      { to: PATHS.ownerDeliveries, label: 'Deliveries', icon: WarehouseOutlinedIcon, module: 'delivery_tracking' },
      { to: PATHS.ownerQuotations, label: 'Quotations', icon: ReceiptLongOutlinedIcon, module: 'quotation' },
    ],
  },
  wholesale: {
    title: 'Wholesale',
    blurb: 'Price lists, sales/purchase orders, and warehouses.',
    accent: '#1F4E5F',
    actions: [
      { to: PATHS.ownerPriceLists, label: 'Price lists', icon: ReceiptLongOutlinedIcon, module: 'price_lists' },
      { to: PATHS.ownerSalesOrders, label: 'Sales orders', icon: LocalMallOutlinedIcon, module: 'sales_orders' },
      { to: PATHS.ownerWarehouses, label: 'Warehouses', icon: WarehouseOutlinedIcon, module: 'warehouse' },
    ],
  },
  travel_agency: {
    title: 'Travel agency',
    blurb: 'Tour packages, bookings, and agent commissions.',
    accent: '#0E6655',
    actions: [
      { to: PATHS.ownerTourPackages, label: 'Packages', icon: TravelExploreOutlinedIcon, module: 'tour_packages' },
      { to: PATHS.ownerTravelBookings, label: 'Bookings', icon: ReceiptLongOutlinedIcon, module: 'travel_bookings' },
      { to: PATHS.ownerTravelAgents, label: 'Agents', icon: StorefrontOutlinedIcon, module: 'travel_commission' },
    ],
  },
};

const DEFAULT_PANEL = {
  title: 'Quick actions',
  blurb: 'Core tools for your business workspace.',
  accent: '#1F4E5F',
  actions: [
    { to: PATHS.billingNew, label: 'New bill', icon: PointOfSaleOutlinedIcon },
    { to: PATHS.ownerItems, label: 'Items', icon: Inventory2OutlinedIcon },
    { to: PATHS.ownerReports, label: 'Reports', icon: ReceiptLongOutlinedIcon },
  ],
};

const OWNER_TO_BILLING = {
  [PATHS.ownerMenu]: PATHS.billingMenu,
  [PATHS.ownerRecipes]: PATHS.billingRecipes,
  [PATHS.ownerWastage]: PATHS.billingWastage,
  [PATHS.ownerTables]: PATHS.billingTables,
  [PATHS.ownerRestaurantBilling]: PATHS.billingRestaurantBilling,
  [PATHS.ownerOrders]: PATHS.billingOrders,
  [PATHS.ownerKitchen]: PATHS.billingKitchen,
  [PATHS.ownerCafe]: PATHS.billingCafe,
  [PATHS.ownerAddons]: PATHS.billingAddons,
  [PATHS.ownerCombos]: PATHS.billingCombos,
  [PATHS.ownerGrocery]: PATHS.billingGrocery,
  [PATHS.ownerStationery]: PATHS.billingStationery,
  [PATHS.ownerHardware]: PATHS.billingHardware,
  [PATHS.ownerClothing]: PATHS.billingClothing,
  [PATHS.ownerReturns]: PATHS.billingReturns,
  [PATHS.ownerCredit]: PATHS.billingCredit,
  [PATHS.ownerItems]: PATHS.billingItems,
  [PATHS.ownerCustomers]: PATHS.billingCustomers,
  [PATHS.ownerPurchases]: PATHS.billingPurchases,
  [PATHS.ownerReports]: PATHS.billingReports,
  [PATHS.ownerStockMovements]: PATHS.billingStockMovements,
  [PATHS.billingNew]: PATHS.billingNew,
  [PATHS.billingStockMovements]: PATHS.billingStockMovements,
};

export default function IndustryDashboardPanel({ compact = false, workspace = 'owner' }) {
  const { user } = useAuth();
  const { isModuleEnabled } = useModules();
  const businessType = user?.tenant?.business_type || '';
  const panel = INDUSTRY_PANELS[businessType] || DEFAULT_PANEL;

  const actions = (panel.actions || [])
    .map((action) => {
      if (workspace !== 'billing') return action;
      const billingTo = OWNER_TO_BILLING[action.to];
      if (!billingTo) return null;
      return { ...action, to: billingTo };
    })
    .filter(Boolean)
    .filter((action) => {
      if (!action.module) return true;
      return isModuleEnabled(action.module);
    });

  if (!actions.length) return null;

  return (
    <Section title={panel.title}>
      <Box
        sx={{
          mb: compact ? 1.5 : 2,
          pl: 1.5,
          borderLeft: '3px solid',
          borderColor: panel.accent,
        }}
      >
        <Typography variant="body2" color="text.secondary" sx={{ lineHeight: 1.5 }}>
          {panel.blurb}
        </Typography>
      </Box>
      <Stack direction="row" spacing={1.25} flexWrap="wrap" useFlexGap>
        {actions.map((action) => {
          const Icon = action.icon;
          return (
            <Button
              key={`${action.to}-${action.label}`}
              component={RouterLink}
              to={action.to}
              variant="outlined"
              startIcon={Icon ? <Icon /> : null}
              sx={{
                borderColor: 'divider',
                '&:hover': { borderColor: panel.accent, color: panel.accent },
              }}
            >
              {action.label}
            </Button>
          );
        })}
      </Stack>
    </Section>
  );
}
