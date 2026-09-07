import { Outlet } from "react-router-dom";

import Footer from "../components/Footer";
import Navbar from "../components/Navbar";
import Sidebar from "../components/Sidebar";

export default function DashboardLayout({ sidebarItems, title }) {
  return (
    <div className="flex min-h-screen flex-col">
      <Navbar />
      <main className="mx-auto w-full max-w-6xl flex-1 px-4 py-6">
        {title && <h1 className="mb-4 text-xl font-bold text-gray-900">{title}</h1>}
        <div className="flex flex-col gap-6 md:flex-row">
          <Sidebar items={sidebarItems} />
          <div className="min-w-0 flex-1">
            <Outlet />
          </div>
        </div>
      </main>
      <Footer />
    </div>
  );
}
