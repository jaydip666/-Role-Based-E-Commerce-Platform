import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";

import ErrorMessage from "../../components/ErrorMessage";
import Loader from "../../components/Loader";
import ProductForm from "../../components/ProductForm";
import { useToast } from "../../context/ToastContext";
import * as productService from "../../services/productService";

export default function EditProduct() {
  const { id } = useParams();
  const navigate = useNavigate();
  const toast = useToast();
  const [product, setProduct] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    productService
      .getProduct(id)
      .then(setProduct)
      .catch((err) => setError(err.friendlyMessage))
      .finally(() => setLoading(false));
  }, [id]);

  const handleSubmit = async (payload) => {
    await productService.updateProduct(id, payload);
    toast.success("Product updated");
    navigate(-1);
  };

  if (loading) return <Loader label="Loading product..." />;
  if (error) return <ErrorMessage message={error} />;

  return (
    <div className="max-w-lg">
      <h1 className="mb-4 text-lg font-semibold text-gray-900">Edit Product</h1>
      <div className="card p-6">
        <ProductForm initialValues={product} onSubmit={handleSubmit} submitLabel="Save changes" />
      </div>
    </div>
  );
}
