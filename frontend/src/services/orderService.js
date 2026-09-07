import api from "./api";

export const listOrders = () => api.get("/orders").then((r) => r.data.data);

export const getOrder = (id) => api.get(`/orders/${id}`).then((r) => r.data.data.order);
