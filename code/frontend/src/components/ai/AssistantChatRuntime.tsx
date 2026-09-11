import { useCallback, useEffect, useRef, useState } from "react";
import {
  AssistantRuntimeProvider,
  useExternalStoreRuntime,
  type AppendMessage,
} from "@assistant-ui/react";
import { fetchChatHistory, streamChatMessage } from "../../services/chatApi";
import { isScopeRefusalMessage } from "../../utils/chatScope";
import { sanitizeInterpretText } from "../../utils/sanitizeInterpret";
import { AiThread } from "./AiThread";
import {
  buildWelcomeMessage,
  chatMessageToAiThreadMessage,
  convertAiThreadMessage,
  extractTextFromAppendMessage,
  newMessageId,
} from "./messageUtils";
import { loadThreadMessages, saveThreadMessages } from "./threadStorage";
import type { AiThreadMessage } from "./types";

interface AssistantChatRuntimeProps {
  agentId: string | null;
  chatEnabled: boolean;
  selectedModel: string;
  sessionTitle: string;
  welcomeHint?: string;
  placeholder?: string;
  scopeHint?: string;
  emptyTitle?: string;
  emptyDescription?: string;
  pendingMessage?: string | null;
  onPendingMessageConsumed?: () => void;
  onError?: (message: string) => void;
}

