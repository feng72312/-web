const USERNAME_RE = /^[a-zA-Z0-9_]{3,32}$/;

export function isValidUsername(value: string): boolean {
  return USERNAME_RE.test(value.trim());
}

export function usernameHint(): string {
  return "3-32 位, 仅字母数字下划线";
}
