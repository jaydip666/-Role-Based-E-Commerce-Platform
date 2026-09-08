import { useState } from "react";

import { useAuth } from "../../context/AuthContext";
import { useToast } from "../../context/ToastContext";
import { formatDate } from "../../utils/format";

export default function Profile() {
  const { user, updateProfile } = useAuth();
  const toast = useToast();

  const [editing, setEditing] = useState(false);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");
  const [form, setForm] = useState({
    name: user?.name || "",
    phone: user?.phone || "",
    address: user?.address || "",
  });

  const handleChange = (field) => (e) => setForm((f) => ({ ...f, [field]: e.target.value }));

  const startEditing = () => {
    setForm({ name: user?.name || "", phone: user?.phone || "", address: user?.address || "" });
    setError("");
    setEditing(true);
  };

  const cancelEditing = () => {
    setError("");
    setEditing(false);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setSaving(true);
    try {
      await updateProfile(form);
      toast.success("Profile updated successfully");
      setEditing(false);
    } catch (err) {
      setError(err.fieldErrors?.join(", ") || err.friendlyMessage || "Failed to update profile");
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="mx-auto max-w-lg px-4 py-8">
      <h1 className="mb-6 text-xl font-bold text-gray-900">Profile</h1>

      {!editing ? (
        <div className="card divide-y divide-gray-100">
          <Row label="Name" value={user?.name} />
          <Row label="Email" value={user?.email} />
          <Row label="Phone" value={user?.phone || "-"} />
          <Row label="Address" value={user?.address || "-"} />
          <Row label="Role" value={user?.role} />
          <Row label="Member since" value={formatDate(user?.created_at)} />
          <div className="p-4">
            <button type="button" className="btn-primary w-full" onClick={startEditing}>
              Edit Profile
            </button>
          </div>
        </div>
      ) : (
        <form onSubmit={handleSubmit} className="card space-y-4 p-6">
          {error && <p className="rounded-md bg-red-50 px-3 py-2 text-sm text-red-700">{error}</p>}

          <div>
            <label htmlFor="profile-name" className="form-label">Name</label>
            <input
              id="profile-name"
              className="form-input"
              value={form.name}
              onChange={handleChange("name")}
              required
              minLength={2}
            />
          </div>

          <div>
            <label htmlFor="profile-phone" className="form-label">Phone</label>
            <input
              id="profile-phone"
              className="form-input"
              value={form.phone}
              onChange={handleChange("phone")}
              placeholder="e.g. 9876543210"
            />
          </div>

          <div>
            <label htmlFor="profile-address" className="form-label">Address</label>
            <textarea
              id="profile-address"
              className="form-input"
              rows={3}
              value={form.address}
              onChange={handleChange("address")}
              placeholder="Street, city, state, PIN"
            />
          </div>

          <div className="flex gap-3">
            <button type="submit" disabled={saving} className="btn-primary flex-1">
              {saving ? "Saving..." : "Save Changes"}
            </button>
            <button type="button" className="btn-secondary flex-1" onClick={cancelEditing} disabled={saving}>
              Cancel
            </button>
          </div>
        </form>
      )}
    </div>
  );
}

function Row({ label, value }) {
  return (
    <div className="flex justify-between p-4 text-sm">
      <span className="text-gray-500">{label}</span>
      <span className="font-medium text-gray-900">{value}</span>
    </div>
  );
}
