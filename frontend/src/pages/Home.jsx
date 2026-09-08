import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

import EmptyState from "../components/EmptyState";
import ErrorMessage from "../components/ErrorMessage";
import Loader from "../components/Loader";
import ProductGrid from "../components/ProductGrid";
import * as productService from "../services/productService";

export default function Home() {
  const [state, setState] = useState({ loading: true, error: "", products: [] });

  const load = async () => {
    setState((s) => ({ ...s, loading: true, error: "" }));
    try {
      const data = await productService.listProducts();
      setState({ loading: false, error: "", products: data.products.slice(0, 8) });
    } catch (err) {
      setState({ loading: false, error: err.friendlyMessage, products: [] });
    }
  };

  useEffect(() => {
    load();
  }, []);

  const categories = [...new Set(state.products.map((p) => p.category))].slice(0, 6);

  return (
    <div>
      <section className="bg-gradient-to-br from-brand-700 to-brand-900 text-white">
        <div className="mx-auto flex max-w-6xl flex-col items-start gap-4 px-4 py-16">
          <h1 className="text-3xl font-bold sm:text-4xl">Shop smarter with Mini-shopping</h1>
          <p className="max-w-xl text-brand-100">
            Browse products from real sellers, build your wishlist, and check out securely with
            Razorpay.It is not a real store, and no real transactions are processed.
          </p>
          <Link to="/products" className="btn-primary bg-white text-brand-700 hover:bg-brand-50">
            Browse products
          </Link>
        </div>
      </section>

      {categories.length > 0 && (
        <section className="mx-auto max-w-6xl px-4 py-8">
          <h2 className="mb-4 text-lg font-semibold text-gray-900">Categories</h2>
          <div className="flex flex-wrap gap-2">
            {categories.map((c) => (
              <Link
                key={c}
                to={`/products?category=${encodeURIComponent(c)}`}
                className="rounded-full border border-gray-300 px-4 py-1.5 text-sm text-gray-700 hover:border-brand-500 hover:text-brand-700"
              >
                {c}
              </Link>
            ))}
          </div>
        </section>
      )}

      <section className="mx-auto max-w-6xl px-4 py-8">
        <div className="mb-4 flex items-center justify-between">
          <h2 className="text-lg font-semibold text-gray-900">Featured products</h2>
          <Link to="/products" className="text-sm font-medium text-brand-600 hover:underline">
            View all
          </Link>
        </div>

        {state.loading && <Loader label="Loading products..." />}
        {!state.loading && state.error && <ErrorMessage message={state.error} onRetry={load} />}
        {!state.loading && !state.error && state.products.length === 0 && (
          <EmptyState title="No products yet" message="Check back soon for new arrivals." />
        )}
        {!state.loading && !state.error && state.products.length > 0 && (
          <ProductGrid products={state.products} />
        )}
      </section>
    </div>
  );
}
