import { useEffect, useRef, useState } from "react";
import { streamChatMessage } from "../services/chatApi";
import type { ChatMessage } from "../types/bazi";

interface ChatPanelProps {
  agentId: string | null;
  chartName?: string;
  dayMaster?: string;
  cursorEnabled: boolean;
  cursorModel: string;
  sessionLoading?: boolean;
  layout?: "embedded" | "page";
  onBack?: () => void;
  onConnect?: () => void;
  connectError?: string;
}

export function ChatPanel({
  agentId,
  chartName,
  dayMaster,
  cursorEnabled,
  cursorModel,
  sessionLoading = false,
  layout = "embedded",
  onBack,
  onConnect,
  connectError = "",
}: ChatPanelProps) {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const lastAgentId = useRef<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement | null>(null);
  const isPage = layout === "page";
  const panelClass = isPage ? "panel chat-panel chat-panel-page" : "panel chat-panel";

  useEffect(() => {
    if (!agentId || !cursorEnabled) {
      return;
    }
    if (lastAgentId.current === agentId) {
      return;
    }
    lastAgentId.current = agentId;
    setMessages([
      {
        role: "assistant",
        content: chartName
          ? `已加载 ${chartName} 的命盘, 可追问格局, 用神, 大运等问题.`
          : "已加载当前命盘, 可追问格局, 用神, 大运等问题.",
      },
    ]);
    setError("");
  }, [agentId, chartName, cursorEnabled]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  const handleSend = () => {
    const text = input.trim();
    if (!text || !agentId || loading) {
      return;
    }

    setInput("");
    setError("");
    setLoading(true);
    setMessages((prev) => [...prev, { role: "user", content: text }]);

    let assistantText = "";
    setMessages((prev) => [...prev, { role: "assistant", content: "" }]);

    streamChatMessage(
      agentId,
      text,
      (delta) => {
        assistantText += delta;
        setMessages((prev) => {
          const next = [...prev];
          next[next.length - 1] = { role: "assistant", content: assistantText };
          return next;
        });
      },
      () => {
        setLoading(false);
      },
      (msg) => {
        setError(msg);
        setLoading(false);
      },
    );
  };

  const header = (
    <div className="chat-header">
      <div className="chat-header-main">
        {isPage && onBack && (
          <button type="button" className="secondary back-btn" onClick={onBack}>
            返回命盘
          </button>
        )}
        <div>
          <h2>AI 命理对话</h2>
          {isPage && chartName && (
            <p className="chat-subtitle">
              {chartName}
              {dayMaster ? ` / 日主 ${dayMaster}` : ""}
            </p>
          )}
        </div>
      </div>
      <span className="chat-model">{cursorModel}</span>
    </div>
  );

  if (!cursorEnabled) {
    return (
      <section className={panelClass}>
        {header}
        <p className="chat-hint">
          请在 backend/.env 中配置 BAZI_CURSOR_API_KEY 后重启后端, 即可使用 Composer
          对话分析.
        </p>
      </section>
    );
  }

  if (!agentId) {
    return (
      <section className={panelClass}>
        {header}
        <div className="chat-empty">
          <p className="chat-hint">
            {sessionLoading
              ? "正在连接 AI 会话..."
              : "请先完成排盘, 再点击下方按钮连接 AI 对话."}
          </p>
          {connectError && <div className="error-box">{connectError}</div>}
          {onConnect && (
            <button
              type="button"
              className="primary-btn"
              disabled={sessionLoading}
              onClick={onConnect}
            >
              {sessionLoading ? "连接中..." : "连接 AI"}
            </button>
          )}
        </div>
      </section>
    );
  }

  return (
    <section className={panelClass}>
      {header}

      <div className={isPage ? "chat-body-page" : "chat-body"}>
        <div className={isPage ? "chat-messages chat-messages-page" : "chat-messages"}>
          {messages.map((msg, idx) => (
            <div
              key={idx}
              className={
                msg.role === "user" ? "chat-bubble-user" : "chat-bubble-assistant"
              }
            >
              {msg.content || (loading && idx === messages.length - 1 ? "..." : "")}
            </div>
          ))}
          <div ref={messagesEndRef} />
        </div>

        {error && <div className="error-box">{error}</div>}

        <div className="chat-input-row">
          <textarea
            className="chat-input"
            rows={isPage ? 4 : 2}
            placeholder="例如: 这个命盘用神是什么? 当前大运要注意什么?"
            value={input}
            disabled={loading}
            onChange={(event) => setInput(event.target.value)}
            onKeyDown={(event) => {
              if (event.key === "Enter" && !event.shiftKey) {
                event.preventDefault();
                handleSend();
              }
            }}
          />
          <button
            type="button"
            className="primary-btn chat-send-btn"
            disabled={loading || !input.trim()}
            onClick={handleSend}
          >
            {loading ? "生成中..." : "发送"}
          </button>
        </div>
      </div>
    </section>
  );
}
