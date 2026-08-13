import { Navigate, Outlet, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { homePathForRole, isValidRole } from '../utils/authRouting';

export default function ProtectedRoute({ roles }) {
  const { isAuthenticated, role } = useAuth();
  const location = useLocation();

  if (!isAuthenticated || !isValidRole(role)) {
    return <Navigate to="/login" replace state={{ from: location }} />;
  }

  if (roles?.length && !roles.includes(role)) {
    const fallback = homePathForRole(role);
    // Prevent Navigate-to-self blank-page loops
    if (
      fallback === location.pathname ||
      (fallback !== '/login' && location.pathname.startsWith(`${fallback}/`))
    ) {
      return <Navigate to="/login" replace />;
    }
    return <Navigate to={fallback} replace />;
  }

  return <Outlet />;
}
