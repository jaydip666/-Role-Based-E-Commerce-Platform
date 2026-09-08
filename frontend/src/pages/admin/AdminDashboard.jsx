import { useEffect, useState } from "react";

import ErrorMessage from "../../components/ErrorMessage";
import Loader from "../../components/Loader";
import StatCard from "../../components/StatCard";
import StatusBadge from "../../components/StatusBadge";
import * as adminService from "../../services/adminService";
import { formatCurrency, formatDate } from "../../utils/format";

export default function AdminDashboard() {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const load = async () => {
    setLoading(true);
    setError("");
    try {
      const data = await adminService.getAdminStats();
      setStats(data);
    } catch (err) {
      setError(err.friendlyMessage);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
  }, []);

  if (loading) return <Loader label="Loading dashboard..." />;
  if (error) return <ErrorMessage message={error} onRetry={load} />;

  return (
    <div>
      <div className="mb-6 grid grid-cols-2 gap-4 sm:grid-cols-4">
        <StatCard label="Total Users" value={stats.total_users} />
        <StatCard label="Total Products" value={stats.total_products} />
        <StatCard label="Total Orders" value={stats.total_orders} />
        <StatCard label="Total Sales" value={formatCurrency(stats.total_sales)} />
      </div>

      <h2 className="mb-3 text-lg font-semibold text-gray-900">Recent orders</h2>
      {stats.recent_orders.length === 0 ? (
        <p className="text-sm text-gray-500">No orders yet.</p>
      ) : (
        <div className="card divide-y divide-gray-100">
          {stats.recent_orders.map((o) => (
            <div key={o.id} className="flex flex-wrap items-center justify-between gap-2 p-4 text-sm">
              <div>
                <p className="font-medium text-gray-900">Order #{o.id.slice(-8)}</p>
                <p className="text-gray-500">{o.customer_name} • {formatDate(o.created_at)}</p>
              </div>
              <StatusBadge status={o.order_status} />
              <span className="font-semibold">{formatCurrency(o.total_amount)}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
