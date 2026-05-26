export const WUXING_CLASS: Record<string, string> = {
  "\u6728": "wx-wood",
  "\u706b": "wx-fire",
  "\u571f": "wx-earth",
  "\u91d1": "wx-metal",
  "\u6c34": "wx-water",
};

export function wuxingClass(value: string): string {
  return WUXING_CLASS[value] || "";
}
