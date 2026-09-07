import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

import ConfirmDialog from "../../components/ConfirmDialog";
import EmptyState from "../../components/EmptyState";
import ErrorMessage from "../../components/ErrorMessage";
import Loader from "../../components/Loader";
import { useToast } from "../../context/ToastContext";
import * as productService from "../../services/productService";
import * as salesService from "../../services/salesService";
import { formatCurrency } from "../../utils/format";

export default function MyProducts() {
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [pendingDelete, setPendingDelete] = useState(null);
  const toast = useToast();

  const load = async () => {
    setLoading(true);
    setError("");
    try {
      const data = await salesService.getOwnProducts();
      setProducts(data.products);
    } catch (err) {
      setError(err.friendlyMessage);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
  }, []);

  const handleDelete = async () => {
    if (!pendingDelete) return;
    try {
      await productService.deleteProduct(pendingDelete.id);
      toast.success("Product deleted");
      setProducts((prev) => prev.filter((p) => p.id !== pendingDelete.id));
    } catch (err) {
      toast.error(err.friendlyMessage || "Could not delete product");
    } finally {
      setPendingDelete(null);
    }
  };

  return (
    <div>
      <div className="mb-4 flex items-center justify-between">
        <h1 className="text-lg font-semibold text-gray-900">My Products</h1>
        <Link to="/sales/products/new" className="btn-primary">+ Add Product</Link>
      </div>

      {loading && <Loader label="Loading your products..." />}
      {!loading && error && <ErrorMessage message={error} onRetry={load} />}
      {!loading && !error && products.length === 0 && (
        <EmptyState
          title="You haven't added any products"
          message="List your first product to start selling."
          action={<Link to="/sales/products/new" className="btn-primary mt-2">Add product</Link>}
        />
      )}

      {!loading && !error && products.length > 0 && (
        <div className="overflow-x-auto">
          <table className="w-full min-w-[600px] border-collapse text-sm">
            <thead>
              <tr className="border-b border-gray-200 text-left text-gray-500">
                <th className="py-2">Product</th>
                <th className="py-2">Category</th>
                <th className="py-2">Price</th>
                <th className="py-2">Stock</th>
                <th className="py-2 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {products.map((p) => (
                <tr key={p.id}>
                  <td className="flex items-center gap-3 py-3">
                    <img src={p.image_url} alt={p.name} className="h-10 w-10 rounded object-cover" />
                    <span className="font-medium text-gray-900">{p.name}</span>
                  </td>
                  <td className="py-3 text-gray-600">{p.category}</td>
                  <td className="py-3 text-gray-600">{formatCurrency(p.price)}</td>
                  <td className="py-3 text-gray-600">{p.stock}</td>
                  <td className="py-3 text-right">
                    <Link to={`/sales/products/${p.id}/edit`} className="mr-3 text-brand-600 hover:underline">
                      Edit
                    </Link>
                    <button
                      type="button"
                      onClick={() => setPendingDelete(p)}
                      className="text-red-600 hover:underline"
                    >
                      Delete
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      <ConfirmDialog
        open={Boolean(pendingDelete)}
        title="Delete product"
        message={`Delete "${pendingDelete?.name}"? This cannot be undone.`}
        confirmLabel="Delete"
        onConfirm={handleDelete}
        onCancel={() => setPendingDelete(null)}
      />
    </div>
  );
}
