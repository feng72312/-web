import { useEffect, useRef, useState, type ReactNode } from "react";
import { createPortal } from "react-dom";
import { CopyTextButton } from "./CopyTextButton";
import { ModelSelector } from "./ModelSelector";
import { fetchChatHistory, streamChatMessage } from "../services/chatApi";
import {
  buildChatExportFilename,
  downloadTextFile,
  formatChatExport,
} from "../utils/exportChat";
import type { ChatMessage, ChatModelOption } from "../types/bazi";

interface ChatPanelProps {
  agentId: string | null;
  chartName?: string;
  dayMaster?: string;
  chatEnabled: boolean;
  chatModels: ChatModelOption[];
  selectedModel: string;
  onModelChange: (modelId: string) => void;
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
  chatEnabled,
  chatModels,
  selectedModel,
  onModelChange,
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
  const streamControllerRef = useRef<AbortController | null>(null);
  const isPage = layout === "page";
  const panelClass = isPage ? "panel chat-panel chat-panel-page" : "panel chat-panel";

  const wrapPageLayout = (content: ReactNode) => {
    if (!isPage) {
      return content;
    }
    return createPortal(<div className="chat-page-overlay">{content}</div>, document.body);
  };

  useEffect(() => {
    if (!isPage) {
      return;
    }
    document.documentElement.classList.add("chat-fullscreen-root");
    document.body.classList.add("chat-fullscreen");
    return () => {
      document.documentElement.classList.remove("chat-fullscreen-root");
      document.body.classList.remove("chat-fullscreen");
    };
  }, [isPage]);

  const welcomeMessage = (): ChatMessage => ({
    role: "assistant",
    content: chartName
      ? `已加载 ${chartName} 的命盘, 可追问格局, 用神, 大运等问题.`
      : "已加载当前命盘, 可追问格局, 用神, 大运等问题.",
  });

  useEffect(() => {
    if (!agentId || !chatEnabled) {
      if (!agentId) {
        lastAgentId.current = null;
      }
      return;
    }
    if (lastAgentId.current === agentId) {
      return;
    }

    const previousId = lastAgentId.current;
    lastAgentId.current = agentId;
    if (previousId !== null) {
      setMessages([]);
    }

    let cancelled = false;
    fetchChatHistory(agentId)
      .then((history) => {
        if (cancelled) {
          return;
        }
        if (history.length > 0) {
          setMessages(history);
        } else {
          setMessages([welcomeMessage()]);
        }
        setError("");
      })
      .catch(() => {
        if (cancelled) {
          return;
        }
        setMessages([welcomeMessage()]);
        setError("");
      });

    return () => {
      cancelled = true;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [agentId, chartName, chatEnabled]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  const canReedit = messages.some((msg) => msg.role === "user");

  const restoreLastUserMessage = () => {
    setMessages((prev) => {
      const next = [...prev];
      if (next.length > 0 && next[next.length - 1].role === "assistant") {
        next.pop();
      }
      if (next.length > 0 && next[next.length - 1].role === "user") {
        const lastUser = next.pop();
        if (lastUser) {
          setInput(lastUser.content);
        }
      }
      return next;
    });
    setError("");
  };

  const finishStream = () => {
    streamControllerRef.current = null;
    setLoading(false);
  };

  const handleStop = () => {
    streamControllerRef.current?.abort();
    restoreLastUserMessage();
    finishStream();
  };

  const handleReedit = () => {
    if (loading) {
      handleStop();
      return;
    }
    restoreLastUserMessage();
  };

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

    streamControllerRef.current?.abort();
    streamControllerRef.current = streamChatMessage(
      agentId,
      text,
      selectedModel,
      (delta) => {
        assistantText += delta;
        setMessages((prev) => {
          const next = [...prev];
          next[next.length - 1] = { role: "assistant", content: assistantText };
          return next;
        });
      },
      () => {
        finishStream();
      },
      (msg) => {
        setError(msg);
        finishStream();
      },
      () => {
        restoreLastUserMessage();
        finishStream();
      },
    );
  };

  const handleExport = () => {
    const exportable = messages.filter((msg) => msg.content.trim());
    if (exportable.length === 0) {
      return;
    }
    const content = formatChatExport(exportable, { chartName, dayMaster });
    downloadTextFile(content, buildChatExportFilename(chartName));
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
      <div className="chat-header-actions">
        {agentId && messages.some((msg) => msg.content.trim()) && (
          <button type="button" className="secondary" onClick={handleExport}>
            导出记录
          </button>
        )}
        <ModelSelector
          models={chatModels}
          value={selectedModel}
          disabled={loading}
          onChange={onModelChange}
        />
      </div>
    </div>
  );

  if (!chatEnabled) {
    return wrapPageLayout(
      <section className={panelClass}>
        {header}
        <p className="chat-hint">
          请在 backend/.env 中配置 BAZI_DEEPSEEK_API_KEY 或 BAZI_CURSOR_API_KEY
          后重启后端, 即可使用 AI 对话分析.
        </p>
      </section>,
    );
  }

  if (!agentId) {
    return wrapPageLayout(
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
      </section>,
    );
  }

  return wrapPageLayout(
    <section className={panelClass}>
      {header}

      <div className={isPage ? "chat-body-page" : "chat-body"}>
        <div className={isPage ? "chat-messages-page" : "chat-messages"}>
          {messages.map((msg, idx) => {
            const content =
              msg.content || (loading && idx === messages.length - 1 ? "..." : "");
            const canCopy = Boolean(msg.content.trim());
            return (
              <div
                key={idx}
                className={
                  msg.role === "user"
                    ? "chat-bubble-wrap chat-bubble-wrap-user"
                    : "chat-bubble-wrap chat-bubble-wrap-assistant"
                }
              >
                <div className="chat-bubble-toolbar">
                  {canCopy && <CopyTextButton text={msg.content} className="chat-copy-btn" />}
                </div>
                <div
                  className={
                    msg.role === "user" ? "chat-bubble-user" : "chat-bubble-assistant"
                  }
                >
                  {content}
                </div>
              </div>
            );
          })}
          <div ref={messagesEndRef} />
        </div>

        {error && <div className="error-box">{error}</div>}

        <div className="chat-input-row">
          <textarea
            className="chat-input"
            rows={isPage ? 3 : 2}
            placeholder="例如: 这个命盘用神是什么? 当前大运要注意什么?"
            value={input}
            onChange={(event) => setInput(event.target.value)}
            onKeyDown={(event) => {
              if (event.key === "Enter" && !event.shiftKey) {
                event.preventDefault();
                if (loading) {
                  return;
                }
                handleSend();
              }
            }}
          />
          <div className="chat-input-actions">
            <button
              type="button"
              className="secondary chat-action-btn"
              disabled={!canReedit}
              onClick={handleReedit}
            >
              重新编辑
            </button>
            {loading ? (
              <button
                type="button"
                className="primary-btn chat-send-btn"
                onClick={handleStop}
              >
                停止
              </button>
            ) : (
              <button
                type="button"
                className="primary-btn chat-send-btn"
                disabled={!input.trim()}
                onClick={handleSend}
              >
                发送
              </button>
            )}
          </div>
        </div>
      </div>
    </section>,
  );
}
