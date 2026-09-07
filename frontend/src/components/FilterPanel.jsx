export default function FilterPanel({ category, minPrice, maxPrice, onChange, onClear, categories = [] }) {
  return (
    <div className="card flex flex-col gap-3 p-4 sm:flex-row sm:items-end sm:gap-4">
      <div className="flex-1">
        <label htmlFor="filter-category" className="form-label">
          Category
        </label>
        <select
          id="filter-category"
          value={category}
          onChange={(e) => onChange({ category: e.target.value })}
          className="form-input"
        >
          <option value="">All categories</option>
          {categories.map((c) => (
            <option key={c} value={c}>
              {c}
            </option>
          ))}
        </select>
      </div>
      <div className="flex-1">
        <label htmlFor="filter-min" className="form-label">
          Min price
        </label>
        <input
          id="filter-min"
          type="number"
          min="0"
          value={minPrice}
          onChange={(e) => onChange({ minPrice: e.target.value })}
          className="form-input"
          placeholder="0"
        />
      </div>
      <div className="flex-1">
        <label htmlFor="filter-max" className="form-label">
          Max price
        </label>
        <input
          id="filter-max"
          type="number"
          min="0"
          value={maxPrice}
          onChange={(e) => onChange({ maxPrice: e.target.value })}
          className="form-input"
          placeholder="Any"
        />
      </div>
      <button type="button" className="btn-secondary" onClick={onClear}>
        Clear filters
      </button>
    </div>
  );
}
