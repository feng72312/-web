import { useEffect, useState } from "react";
import { AiChatWorkspace } from "../components/ai/AiChatWorkspace";
import { fetchChatStatus } from "../services/chatApi";
import type { ChatModelOption } from "../types/bazi";
import type { AiChatSession } from "../components/ai/types";

interface AiChatPageProps {
  onGoModules: () => void;
  pendingSession?: AiChatSession | null;
  onPendingSessionConsumed?: () => void;
  isActive?: boolean;
}

export function AiChatPage({
  onGoModules,
  pendingSession = null,
  onPendingSessionConsumed,
  isActive = true,
}: AiChatPageProps) {
  const [chatEnabled, setChatEnabled] = useState(false);
  const [chatModels, setChatModels] = useState<ChatModelOption[]>([]);
  const [selectedModel, setSelectedModel] = useState("deepseek-chat");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchChatStatus()
      .then((status) => {
        setChatEnabled(status.enabled);
        setChatModels(status.models ?? []);
        if (status.model) {
          setSelectedModel(status.model);
        } else if (status.models?.length) {
          setSelectedModel(status.models[0].id);
        }
      })
      .catch(() => setChatEnabled(false))
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="ai-chat-page">
        <p className="ai-chat-loading">正在检查 AI 服务...</p>
      </div>
    );
  }

  return (
    <div className="ai-chat-page">
      <AiChatWorkspace
        chatEnabled={chatEnabled}
        chatModels={chatModels}
        selectedModel={selectedModel}
        onModelChange={setSelectedModel}
        onGoModules={onGoModules}
        pendingSession={pendingSession}
        onPendingSessionConsumed={onPendingSessionConsumed}
        isActive={isActive}
      />
    </div>
  );
}
