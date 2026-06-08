const FOOTER_PATTERN =
  /(以上内容由|由.+生成|DeepSeek|deepseek|ChatGPT|仅供娱乐|玄学虽有趣|生活更值得用心|愿你在现实中)/i;

export function sanitizeInterpretText(text: string): string {
  const lines = text.split(/\r?\n/);
  let end = lines.length;
  for (let i = 0; i < lines.length; i += 1) {
    const stripped = lines[i].trim();
    if (stripped === "---" || stripped === "***" || stripped === "___") {
      end = Math.min(end, i);
      continue;
    }
    if (FOOTER_PATTERN.test(stripped)) {
      end = Math.min(end, i);
    }
  }
  return lines.slice(0, end).join("\n").replace(/\n-{3,}\s*$/u, "").trim();
}
