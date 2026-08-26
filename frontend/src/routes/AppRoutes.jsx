import { Navigate, Route, Routes } from 'react-router-dom';
import { Suspense, lazy } from 'react';
import { Box, CircularProgress } from '@mui/material';
import AuthLayout from '../layouts/AuthLayout';
import BillingLayout from '../layouts/BillingLayout';
import MasterLayout from '../layouts/MasterLayout';
import OwnerLayout from '../layouts/OwnerLayout';
import LoginPage from '../pages/auth/LoginPage';
import MasterLoginPage from '../pages/master/MasterLoginPage';
import RouteErrorBoundary from '../components/RouteErrorBoundary';
import ProtectedRoute from './ProtectedRoute';

const HomePage = lazy(() => import('../pages/HomePage'));
const PrivacyPolicyPage = lazy(() => import('../pages/legal/PrivacyPolicyPage'));
const TermsOfServicePage = lazy(() => import('../pages/legal/TermsOfServicePage'));
const RegisterBusinessPage = lazy(() => import('../pages/auth/RegisterBusinessPage'));
const ForgotPasswordPage = lazy(() => import('../pages/auth/ForgotPasswordPage'));
const ResetPasswordPage = lazy(() => import('../pages/auth/ResetPasswordPage'));
const VerifyEmailPage = lazy(() => import('../pages/auth/VerifyEmailPage'));
const ChangePasswordPage = lazy(() => import('../pages/account/ChangePasswordPage'));
const ProfilePage = lazy(() => import('../pages/account/ProfilePage'));
const BillingBillsPage = lazy(() => import('../pages/billing/BillingBillsPage'));
const BillingCategoriesPage = lazy(() => import('../pages/billing/BillingCategoriesPage'));
const BillingHomePage = lazy(() => import('../pages/billing/BillingHomePage'));
const NewBillPage = lazy(() => import('../pages/billing/NewBillPage'));
const PrintBillPage = lazy(() => import('../pages/print/PrintBillPage'));
const AuditPage = lazy(() => import('../pages/owner/AuditPage'));
const AiAssistantPage = lazy(() => import('../pages/owner/AiAssistantPage'));
const CategoriesPage = lazy(() => import('../pages/owner/CategoriesPage'));
const CustomersPage = lazy(() => import('../pages/owner/CustomersPage'));
const SuppliersPage = lazy(() => import('../pages/owner/SuppliersPage'));
const PurchasesPage = lazy(() => import('../pages/owner/PurchasesPage'));
const ExpensesPage = lazy(() => import('../pages/owner/ExpensesPage'));
const ItemActivityPage = lazy(() => import('../pages/owner/ItemActivityPage'));
const ItemsPage = lazy(() => import('../pages/owner/ItemsPage'));
const StockMovementsPage = lazy(() => import('../pages/owner/StockMovementsPage'));
const OwnerBillsPage = lazy(() => import('../pages/owner/OwnerBillsPage'));
const OwnerDashboardPage = lazy(() => import('../pages/owner/OwnerDashboardPage'));
const MasterDashboardPage = lazy(() => import('../pages/master/MasterDashboardPage'));
const MasterRegistrationRequestsPage = lazy(
  () => import('../pages/master/MasterRegistrationRequestsPage')
);
const MasterTrialsPage = lazy(() => import('../pages/master/MasterTrialsPage'));
const MasterTrialSettingsPage = lazy(() => import('../pages/master/MasterTrialSettingsPage'));
const MasterPlansPage = lazy(() => import('../pages/master/MasterPlansPage'));
const MasterBusinessesPage = lazy(() => import('../pages/master/MasterBusinessesPage'));
const MasterAuditPage = lazy(() => import('../pages/master/MasterAuditPage'));
const SettingsPage = lazy(() => import('../pages/owner/SettingsPage'));
const UsersPage = lazy(() => import('../pages/owner/UsersPage'));
const ReportsPage = lazy(() => import('../pages/reports/ReportsPage'));
const OutstandingReportPage = lazy(() => import('../pages/reports/OutstandingReportPage'));
const MenuPage = lazy(() => import('../pages/modules/MenuPage'));
const OrdersPage = lazy(() => import('../pages/modules/OrdersPage'));
const NewOrderPage = lazy(() => import('../pages/modules/NewOrderPage'));
const TablesPage = lazy(() => import('../pages/modules/TablesPage'));
const KitchenPage = lazy(() => import('../pages/modules/KitchenPage'));
const RecipesPage = lazy(() => import('../pages/owner/RecipesPage'));
const CafePosPage = lazy(() => import('../pages/modules/CafePosPage'));
const WastagePage = lazy(() => import('../pages/owner/WastagePage'));
const ProductionPage = lazy(() => import('../pages/owner/ProductionPage'));
const CakeOrdersPage = lazy(() => import('../pages/owner/CakeOrdersPage'));
const FurnitureOrdersPage = lazy(() => import('../pages/owner/FurnitureOrdersPage'));
const BatchesPage = lazy(() => import('../pages/owner/BatchesPage'));
const GroceryCreditPage = lazy(() => import('../pages/owner/GroceryCreditPage'));
const GroceryPosPage = lazy(() => import('../pages/modules/GroceryPosPage'));
const StationeryPosPage = lazy(() => import('../pages/modules/StationeryPosPage'));
const HardwarePosPage = lazy(() => import('../pages/modules/HardwarePosPage'));
const ClothingPosPage = lazy(() => import('../pages/modules/ClothingPosPage'));
const ReturnsPage = lazy(() => import('../pages/owner/ReturnsPage'));
const RepairsPage = lazy(() => import('../pages/owner/RepairsPage'));
const InstallationsPage = lazy(() => import('../pages/owner/InstallationsPage'));
const DeliveriesPage = lazy(() => import('../pages/owner/DeliveriesPage'));
const QuotationsPage = lazy(() => import('../pages/owner/QuotationsPage'));
const PriceListsPage = lazy(() => import('../pages/owner/PriceListsPage'));
const SalesOrdersPage = lazy(() => import('../pages/owner/SalesOrdersPage'));
const PurchaseOrdersPage = lazy(() => import('../pages/owner/PurchaseOrdersPage'));
const ChallansPage = lazy(() => import('../pages/owner/ChallansPage'));
const WarehousesPage = lazy(() => import('../pages/owner/WarehousesPage'));
const TourPackagesPage = lazy(() => import('../pages/owner/TourPackagesPage'));
const TravelBookingsPage = lazy(() => import('../pages/owner/TravelBookingsPage'));
const TravelAgentsPage = lazy(() => import('../pages/owner/TravelAgentsPage'));
const PrintKotPage = lazy(() => import('../pages/print/PrintKotPage'));

