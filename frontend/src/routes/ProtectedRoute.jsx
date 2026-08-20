import { Navigate, Outlet, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { PATHS } from './paths';
import { homePathForRole, isValidRole } from '../utils/authRouting';

function loginPathFor(pathname) {
  return pathname.startsWith('/master') ? PATHS.masterLogin : PATHS.login;
}

export default function ProtectedRoute({ roles }) {
  const { isAuthenticated, role, sessionReady } = useAuth();
  const location = useLocation();

  if (!sessionReady) {
    return null;
  }

  if (!isAuthenticated || !isValidRole(role)) {
    return <Navigate to={loginPathFor(location.pathname)} replace state={{ from: location }} />;
  }

  if (roles?.length && !roles.includes(role)) {
    const fallback = homePathForRole(role);
    // Prevent Navigate-to-self blank-page loops
    if (
      fallback === location.pathname ||
      (fallback !== PATHS.login && location.pathname.startsWith(`${fallback}/`))
    ) {
      return <Navigate to={loginPathFor(location.pathname)} replace />;
    }
    return <Navigate to={fallback} replace />;
  }

  return <Outlet />;
}
