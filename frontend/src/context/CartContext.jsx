import { createContext, useCallback, useContext, useEffect, useMemo, useState } from "react";

import * as cartService from "../services/cartService";
import { useAuth } from "./AuthContext";

const CartContext = createContext(null);

const emptyCart = { items: [], item_count: 0, subtotal: 0, total: 0 };

export function CartProvider({ children }) {
  const { isAuthenticated } = useAuth();
  const [cart, setCart] = useState(emptyCart);
  const [loading, setLoading] = useState(false);

  const refreshCart = useCallback(async () => {
    if (!isAuthenticated) {
      setCart(emptyCart);
      return;
    }
    setLoading(true);
    try {
      const data = await cartService.getCart();
      setCart(data);
    } finally {
      setLoading(false);
    }
  }, [isAuthenticated]);

  useEffect(() => {
    refreshCart();
  }, [refreshCart]);

  const addItem = async (productId, quantity = 1) => {
    const data = await cartService.addToCart(productId, quantity);
    setCart(data);
    return data;
  };

  const updateItem = async (productId, quantity) => {
    const data = await cartService.updateCartItem(productId, quantity);
    setCart(data);
    return data;
  };

  const removeItem = async (productId) => {
    const data = await cartService.removeCartItem(productId);
    setCart(data);
    return data;
  };

  const value = useMemo(
    () => ({ cart, loading, refreshCart, addItem, updateItem, removeItem }),
    [cart, loading, refreshCart]
  );

  return <CartContext.Provider value={value}>{children}</CartContext.Provider>;
}

export function useCart() {
  const ctx = useContext(CartContext);
  if (!ctx) throw new Error("useCart must be used within a CartProvider");
  return ctx;
}
