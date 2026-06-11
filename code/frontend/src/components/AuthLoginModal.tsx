import { useState } from "react";

import { getCloudbaseAuth } from "../services/cloudbaseClient";
import { isValidCnPhone, phoneHint, toCloudbasePhone } from "../utils/phoneFormat";
import {
  formatAuthErrorMessage,
  loginAccountHint,
  parsePasswordLoginInput,
} from "../utils/loginAccount";

type TabId = "password" | "phone";

interface AuthLoginModalProps {
  onClose: () => void;
  onSuccess: () => void | Promise<void>;
}

export function AuthLoginModal({ onClose, onSuccess }: AuthLoginModalProps) {
  const [tab, setTab] = useState<TabId>("password");
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [phone, setPhone] = useState("");
  const [otp, setOtp] = useState("");
  const [otpSent, setOtpSent] = useState(false);
  const [verifyOtpFn, setVerifyOtpFn] = useState<
    ((args: { token: string }) => Promise<{ data: unknown; error: unknown }>) | null
  >(null);
  const [isRegister, setIsRegister] = useState(false);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState("");

  const auth = getCloudbaseAuth();

  const handlePassword = async () => {
    if (isRegister) {
      setMessage("当前环境不支持仅用用户名注册, 请切换到「手机验证码」注册");
      return;
    }
    const loginParams = parsePasswordLoginInput(username, password);
    if (!loginParams) {
      setMessage(loginAccountHint());
      return;
    }
    if (password.length < 6) {
      setMessage("密码至少 6 位");
      return;
    }
    setLoading(true);
    setMessage("");
    try {
      const { error } = await auth.signInWithPassword(loginParams);
      if (error) {
        throw error;
      }
      await onSuccess();
    } catch (err) {
      setMessage(formatAuthErrorMessage(err));
    } finally {
      setLoading(false);
    }
  };

  const handleSendOtp = async () => {
    if (!isValidCnPhone(phone)) {
      setMessage(phoneHint());
      return;
    }
    setLoading(true);
    setMessage("");
    try {
      const { data, error } = await auth.signInWithOtp({ phone: toCloudbasePhone(phone) });
      if (error || !data?.verifyOtp) {
        throw new Error("发送验证码失败");
      }
      const verify = data.verifyOtp;
      setVerifyOtpFn(() => (args: { token: string }) => verify(args));
      setOtpSent(true);
      setMessage("验证码已发送");
    } catch (err) {
      setMessage(err instanceof Error ? err.message : "发送失败");
    } finally {
      setLoading(false);
    }
  };

  const handleVerifyOtp = async () => {
    if (!otp.trim() || !verifyOtpFn) {
      setMessage("请输入验证码");
      return;
    }
    setLoading(true);
    setMessage("");
    try {
      const { error } = await verifyOtpFn({ token: otp.trim() });
      if (error) {
        throw new Error("验证码错误或已过期");
      }
      await onSuccess();
    } catch (err) {
      setMessage(err instanceof Error ? err.message : "验证失败");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-modal-overlay">
      <div className="auth-modal" onClick={(event) => event.stopPropagation()}>
        <div className="auth-modal-header">
          <h2>登录 / 注册</h2>
          <button type="button" className="auth-modal-close" onClick={onClose} aria-label="关闭">
            x
          </button>
        </div>
        <p className="auth-modal-hint">
          免费次数用完后需登录才能继续使用 AI; 排盘、起卦等功能无需登录.
        </p>
        <div className="auth-tabs">
          <button
            type="button"
            className={tab === "password" ? "auth-tab active" : "auth-tab"}
            onClick={() => setTab("password")}
          >
            账号密码
          </button>
          <button
            type="button"
            className={tab === "phone" ? "auth-tab active" : "auth-tab"}
            onClick={() => setTab("phone")}
          >
            手机验证码
          </button>
        </div>

        {tab === "password" && (
          <div className="auth-form">
            <label>
              账号
              <input
                type="text"
                value={username}
                autoComplete="username"
                onChange={(event) => setUsername(event.target.value)}
                placeholder={loginAccountHint()}
              />
            </label>
            <p className="hint">手机验证码注册的用户请填手机号, 需先在个人中心设置密码</p>
            <label>
              密码
              <input
                type="password"
                value={password}
                autoComplete={isRegister ? "new-password" : "current-password"}
                onChange={(event) => setPassword(event.target.value)}
              />
            </label>
            <div className="auth-form-actions">
              <button type="button" className="primary-btn" disabled={loading} onClick={() => void handlePassword()}>
                {loading ? "登录中..." : "登录"}
              </button>
              <button
                type="button"
                className="secondary"
                disabled={loading}
                onClick={() => {
                  setIsRegister(true);
                  setTab("phone");
                  setMessage("请用手机验证码注册新账号");
                }}
              >
                没有账号? 用手机注册
              </button>
            </div>
          </div>
        )}

        {tab === "phone" && (
          <div className="auth-form">
            <label>
              手机号
              <input
                type="tel"
                value={phone}
                onChange={(event) => setPhone(event.target.value)}
                placeholder={phoneHint()}
                disabled={otpSent}
              />
            </label>
            {otpSent ? (
              <label>
                验证码
                <input type="text" value={otp} onChange={(event) => setOtp(event.target.value)} placeholder="6 位验证码" />
              </label>
            ) : null}
            <div className="auth-form-actions">
              {!otpSent ? (
                <button type="button" className="primary-btn" disabled={loading} onClick={() => void handleSendOtp()}>
                  {loading ? "发送中..." : "发送验证码"}
                </button>
              ) : (
                <button type="button" className="primary-btn" disabled={loading} onClick={() => void handleVerifyOtp()}>
                  {loading ? "验证中..." : "登录"}
                </button>
              )}
            </div>
          </div>
        )}

        {message ? <p className="auth-message">{message}</p> : null}
      </div>
    </div>
  );
}
