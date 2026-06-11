import { ConfigProvider, message } from "antd";
import { useCallback, useEffect, useState } from "react";
import { useTheme } from "../context/ThemeContext";
import {
  AdminAuthError,
  adminLogin,
  adminLogout,
  adminMe,
  adminOverview,
  getAdminToken,
  type AdminOverview,
} from "../services/adminApi";
import "./admin.css";
import { AdminLogin } from "./AdminLogin";
import { AdminOverviewPanel } from "./AdminOverview";
import { AdminShell } from "./AdminShell";
import { getAdminThemeConfig } from "./adminTheme";
import type { AdminPageKey } from "./adminTypes";
import { KeyManager } from "./KeyManager";
import { SystemHealthPanel } from "./SystemHealth";

export default function AdminPage() {
  const { theme, toggleTheme } = useTheme();
  const [authed, setAuthed] = useState(false);
  const [loginUser, setLoginUser] = useState("");
  const [activePage, setActivePage] = useState<AdminPageKey>("overview");
  const [refreshing, setRefreshing] = useState(false);
  const [refreshToken, setRefreshToken] = useState(0);

  const [overview, setOverview] = useState<AdminOverview | null>(null);
  const [overviewLoading, setOverviewLoading] = useState(false);
  const [overviewError, setOverviewError] = useState("");

  const handleAuthFailure = useCallback((err: unknown) => {
    if (err instanceof AdminAuthError) {
      setAuthed(false);
      setLoginUser("");
      setOverview(null);
      message.error(err.message);
      return true;
    }
    return false;
  }, []);

  const loadOverview = useCallback(async () => {
    setOverviewLoading(true);
    setOverviewError("");
    try {
      const data = await adminOverview();
      setOverview(data);
    } catch (err) {
      if (!handleAuthFailure(err)) {
        setOverviewError(err instanceof Error ? err.message : "加载总览失败");
      }
    } finally {
      setOverviewLoading(false);
    }
  }, [handleAuthFailure]);

  useEffect(() => {
    const token = getAdminToken();
    if (!token) {
      return;
    }
    adminMe()
      .then((data) => {
        setLoginUser(data.username);
        setAuthed(true);
      })
      .catch((err) => {
        if (!handleAuthFailure(err)) {
          setAuthed(false);
        }
      });
  }, [handleAuthFailure]);

  useEffect(() => {
    if (!authed) {
      return;
    }
    void loadOverview();
  }, [authed, refreshToken, loadOverview]);

  const handleLogin = async (username: string, password: string) => {
    await adminLogin(username, password);
    const data = await adminMe();
    setLoginUser(data.username);
    setAuthed(true);
    setActivePage("overview");
    setRefreshToken((value) => value + 1);
  };

  const handleLogout = async () => {
    await adminLogout();
    setAuthed(false);
    setLoginUser("");
    setOverview(null);
    setActivePage("overview");
  };

  const handleRefresh = async () => {
    if (!authed) {
      return;
    }
    setRefreshing(true);
    try {
      await loadOverview();
      setRefreshToken((value) => value + 1);
    } finally {
      setRefreshing(false);
    }
  };

  const handleDataChanged = () => {
    setRefreshToken((value) => value + 1);
  };

  return (
    <ConfigProvider theme={getAdminThemeConfig(theme)}>
      <div className="admin-root" data-theme={theme}>
        {!authed ? (
          <AdminLogin onLogin={handleLogin} />
        ) : (
          <AdminShell
            activePage={activePage}
            username={loginUser}
            theme={theme}
            refreshing={refreshing}
            onPageChange={setActivePage}
            onRefresh={() => void handleRefresh()}
            onLogout={() => void handleLogout()}
            onToggleTheme={toggleTheme}
          >
            {activePage === "overview" ? (
              <AdminOverviewPanel
                data={overview}
                loading={overviewLoading}
                error={overviewError}
                onGoKeys={() => setActivePage("keys")}
              />
            ) : null}
            {activePage === "keys" ? (
              <KeyManager refreshToken={refreshToken} onDataChanged={handleDataChanged} />
            ) : null}
            {activePage === "health" ? (
              <SystemHealthPanel
                data={overview}
                loading={overviewLoading}
                error={overviewError}
              />
            ) : null}
          </AdminShell>
        )}
      </div>
    </ConfigProvider>
  );
}
