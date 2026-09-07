import { useEffect, useState } from "react";

import ErrorMessage from "../../components/ErrorMessage";
import Loader from "../../components/Loader";
import { useAuth } from "../../context/AuthContext";
import { useToast } from "../../context/ToastContext";
import * as adminService from "../../services/adminService";
import { formatDate } from "../../utils/format";
import { ROLES } from "../../utils/roles";

const ROLE_OPTIONS = [ROLES.USER, ROLES.SALES_PERSON, ROLES.ADMIN];

export default function UserManagement() {
  const { user: currentUser } = useAuth();
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [updatingId, setUpdatingId] = useState(null);
  const toast = useToast();

  const load = async () => {
    setLoading(true);
    setError("");
    try {
      const data = await adminService.listUsers();
      setUsers(data.users);
    } catch (err) {
      setError(err.friendlyMessage);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
  }, []);

  const handleRoleChange = async (userId, role) => {
    setUpdatingId(userId);
    try {
      const updated = await adminService.updateUserRole(userId, role);
      setUsers((prev) => prev.map((u) => (u.id === userId ? updated : u)));
      toast.success(`Updated role for ${updated.name}`);
    } catch (err) {
      toast.error(err.friendlyMessage || "Could not update role");
    } finally {
      setUpdatingId(null);
    }
  };

  return (
    <div>
      <h1 className="mb-4 text-lg font-semibold text-gray-900">User Management</h1>

      {loading && <Loader label="Loading users..." />}
      {!loading && error && <ErrorMessage message={error} onRetry={load} />}

      {!loading && !error && (
        <div className="overflow-x-auto">
          <table className="w-full min-w-[600px] border-collapse text-sm">
            <thead>
              <tr className="border-b border-gray-200 text-left text-gray-500">
                <th className="py-2">Name</th>
                <th className="py-2">Email</th>
                <th className="py-2">Role</th>
                <th className="py-2">Joined</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {users.map((u) => (
                <tr key={u.id}>
                  <td className="py-3 font-medium text-gray-900">{u.name}</td>
                  <td className="py-3 text-gray-600">{u.email}</td>
                  <td className="py-3">
                    <select
                      className="form-input w-40"
                      value={u.role}
                      disabled={updatingId === u.id || u.id === currentUser?.id}
                      onChange={(e) => handleRoleChange(u.id, e.target.value)}
                    >
                      {ROLE_OPTIONS.map((r) => (
                        <option key={r} value={r}>{r}</option>
                      ))}
                    </select>
                  </td>
                  <td className="py-3 text-gray-600">{formatDate(u.created_at)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
