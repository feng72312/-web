import type { AppendMessage, ThreadMessageLike } from "@assistant-ui/react";
import type { ChatMessage } from "../../types/bazi";
import type { AiThreadMessage } from "./types";

export function newMessageId(): string {
  if (typeof crypto !== "undefined" && "randomUUID" in crypto) {
    return crypto.randomUUID();
  }
  return `${Date.now()}-${Math.random().toString(36).slice(2, 9)}`;
}

export function extractTextFromAppendMessage(message: AppendMessage): string {
  const content = message.content as string | ReadonlyArray<{ type: string; text?: string }>;
  if (typeof content === "string") {
    return content.trim();
  }
  return content
    .filter((part) => part.type === "text")
    .map((part) => (part.text ? String(part.text) : ""))
    .join("")
    .trim();
}

export function chatMessageToAiThreadMessage(
  message: ChatMessage,
  id?: string,
): AiThreadMessage {
  const role = message.role === "assistant" ? "assistant" : "user";
  const converted: AiThreadMessage = {
    id: id ?? newMessageId(),
    role,
    content: message.content,
  };
  if (role === "assistant") {
    converted.status = "complete";
  }
  return converted;
}

export function convertAiThreadMessage(message: AiThreadMessage): ThreadMessageLike {
  if (message.role === "user") {
    return {
      role: message.role,
      content: message.content,
      id: message.id,
    };
  }

  return {
    role: message.role,
    content: message.content,
    id: message.id,
    status:
      message.status === "running"
        ? { type: "running" }
        : message.status === "error"
          ? {
              type: "incomplete",
              reason: "error",
              error: message.errorText ?? "生成失败",
            }
          : { type: "complete", reason: "stop" },
  };
}

export function buildWelcomeMessage(title: string, hint?: string): AiThreadMessage {
  const content =
    hint?.trim() ||
    `欢迎来到「${title}」. 我是紫云命理天文馆的东方术数顾问, ` +
      "可解答八字, 紫微, 六爻, 梅花, 奇门, 塔罗等问题. 请先说明你的背景与想问的事.";
  return {
    id: newMessageId(),
    role: "assistant",
    content,
    status: "complete",
  };
}

export function buildFusionWelcomeMessage(labels: string[]): string {
  const joined = labels.join(", ");
  return (
    `已加载 ${labels.length} 个盘面: ${joined}. ` +
    "可追问同向点, 冲突点, 大运流年与宫位对应关系, 或请 AI 先做一轮融合总览."
  );
}
