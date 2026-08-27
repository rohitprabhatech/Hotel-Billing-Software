import { Box, CircularProgress } from '@mui/material';
import { Navigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { useModuleGate, useModules } from '../context/ModulesContext';
import { PATHS } from './paths';

/**
 * Route-level business-module gate. Deep links to unsupported modules redirect home.
 * Backend @module_required remains authoritative for APIs.
 */
export default function RequireModule({ module, children, fallbackTo }) {
  const { loading } = useModules();
  const enabled = useModuleGate(module);
  const { user } = useAuth();

  if (loading) {
    return (
      <Box sx={{ py: 8, display: 'grid', placeItems: 'center' }}>
        <CircularProgress size={28} />
      </Box>
    );
  }

  if (!enabled) {
    const role = user?.role;
    const home =
      fallbackTo ||
      (role === 'OWNER' || role === 'MANAGER' ? PATHS.ownerDashboard : PATHS.billingHome);
    return <Navigate to={home} replace />;
  }

  return children;
}
