import api from "./api";

export const listProducts = (filters = {}) => {
  const params = {};
  if (filters.search) params.search = filters.search;
  if (filters.category) params.category = filters.category;
  if (filters.minPrice !== undefined && filters.minPrice !== "") params.minPrice = filters.minPrice;
  if (filters.maxPrice !== undefined && filters.maxPrice !== "") params.maxPrice = filters.maxPrice;
  if (filters.ownerId) params.owner_id = filters.ownerId;
  return api.get("/products", { params }).then((r) => r.data.data);
};

export const getProduct = (id) => api.get(`/products/${id}`).then((r) => r.data.data.product);

const toFormData = (payload) => {
  const formData = new FormData();
  Object.entries(payload).forEach(([key, value]) => {
    if (value === undefined || value === null) return;
    formData.append(key, value);
  });
  return formData;
};

export const createProduct = (payload) => {
  const body = payload.imageFile
    ? toFormData({ ...withoutImageFile(payload), image: payload.imageFile })
    : withoutImageFile(payload);
  return api.post("/products", body).then((r) => r.data.data.product);
};

export const updateProduct = (id, payload) => {
  const body = payload.imageFile
    ? toFormData({ ...withoutImageFile(payload), image: payload.imageFile })
    : withoutImageFile(payload);
  return api.put(`/products/${id}`, body).then((r) => r.data.data.product);
};

export const deleteProduct = (id) => api.delete(`/products/${id}`).then((r) => r.data);

function withoutImageFile(payload) {
  const { imageFile, ...rest } = payload;
  return rest;
}
