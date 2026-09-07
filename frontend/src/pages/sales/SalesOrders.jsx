import { useEffect, useState } from "react";

import EmptyState from "../../components/EmptyState";
import ErrorMessage from "../../components/ErrorMessage";
import Loader from "../../components/Loader";
import StatusBadge from "../../components/StatusBadge";
import * as salesService from "../../services/salesService";
import { formatCurrency, formatDate } from "../../utils/format";

export default function SalesOrders() {
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const load = async () => {
    setLoading(true);
    setError("");
    try {
      const data = await salesService.getRelevantOrders();
      setOrders(data.orders);
    } catch (err) {
      setError(err.friendlyMessage);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
  }, []);

  return (
    <div>
      <h1 className="mb-4 text-lg font-semibold text-gray-900">Orders with my products</h1>

      {loading && <Loader label="Loading orders..." />}
      {!loading && error && <ErrorMessage message={error} onRetry={load} />}
      {!loading && !error && orders.length === 0 && (
        <EmptyState title="No relevant orders yet" message="Orders containing your products will appear here." />
      )}

      {!loading && !error && orders.length > 0 && (
        <div className="space-y-4">
          {orders.map((order) => (
            <div key={order.id} className="card p-4">
              <div className="flex flex-wrap items-center justify-between gap-2 border-b border-gray-100 pb-3">
                <div>
                  <p className="font-medium text-gray-900">Order #{order.id.slice(-8)}</p>
                  <p className="text-xs text-gray-500">{formatDate(order.created_at)} • {order.customer_name}</p>
                </div>
                <StatusBadge status={order.order_status} />
              </div>
              <div className="divide-y divide-gray-100">
                {order.items.map((item) => (
                  <div key={item.product_id} className="flex justify-between py-2 text-sm">
                    <span>{item.product_name} × {item.quantity}</span>
                    <span>{formatCurrency(item.subtotal)}</span>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
