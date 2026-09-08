import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

import EmptyState from "../../components/EmptyState";
import ErrorMessage from "../../components/ErrorMessage";
import Loader from "../../components/Loader";
import StatusBadge from "../../components/StatusBadge";
import * as orderService from "../../services/orderService";
import { formatCurrency, formatDate } from "../../utils/format";

export default function MyOrders() {
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const load = async () => {
    setLoading(true);
    setError("");
    try {
      const data = await orderService.listOrders();
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
    <div className="mx-auto max-w-4xl px-4 py-8">
      <h1 className="mb-6 text-xl font-bold text-gray-900">My Orders</h1>

      {loading && <Loader label="Loading orders..." />}
      {!loading && error && <ErrorMessage message={error} onRetry={load} />}
      {!loading && !error && orders.length === 0 && (
        <EmptyState
          title="No orders yet"
          message="Your order history will show up here."
          action={<Link to="/products" className="btn-primary mt-2">Start shopping</Link>}
        />
      )}

      {!loading && !error && orders.length > 0 && (
        <div className="space-y-4">
          {orders.map((order) => (
            <div key={order.id} className="card p-4">
              <div className="flex flex-wrap items-center justify-between gap-2 border-b border-gray-100 pb-3">
                <div>
                  <p className="font-medium text-gray-900">Order #{order.id.slice(-8)}</p>
                  <p className="text-xs text-gray-500">{formatDate(order.created_at)}</p>
                </div>
                <div className="flex gap-2">
                  <StatusBadge status={order.payment_status} />
                  <StatusBadge status={order.order_status} />
                </div>
              </div>
              <div className="divide-y divide-gray-100">
                {order.items.map((item) => (
                  <div key={item.product_id} className="flex justify-between py-2 text-sm">
                    <span>{item.product_name} × {item.quantity}</span>
                    <span>{formatCurrency(item.subtotal)}</span>
                  </div>
                ))}
              </div>
              <div className="flex justify-between pt-3 text-sm font-semibold text-gray-900">
                <span>Total</span>
                <span>{formatCurrency(order.total_amount)}</span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
