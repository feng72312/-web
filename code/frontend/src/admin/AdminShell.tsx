import { Button, Layout, Menu, Space, Typography } from "antd";
import {
  Activity,
  KeyRound,
  LayoutDashboard,
  LogOut,
  Moon,
  RefreshCw,
  Sun,
} from "lucide-react";
import type { ReactNode } from "react";
import type { AdminPageKey } from "./adminTypes";

const { Header, Sider, Content } = Layout;

interface AdminShellProps {
  activePage: AdminPageKey;
  username: string;
  theme: "light" | "dark";
  refreshing: boolean;
  onPageChange: (page: AdminPageKey) => void;
  onRefresh: () => void;
  onLogout: () => void;
  onToggleTheme: () => void;
  children: ReactNode;
}

const menuItems = [
  { key: "overview" as const, label: "运营总览", icon: <LayoutDashboard size={16} /> },
  { key: "keys" as const, label: "秘钥管理", icon: <KeyRound size={16} /> },
  { key: "health" as const, label: "系统健康", icon: <Activity size={16} /> },
];

export function AdminShell({
  activePage,
  username,
  theme,
  refreshing,
  onPageChange,
  onRefresh,
  onLogout,
  onToggleTheme,
  children,
}: AdminShellProps) {
  return (
    <Layout style={{ minHeight: "100vh" }}>
      <Sider breakpoint="lg" collapsedWidth={0} width={220}>
        <div className="admin-shell-logo">术数运营台</div>
        <Menu
          mode="inline"
          selectedKeys={[activePage]}
          items={menuItems.map((item) => ({
            key: item.key,
            label: item.label,
            icon: item.icon,
          }))}
          onClick={({ key }) => onPageChange(key as AdminPageKey)}
        />
      </Sider>
      <Layout>
        <Header
          style={{
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
            padding: "0 20px",
            borderBottom: "1px solid rgba(0,0,0,0.06)",
          }}
        >
          <Typography.Text>当前管理员: {username}</Typography.Text>
          <Space wrap>
            <Button
              icon={<RefreshCw size={14} />}
              loading={refreshing}
              onClick={onRefresh}
            >
              刷新
            </Button>
            <Button
              icon={theme === "dark" ? <Sun size={14} /> : <Moon size={14} />}
              onClick={onToggleTheme}
            >
              {theme === "dark" ? "浅色" : "暗色"}
            </Button>
            <Button href="/">返回主站</Button>
            <Button danger icon={<LogOut size={14} />} onClick={onLogout}>
              退出登录
            </Button>
          </Space>
        </Header>
        <Content className="admin-shell-content">{children}</Content>
      </Layout>
    </Layout>
  );
}
