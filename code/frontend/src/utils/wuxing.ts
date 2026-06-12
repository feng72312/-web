export const WUXING_CLASS: Record<string, string> = {
  "\u6728": "wx-wood",
  "\u706b": "wx-fire",
  "\u571f": "wx-earth",
  "\u91d1": "wx-metal",
  "\u6c34": "wx-water",
};

export const GAN_WUXING: Record<string, string> = {
  "\u7532": "\u6728",
  "\u4e59": "\u6728",
  "\u4e19": "\u706b",
  "\u4e01": "\u706b",
  "\u620a": "\u571f",
  "\u5df1": "\u571f",
  "\u5e9a": "\u91d1",
  "\u8f9b": "\u91d1",
  "\u58ec": "\u6c34",
  "\u7678": "\u6c34",
};

export function wuxingClass(value: string): string {
  return WUXING_CLASS[value] || "";
}

export function ganWuxingClass(gan: string): string {
  return wuxingClass(GAN_WUXING[gan] || "");
}
