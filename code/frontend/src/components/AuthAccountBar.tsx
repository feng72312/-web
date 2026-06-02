import { useAuth } from "../context/AuthContext";

export function AuthAccountBar() {
  const { enabled, loading, user, openLogin, openUserCenter } = useAuth();

  if (!enabled) {
    return null;
  }

  if (loading) {
    return <div className="auth-account-bar">账号加载中...</div>;
  }

  if (!user) {
    return (
      <div className="auth-account-bar">
        <button type="button" className="secondary" onClick={() => openLogin()}>
          登录
        </button>
      </div>
    );
  }

  const label = user.username || user.phone || `${user.id.slice(0, 8)}...`;
  return (
    <div className="auth-account-bar">
      <button type="button" className="secondary" onClick={() => openUserCenter()}>
        {label}
      </button>
    </div>
  );
}
