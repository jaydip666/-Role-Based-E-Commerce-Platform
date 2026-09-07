import api from "./api";

export const getCart = () => api.get("/cart").then((r) => r.data.data);

export const addToCart = (productId, quantity = 1) =>
  api.post("/cart", { product_id: productId, quantity }).then((r) => r.data.data);

export const updateCartItem = (productId, quantity) =>
  api.put(`/cart/${productId}`, { quantity }).then((r) => r.data.data);

export const removeCartItem = (productId) =>
  api.delete(`/cart/${productId}`).then((r) => r.data.data);
