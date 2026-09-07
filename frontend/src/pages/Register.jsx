import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";

import { useAuth } from "../context/AuthContext";
import { useToast } from "../context/ToastContext";

export default function Register() {
  const { register } = useAuth();
  const navigate = useNavigate();
  const toast = useToast();

  const [form, setForm] = useState({ name: "", email: "", password: "" });
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  const handleChange = (field) => (e) => setForm((f) => ({ ...f, [field]: e.target.value }));

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setSubmitting(true);
    try {
      await register(form.name, form.email, form.password);
      toast.success("Account created! Welcome to ShopHub.");
      navigate("/", { replace: true });
    } catch (err) {
      const messages = err.fieldErrors?.join(", ") || err.friendlyMessage || "Registration failed";
      setError(messages);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="mx-auto flex max-w-md flex-col gap-6 px-4 py-16">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Create an account</h1>
        <p className="mt-1 text-sm text-gray-500">Registers you as a customer (USER role).</p>
      </div>

      <form onSubmit={handleSubmit} className="card space-y-4 p-6">
        {error && <p className="rounded-md bg-red-50 px-3 py-2 text-sm text-red-700">{error}</p>}

        <div>
          <label htmlFor="reg-name" className="form-label">Full name</label>
          <input id="reg-name" className="form-input" value={form.name} onChange={handleChange("name")} required minLength={2} />
        </div>

        <div>
          <label htmlFor="reg-email" className="form-label">Email</label>
          <input id="reg-email" type="email" className="form-input" value={form.email} onChange={handleChange("email")} required autoComplete="email" />
        </div>

        <div>
          <label htmlFor="reg-password" className="form-label">Password</label>
          <input
            id="reg-password"
            type="password"
            className="form-input"
            value={form.password}
            onChange={handleChange("password")}
            required
            minLength={6}
            autoComplete="new-password"
          />
          <p className="mt-1 text-xs text-gray-500">At least 6 characters, with a letter and a number.</p>
        </div>

        <button type="submit" disabled={submitting} className="btn-primary w-full">
          {submitting ? "Creating account..." : "Register"}
        </button>
      </form>

      <p className="text-center text-sm text-gray-500">
        Already have an account?{" "}
        <Link to="/login" className="font-medium text-brand-600 hover:underline">
          Login
        </Link>
      </p>
    </div>
  );
}
