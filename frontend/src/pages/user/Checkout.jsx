import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";

import EmptyState from "../../components/EmptyState";
import { useAuth } from "../../context/AuthContext";
import { useCart } from "../../context/CartContext";
import { useToast } from "../../context/ToastContext";
import * as paymentService from "../../services/paymentService";
import { formatCurrency } from "../../utils/format";
import { loadRazorpayScript } from "../../utils/loadRazorpayScript";

export default function Checkout() {
  const { cart, refreshCart } = useCart();
  const { user } = useAuth();
  const toast = useToast();
  const navigate = useNavigate();
  const [paying, setPaying] = useState(false);
  const [error, setError] = useState("");

  const handlePayNow = async () => {
    setError("");
    setPaying(true);
    try {
      // The backend recomputes the amount from trusted DB product prices —
      // whatever we render on this page is never sent to Razorpay as-is.
      const razorpayOrder = await paymentService.createRazorpayOrder();

      const scriptLoaded = await loadRazorpayScript();
      if (!scriptLoaded) {
        throw new Error("Could not load Razorpay checkout. Check your connection.");
      }

      const keyId = razorpayOrder.key_id || import.meta.env.VITE_RAZORPAY_KEY_ID;

      const options = {
        key: keyId,
        amount: razorpayOrder.amount,
        currency: razorpayOrder.currency,
        name: "ShopHub",
        description: "Order payment (Razorpay test mode)",
        order_id: razorpayOrder.razorpay_order_id,
        prefill: { name: user?.name, email: user?.email },
        theme: { color: "#2563eb" },
        handler: async (response) => {
          try {
            const order = await paymentService.verifyPayment({
              razorpay_order_id: response.razorpay_order_id,
              razorpay_payment_id: response.razorpay_payment_id,
              razorpay_signature: response.razorpay_signature,
            });
            await refreshCart();
            toast.success("Payment verified! Order placed.");
            navigate(`/orders`, { state: { justPlacedOrderId: order.id } });
          } catch (err) {
            setError(err.friendlyMessage || "Payment verification failed. No order was created.");
            toast.error("Payment could not be verified");
          } finally {
            setPaying(false);
          }
        },
        modal: {
          ondismiss: () => setPaying(false),
        },
      };

      const razorpay = new window.Razorpay(options);
      razorpay.open();
    } catch (err) {
      setError(err.friendlyMessage || err.message || "Could not start payment");
      setPaying(false);
    }
  };

  if (cart.items.length === 0) {
    return (
      <div className="mx-auto max-w-2xl px-4 py-16">
        <EmptyState
          title="Your cart is empty"
          message="Add products to your cart before checking out."
          action={<Link to="/products" className="btn-primary mt-2">Browse products</Link>}
        />
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-2xl px-4 py-8">
      <h1 className="mb-6 text-xl font-bold text-gray-900">Checkout</h1>

      <div className="card divide-y divide-gray-100">
        {cart.items.map((item) => (
          <div key={item.product_id} className="flex items-center justify-between p-4 text-sm">
            <div>
              <p className="font-medium text-gray-900">{item.name}</p>
              <p className="text-gray-500">Qty {item.quantity} × {formatCurrency(item.price)}</p>
            </div>
            <p className="font-semibold">{formatCurrency(item.subtotal)}</p>
          </div>
        ))}
        <div className="flex justify-between p-4 font-semibold text-gray-900">
          <span>Total</span>
          <span>{formatCurrency(cart.total)}</span>
        </div>
      </div>

      {error && <p className="mt-4 rounded-md bg-red-50 px-3 py-2 text-sm text-red-700">{error}</p>}

      <button type="button" onClick={handlePayNow} disabled={paying} className="btn-primary mt-6 w-full">
        {paying ? "Processing..." : `Pay Now (${formatCurrency(cart.total)})`}
      </button>
      <p className="mt-2 text-center text-xs text-gray-400">
        Razorpay Test Mode — use test card 4111 1111 1111 1111, any future expiry &amp; CVV.
      </p>
    </div>
  );
}
