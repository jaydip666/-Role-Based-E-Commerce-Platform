import { NavLink } from "react-router-dom";

const itemClass = ({ isActive }) =>
  `block rounded-md px-3 py-2 text-sm font-medium ${
    isActive ? "bg-brand-50 text-brand-700" : "text-gray-600 hover:bg-gray-100"
  }`;

export default function Sidebar({ items }) {
  return (
    <aside className="w-full shrink-0 md:w-56">
      <nav className="card flex flex-row gap-1 overflow-x-auto p-2 md:flex-col md:overflow-visible">
        {items.map((item) => (
          <NavLink key={item.to} to={item.to} end={item.end} className={itemClass}>
            {item.label}
          </NavLink>
        ))}
      </nav>
    </aside>
  );
}
