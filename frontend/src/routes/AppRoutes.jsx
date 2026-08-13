import { Navigate, Route, Routes } from 'react-router-dom';
import AuthLayout from '../layouts/AuthLayout';
import BillingLayout from '../layouts/BillingLayout';
import OwnerLayout from '../layouts/OwnerLayout';
import LoginPage from '../pages/auth/LoginPage';
import BillingBillsPage from '../pages/billing/BillingBillsPage';
import BillingHomePage from '../pages/billing/BillingHomePage';
import NewBillPage from '../pages/billing/NewBillPage';
import PlaceholderPage from '../pages/common/PlaceholderPage';
import HomePage from '../pages/HomePage';
import OwnerDashboardPage from '../pages/owner/OwnerDashboardPage';

export default function AppRoutes() {
  return (
    <Routes>
      <Route path="/" element={<HomePage />} />

      <Route element={<AuthLayout />}>
        <Route path="/login" element={<LoginPage />} />
      </Route>

      <Route path="/owner" element={<OwnerLayout />}>
        <Route index element={<Navigate to="dashboard" replace />} />
        <Route path="dashboard" element={<OwnerDashboardPage />} />
        <Route
          path="categories"
          element={
            <PlaceholderPage
              title="Categories"
              message="Category management arrives in Sprint 4."
            />
          }
        />
        <Route
          path="items"
          element={
            <PlaceholderPage
              title="Items"
              message="Item and price management arrives in Sprint 4."
            />
          }
        />
        <Route
          path="bills"
          element={
            <PlaceholderPage
              title="Bills"
              message="Owner bill history arrives in Sprint 6."
            />
          }
        />
        <Route
          path="reports"
          element={
            <PlaceholderPage
              title="Reports"
              message="Sales reports and exports arrive in Sprint 7."
            />
          }
        />
        <Route
          path="audit"
          element={
            <PlaceholderPage
              title="Activity & Audit"
              message="Audit and fraud monitoring arrives in Sprint 8."
            />
          }
        />
        <Route
          path="users"
          element={
            <PlaceholderPage
              title="Users"
              message="Billing user management arrives in Sprint 3."
            />
          }
        />
        <Route
          path="settings"
          element={
            <PlaceholderPage
              title="Hotel Settings"
              message="Tenant profile settings arrive with auth/tenant work in Sprint 3."
            />
          }
        />
      </Route>

      <Route path="/billing" element={<BillingLayout />}>
        <Route index element={<BillingHomePage />} />
        <Route path="new" element={<NewBillPage />} />
        <Route path="bills" element={<BillingBillsPage />} />
      </Route>

      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}