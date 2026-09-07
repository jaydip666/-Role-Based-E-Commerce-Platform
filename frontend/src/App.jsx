import { Route, Routes } from "react-router-dom";

import DashboardLayout from "./layouts/DashboardLayout";
import MainLayout from "./layouts/MainLayout";
import AdminDashboard from "./pages/admin/AdminDashboard";
import OrderManagement from "./pages/admin/OrderManagement";
import ProductManagement from "./pages/admin/ProductManagement";
import UserManagement from "./pages/admin/UserManagement";
import Home from "./pages/Home";
import Login from "./pages/Login";
import NotFound from "./pages/NotFound";
import ProductDetails from "./pages/ProductDetails";
import Products from "./pages/Products";
import Register from "./pages/Register";
import AddProduct from "./pages/sales/AddProduct";
import EditProduct from "./pages/sales/EditProduct";
import MyProducts from "./pages/sales/MyProducts";
import SalesDashboard from "./pages/sales/SalesDashboard";
import SalesOrders from "./pages/sales/SalesOrders";
import Cart from "./pages/user/Cart";
import Checkout from "./pages/user/Checkout";
import MyOrders from "./pages/user/MyOrders";
import Profile from "./pages/user/Profile";
import UserDashboard from "./pages/user/UserDashboard";
import Wishlist from "./pages/user/Wishlist";
import ProtectedRoute from "./routes/ProtectedRoute";
import RoleRoute from "./routes/RoleRoute";
import { ROLES } from "./utils/roles";

const adminSidebar = [
  { to: "/admin/dashboard", label: "Dashboard", end: true },
  { to: "/admin/products", label: "Products" },
  { to: "/admin/users", label: "Users" },
  { to: "/admin/orders", label: "Orders" },
];

const salesSidebar = [
  { to: "/sales/dashboard", label: "Dashboard", end: true },
  { to: "/sales/products", label: "My Products" },
  { to: "/sales/products/new", label: "Add Product" },
  { to: "/sales/orders", label: "Orders" },
];

export default function App() {
  return (
    <Routes>
      <Route element={<MainLayout />}>
        {/* Public */}
        <Route path="/" element={<Home />} />
        <Route path="/products" element={<Products />} />
        <Route path="/products/:id" element={<ProductDetails />} />
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />

        {/* Any authenticated user (USER-focused pages) */}
        <Route element={<ProtectedRoute />}>
          <Route path="/dashboard" element={<UserDashboard />} />
          <Route path="/wishlist" element={<Wishlist />} />
          <Route path="/cart" element={<Cart />} />
          <Route path="/checkout" element={<Checkout />} />
          <Route path="/orders" element={<MyOrders />} />
          <Route path="/profile" element={<Profile />} />
        </Route>

        <Route path="*" element={<NotFound />} />
      </Route>

      {/* Sales person */}
      <Route element={<RoleRoute allowedRoles={[ROLES.SALES_PERSON]} />}>
        <Route element={<DashboardLayout sidebarItems={salesSidebar} title="Sales Dashboard" />}>
          <Route path="/sales/dashboard" element={<SalesDashboard />} />
          <Route path="/sales/products" element={<MyProducts />} />
          <Route path="/sales/products/new" element={<AddProduct />} />
          <Route path="/sales/products/:id/edit" element={<EditProduct />} />
          <Route path="/sales/orders" element={<SalesOrders />} />
        </Route>
      </Route>

      {/* Admin */}
      <Route element={<RoleRoute allowedRoles={[ROLES.ADMIN]} />}>
        <Route element={<DashboardLayout sidebarItems={adminSidebar} title="Admin Dashboard" />}>
          <Route path="/admin/dashboard" element={<AdminDashboard />} />
          <Route path="/admin/products" element={<ProductManagement />} />
          <Route path="/admin/users" element={<UserManagement />} />
          <Route path="/admin/orders" element={<OrderManagement />} />
        </Route>
      </Route>
    </Routes>
  );
}
