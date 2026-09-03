import AdminPage from "./AdminPage";
import AppShell from "./AppShell";
import { AccessCodeGate } from "./components/AccessCodeGate";

function isAdminRoute(): boolean {
  const hash = window.location.hash;
  const path = window.location.pathname;
  return hash === "#/admin" || path === "/admin" || path.endsWith("/admin/");
}

export default function App() {
  const page = isAdminRoute() ? <AdminPage /> : <AppShell />;
  return (
    <>
      {page}
      <AccessCodeGate />
    </>
  );
}
