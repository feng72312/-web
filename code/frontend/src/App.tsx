import AdminPage from "./AdminPage";
import AppShell from "./AppShell";

function isAdminRoute(): boolean {
  const hash = window.location.hash;
  const path = window.location.pathname;
  return hash === "#/admin" || path === "/admin" || path.endsWith("/admin/");
}

export default function App() {
  if (isAdminRoute()) {
    return <AdminPage />;
  }
  return <AppShell />;
}
