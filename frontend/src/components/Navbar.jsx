import { useState } from "react";
import { Link, NavLink, useNavigate } from "react-router-dom";

import { useAuth } from "../context/AuthContext";
import { useCart } from "../context/CartContext";
import { ROLES } from "../utils/roles";

const linkClass = ({ isActive }) =>
  `text-sm font-medium transition-colors ${isActive ? "text-brand-700" : "text-gray-600 hover:text-brand-700"}`;

function NavLinksFor({ role, isAuthenticated }) {
  if (!isAuthenticated) {
    return (
      <>
        <NavLink to="/" end className={linkClass}>Home</NavLink>
        <NavLink to="/products" className={linkClass}>Products</NavLink>
      </>
    );
  }

  if (role === ROLES.ADMIN) {
    return (
      <>
        <NavLink to="/admin/dashboard" className={linkClass}>Dashboard</NavLink>
        <NavLink to="/admin/products" className={linkClass}>Products</NavLink>
        <NavLink to="/admin/users" className={linkClass}>Users</NavLink>
        <NavLink to="/admin/orders" className={linkClass}>Orders</NavLink>
      </>
    );
  }

  if (role === ROLES.SALES_PERSON) {
    return (
      <>
        <NavLink to="/sales/dashboard" className={linkClass}>Dashboard</NavLink>
        <NavLink to="/sales/products" className={linkClass}>Products</NavLink>
        <NavLink to="/sales/products/new" className={linkClass}>Add Product</NavLink>
        <NavLink to="/sales/orders" className={linkClass}>Orders</NavLink>
        <NavLink to="/profile" className={linkClass}>Profile</NavLink>
      </>
    );
  }

  return (
    <>
      <NavLink to="/" end className={linkClass}>Home</NavLink>
      <NavLink to="/products" className={linkClass}>Products</NavLink>
      <NavLink to="/wishlist" className={linkClass}>Wishlist</NavLink>
      <NavLink to="/cart" className={linkClass}>Cart</NavLink>
      <NavLink to="/orders" className={linkClass}>Orders</NavLink>
      <NavLink to="/profile" className={linkClass}>Profile</NavLink>
    </>
  );
}

export default function Navbar() {
  const { isAuthenticated, user, role, logout } = useAuth();
  const { cart } = useCart();
  const navigate = useNavigate();
  const [menuOpen, setMenuOpen] = useState(false);

  const handleLogout = () => {
    logout();
    setMenuOpen(false);
    navigate("/");
  };

  return (
    <header className="sticky top-0 z-30 border-b border-gray-200 bg-white/95 backdrop-blur">
      <div className="mx-auto flex max-w-6xl items-center justify-between px-4 py-3">
        <Link to="/" className="text-lg font-bold text-brand-700">
        Mini-Shopping
        </Link>

        <nav className="hidden items-center gap-6 md:flex">
          <NavLinksFor role={role} isAuthenticated={isAuthenticated} />
        </nav>

        <div className="hidden items-center gap-3 md:flex">
          {isAuthenticated && role === ROLES.USER && (
            <Link to="/cart" className="relative text-gray-600 hover:text-brand-700" aria-label="Cart">
              🛒
              {cart.item_count > 0 && (
                <span className="absolute -right-2 -top-2 flex h-4 min-w-4 items-center justify-center rounded-full bg-brand-600 px-1 text-[10px] font-semibold text-white">
                  {cart.item_count}
                </span>
              )}
            </Link>
          )}
          {isAuthenticated ? (
            <>
              <span className="text-sm text-gray-500">Hi, {user?.name?.split(" ")[0]}</span>
              <button type="button" className="btn-secondary" onClick={handleLogout}>
                Logout
              </button>
            </>
          ) : (
            <>
              <Link to="/login" className="btn-secondary">Login</Link>
              <Link to="/register" className="btn-primary">Register</Link>
            </>
          )}
        </div>

        <button
          type="button"
          className="text-2xl text-gray-600 md:hidden"
          onClick={() => setMenuOpen((v) => !v)}
          aria-label="Toggle menu"
        >
          {menuOpen ? "✕" : "☰"}
        </button>
      </div>

      {menuOpen && (
        <div className="border-t border-gray-200 bg-white px-4 py-3 md:hidden">
          <nav className="flex flex-col gap-3">
            <NavLinksFor role={role} isAuthenticated={isAuthenticated} />
            {isAuthenticated ? (
              <button type="button" className="btn-secondary w-full" onClick={handleLogout}>
                Logout
              </button>
            ) : (
              <div className="flex gap-2">
                <Link to="/login" className="btn-secondary flex-1 text-center" onClick={() => setMenuOpen(false)}>
                  Login
                </Link>
                <Link to="/register" className="btn-primary flex-1 text-center" onClick={() => setMenuOpen(false)}>
                  Register
                </Link>
              </div>
            )}
          </nav>
        </div>
      )}
    </header>
  );
}
