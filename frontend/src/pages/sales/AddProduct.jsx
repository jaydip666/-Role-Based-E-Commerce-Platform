import { useNavigate } from "react-router-dom";

import ProductForm from "../../components/ProductForm";
import { useToast } from "../../context/ToastContext";
import * as productService from "../../services/productService";

export default function AddProduct() {
  const navigate = useNavigate();
  const toast = useToast();

  const handleSubmit = async (payload) => {
    await productService.createProduct(payload);
    toast.success("Product created");
    navigate("/sales/products");
  };

  return (
    <div className="max-w-lg">
      <h1 className="mb-4 text-lg font-semibold text-gray-900">Add Product</h1>
      <div className="card p-6">
        <ProductForm onSubmit={handleSubmit} submitLabel="Create product" />
      </div>
    </div>
  );
}
