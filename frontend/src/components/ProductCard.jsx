import { Link, useNavigate } from "react-router-dom";

import { useAuth } from "../context/AuthContext";
import { useCart } from "../context/CartContext";
import { useToast } from "../context/ToastContext";
import { useWishlist } from "../context/WishlistContext";
import { formatCurrency } from "../utils/format";
import { ROLES } from "../utils/roles";

export default function ProductCard({ product }) {
  const { isAuthenticated, role } = useAuth();
  const { addItem } = useCart();
  const { isWishlisted, addProduct, removeProduct } = useWishlist();
  const toast = useToast();
  const navigate = useNavigate();

  const canShop = !isAuthenticated || role === ROLES.USER;
  const outOfStock = product.stock <= 0;
  const wishlisted = isWishlisted(product.id);

  const requireLogin = () => {
    toast.info("Please login to continue");
    navigate("/login");
  };

  const handleAddToCart = async (e) => {
    e.preventDefault();
    if (!isAuthenticated) return requireLogin();
    try {
      await addItem(product.id, 1);
      toast.success("Added to cart");
    } catch (err) {
      toast.error(err.friendlyMessage || "Could not add to cart");
    }
  };

  const handleToggleWishlist = async (e) => {
    e.preventDefault();
    if (!isAuthenticated) return requireLogin();
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
    }
  };

  return (
    <Link to={`/products/${product.id}`} className="card group flex flex-col overflow-hidden">
      <div className="relative aspect-square w-full overflow-hidden bg-gray-100">
        <img
          src={product.image_url}
          alt={product.name}
          className="h-full w-full object-cover transition-transform group-hover:scale-105"
          loading="lazy"
        />
        {canShop && (
          <button
            type="button"
            onClick={handleToggleWishlist}
            aria-label={wishlisted ? "Remove from wishlist" : "Add to wishlist"}
            className={`absolute right-2 top-2 flex h-8 w-8 items-center justify-center rounded-full bg-white shadow ${
              wishlisted ? "text-red-500" : "text-gray-400"
            }`}
          >
            {wishlisted ? "♥" : "♡"}
          </button>
        )}
        {outOfStock && (
          <span className="absolute left-2 top-2 rounded bg-gray-900/80 px-2 py-1 text-xs font-medium text-white">
            Out of stock
          </span>
        )}
      </div>
      <div className="flex flex-1 flex-col gap-1 p-3">
        <span className="text-xs font-medium uppercase tracking-wide text-brand-600">{product.category}</span>
        <h3 className="line-clamp-2 text-sm font-semibold text-gray-900">{product.name}</h3>
        <div className="mt-1 flex items-center justify-between">
          <span className="text-base font-bold text-gray-900">{formatCurrency(product.price)}</span>
          <span className="text-xs text-gray-500">{product.stock} in stock</span>
        </div>
        {canShop && (
          <button
            type="button"
            onClick={handleAddToCart}
            disabled={outOfStock}
            className="btn-primary mt-2 w-full text-xs"
          >
            {outOfStock ? "Out of stock" : "Add to cart"}
          </button>
        )}
      </div>
    </Link>
  );
}