const VariantsPage = lazy(() => import('../pages/owner/VariantsPage'));
const SerialUnitsPage = lazy(() => import('../pages/owner/SerialUnitsPage'));

function RouteFallback() {
  return (
    <Box sx={{ py: 8, display: 'grid', placeItems: 'center' }}>
      <CircularProgress size={28} />
    </Box>
  );
}

export default function AppRoutes() {
  return (
    <Suspense fallback={<RouteFallback />}>
      <Routes>
        <Route
          path="/"
          element={
            <RouteErrorBoundary>
              <HomePage />
            </RouteErrorBoundary>
          }
        />
        <Route path="/privacy" element={<PrivacyPolicyPage />} />
        <Route path="/terms" element={<TermsOfServicePage />} />

        <Route element={<AuthLayout />}>
          <Route path="/login" element={<LoginPage />} />
          <Route path="/master/login" element={<MasterLoginPage />} />
          <Route path="/register" element={<RegisterBusinessPage />} />
          <Route path="/forgot-password" element={<ForgotPasswordPage />} />
          <Route path="/reset-password" element={<ResetPasswordPage />} />
          <Route path="/verify-email" element={<VerifyEmailPage />} />
        </Route>

        <Route element={<ProtectedRoute roles={['MASTER_ADMIN']} />}>
          <Route path="/master" element={<MasterLayout />}>
            <Route index element={<Navigate to="dashboard" replace />} />
            <Route path="dashboard" element={<MasterDashboardPage />} />
            <Route path="registration-requests" element={<MasterRegistrationRequestsPage />} />
            <Route path="trials" element={<MasterTrialsPage />} />
            <Route path="plans" element={<MasterPlansPage />} />
            <Route path="businesses" element={<MasterBusinessesPage />} />
            <Route path="audit" element={<MasterAuditPage />} />
            <Route path="settings/trial" element={<MasterTrialSettingsPage />} />
            <Route path="change-password" element={<ChangePasswordPage />} />
          </Route>
        </Route>

        <Route element={<ProtectedRoute roles={['OWNER']} />}>
          <Route path="/owner" element={<OwnerLayout />}>
            <Route index element={<Navigate to="dashboard" replace />} />
            <Route path="dashboard" element={<OwnerDashboardPage />} />
            <Route path="categories" element={<CategoriesPage />} />
            <Route path="customers" element={<CustomersPage />} />
            <Route path="suppliers" element={<SuppliersPage />} />
            <Route path="purchases" element={<PurchasesPage />} />
            <Route path="expenses" element={<ExpensesPage />} />
            <Route path="tables" element={<TablesPage />} />
            <Route path="menu" element={<MenuPage />} />
            <Route path="orders" element={<OrdersPage />} />
            <Route path="orders/new" element={<NewOrderPage />} />
            <Route path="kitchen" element={<KitchenPage />} />
            <Route path="cafe" element={<CafePosPage />} />
            <Route path="grocery" element={<GroceryPosPage />} />
            <Route path="stationery" element={<StationeryPosPage />} />
            <Route path="hardware" element={<HardwarePosPage />} />
            <Route path="clothing" element={<ClothingPosPage />} />
            <Route path="returns" element={<ReturnsPage />} />
            <Route path="credit" element={<GroceryCreditPage />} />
            <Route path="outstanding" element={<OutstandingReportPage />} />
            <Route path="recipes" element={<RecipesPage />} />
            <Route path="production" element={<ProductionPage />} />
            <Route path="cake-orders" element={<CakeOrdersPage />} />
            <Route path="furniture-orders" element={<FurnitureOrdersPage />} />
            <Route path="wastage" element={<WastagePage />} />
            <Route path="batches" element={<BatchesPage />} />
            <Route path="variants" element={<VariantsPage />} />
            <Route path="serials" element={<SerialUnitsPage />} />
            <Route path="repairs" element={<RepairsPage />} />
            <Route path="installations" element={<InstallationsPage />} />
            <Route path="deliveries" element={<DeliveriesPage />} />
            <Route path="quotations" element={<QuotationsPage />} />
            <Route path="price-lists" element={<PriceListsPage />} />
            <Route path="sales-orders" element={<SalesOrdersPage />} />
            <Route path="purchase-orders" element={<PurchaseOrdersPage />} />
            <Route path="challans" element={<ChallansPage />} />
            <Route path="warehouses" element={<WarehousesPage />} />
            <Route path="tour-packages" element={<TourPackagesPage />} />
            <Route path="travel-bookings" element={<TravelBookingsPage />} />
            <Route path="travel-agents" element={<TravelAgentsPage />} />
            <Route path="items" element={<ItemsPage />} />
            <Route path="item-activity" element={<ItemActivityPage />} />
            <Route path="stock-movements" element={<StockMovementsPage />} />
            <Route path="bills" element={<OwnerBillsPage />} />
            <Route path="reports" element={<ReportsPage />} />
            <Route path="ai" element={<AiAssistantPage />} />
            <Route path="audit" element={<AuditPage />} />
            <Route path="users" element={<UsersPage />} />
            <Route path="settings" element={<SettingsPage />} />
            <Route path="profile" element={<ProfilePage />} />
            <Route path="change-password" element={<ChangePasswordPage />} />
          </Route>
        </Route>

        <Route element={<ProtectedRoute roles={['BILLING_USER', 'OWNER', 'MANAGER']} />}>
          <Route path="/billing" element={<BillingLayout />}>
            <Route index element={<BillingHomePage />} />
            <Route path="new" element={<NewBillPage />} />
            <Route path="bills" element={<BillingBillsPage />} />
            <Route path="items" element={<ItemsPage />} />
            <Route path="categories" element={<BillingCategoriesPage />} />
            <Route path="customers" element={<CustomersPage />} />
            <Route path="suppliers" element={<SuppliersPage />} />
            <Route path="purchases" element={<PurchasesPage />} />
            <Route path="expenses" element={<ExpensesPage />} />
            <Route path="tables" element={<TablesPage />} />
            <Route path="menu" element={<MenuPage />} />
            <Route path="orders" element={<OrdersPage />} />
            <Route path="orders/new" element={<NewOrderPage />} />
            <Route path="kitchen" element={<KitchenPage />} />
            <Route path="cafe" element={<CafePosPage />} />
            <Route path="grocery" element={<GroceryPosPage />} />
            <Route path="stationery" element={<StationeryPosPage />} />
            <Route path="hardware" element={<HardwarePosPage />} />
            <Route path="clothing" element={<ClothingPosPage />} />
            <Route path="returns" element={<ReturnsPage />} />
            <Route path="credit" element={<GroceryCreditPage />} />
            <Route path="reports" element={<ReportsPage />} />
            <Route path="stock-movements" element={<StockMovementsPage />} />
            <Route path="profile" element={<ProfilePage />} />
            <Route path="change-password" element={<ChangePasswordPage />} />
          </Route>
          <Route
            path="/print/bills/:billId"
            element={
              <RouteErrorBoundary>
                <PrintBillPage />
              </RouteErrorBoundary>
            }
          />
          <Route
            path="/print/kots/:kotId"
            element={
              <RouteErrorBoundary>
                <PrintKotPage />
              </RouteErrorBoundary>
            }
          />
        </Route>

        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </Suspense>
  );
}
