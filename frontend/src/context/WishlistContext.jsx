import { createContext, useCallback, useContext, useEffect, useMemo, useState } from "react";

import * as wishlistService from "../services/wishlistService";
import { useAuth } from "./AuthContext";

const WishlistContext = createContext(null);

export function WishlistProvider({ children }) {
  const { isAuthenticated } = useAuth();
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(false);

  const idSet = useMemo(() => new Set(products.map((p) => p.id)), [products]);

  const refreshWishlist = useCallback(async () => {
    if (!isAuthenticated) {
      setProducts([]);
      return;
    }
    setLoading(true);
    try {
      const data = await wishlistService.getWishlist();
      setProducts(data.products);
    } finally {
      setLoading(false);
    }
  }, [isAuthenticated]);

  useEffect(() => {
    refreshWishlist();
  }, [refreshWishlist]);

  const isWishlisted = (productId) => idSet.has(productId);

  const addProduct = async (productId) => {
    if (idSet.has(productId)) return; // avoid unnecessary duplicate API calls
    await wishlistService.addToWishlist(productId);
    await refreshWishlist();
  };

  const removeProduct = async (productId) => {
    if (!idSet.has(productId)) return;
    await wishlistService.removeFromWishlist(productId);
    setProducts((prev) => prev.filter((p) => p.id !== productId));
  };

  const value = useMemo(
    () => ({ products, loading, refreshWishlist, isWishlisted, addProduct, removeProduct }),
    [products, loading, refreshWishlist]
  );

  return <WishlistContext.Provider value={value}>{children}</WishlistContext.Provider>;
}

export function useWishlist() {
  const ctx = useContext(WishlistContext);
  if (!ctx) throw new Error("useWishlist must be used within a WishlistProvider");
  return ctx;
}
