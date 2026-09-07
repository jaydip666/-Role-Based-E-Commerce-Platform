import { useAuth } from "../../context/AuthContext";
import { formatDate } from "../../utils/format";

export default function Profile() {
  const { user } = useAuth();

  return (
    <div className="mx-auto max-w-lg px-4 py-8">
      <h1 className="mb-6 text-xl font-bold text-gray-900">Profile</h1>
      <div className="card divide-y divide-gray-100">
        <Row label="Name" value={user?.name} />
        <Row label="Email" value={user?.email} />
        <Row label="Role" value={user?.role} />
        <Row label="Member since" value={formatDate(user?.created_at)} />
      </div>
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
