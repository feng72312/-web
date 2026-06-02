import { isValidCnPhone, toCloudbasePhone } from "./phoneFormat";
import { isValidUsername } from "./username";

export type PasswordLoginParams =
  | { phone: string; password: string }
  | { username: string; password: string };

export function loginAccountHint(): string {
  return "用户名或11位大陆手机号";
}

export function parsePasswordLoginInput(
  account: string,
  password: string,
): PasswordLoginParams | null {
  const trimmed = account.trim();
  if (isValidCnPhone(trimmed)) {
    return { phone: toCloudbasePhone(trimmed), password };
  }
  if (isValidUsername(trimmed)) {
    return { username: trimmed, password };
  }
  return null;
}

export function formatAuthErrorMessage(error: unknown): string {
  if (typeof error === "object" && error !== null) {
    const record = error as { message?: string; code?: string; error?: string };
    const code = String(record.code || record.error || "").toLowerCase();
    const message = String(record.message || "");
    if (code.includes("invalid_username_or_password") || message.includes("incorrect")) {
      return "账号或密码错误。手机验证码注册的用户请用手机号登录, 并确认已在个人中心设置密码";
    }
  }
  if (error instanceof Error && error.message) {
    return error.message;
  }
  return "登录失败";
}
