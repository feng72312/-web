import type { ChatMessage } from "../types/bazi";

export interface ChatExportMeta {
  chartName?: string;
  dayMaster?: string;
}

export function formatChatExport(
  messages: ChatMessage[],
  meta?: ChatExportMeta,
): string {
  const lines: string[] = ["AI 命理对话记录"];
  if (meta?.chartName) {
    lines.push(`命盘: ${meta.chartName}`);
  }
  if (meta?.dayMaster) {
    lines.push(`日主: ${meta.dayMaster}`);
  }
  const now = new Date();
  const pad = (n: number) => String(n).padStart(2, "0");
  lines.push(
    `导出时间: ${now.getFullYear()}-${pad(now.getMonth() + 1)}-${pad(now.getDate())} ${pad(now.getHours())}:${pad(now.getMinutes())}`,
  );
  lines.push("");

  for (const msg of messages) {
    const content = msg.content.trim();
    if (!content) {
      continue;
    }
    lines.push(msg.role === "user" ? "【用户】" : "【AI】");
    lines.push(content);
    lines.push("");
  }

  return lines.join("\n").trimEnd() + "\n";
}

export function downloadTextFile(content: string, filename: string): void {
  const blob = new Blob(["\ufeff", content], { type: "text/plain;charset=utf-8" });
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement("a");
  anchor.href = url;
  anchor.download = filename;
  anchor.click();
  URL.revokeObjectURL(url);
}

export function buildChatExportFilename(chartName?: string): string {
  const now = new Date();
  const pad = (n: number) => String(n).padStart(2, "0");
  const stamp = `${now.getFullYear()}${pad(now.getMonth() + 1)}${pad(now.getDate())}-${pad(now.getHours())}${pad(now.getMinutes())}`;
  const safeName = (chartName || "chat")
    .replace(/[\\/:*?"<>|]/g, "_")
    .slice(0, 24);
  return `AI对话-${safeName}-${stamp}.txt`;
}
