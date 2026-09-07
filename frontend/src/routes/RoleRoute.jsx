import { Navigate, Outlet } from "react-router-dom";

import Loader from "../components/Loader";
import { useAuth } from "../context/AuthContext";
import { dashboardPathForRole } from "../utils/roles";

/**
 * Restricts a subtree to specific roles for navigation/UX purposes only.
 * The backend independently re-checks every request — this never
 * substitutes for that enforcement.
 */
export default function RoleRoute({ allowedRoles }) {
  const { isAuthenticated, loading, role } = useAuth();

  if (loading) return <Loader label="Checking your session..." />;

  if (!isAuthenticated) return <Navigate to="/login" replace />;

  if (!allowedRoles.includes(role)) {
    return <Navigate to={dashboardPathForRole(role)} replace />;
  }

  return <Outlet />;
}
