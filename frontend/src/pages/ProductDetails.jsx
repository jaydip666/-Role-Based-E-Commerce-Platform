import { useEffect, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";

import ErrorMessage from "../components/ErrorMessage";
import Loader from "../components/Loader";
import { useAuth } from "../context/AuthContext";
import { useCart } from "../context/CartContext";
import { useToast } from "../context/ToastContext";
import { useWishlist } from "../context/WishlistContext";
import * as productService from "../services/productService";
import { formatCurrency } from "../utils/format";
import { ROLES } from "../utils/roles";

export default function ProductDetails() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { isAuthenticated, role } = useAuth();
  const { addItem } = useCart();
  const { isWishlisted, addProduct, removeProduct } = useWishlist();
  const toast = useToast();

  const [product, setProduct] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [quantity, setQuantity] = useState(1);
  const [busy, setBusy] = useState(false);

  const load = async () => {
    setLoading(true);
    setError("");
    try {
      const data = await productService.getProduct(id);
      setProduct(data);
    } catch (err) {
      setError(err.friendlyMessage);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [id]);

  if (loading) return <Loader label="Loading product..." />;
  if (error) return <div className="mx-auto max-w-4xl px-4 py-8"><ErrorMessage message={error} onRetry={load} /></div>;
  if (!product) return null;

  const canShop = !isAuthenticated || role === ROLES.USER;
  const outOfStock = product.stock <= 0;
  const wishlisted = isWishlisted(product.id);

  const requireLogin = () => {
    toast.info("Please login to continue");
    navigate("/login");
  };

  const handleAddToCart = async () => {
    if (!isAuthenticated) return requireLogin();
    setBusy(true);
    try {
      await addItem(product.id, quantity);
      toast.success("Added to cart");
    } catch (err) {
      toast.error(err.friendlyMessage || "Could not add to cart");
    } finally {
      setBusy(false);
    }
  };

  const handleToggleWishlist = async () => {
    if (!isAuthenticated) return requireLogin();
    setBusy(true);
    try {
      if (wishlisted) {
        await removeProduct(product.id);
        toast.info("Removed from wishlist");
      } else {
        await addProduct(product.id);
        toast.success("Added to wishlist");
      }
    } catch (err) {
      toast.error(err.friendlyMessage || "Wishlist action failed");
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="mx-auto max-w-4xl px-4 py-8">
      <Link to="/products" className="mb-4 inline-block text-sm text-brand-600 hover:underline">
        &larr; Back to products
      </Link>
      <div className="grid gap-8 sm:grid-cols-2">
        <div className="aspect-square overflow-hidden rounded-lg bg-gray-100">
          <img src={product.image_url} alt={product.name} className="h-full w-full object-cover" />
        </div>
        <div>
          <span className="text-xs font-medium uppercase tracking-wide text-brand-600">{product.category}</span>
          <h1 className="mt-1 text-2xl font-bold text-gray-900">{product.name}</h1>
          <p className="mt-3 text-gray-600">{product.description}</p>
          <p className="mt-4 text-2xl font-bold text-gray-900">{formatCurrency(product.price)}</p>
          <p className="mt-1 text-sm text-gray-500">
            {outOfStock ? "Out of stock" : `${product.stock} unit(s) available`}
          </p>
          {product.owner_name && (
            <p className="mt-1 text-sm text-gray-500">Sold by {product.owner_name}</p>
          )}

          {canShop && (
            <div className="mt-6 flex flex-col gap-3 sm:flex-row sm:items-center">
              <div className="flex items-center gap-2">
                <label htmlFor="qty" className="text-sm text-gray-600">Qty</label>
                <input
                  id="qty"
                  type="number"
                  min={1}
                  max={product.stock || 1}
                  value={quantity}
                  onChange={(e) => setQuantity(Math.max(1, Number(e.target.value) || 1))}
                  className="form-input w-20"
                  disabled={outOfStock}
                />
              </div>
              <button
                type="button"
                onClick={handleAddToCart}
                disabled={outOfStock || busy}
                className="btn-primary flex-1"
              >
                {outOfStock ? "Out of stock" : "Add to cart"}
              </button>
              <button type="button" onClick={handleToggleWishlist} disabled={busy} className="btn-secondary">
                {wishlisted ? "♥ Wishlisted" : "♡ Wishlist"}
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
