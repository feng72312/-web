import { useCallback, useEffect, useState } from "react";
import {
  adminGenerateKeys,
  adminListKeys,
  adminLogin,
  adminLogout,
  adminMe,
  getAdminToken,
  type GeneratedKey,
  type LicenseKeyRecord,
} from "./services/adminApi";
import "./styles/app.css";

const TIERS = [
  { value: 10, label: "10 元 / 20 次" },
  { value: 20, label: "20 元 / 50 次" },
  { value: 50, label: "50 元 / 150 次" },
  { value: 100, label: "100 元 / 500 次" },
];

function formatTime(ts: number | null): string {
  if (!ts) {
    return "-";
  }
  return new Date(ts * 1000).toLocaleString("zh-CN", { hour12: false });
}

export default function AdminPage() {
  const [authed, setAuthed] = useState(false);
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [loginUser, setLoginUser] = useState("");
  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState(false);

  const [tier, setTier] = useState(10);
  const [count, setCount] = useState(1);
  const [note, setNote] = useState("");
  const [generated, setGenerated] = useState<GeneratedKey[]>([]);

  const [records, setRecords] = useState<LicenseKeyRecord[]>([]);
  const [total, setTotal] = useState(0);
  const [statusFilter, setStatusFilter] = useState<"" | "unused" | "redeemed">("");

  const refreshList = useCallback(async () => {
    const data = await adminListKeys({
      limit: 50,
      status: statusFilter || undefined,
    });
    setRecords(data.items);
    setTotal(data.total);
  }, [statusFilter]);

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
      .catch(() => {
        setAuthed(false);
      });
  }, []);

  useEffect(() => {
    if (!authed) {
      return;
    }
    refreshList().catch((err: Error) => setMessage(err.message));
  }, [authed, refreshList]);

  const handleLogin = async (event: React.FormEvent) => {
    event.preventDefault();
    setLoading(true);
    setMessage("");
    try {
      await adminLogin(username.trim(), password);
      const data = await adminMe();
      setLoginUser(data.username);
      setAuthed(true);
      setPassword("");
    } catch (err) {
      setMessage(err instanceof Error ? err.message : "login failed");
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = async () => {
    await adminLogout();
    setAuthed(false);
    setLoginUser("");
    setGenerated([]);
    setRecords([]);
  };

  const handleGenerate = async (event: React.FormEvent) => {
    event.preventDefault();
    setLoading(true);
    setMessage("");
    try {
      const keys = await adminGenerateKeys({
        tier,
        count,
        note: note.trim(),
      });
      setGenerated(keys);
      await refreshList();
      setMessage(`已生成 ${keys.length} 个秘钥`);
    } catch (err) {
      setMessage(err instanceof Error ? err.message : "generate failed");
    } finally {
      setLoading(false);
    }
  };

  const copyText = async (text: string) => {
    try {
      await navigator.clipboard.writeText(text);
      setMessage("已复制到剪贴板");
    } catch {
      setMessage("复制失败, 请手动复制");
    }
  };

  if (!authed) {
    return (
      <div className="admin-page">
        <div className="admin-card admin-login-card">
          <h1>秘钥管理后台</h1>
          <p className="admin-subtitle">管理员登录后发放 AI 次数秘钥</p>
          <form className="admin-form" onSubmit={handleLogin}>
            <label>
              账号
              <input
                className="text-input"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                autoComplete="username"
              />
            </label>
            <label>
              密码
              <input
                className="text-input"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                autoComplete="current-password"
              />
            </label>
            <button className="primary-btn" type="submit" disabled={loading}>
              {loading ? "登录中..." : "登录"}
            </button>
          </form>
          {message && <p className="admin-message">{message}</p>}
          <p className="admin-footnote">
            <a href="/">返回主站</a>
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="admin-page">
      <header className="admin-header">
        <div>
          <p className="eyebrow">Admin Console</p>
          <h1>秘钥发放后台</h1>
          <p className="admin-subtitle">当前管理员: {loginUser}</p>
        </div>
        <div className="admin-header-actions">
          <a className="ghost-btn" href="/">
            返回主站
          </a>
          <button className="ghost-btn" type="button" onClick={handleLogout}>
            退出登录
          </button>
        </div>
      </header>

      {message && <p className="admin-message">{message}</p>}

      <section className="admin-card">
        <h2>生成秘钥</h2>
        <form className="admin-form admin-form-inline" onSubmit={handleGenerate}>
          <label>
            面额
            <select
              className="text-input"
              value={tier}
              onChange={(e) => setTier(Number(e.target.value))}
            >
              {TIERS.map((item) => (
                <option key={item.value} value={item.value}>
                  {item.label}
                </option>
              ))}
            </select>
          </label>
          <label>
            数量
            <input
              className="text-input"
              type="number"
              min={1}
              max={100}
              value={count}
              onChange={(e) => setCount(Number(e.target.value))}
            />
          </label>
          <label className="admin-note-field">
            备注
            <input
              className="text-input"
              value={note}
              onChange={(e) => setNote(e.target.value)}
              placeholder="买家/订单备注"
            />
          </label>
          <button className="primary-btn" type="submit" disabled={loading}>
            {loading ? "生成中..." : "生成秘钥"}
          </button>
        </form>

        {generated.length > 0 && (
          <div className="admin-generated">
            <div className="admin-generated-head">
              <h3>本次生成的明文秘钥 (仅显示一次, 请及时复制)</h3>
              <button
                type="button"
                className="ghost-btn"
                onClick={() => copyText(generated.map((item) => item.key).join("\n"))}
              >
                复制全部
              </button>
            </div>
            <ul className="admin-key-list">
              {generated.map((item) => (
                <li key={item.key}>
                  <code>{item.key}</code>
                  <span>
                    {item.tier} 元 / {item.credits} 次
                  </span>
                  <button type="button" className="ghost-btn" onClick={() => copyText(item.key)}>
                    复制
                  </button>
                </li>
              ))}
            </ul>
          </div>
        )}
      </section>

      <section className="admin-card">
        <div className="admin-list-head">
          <h2>秘钥记录</h2>
          <div className="admin-list-tools">
            <select
              className="text-input"
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value as "" | "unused" | "redeemed")}
            >
              <option value="">全部状态</option>
              <option value="unused">未使用</option>
              <option value="redeemed">已兑换</option>
            </select>
            <button type="button" className="ghost-btn" onClick={() => refreshList()}>
              刷新
            </button>
          </div>
        </div>
        <p className="admin-subtitle">共 {total} 条 (不含明文, 明文仅在生成时显示)</p>
        <div className="admin-table-wrap">
          <table className="admin-table">
            <thead>
              <tr>
                <th>ID</th>
                <th>面额</th>
                <th>次数</th>
                <th>状态</th>
                <th>备注</th>
                <th>创建时间</th>
                <th>兑换设备</th>
                <th>兑换时间</th>
              </tr>
            </thead>
            <tbody>
              {records.map((row) => (
                <tr key={row.id}>
                  <td>{row.id}</td>
                  <td>{row.tierLabel} 元</td>
                  <td>{row.credits}</td>
                  <td>{row.status === "unused" ? "未使用" : "已兑换"}</td>
                  <td>{row.note || "-"}</td>
                  <td>{formatTime(row.createdAt)}</td>
                  <td>{row.redeemedDeviceId || "-"}</td>
                  <td>{formatTime(row.redeemedAt)}</td>
                </tr>
              ))}
              {records.length === 0 && (
                <tr>
                  <td colSpan={8}>暂无记录</td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  );
}
