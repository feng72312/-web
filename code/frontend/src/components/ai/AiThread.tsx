import {
  AuiIf,
  ComposerPrimitive,
  MessagePrimitive,
  ThreadPrimitive,
} from "@assistant-ui/react";

interface AiThreadProps {
  error?: string;
  placeholder?: string;
}

function UserMessage() {
  return (
    <MessagePrimitive.Root className="ai-chat-message ai-chat-message-user">
      <div className="ai-chat-message-content">
        <MessagePrimitive.Content />
      </div>
    </MessagePrimitive.Root>
  );
}

function AssistantMessage() {
  return (
    <MessagePrimitive.Root className="ai-chat-message ai-chat-message-assistant">
      <div className="ai-chat-message-content">
        <MessagePrimitive.Content />
      </div>
      <div className="ai-chat-message-error">
        <MessagePrimitive.Error />
      </div>
    </MessagePrimitive.Root>
  );
}

export function AiThread({ error = "", placeholder }: AiThreadProps) {
  return (
    <div className="ai-chat-thread-card">
      {error ? <p className="ai-chat-thread-error">{error}</p> : null}
      <ThreadPrimitive.Root className="ai-chat-thread-root">
        <ThreadPrimitive.Viewport className="ai-chat-thread-viewport">
          <AuiIf condition={(state) => state.thread.isEmpty}>
            <div className="ai-chat-thread-empty">
              <p>输入问题开始对话, 或从右侧选择快捷问题.</p>
            </div>
          </AuiIf>
          <ThreadPrimitive.Messages
            components={{
              UserMessage,
              AssistantMessage,
            }}
          />
          <ThreadPrimitive.ViewportFooter className="ai-chat-thread-footer">
            <ComposerPrimitive.Root className="ai-chat-composer">
              <ComposerPrimitive.Input
                className="ai-chat-composer-input"
                placeholder={placeholder ?? "输入预测、命理、占卜或问事相关问题..."}
                rows={1}
                autoFocus
              />
              <p className="ai-chat-scope-hint">
                仅支持预测、命理、占卜、排盘与问事相关咨询.
              </p>
              <div className="ai-chat-composer-actions">
                <AuiIf condition={(state) => state.thread.isRunning}>
                  <ComposerPrimitive.Cancel className="ai-chat-composer-cancel">
                    停止
                  </ComposerPrimitive.Cancel>
                </AuiIf>
                <AuiIf condition={(state) => !state.thread.isRunning}>
                  <ComposerPrimitive.Send className="ai-chat-composer-send">
                    发送
                  </ComposerPrimitive.Send>
                </AuiIf>
              </div>
            </ComposerPrimitive.Root>
          </ThreadPrimitive.ViewportFooter>
        </ThreadPrimitive.Viewport>
      </ThreadPrimitive.Root>
    </div>
  );
}
