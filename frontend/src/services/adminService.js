import api from "./api";

export const listUsers = () => api.get("/admin/users").then((r) => r.data.data);

export const updateUserRole = (userId, role) =>
  api.put(`/admin/users/${userId}/role`, { role }).then((r) => r.data.data.user);

export const updateUser = (userId, updates) =>
  api.put(`/admin/users/${userId}`, updates).then((r) => r.data.data.user);

export const deleteUser = (userId) => api.delete(`/admin/users/${userId}`).then((r) => r.data);

export const listAllOrders = () => api.get("/admin/orders").then((r) => r.data.data);

export const updateOrderStatus = (orderId, orderStatus) =>
  api.put(`/admin/orders/${orderId}/status`, { order_status: orderStatus }).then((r) => r.data.data.order);

export const getAdminStats = () => api.get("/admin/stats").then((r) => r.data.data);
