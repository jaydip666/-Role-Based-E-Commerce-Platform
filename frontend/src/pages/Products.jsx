import { useEffect, useState } from "react";
import { useSearchParams } from "react-router-dom";

import EmptyState from "../components/EmptyState";
import ErrorMessage from "../components/ErrorMessage";
import FilterPanel from "../components/FilterPanel";
import Loader from "../components/Loader";
import ProductGrid from "../components/ProductGrid";
import SearchBar from "../components/SearchBar";
import * as productService from "../services/productService";

export default function Products() {
  const [searchParams, setSearchParams] = useSearchParams();
  const [searchInput, setSearchInput] = useState(searchParams.get("search") || "");
  const [products, setProducts] = useState([]);
  const [allCategories, setAllCategories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const filters = {
    search: searchParams.get("search") || "",
    category: searchParams.get("category") || "",
    minPrice: searchParams.get("minPrice") || "",
    maxPrice: searchParams.get("maxPrice") || "",
  };

  const load = async () => {
    setLoading(true);
    setError("");
    try {
      const data = await productService.listProducts(filters);
      setProducts(data.products);
      if (!filters.category && !filters.search && !filters.minPrice && !filters.maxPrice) {
        setAllCategories([...new Set(data.products.map((p) => p.category))]);
      }
    } catch (err) {
      setError(err.friendlyMessage);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [searchParams]);

  useEffect(() => {
    // Load the full category list once for the filter dropdown.
    productService.listProducts().then((data) => {
      setAllCategories([...new Set(data.products.map((p) => p.category))]);
    }).catch(() => {});
  }, []);

  const updateFilters = (updates) => {
    const next = new URLSearchParams(searchParams);
    Object.entries(updates).forEach(([key, value]) => {
      if (value) next.set(key, value);
      else next.delete(key);
    });
    setSearchParams(next);
  };

  const handleSearchSubmit = () => updateFilters({ search: searchInput });

  const handleClear = () => {
    setSearchInput("");
    setSearchParams({});
  };

  return (
    <div className="mx-auto max-w-6xl px-4 py-8">
      <h1 className="mb-4 text-xl font-bold text-gray-900">All Products</h1>

      <div className="mb-4">
        <SearchBar value={searchInput} onChange={setSearchInput} onSubmit={handleSearchSubmit} />
      </div>

      <div className="mb-6">
        <FilterPanel
          category={filters.category}
          minPrice={filters.minPrice}
          maxPrice={filters.maxPrice}
          categories={allCategories}
          onChange={updateFilters}
          onClear={handleClear}
        />
      </div>

      {loading && <Loader label="Loading products..." />}
      {!loading && error && <ErrorMessage message={error} onRetry={load} />}
      {!loading && !error && products.length === 0 && (
        <EmptyState title="No products found" message="Try adjusting your search or filters." />
      )}
      {!loading && !error && products.length > 0 && <ProductGrid products={products} />}
    </div>
  );
}
