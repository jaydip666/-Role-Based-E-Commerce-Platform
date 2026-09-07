import { Link, useNavigate } from "react-router-dom";

import EmptyState from "../../components/EmptyState";
import Loader from "../../components/Loader";
import { useCart } from "../../context/CartContext";
import { useToast } from "../../context/ToastContext";
import { formatCurrency } from "../../utils/format";

export default function Cart() {
  const { cart, loading, updateItem, removeItem } = useCart();
  const toast = useToast();
  const navigate = useNavigate();

  const handleQuantity = async (productId, quantity) => {
    if (quantity < 1) return;
    try {
      await updateItem(productId, quantity);
    } catch (err) {
      toast.error(err.friendlyMessage || "Could not update quantity");
    }
  };

  const handleRemove = async (productId) => {
    try {
      await removeItem(productId);
      toast.info("Item removed from cart");
    } catch (err) {
      toast.error(err.friendlyMessage || "Could not remove item");
    }
  };

  if (loading) return <Loader label="Loading cart..." />;

  return (
    <div className="mx-auto max-w-4xl px-4 py-8">
      <h1 className="mb-6 text-xl font-bold text-gray-900">Your Cart</h1>

      {cart.items.length === 0 ? (
        <EmptyState
          title="Your cart is empty"
          message="Add some products to get started."
          action={
            <Link to="/products" className="btn-primary mt-2">
              Browse products
            </Link>
          }
        />
      ) : (
        <div className="grid gap-6 lg:grid-cols-3">
          <div className="card divide-y divide-gray-100 lg:col-span-2">
            {cart.items.map((item) => (
              <div key={item.product_id} className="flex flex-col gap-3 p-4 sm:flex-row sm:items-center">
                <img src={item.image_url} alt={item.name} className="h-20 w-20 rounded-md object-cover" />
                <div className="flex-1">
                  <p className="font-medium text-gray-900">{item.name}</p>
                  <p className="text-sm text-gray-500">{formatCurrency(item.price)} each</p>
                </div>
                <div className="flex items-center gap-2">
                  <button
                    type="button"
                    className="btn-secondary px-3 py-1"
                    onClick={() => handleQuantity(item.product_id, item.quantity - 1)}
                    aria-label="Decrease quantity"
                  >
                    −
                  </button>
                  <input
                    type="number"
                    min={1}
                    max={item.stock}
                    value={item.quantity}
                    onChange={(e) => handleQuantity(item.product_id, Number(e.target.value) || 1)}
                    className="form-input w-16 text-center"
                    aria-label={`Quantity for ${item.name}`}
                  />
                  <button
                    type="button"
                    className="btn-secondary px-3 py-1"
                    onClick={() => handleQuantity(item.product_id, item.quantity + 1)}
                    aria-label="Increase quantity"
                    disabled={item.quantity >= item.stock}
                  >
                    +
                  </button>
                </div>
                <p className="w-24 text-right font-semibold">{formatCurrency(item.subtotal)}</p>
                <button
                  type="button"
                  onClick={() => handleRemove(item.product_id)}
                  className="text-sm text-red-600 hover:underline"
                >
                  Remove
                </button>
              </div>
            ))}
          </div>

          <div className="card h-fit p-4">
            <h2 className="mb-3 font-semibold text-gray-900">Order Summary</h2>
            <div className="flex justify-between text-sm text-gray-600">
              <span>Subtotal</span>
              <span>{formatCurrency(cart.subtotal)}</span>
            </div>
            <div className="mt-2 flex justify-between border-t border-gray-100 pt-2 font-semibold text-gray-900">
              <span>Total</span>
              <span>{formatCurrency(cart.total)}</span>
            </div>
            <button type="button" className="btn-primary mt-4 w-full" onClick={() => navigate("/checkout")}>
              Proceed to checkout
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
