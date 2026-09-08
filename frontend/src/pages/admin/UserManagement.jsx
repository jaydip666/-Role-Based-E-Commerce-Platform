import { useEffect, useMemo, useState } from "react";

import ConfirmDialog from "../../components/ConfirmDialog";
import EmptyState from "../../components/EmptyState";
import ErrorMessage from "../../components/ErrorMessage";
import Loader from "../../components/Loader";
import Modal from "../../components/Modal";
import { useAuth } from "../../context/AuthContext";
import { useToast } from "../../context/ToastContext";
import * as adminService from "../../services/adminService";
import { formatDate } from "../../utils/format";
import { ROLES } from "../../utils/roles";

// All roles, used for the filter dropdown and role badges — includes ADMIN
// so existing admin accounts stay visible/searchable.
const ROLE_OPTIONS = [ROLES.USER, ROLES.SALES_PERSON, ROLES.ADMIN];

// Roles assignable from the role-change control. ADMIN is deliberately
// excluded — promoting someone to Admin is not available from this UI.
const ASSIGNABLE_ROLE_OPTIONS = [ROLES.USER, ROLES.SALES_PERSON];

const ROLE_LABELS = {
  [ROLES.USER]: "User",
  [ROLES.SALES_PERSON]: "Sales Person",
  [ROLES.ADMIN]: "Admin",
};

const ROLE_BADGE_STYLES = {
  [ROLES.USER]: "bg-gray-100 text-gray-700",
  [ROLES.SALES_PERSON]: "bg-blue-100 text-blue-700",
  [ROLES.ADMIN]: "bg-indigo-100 text-indigo-700",
};

function RoleBadge({ role }) {
  return (
    <span className={`inline-block rounded-full px-2.5 py-0.5 text-xs font-medium ${ROLE_BADGE_STYLES[role] || "bg-gray-100 text-gray-700"}`}>
      {ROLE_LABELS[role] || role}
    </span>
  );
}

function EditIcon() {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="h-4 w-4">
      <path d="M12 20h9" />
      <path d="M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4Z" />
    </svg>
  );
}

function DeleteIcon() {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="h-4 w-4">
      <path d="M3 6h18" />
      <path d="M8 6V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2" />
      <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6" />
      <path d="M10 11v6M14 11v6" />
    </svg>
  );
}

