import { useState } from "react";

const emptyForm = { name: "", description: "", price: "", category: "", stock: "" };

export default function ProductForm({ initialValues, onSubmit, submitLabel = "Save product" }) {
  const [form, setForm] = useState({ ...emptyForm, ...initialValues });
  const [imageFile, setImageFile] = useState(null);
  const [preview, setPreview] = useState(initialValues?.image_url || "");
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");

  const handleChange = (field) => (e) => setForm((f) => ({ ...f, [field]: e.target.value }));

  const handleFile = (e) => {
    const file = e.target.files?.[0];
    setImageFile(file || null);
    if (file) setPreview(URL.createObjectURL(file));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setSubmitting(true);
    try {
      await onSubmit({
        name: form.name,
        description: form.description,
        price: form.price,
        category: form.category,
        stock: form.stock,
        imageFile: imageFile || undefined,
      });
    } catch (err) {
      const messages = err.fieldErrors?.join(", ") || err.friendlyMessage || "Could not save product";
      setError(messages);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      {error && <p className="rounded-md bg-red-50 px-3 py-2 text-sm text-red-700">{error}</p>}

      <div>
        <label htmlFor="pf-name" className="form-label">Name</label>
        <input id="pf-name" className="form-input" value={form.name} onChange={handleChange("name")} required minLength={2} />
      </div>

      <div>
        <label htmlFor="pf-description" className="form-label">Description</label>
        <textarea
          id="pf-description"
          className="form-input"
          rows={3}
          value={form.description}
          onChange={handleChange("description")}
          required
        />
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div>
          <label htmlFor="pf-price" className="form-label">Price (₹)</label>
          <input
            id="pf-price"
            type="number"
            min="0"
            step="0.01"
            className="form-input"
            value={form.price}
            onChange={handleChange("price")}
            required
          />
        </div>
        <div>
          <label htmlFor="pf-stock" className="form-label">Stock</label>
          <input
            id="pf-stock"
            type="number"
            min="0"
            className="form-input"
            value={form.stock}
            onChange={handleChange("stock")}
            required
          />
        </div>
      </div>

      <div>
        <label htmlFor="pf-category" className="form-label">Category</label>
        <input id="pf-category" className="form-input" value={form.category} onChange={handleChange("category")} required />
      </div>

      <div>
        <label htmlFor="pf-image" className="form-label">Product image</label>
        <input id="pf-image" type="file" accept="image/png,image/jpeg,image/jpg,image/gif,image/webp" onChange={handleFile} className="text-sm" />
        {preview && (
          <img src={preview} alt="Preview" className="mt-2 h-32 w-32 rounded-md border border-gray-200 object-cover" />
        )}
      </div>

      <button type="submit" disabled={submitting} className="btn-primary w-full">
        {submitting ? "Saving..." : submitLabel}
      </button>
    </form>
  );
}
