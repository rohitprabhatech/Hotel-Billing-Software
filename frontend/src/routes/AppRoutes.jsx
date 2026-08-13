import { Navigate, Route, Routes } from 'react-router-dom';
import AuthLayout from '../layouts/AuthLayout';
import BillingLayout from '../layouts/BillingLayout';
import OwnerLayout from '../layouts/OwnerLayout';
import ChangePasswordPage from '../pages/account/ChangePasswordPage';
import ProfilePage from '../pages/account/ProfilePage';
import ForgotPasswordPage from '../pages/auth/ForgotPasswordPage';
import LoginPage from '../pages/auth/LoginPage';
import RegisterHotelPage from '../pages/auth/RegisterHotelPage';
import ResetPasswordPage from '../pages/auth/ResetPasswordPage';
import VerifyEmailPage from '../pages/auth/VerifyEmailPage';
import BillingBillsPage from '../pages/billing/BillingBillsPage';
import BillingCategoriesPage from '../pages/billing/BillingCategoriesPage';
import BillingHomePage from '../pages/billing/BillingHomePage';
import NewBillPage from '../pages/billing/NewBillPage';
import HomePage from '../pages/HomePage';
import PrintBillPage from '../pages/print/PrintBillPage';
import AuditPage from '../pages/owner/AuditPage';
import CategoriesPage from '../pages/owner/CategoriesPage';
import ItemActivityPage from '../pages/owner/ItemActivityPage';
import ItemsPage from '../pages/owner/ItemsPage';
import OwnerBillsPage from '../pages/owner/OwnerBillsPage';
import OwnerDashboardPage from '../pages/owner/OwnerDashboardPage';
import SettingsPage from '../pages/owner/SettingsPage';
import UsersPage from '../pages/owner/UsersPage';
import ReportsPage from '../pages/reports/ReportsPage';
import ProtectedRoute from './ProtectedRoute';

export default function AppRoutes() {
  return (
    <Routes>
      <Route path="/" element={<HomePage />} />

      <Route element={<AuthLayout />}>
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterHotelPage />} />
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
          <Route path="bills" element={<OwnerBillsPage />} />
          <Route path="reports" element={<ReportsPage />} />
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
        <Route path="/print/bills/:billId" element={<PrintBillPage />} />
      </Route>

      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
