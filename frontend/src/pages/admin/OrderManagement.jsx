import { useEffect, useState } from "react";

import ErrorMessage from "../../components/ErrorMessage";
import Loader from "../../components/Loader";
import StatusBadge from "../../components/StatusBadge";
import { useToast } from "../../context/ToastContext";
import * as adminService from "../../services/adminService";
import { formatCurrency, formatDate } from "../../utils/format";
import { ORDER_STATUSES } from "../../utils/roles";

export default function OrderManagement() {
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [updatingId, setUpdatingId] = useState(null);
  const toast = useToast();

  const load = async () => {
    setLoading(true);
    setError("");
    try {
      const data = await adminService.listAllOrders();
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

  const handleStatusChange = async (orderId, status) => {
    setUpdatingId(orderId);
    try {
      const updated = await adminService.updateOrderStatus(orderId, status);
      setOrders((prev) => prev.map((o) => (o.id === orderId ? updated : o)));
      toast.success("Order status updated");
    } catch (err) {
      toast.error(err.friendlyMessage || "Could not update order status");
    } finally {
      setUpdatingId(null);
    }
  };

  return (
    <div>
      <h1 className="mb-4 text-lg font-semibold text-gray-900">Order Management</h1>

      {loading && <Loader label="Loading orders..." />}
      {!loading && error && <ErrorMessage message={error} onRetry={load} />}
      {!loading && !error && orders.length === 0 && <p className="text-sm text-gray-500">No orders yet.</p>}

      {!loading && !error && orders.length > 0 && (
        <div className="space-y-4">
          {orders.map((order) => (
            <div key={order.id} className="card p-4">
              <div className="flex flex-wrap items-center justify-between gap-3 border-b border-gray-100 pb-3">
                <div>
                  <p className="font-medium text-gray-900">Order #{order.id.slice(-8)}</p>
                  <p className="text-xs text-gray-500">{order.customer_name} • {formatDate(order.created_at)}</p>
                </div>
                <div className="flex items-center gap-2">
                  <StatusBadge status={order.payment_status} />
                  <select
                    className="form-input w-40"
                    value={order.order_status}
                    disabled={updatingId === order.id}
                    onChange={(e) => handleStatusChange(order.id, e.target.value)}
                  >
                    {ORDER_STATUSES.map((s) => (
                      <option key={s} value={s}>{s}</option>
                    ))}
                  </select>
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
