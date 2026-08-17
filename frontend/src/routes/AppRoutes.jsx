import { Navigate, Route, Routes } from 'react-router-dom';
import { Suspense, lazy } from 'react';
import { Box, CircularProgress } from '@mui/material';
import AuthLayout from '../layouts/AuthLayout';
import BillingLayout from '../layouts/BillingLayout';
import OwnerLayout from '../layouts/OwnerLayout';
import LoginPage from '../pages/auth/LoginPage';
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
const ItemActivityPage = lazy(() => import('../pages/owner/ItemActivityPage'));
const ItemsPage = lazy(() => import('../pages/owner/ItemsPage'));
const StockMovementsPage = lazy(() => import('../pages/owner/StockMovementsPage'));
const OwnerBillsPage = lazy(() => import('../pages/owner/OwnerBillsPage'));
const OwnerDashboardPage = lazy(() => import('../pages/owner/OwnerDashboardPage'));
const SettingsPage = lazy(() => import('../pages/owner/SettingsPage'));
const UsersPage = lazy(() => import('../pages/owner/UsersPage'));
const ReportsPage = lazy(() => import('../pages/reports/ReportsPage'));

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
        <Route path="/" element={<HomePage />} />
        <Route path="/privacy" element={<PrivacyPolicyPage />} />
        <Route path="/terms" element={<TermsOfServicePage />} />

        <Route element={<AuthLayout />}>
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterBusinessPage />} />
          <Route path="/forgot-password" element={<ForgotPasswordPage />} />
          <Route path="/reset-password" element={<ResetPasswordPage />} />
          <Route path="/verify-email" element={<VerifyEmailPage />} />
        </Route>

        <Route element={<ProtectedRoute roles={['OWNER']} />}>
          <Route path="/owner" element={<OwnerLayout />}>
            <Route index element={<Navigate to="dashboard" replace />} />
            <Route path="dashboard" element={<OwnerDashboardPage />} />
            <Route path="categories" element={<CategoriesPage />} />
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

        <Route element={<ProtectedRoute roles={['BILLING_USER', 'OWNER']} />}>
          <Route path="/billing" element={<BillingLayout />}>
            <Route index element={<BillingHomePage />} />
            <Route path="new" element={<NewBillPage />} />
            <Route path="bills" element={<BillingBillsPage />} />
            <Route path="items" element={<ItemsPage />} />
            <Route path="categories" element={<BillingCategoriesPage />} />
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
        </Route>

        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </Suspense>
  );
}
