import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

import ErrorMessage from "../../components/ErrorMessage";
import Loader from "../../components/Loader";
import StatCard from "../../components/StatCard";
import StatusBadge from "../../components/StatusBadge";
import { useAuth } from "../../context/AuthContext";
import { useCart } from "../../context/CartContext";
import { useWishlist } from "../../context/WishlistContext";
import * as orderService from "../../services/orderService";
import { formatCurrency, formatDate } from "../../utils/format";

export default function UserDashboard() {
  const { user } = useAuth();
  const { cart } = useCart();
  const { products: wishlistProducts } = useWishlist();
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
    <div>
      <h1 className="mb-1 text-xl font-bold text-gray-900">Welcome, {user?.name}</h1>
      <p className="mb-6 text-sm text-gray-500">Here&apos;s a quick look at your account.</p>

      <div className="mb-8 grid grid-cols-2 gap-4 sm:grid-cols-4">
        <StatCard label="Cart items" value={cart.item_count} />
        <StatCard label="Wishlist" value={wishlistProducts.length} />
        <StatCard label="Orders" value={orders.length} />
        <StatCard label="Cart total" value={formatCurrency(cart.total)} />
      </div>

      <h2 className="mb-3 text-lg font-semibold text-gray-900">Recent orders</h2>
      {loading && <Loader label="Loading orders..." />}
      {!loading && error && <ErrorMessage message={error} onRetry={load} />}
      {!loading && !error && orders.length === 0 && (
        <p className="text-sm text-gray-500">
          No orders yet. <Link to="/products" className="text-brand-600 hover:underline">Start shopping</Link>.
        </p>
      )}
      {!loading && !error && orders.length > 0 && (
        <div className="card divide-y divide-gray-100">
          {orders.slice(0, 5).map((o) => (
            <div key={o.id} className="flex flex-wrap items-center justify-between gap-2 p-4 text-sm">
              <div>
                <p className="font-medium text-gray-900">Order #{o.id.slice(-8)}</p>
                <p className="text-gray-500">{formatDate(o.created_at)}</p>
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
