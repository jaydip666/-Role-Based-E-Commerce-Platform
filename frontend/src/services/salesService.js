import api from "./api";

export const getOwnProducts = () => api.get("/sales/products").then((r) => r.data.data);

export const getRelevantOrders = () => api.get("/sales/orders").then((r) => r.data.data);

export const getSalesStats = () => api.get("/sales/stats").then((r) => r.data.data);
