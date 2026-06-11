import { Alert, Button, Card, Form, Input } from "antd";
import { useState } from "react";

interface AdminLoginProps {
  onLogin: (username: string, password: string) => Promise<void>;
}

interface LoginFormValues {
  username: string;
  password: string;
}

export function AdminLogin({ onLogin }: AdminLoginProps) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleSubmit = async (values: LoginFormValues) => {
    setLoading(true);
    setError("");
    try {
      await onLogin(values.username.trim(), values.password);
    } catch (err) {
      setError(err instanceof Error ? err.message : "登录失败");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="admin-login-wrap">
      <Card className="admin-login-card">
        <h1 className="admin-brand-title">秘钥管理后台</h1>
        <p className="admin-brand-subtitle">管理员登录后发放 AI 次数秘钥</p>
        <Form<LoginFormValues> layout="vertical" onFinish={handleSubmit} autoComplete="on">
          <Form.Item
            label="账号"
            name="username"
            rules={[{ required: true, message: "请输入账号" }]}
          >
            <Input autoComplete="username" />
          </Form.Item>
          <Form.Item
            label="密码"
            name="password"
            rules={[{ required: true, message: "请输入密码" }]}
          >
            <Input.Password autoComplete="current-password" />
          </Form.Item>
          <Form.Item>
            <Button type="primary" htmlType="submit" loading={loading} block>
              登录
            </Button>
          </Form.Item>
        </Form>
        {error ? <Alert type="error" message={error} showIcon /> : null}
        <p style={{ marginTop: 16 }}>
          <a href="/">返回主站</a>
        </p>
      </Card>
    </div>
  );
}