export default function UserManagement() {
  const { user: currentUser } = useAuth();
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [updatingId, setUpdatingId] = useState(null);
  const toast = useToast();

  const [search, setSearch] = useState("");
  const [roleFilter, setRoleFilter] = useState("");

  const [editingUser, setEditingUser] = useState(null);
  const [editForm, setEditForm] = useState({ name: "", phone: "", address: "" });
  const [editError, setEditError] = useState("");
  const [savingEdit, setSavingEdit] = useState(false);

  const [deletingUser, setDeletingUser] = useState(null);
  const [deleteError, setDeleteError] = useState("");
  const [deleting, setDeleting] = useState(false);

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

  const filteredUsers = useMemo(() => {
    const query = search.trim().toLowerCase();
    return users.filter((u) => {
      const matchesQuery =
        !query || u.name?.toLowerCase().includes(query) || u.email?.toLowerCase().includes(query);
      const matchesRole = !roleFilter || u.role === roleFilter;
      return matchesQuery && matchesRole;
    });
  }, [users, search, roleFilter]);

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

  const openEdit = (u) => {
    setEditingUser(u);
    setEditForm({ name: u.name || "", phone: u.phone || "", address: u.address || "" });
    setEditError("");
  };

  const closeEdit = () => {
    if (savingEdit) return;
    setEditingUser(null);
  };

  const handleEditSubmit = async (e) => {
    e.preventDefault();
    setEditError("");
    setSavingEdit(true);
    try {
      const updated = await adminService.updateUser(editingUser.id, editForm);
      setUsers((prev) => prev.map((u) => (u.id === updated.id ? updated : u)));
      toast.success(`Updated ${updated.name}'s profile`);
      setEditingUser(null);
    } catch (err) {
      setEditError(err.fieldErrors?.join(", ") || err.friendlyMessage || "Could not update user");
    } finally {
      setSavingEdit(false);
    }
  };

  const openDelete = (u) => {
    setDeletingUser(u);
    setDeleteError("");
  };

  const closeDelete = () => {
    if (deleting) return;
    setDeletingUser(null);
  };

  const handleDeleteConfirm = async () => {
    setDeleteError("");
    setDeleting(true);
    try {
      await adminService.deleteUser(deletingUser.id);
      setUsers((prev) => prev.filter((u) => u.id !== deletingUser.id));
      toast.success(`Deleted ${deletingUser.name}`);
      setDeletingUser(null);
    } catch (err) {
      setDeleteError(err.friendlyMessage || "Could not delete user");
    } finally {
      setDeleting(false);
    }
  };

  return (
    <div>
      <div className="mb-6">
        <h1 className="text-lg font-semibold text-gray-900">User Management</h1>
        <p className="text-sm text-gray-500">Manage registered users and their roles.</p>
      </div>

      {loading && <Loader label="Loading users..." />}
      {!loading && error && <ErrorMessage message={error} onRetry={load} />}

      {!loading && !error && (
        <>
          <div className="mb-4 flex flex-col gap-3 sm:flex-row sm:items-center">
            <div className="flex-1">
              <label htmlFor="user-search" className="sr-only">Search users</label>
              <input
                id="user-search"
                type="search"
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                placeholder="Search users by name or email..."
                className="form-input"
              />
            </div>
            <div className="sm:w-56">
              <label htmlFor="role-filter" className="sr-only">Filter by role</label>
              <select
                id="role-filter"
                value={roleFilter}
                onChange={(e) => setRoleFilter(e.target.value)}
                className="form-input"
              >
                <option value="">All Roles</option>
                {ROLE_OPTIONS.map((r) => (
                  <option key={r} value={r}>{ROLE_LABELS[r]}</option>
                ))}
              </select>
            </div>
          </div>

          {filteredUsers.length === 0 ? (
            <EmptyState title="No users found" message="Try a different search term or role filter." />
          ) : (
            <>
              {/* Desktop table */}
              <div className="hidden overflow-x-auto rounded-lg border border-gray-200 bg-white sm:block">
                <table className="w-full min-w-[720px] border-collapse text-sm">
                  <thead>
                    <tr className="border-b border-gray-200 bg-gray-50 text-left text-gray-500">
                      <th className="px-4 py-3 font-medium">Name</th>
                      <th className="px-4 py-3 font-medium">Email</th>
                      <th className="px-4 py-3 font-medium">Role</th>
                      <th className="px-4 py-3 font-medium">Joined</th>
                      <th className="px-4 py-3 font-medium">Actions</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-100">
                    {filteredUsers.map((u) => {
                      const isSelf = u.id === currentUser?.id;
                      return (
                        <tr key={u.id}>
                          <td className="px-4 py-3 font-medium text-gray-900">{u.name}</td>
                          <td className="px-4 py-3 text-gray-600">{u.email}</td>
                          <td className="px-4 py-3">
                            <div className="flex items-center gap-2">
                              <RoleBadge role={u.role} />
                              {u.role !== ROLES.ADMIN && (
                                <select
                                  className="form-input w-40"
                                  value={u.role}
                                  disabled={updatingId === u.id || isSelf}
                                  aria-label={`Change role for ${u.name}`}
                                  onChange={(e) => handleRoleChange(u.id, e.target.value)}
                                >
                                  {ASSIGNABLE_ROLE_OPTIONS.map((r) => (
                                    <option key={r} value={r}>{ROLE_LABELS[r]}</option>
                                  ))}
                                </select>
                              )}
                            </div>
                          </td>
                          <td className="px-4 py-3 text-gray-600">{formatDate(u.created_at)}</td>
                          <td className="px-4 py-3">
                            <div className="flex items-center gap-1">
                              <button
                                type="button"
                                onClick={() => openEdit(u)}
                                aria-label={`Edit ${u.name}`}
                                title="Edit user"
                                className="rounded-md p-2 text-gray-500 hover:bg-gray-100 hover:text-gray-700 focus:outline-none focus-visible:ring-2 focus-visible:ring-brand-500"
                              >
                                <EditIcon />
                              </button>
                              {!isSelf && (
                                <button
                                  type="button"
                                  onClick={() => openDelete(u)}
                                  aria-label={`Delete ${u.name}`}
                                  title="Delete user"
                                  className="rounded-md p-2 text-gray-500 hover:bg-red-50 hover:text-red-600 focus:outline-none focus-visible:ring-2 focus-visible:ring-red-500"
                                >
                                  <DeleteIcon />
                                </button>
                              )}
                            </div>
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>

              {/* Mobile cards */}
              <div className="space-y-3 sm:hidden">
                {filteredUsers.map((u) => {
                  const isSelf = u.id === currentUser?.id;
                  return (
                    <div key={u.id} className="card p-4">
                      <div className="flex items-start justify-between gap-2">
                        <div>
                          <p className="font-medium text-gray-900">{u.name}</p>
                          <p className="text-sm text-gray-500">{u.email}</p>
                        </div>
                        <RoleBadge role={u.role} />
                      </div>
                      <p className="mt-2 text-xs text-gray-500">Joined {formatDate(u.created_at)}</p>

                      {u.role !== ROLES.ADMIN && (
                        <div className="mt-3">
                          <label htmlFor={`role-${u.id}`} className="form-label">Role</label>
                          <select
                            id={`role-${u.id}`}
                            className="form-input"
                            value={u.role}
                            disabled={updatingId === u.id || isSelf}
                            onChange={(e) => handleRoleChange(u.id, e.target.value)}
                          >
                            {ASSIGNABLE_ROLE_OPTIONS.map((r) => (
                              <option key={r} value={r}>{ROLE_LABELS[r]}</option>
                            ))}
                          </select>
                        </div>
                      )}

                      <div className="mt-3 flex gap-2">
                        <button type="button" className="btn-secondary flex-1" onClick={() => openEdit(u)}>
                          Edit
                        </button>
                        {!isSelf && (
                          <button type="button" className="btn-danger flex-1" onClick={() => openDelete(u)}>
                            Delete
                          </button>
                        )}
                      </div>
                    </div>
                  );
                })}
              </div>
            </>
          )}
        </>
      )}

      <Modal
        open={Boolean(editingUser)}
        title="Edit User"
        onClose={closeEdit}
        footer={
          <>
            <button type="button" className="btn-secondary" onClick={closeEdit} disabled={savingEdit}>
              Cancel
            </button>
            <button type="submit" form="edit-user-form" className="btn-primary" disabled={savingEdit}>
              {savingEdit ? "Saving..." : "Save Changes"}
            </button>
          </>
        }
      >
        <form id="edit-user-form" onSubmit={handleEditSubmit} className="space-y-4">
          {editError && <p className="rounded-md bg-red-50 px-3 py-2 text-sm text-red-700">{editError}</p>}
          <div>
            <label htmlFor="edit-name" className="form-label">Name</label>
            <input
              id="edit-name"
              className="form-input"
              value={editForm.name}
              onChange={(e) => setEditForm((f) => ({ ...f, name: e.target.value }))}
              required
              minLength={2}
            />
          </div>
          <div>
            <label htmlFor="edit-phone" className="form-label">Phone</label>
            <input
              id="edit-phone"
              className="form-input"
              value={editForm.phone}
              onChange={(e) => setEditForm((f) => ({ ...f, phone: e.target.value }))}
              placeholder="e.g. 9876543210"
            />
          </div>
          <div>
            <label htmlFor="edit-address" className="form-label">Address</label>
            <textarea
              id="edit-address"
              className="form-input"
              rows={3}
              value={editForm.address}
              onChange={(e) => setEditForm((f) => ({ ...f, address: e.target.value }))}
              placeholder="Street, city, state, PIN"
            />
          </div>
        </form>
      </Modal>

      <ConfirmDialog
        open={Boolean(deletingUser)}
        title="Delete user"
        message={
          <>
            Are you sure you want to delete {deletingUser?.name || "this user"}? This action cannot be undone.
            {deleteError && (
              <span className="mt-2 block rounded-md bg-red-50 px-3 py-2 text-red-700">{deleteError}</span>
            )}
          </>
        }
        confirmLabel={deleting ? "Deleting..." : "Delete User"}
        danger
        onConfirm={handleDeleteConfirm}
        onCancel={closeDelete}
      />
    </div>
  );
}
