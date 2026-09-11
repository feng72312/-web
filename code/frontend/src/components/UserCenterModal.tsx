import { useEffect, useState } from "react";
import { X } from "lucide-react";

import { useAuth } from "../context/AuthContext";
import { getCloudbaseAuth } from "../services/cloudbaseClient";
import { isValidCnPhone, phoneHint, toCloudbasePhone } from "../utils/phoneFormat";

interface UserCenterModalProps {
  user: { id: string; username?: string; phone?: string };
  onClose: () => void;
}

type IdentityItem = {
  id?: string;
  provider?: string;
};

type ReauthUpdateUser = (attributes: {
  nonce: string;
  password?: string;
}) => Promise<{ data: unknown; error: unknown }>;

export function UserCenterModal({ user, onClose }: UserCenterModalProps) {
  const { signOut, refreshSession } = useAuth();
  const [identities, setIdentities] = useState<IdentityItem[]>([]);
  const [hasPassword, setHasPassword] = useState<boolean | null>(null);
  const [profilePhone, setProfilePhone] = useState<string | undefined>(user.phone);
  const [phone, setPhone] = useState("");
  const [otp, setOtp] = useState("");
  const [otpSent, setOtpSent] = useState(false);
  const [verifyOtpFn, setVerifyOtpFn] = useState<
    ((args: { token: string }) => Promise<{ data: unknown; error: unknown }>) | null
  >(null);
  const [oldPassword, setOldPassword] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [passwordOtp, setPasswordOtp] = useState("");
  const [passwordOtpSent, setPasswordOtpSent] = useState(false);
  const [reauthUpdateUser, setReauthUpdateUser] = useState<ReauthUpdateUser | null>(null);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState("");

  const boundPhone = profilePhone || user.phone;

  useEffect(() => {
    void (async () => {
      const auth = await getCloudbaseAuth();
      const [{ data: idData }, { data: userData }] = await Promise.all([
        auth.getUserIdentities(),
        auth.getUser(),
      ]);
      const list = (idData as { identities?: IdentityItem[] } | null)?.identities ?? [];
      setIdentities(list);
      const rawUser = (userData as { user?: { hasPassword?: boolean; phone?: string } } | null)?.user;
      setHasPassword(Boolean(rawUser?.hasPassword));
      if (typeof rawUser?.phone === "string" && rawUser.phone) {
        setProfilePhone(rawUser.phone);
      }
    })();
  }, []);

  const handleBindPhone = async () => {
    if (!isValidCnPhone(phone)) {
      setMessage(phoneHint());
      return;
    }
    setLoading(true);
    setMessage("");
    try {
      const auth = await getCloudbaseAuth();
      const { data, error } = await auth.signInWithOtp({
        phone: toCloudbasePhone(phone),
        options: { shouldCreateUser: false },
      });
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

  const handleVerifyBindPhone = async () => {
    if (!verifyOtpFn || !otp.trim()) {
      setMessage("请输入验证码");
      return;
    }
    setLoading(true);
    setMessage("");
    try {
      const { error } = await verifyOtpFn({ token: otp.trim() });
      if (error) {
        throw new Error("绑定失败, 请确认验证码");
      }
      await refreshSession();
      setMessage("手机号已绑定");
      setOtpSent(false);
      setOtp("");
      const auth = await getCloudbaseAuth();
      const { data } = await auth.getUser();
      const rawUser = (data as { user?: { phone?: string } } | null)?.user;
      if (typeof rawUser?.phone === "string") {
        setProfilePhone(rawUser.phone);
      }
    } catch (err) {
      setMessage(err instanceof Error ? err.message : "绑定失败");
    } finally {
      setLoading(false);
    }
  };

  const validateNewPasswordPair = (): string | null => {
    if (newPassword.length < 6) {
      return "新密码至少 6 位";
    }
    if (newPassword !== confirmPassword) {
      return "两次输入的新密码不一致";
    }
    return null;
  };

  const handleSendPasswordCode = async () => {
    const pairError = validateNewPasswordPair();
    if (pairError) {
      setMessage(pairError);
      return;
    }
    if (!boundPhone) {
      setMessage("请先绑定手机号后再设置密码");
      return;
    }
    setLoading(true);
    setMessage("");
    try {
      const auth = await getCloudbaseAuth();
      const { data, error } = await auth.reauthenticate();
      if (error || !data?.updateUser) {
        throw new Error("发送验证码失败, 请确认已绑定手机");
      }
      setReauthUpdateUser(() => data.updateUser as ReauthUpdateUser);
      setPasswordOtpSent(true);
      setMessage("验证码已发送到绑定手机");
    } catch (err) {
      setMessage(err instanceof Error ? err.message : "发送失败");
    } finally {
      setLoading(false);
    }
  };

  const handleConfirmSetPassword = async () => {
    const pairError = validateNewPasswordPair();
    if (pairError) {
      setMessage(pairError);
      return;
    }
    if (!passwordOtp.trim() || !reauthUpdateUser) {
      setMessage("请输入验证码");
      return;
    }
    setLoading(true);
    setMessage("");
    try {
      const { error } = await reauthUpdateUser({
        nonce: passwordOtp.trim(),
        password: newPassword,
      });
      if (error) {
        throw new Error("设置失败, 请检查验证码");
      }
      setHasPassword(true);
      setPasswordOtpSent(false);
      setPasswordOtp("");
      setNewPassword("");
      setConfirmPassword("");
      setReauthUpdateUser(null);
      setMessage("密码已设置, 可用手机号+密码登录");
      await refreshSession();
    } catch (err) {
      setMessage(err instanceof Error ? err.message : "设置失败");
    } finally {
      setLoading(false);
    }
  };

  const handleChangePassword = async () => {
    const pairError = validateNewPasswordPair();
    if (pairError) {
      setMessage(pairError);
      return;
    }
    if (!oldPassword) {
      setMessage("请输入当前密码");
      return;
    }
    setLoading(true);
    setMessage("");
    try {
      const auth = await getCloudbaseAuth();
      const { error } = await auth.resetPasswordForOld({
        old_password: oldPassword,
        new_password: newPassword,
      });
      if (error) {
        throw new Error(
          typeof error === "object" && error && "message" in error
            ? String((error as { message: string }).message)
            : "修改失败",
        );
      }
      setOldPassword("");
      setNewPassword("");
      setConfirmPassword("");
      setMessage("密码已修改");
    } catch (err) {
      setMessage(err instanceof Error ? err.message : "修改失败");
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = async () => {
    await signOut();
    onClose();
  };

  return (
    <div className="auth-modal-overlay">
      <div
        className="auth-modal user-center-modal"
        role="dialog"
        aria-modal="true"
        aria-labelledby="user-center-title"
        onClick={(event) => event.stopPropagation()}
      >
        <div className="auth-modal-header">
          <h2 id="user-center-title">个人中心</h2>
          <button type="button" className="auth-modal-close" onClick={onClose} aria-label="关闭">
            <X size={17} strokeWidth={1.8} aria-hidden="true" />
          </button>
        </div>
        <div className="user-center-info">
          <p>用户 ID: {user.id.slice(0, 8)}...</p>
          {user.username ? <p>用户名: {user.username}</p> : null}
          {boundPhone ? <p>手机: {boundPhone}</p> : <p>手机: 未绑定</p>}
          {hasPassword === false ? (
            <p className="hint">手机验证码登录的账号默认没有密码, 可在下方设置</p>
          ) : null}
        </div>
        <div className="user-center-section">
          <h3>已关联登录方式</h3>
          {identities.length === 0 ? (
            <p className="hint">暂无额外关联</p>
          ) : (
            <ul className="identity-list">
              {identities.map((item) => (
                <li key={item.id ?? item.provider}>{item.provider ?? item.id}</li>
              ))}
            </ul>
          )}
        </div>
        <div className="user-center-section auth-form">
          <h3>{hasPassword ? "修改密码" : "设置登录密码"}</h3>
          {hasPassword ? (
            <label>
              当前密码
              <input
                type="password"
                value={oldPassword}
                autoComplete="current-password"
                onChange={(event) => setOldPassword(event.target.value)}
              />
            </label>
          ) : null}
          <label>
            {hasPassword ? "新密码" : "密码"}
            <input
              type="password"
              value={newPassword}
              autoComplete="new-password"
              onChange={(event) => setNewPassword(event.target.value)}
            />
          </label>
          <label>
            确认密码
            <input
              type="password"
              value={confirmPassword}
              autoComplete="new-password"
              onChange={(event) => setConfirmPassword(event.target.value)}
            />
          </label>
          {hasPassword ? (
            <button type="button" className="secondary" disabled={loading} onClick={() => void handleChangePassword()}>
              {loading ? "处理中..." : "保存新密码"}
            </button>
          ) : (
            <>
              {passwordOtpSent ? (
                <label>
                  手机验证码
                  <input
                    type="text"
                    value={passwordOtp}
                    onChange={(event) => setPasswordOtp(event.target.value)}
                    placeholder="6 位验证码"
                  />
                </label>
              ) : null}
              <button
                type="button"
                className="secondary"
                disabled={loading}
                onClick={() => void (passwordOtpSent ? handleConfirmSetPassword() : handleSendPasswordCode())}
              >
                {loading ? "处理中..." : passwordOtpSent ? "确认设置密码" : "发送验证码并设置密码"}
              </button>
            </>
          )}
          {!hasPassword && boundPhone ? (
            <p className="hint">设置后在「账号密码」页填写本页显示的手机号(11位)和密码登录</p>
          ) : null}
        </div>
        {!boundPhone ? (
          <div className="user-center-section auth-form">
            <h3>绑定手机</h3>
            <input type="tel" value={phone} onChange={(event) => setPhone(event.target.value)} placeholder={phoneHint()} />
            {otpSent ? (
              <input type="text" value={otp} onChange={(event) => setOtp(event.target.value)} placeholder="验证码" />
            ) : null}
            <button
              type="button"
              className="secondary"
              disabled={loading}
              onClick={() => void (otpSent ? handleVerifyBindPhone() : handleBindPhone())}
            >
              {otpSent ? "确认绑定" : "发送验证码"}
            </button>
          </div>
        ) : null}
        {message ? <p className="auth-message">{message}</p> : null}
        <div className="auth-form-actions">
          <button type="button" className="secondary" onClick={() => void handleLogout()}>
            退出登录
          </button>
        </div>
      </div>
    </div>
  );
}
