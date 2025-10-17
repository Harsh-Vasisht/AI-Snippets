
import React, { useState, useEffect } from "react";
import axios from "axios";

export const InventorySearch = () => {
  const [query, setQuery] = useState("");
  const [filters, setFilters] = useState({ category: "", stockStatus: "" });
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSearch = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await axios.get("/api/inventory/search", {
        params: { q: query, ...filters },
      });
      setResults(res.data.results);
    } catch (err) {
      setError("Failed to fetch inventory results");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    handleSearch();
  }, [query, filters]);

  return (
    <div className="p-4">
      <div className="flex gap-2 mb-4">
        <input
          type="text"
          placeholder="Search inventory..."
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          className="border p-2 rounded flex-1"
        />
        <select
          value={filters.category}
          onChange={(e) => setFilters({ ...filters, category: e.target.value })}
          className="border p-2 rounded"
        >
          <option value="">All Categories</option>
          <option value="Electronics">Electronics</option>
          <option value="Apparel">Apparel</option>
        </select>
        <select
          value={filters.stockStatus}
          onChange={(e) => setFilters({ ...filters, stockStatus: e.target.value })}
          className="border p-2 rounded"
        >
          <option value="">All Stock</option>
          <option value="InStock">In Stock</option>
          <option value="OutOfStock">Out of Stock</option>
        </select>
      </div>

      {loading && <p>Loading...</p>}
      {error && <p className="text-red-500">{error}</p>}
      <ul>
        {results.map((item) => (
          <li key={item.id} className="border-b py-2">
            {item.name} - {item.category} ({item.stockStatus})
          </li>
        ))}
      </ul>
    </div>
  );
};