function AssistantChatRuntimeInner({
  agentId,
  chatEnabled,
  selectedModel,
  sessionTitle,
  welcomeHint,
  placeholder,
  scopeHint,
  emptyTitle,
  emptyDescription,
  pendingMessage,
  onPendingMessageConsumed,
  onError,
}: AssistantChatRuntimeProps) {
  const [messages, setMessages] = useState<AiThreadMessage[]>([]);
  const [isRunning, setIsRunning] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");
  const streamControllerRef = useRef<AbortController | null>(null);
  const lastAgentIdRef = useRef<string | null>(null);
  const pendingMessageRef = useRef<string | null>(null);

  const reportError = useCallback(
    (message: string) => {
      setError(message);
      onError?.(message);
    },
    [onError],
  );

  const sendUserMessage = useCallback(
    async (text: string) => {
      if (!agentId || !chatEnabled || !text.trim() || isRunning) {
        return;
      }

      const userMessage: AiThreadMessage = {
        id: newMessageId(),
        role: "user",
        content: text.trim(),
      };
      const assistantId = newMessageId();
      const assistantMessage: AiThreadMessage = {
        id: assistantId,
        role: "assistant",
        content: "",
        status: "running",
      };

      setMessages((prev) => [...prev, userMessage, assistantMessage]);
      setIsRunning(true);
      setError("");
      streamControllerRef.current?.abort();
      const controller = streamChatMessage(
        agentId,
        text.trim(),
        selectedModel,
        (delta) => {
          setMessages((prev) =>
            prev.map((item) =>
              item.id === assistantId
                ? { ...item, content: item.content + delta }
                : item,
            ),
          );
        },
        () => {
          setMessages((prev) =>
            prev.map((item) =>
              item.id === assistantId
                ? {
                    ...item,
                    status: "complete",
                    content: sanitizeInterpretText(item.content),
                  }
                : item,
            ),
          );
          setIsRunning(false);
          streamControllerRef.current = null;
        },
        (message) => {
          const scopeRefusal = isScopeRefusalMessage(message);
          setMessages((prev) =>
            prev.map((item) =>
              item.id === assistantId
                ? scopeRefusal
                  ? {
                      ...item,
                      status: "complete",
                      content: message,
                    }
                  : {
                      ...item,
                      status: "error",
                      errorText: message,
                      content: item.content || message,
                    }
                : item,
            ),
          );
          if (!scopeRefusal) {
            reportError(message);
          }
          setIsRunning(false);
          streamControllerRef.current = null;
        },
        () => {
          setMessages((prev) =>
            prev.map((item) =>
              item.id === assistantId && item.status === "running"
                ? {
                    ...item,
                    status: "complete",
                    content: item.content || "(已停止生成)",
                  }
                : item,
            ),
          );
          setIsRunning(false);
          streamControllerRef.current = null;
        },
      );
      streamControllerRef.current = controller;
    },
    [agentId, chatEnabled, isRunning, reportError, selectedModel],
  );

  useEffect(() => {
    pendingMessageRef.current = pendingMessage?.trim() || null;
  }, [pendingMessage]);

  useEffect(() => {
    const queued = pendingMessage?.trim();
    if (!queued || !agentId || !chatEnabled || isLoading || isRunning) {
      return;
    }
    if (lastAgentIdRef.current !== agentId) {
      return;
    }
    pendingMessageRef.current = null;
    onPendingMessageConsumed?.();
    void sendUserMessage(queued);
  }, [
    agentId,
    chatEnabled,
    isLoading,
    isRunning,
    onPendingMessageConsumed,
    pendingMessage,
    sendUserMessage,
  ]);

  useEffect(() => {
    if (!agentId || !chatEnabled) {
      if (!agentId) {
        lastAgentIdRef.current = null;
        setMessages([]);
      }
      return;
    }

    if (lastAgentIdRef.current === agentId) {
      return;
    }

    const previousId = lastAgentIdRef.current;
    lastAgentIdRef.current = agentId;
    if (previousId !== null) {
      setMessages([]);
    }

    let cancelled = false;
    setIsLoading(true);
    setError("");
    const cachedMessages = loadThreadMessages(agentId);

    fetchChatHistory(agentId)
      .then(async (history) => {
        if (cancelled) {
          return;
        }
        const serverMessages = history.map((item) =>
          chatMessageToAiThreadMessage({
            ...item,
            content:
              item.role === "assistant"
                ? sanitizeInterpretText(item.content)
                : item.content,
          }),
        );
        if (cachedMessages.length > serverMessages.length) {
          setMessages(cachedMessages);
        } else if (serverMessages.length > 0) {
          setMessages(serverMessages);
        } else {
          setMessages([buildWelcomeMessage(sessionTitle, welcomeHint)]);
        }

        const queued = pendingMessageRef.current;
        if (queued) {
          pendingMessageRef.current = null;
          onPendingMessageConsumed?.();
          await sendUserMessage(queued);
        }
      })
      .catch(() => {
        if (cancelled) {
          return;
        }
        setMessages(
          cachedMessages.length > 0
            ? cachedMessages
            : [buildWelcomeMessage(sessionTitle, welcomeHint)],
        );
        const queued = pendingMessageRef.current;
        if (queued) {
          pendingMessageRef.current = null;
          onPendingMessageConsumed?.();
          void sendUserMessage(queued);
        }
      })
      .finally(() => {
        if (!cancelled) {
          setIsLoading(false);
        }
      });

    return () => {
      cancelled = true;
    };
  }, [
    agentId,
    chatEnabled,
    onPendingMessageConsumed,
    sendUserMessage,
    sessionTitle,
    welcomeHint,
  ]);

  useEffect(() => {
    if (!agentId || messages.length === 0) {
      return;
    }
    saveThreadMessages(agentId, messages);
  }, [agentId, messages]);

  useEffect(() => {
    return () => {
      streamControllerRef.current?.abort();
    };
  }, []);

  const onNew = useCallback(
    async (message: AppendMessage) => {
      const text = extractTextFromAppendMessage(message);
      if (!text) {
        return;
      }
      await sendUserMessage(text);
    },
    [sendUserMessage],
  );

  const runtime = useExternalStoreRuntime({
    isRunning,
    isLoading,
    isDisabled: !chatEnabled || !agentId,
    messages,
    convertMessage: convertAiThreadMessage,
    onNew,
    onCancel: async () => {
      streamControllerRef.current?.abort();
      setIsRunning(false);
    },
  });

  return (
    <AssistantRuntimeProvider runtime={runtime}>
      <AiThread
        error={error}
        placeholder={placeholder}
        scopeHint={scopeHint}
        emptyTitle={emptyTitle}
        emptyDescription={emptyDescription}
      />
    </AssistantRuntimeProvider>
  );
}

export function AssistantChatRuntime(props: AssistantChatRuntimeProps) {
  if (!props.agentId) {
    return (
      <div className="ai-chat-thread-card ai-chat-thread-placeholder">
        <p>正在准备会话...</p>
      </div>
    );
  }

  return <AssistantChatRuntimeInner {...props} />;
}
