/** Mainland China 11-digit mobile. International numbers reserved for later. */
const CN_PHONE_RE = /^1[3-9]\d{9}$/;

export function isValidCnPhone(value: string): boolean {
  return CN_PHONE_RE.test(value.trim());
}

/** CloudBase Web SDK phone field for CN numbers. */
export function toCloudbasePhone(value: string): string {
  const trimmed = value.trim();
  if (trimmed.startsWith("+")) {
    return trimmed;
  }
  if (CN_PHONE_RE.test(trimmed)) {
    return `+86${trimmed}`;
  }
  return trimmed;
}

export function phoneHint(): string {
  return "请输入 11 位大陆手机号";
}
