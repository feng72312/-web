export type AdminPageKey = "overview" | "keys" | "health";

export const KEY_TIERS = [
  { value: 10, label: "10 元 / 20 次", credits: 20 },
  { value: 20, label: "20 元 / 50 次", credits: 50 },
  { value: 50, label: "50 元 / 150 次", credits: 150 },
  { value: 100, label: "100 元 / 500 次", credits: 500 },
] as const;
