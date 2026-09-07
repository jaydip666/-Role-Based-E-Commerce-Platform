import EmptyState from "../../components/EmptyState";
import Loader from "../../components/Loader";
import ProductGrid from "../../components/ProductGrid";
import { useWishlist } from "../../context/WishlistContext";

export default function Wishlist() {
  const { products, loading } = useWishlist();

  return (
    <div>
      <h1 className="mb-4 text-lg font-semibold text-gray-900">My Wishlist</h1>
      {loading && <Loader label="Loading wishlist..." />}
      {!loading && products.length === 0 && (
        <EmptyState title="Your wishlist is empty" message="Save products you love for later." />
      )}
      {!loading && products.length > 0 && <ProductGrid products={products} />}
    </div>
  );
}
