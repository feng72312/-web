import { lazy, Suspense } from "react";
import AppShell from "./AppShell";
import { AccessCodeGate } from "./components/AccessCodeGate";

const AdminPage = lazy(() => import("./AdminPage"));

function isAdminRoute(): boolean {
  const hash = window.location.hash;
  const path = window.location.pathname;
  return hash === "#/admin" || path === "/admin" || path.endsWith("/admin/");
}

export default function App() {
  const page = isAdminRoute() ? (
    <Suspense fallback={<div className="route-loading">正在载入管理工作台...</div>}>
      <AdminPage />
    </Suspense>
  ) : (
    <AppShell />
  );
  return (
    <>
      {page}
      <AccessCodeGate />
    </>
  );
}
