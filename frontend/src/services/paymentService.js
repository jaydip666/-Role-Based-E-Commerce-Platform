import api from "./api";

export const createRazorpayOrder = () =>
  api.post("/payment/create-order").then((r) => r.data.data);

export const verifyPayment = (payload) =>
  api.post("/payment/verify", payload).then((r) => r.data.data.order);
