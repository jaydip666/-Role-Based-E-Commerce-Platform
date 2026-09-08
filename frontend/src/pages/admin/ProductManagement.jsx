import { useEffect, useState } from "react";

import ConfirmDialog from "../../components/ConfirmDialog";
import ErrorMessage from "../../components/ErrorMessage";
import Loader from "../../components/Loader";
import Modal from "../../components/Modal";
import ProductForm from "../../components/ProductForm";
import { useToast } from "../../context/ToastContext";
import * as productService from "../../services/productService";
import { formatCurrency } from "../../utils/format";

export default function ProductManagement() {
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [editing, setEditing] = useState(null); // product being edited, or "new"
  const [pendingDelete, setPendingDelete] = useState(null);
  const toast = useToast();

  const load = async () => {
    setLoading(true);
    setError("");
    try {
      const data = await productService.listProducts();
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

  const handleSubmit = async (payload) => {
    if (editing === "new") {
      await productService.createProduct(payload);
      toast.success("Product created");
    } else {
      await productService.updateProduct(editing.id, payload);
      toast.success("Product updated");
    }
    setEditing(null);
    load();
  };

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
        <h1 className="text-lg font-semibold text-gray-900">Product Management</h1>
        <button type="button" className="btn-primary" onClick={() => setEditing("new")}>
          + Add Product
        </button>
      </div>

      {loading && <Loader label="Loading products..." />}
      {!loading && error && <ErrorMessage message={error} onRetry={load} />}

      {!loading && !error && (
        <div className="overflow-x-auto">
          <table className="w-full min-w-[700px] border-collapse text-sm">
            <thead>
              <tr className="border-b border-gray-200 text-left text-gray-500">
                <th className="py-2">Product</th>
                <th className="py-2">Seller</th>
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
                  <td className="py-3 text-gray-600">{p.owner_name || "-"}</td>
                  <td className="py-3 text-gray-600">{p.category}</td>
                  <td className="py-3 text-gray-600">{formatCurrency(p.price)}</td>
                  <td className="py-3 text-gray-600">{p.stock}</td>
                  <td className="py-3 text-right">
                    <button type="button" className="mr-3 text-brand-600 hover:underline" onClick={() => setEditing(p)}>
                      Edit
                    </button>
                    <button type="button" className="text-red-600 hover:underline" onClick={() => setPendingDelete(p)}>
                      Delete
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      <Modal open={Boolean(editing)} title={editing === "new" ? "Add Product" : "Edit Product"} onClose={() => setEditing(null)}>
        {editing && (
          <ProductForm
            initialValues={editing === "new" ? undefined : editing}
            onSubmit={handleSubmit}
            submitLabel={editing === "new" ? "Create product" : "Save changes"}
          />
        )}
      </Modal>

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
