export const ROLES = {
  ADMIN: "ADMIN",
  SALES_PERSON: "SALES_PERSON",
  USER: "USER",
};

export const ORDER_STATUSES = ["Pending", "Confirmed", "Processing", "Shipped", "Delivered", "Cancelled"];

export function dashboardPathForRole(role) {
  switch (role) {
    case ROLES.ADMIN:
      return "/admin/dashboard";
    case ROLES.SALES_PERSON:
      return "/sales/dashboard";
    default:
      return "/dashboard";
  }
}
