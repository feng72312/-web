import { useCallback, useEffect, useMemo, useState } from "react";
import { InterpretModelPicker } from "../InterpretModelPicker";
import { initFusionChatSession, initGeneralChatSession } from "../../services/chatApi";
import { listProfiles } from "../../services/profileStorage";
import type { ChatModelOption, SavedProfile } from "../../types/bazi";
import type { GeneralChatScenario } from "../../services/chatApi";
import { AiChatContextPanel } from "./AiChatContextPanel";
import { AiChatSidebar } from "./AiChatSidebar";
import { AssistantChatRuntime } from "./AssistantChatRuntime";
import { buildFusionSessionTitle } from "./fusionSourceBuilder";
import {
  hydrateAllBaziProfilesFromSaved,
  loadBaziFusionSourceFromProfile,
  loadZiweiFusionSourceFromProfile,
} from "./fusionProfileImporter";
import { createFusionChatSessionRecord } from "./fusionSession";
import { loadFusionSources, removeFusionSource } from "./fusionSourceStorage";
import { buildFusionWelcomeMessage } from "./messageUtils";
import { buildGeneralChatTitle } from "./moduleSession";
import { getScenarioConfig } from "./scenarioConfig";
import {
  loadRecentSessions,
  removeRecentSession,
  upsertRecentSession,
} from "./sessionStorage";
import { clearThreadMessages } from "./threadStorage";
import type { AiChatSession } from "./types";

interface AiChatWorkspaceProps {
  chatEnabled: boolean;
  chatModels: ChatModelOption[];
  selectedModel: string;
  onModelChange: (modelId: string) => void;
  onGoModules: () => void;
  pendingSession?: AiChatSession | null;
  onPendingSessionConsumed?: () => void;
  isActive?: boolean;
}

function createSessionRecord(
  agentId: string,
  title: string,
  scenario: GeneralChatScenario,
  options?: { subtitle?: string },
): AiChatSession {
  const config = getScenarioConfig(scenario);
  return {
    agentId,
    title,
    scenario,
    createdAt: new Date().toISOString(),
    source: "general",
    subtitle: options?.subtitle ?? config?.label,
  };
}

export function AiChatWorkspace({
  chatEnabled,
  chatModels,
  selectedModel,
  onModelChange,
  onGoModules,
  pendingSession = null,
  onPendingSessionConsumed,
  isActive = true,
}: AiChatWorkspaceProps) {
  const [recentSessions, setRecentSessions] = useState<AiChatSession[]>(() =>
    loadRecentSessions(),
  );
  const [activeSession, setActiveSession] = useState<AiChatSession | null>(null);
  const [sessionBusy, setSessionBusy] = useState(false);
  const [initError, setInitError] = useState("");
  const [pendingMessage, setPendingMessage] = useState<string | null>(null);
  const [fusionSources, setFusionSources] = useState(() => loadFusionSources());
  const [selectedFusionIds, setSelectedFusionIds] = useState<string[]>([]);
  const [savedProfiles, setSavedProfiles] = useState<SavedProfile[]>(() => listProfiles());
  const [loadingProfileId, setLoadingProfileId] = useState<string | null>(null);
  const [loadingModuleId, setLoadingModuleId] = useState<string | null>(null);
  const [bulkProfileLoading, setBulkProfileLoading] = useState(false);
  const [fusionImportError, setFusionImportError] = useState("");

  const refreshFusionSources = useCallback(() => {
    setFusionSources(loadFusionSources());
    setSavedProfiles(listProfiles());
  }, []);

  const createSession = useCallback(
    async (
      scenario: GeneralChatScenario,
      options?: { initialPrompt?: string; title?: string },
    ) => {
      if (!chatEnabled) {
        return null;
      }
      setSessionBusy(true);
      setInitError("");
      try {
        const config = getScenarioConfig(scenario);
        const createdAt = new Date().toISOString();
        const sessionTitle = buildGeneralChatTitle(
          options?.title ?? config?.title ?? "AI 对话",
          {
            initialPrompt: options?.initialPrompt,
            createdAt,
          },
        );
        const result = await initGeneralChatSession({
          scenario,
          title: sessionTitle,
          initialPrompt: options?.initialPrompt,
        });
        const session = createSessionRecord(
          result.agentId,
          sessionTitle,
          result.scenario,
          { subtitle: config?.label },
        );
        session.createdAt = createdAt;
        setActiveSession(session);
        setRecentSessions(upsertRecentSession(session));
        return session;
      } catch (err) {
        const message =
          err instanceof Error ? err.message : "创建会话失败, 请稍后重试.";
        setInitError(message);
        return null;
      } finally {
        setSessionBusy(false);
      }
    },
    [chatEnabled],
  );

  const handleCreateFusionSession = useCallback(async () => {
    if (!chatEnabled || selectedFusionIds.length < 2) {
      return;
    }
    const selectedSources = fusionSources.filter((item) =>
      selectedFusionIds.includes(item.sourceId),
    );
    if (selectedSources.length < 2) {
      return;
    }
    setSessionBusy(true);
    setInitError("");
    try {
      const title = buildFusionSessionTitle(selectedSources);
      const result = await initFusionChatSession({
        title,
        sources: selectedSources.map((item) => ({
          moduleId: item.moduleId,
          moduleLabel: item.moduleLabel,
          title: item.title,
          question: item.question,
          chartSnapshot: item.chartSnapshot,
          summaryPlain: item.summaryPlain,
          summaryProfessional: item.summaryProfessional,
          createdAt: item.createdAt,
        })),
      });
      const session = createFusionChatSessionRecord(
        result.agentId,
        selectedSources,
        result.title,
      );
      clearThreadMessages(result.agentId);
      setActiveSession(session);
      setRecentSessions(upsertRecentSession(session));
      setSelectedFusionIds([]);
    } catch (err) {
      const message =
        err instanceof Error ? err.message : "创建融合会话失败, 请稍后重试.";
      setInitError(message);
    } finally {
      setSessionBusy(false);
    }
  }, [chatEnabled, fusionSources, selectedFusionIds]);

  useEffect(() => {
    if (!pendingSession) {
      return;
    }
    setActiveSession(pendingSession);
    setRecentSessions(upsertRecentSession(pendingSession));
    setInitError("");
    setPendingMessage(null);
    refreshFusionSources();
    onPendingSessionConsumed?.();
  }, [onPendingSessionConsumed, pendingSession, refreshFusionSources]);

  useEffect(() => {
    if (!isActive) {
      return;
    }
    refreshFusionSources();
  }, [isActive, refreshFusionSources]);

  useEffect(() => {
    if (!isActive) {
      return;
    }
    const onFocus = () => refreshFusionSources();
    window.addEventListener("focus", onFocus);
    return () => window.removeEventListener("focus", onFocus);
  }, [isActive, refreshFusionSources]);

  const handleLoadProfileBazi = useCallback(
    async (profile: SavedProfile) => {
      setLoadingProfileId(profile.id);
      setLoadingModuleId("01");
      setFusionImportError("");
      try {
        await loadBaziFusionSourceFromProfile(profile);
        refreshFusionSources();
      } catch (err) {
        setFusionImportError(
          err instanceof Error ? err.message : "加载八字盘失败, 请稍后重试.",
        );
      } finally {
        setLoadingProfileId(null);
        setLoadingModuleId(null);
      }
    },
    [refreshFusionSources],
  );

  const handleLoadProfileZiwei = useCallback(
    async (profile: SavedProfile) => {
      setLoadingProfileId(profile.id);
      setLoadingModuleId("11");
      setFusionImportError("");
      try {
        await loadZiweiFusionSourceFromProfile(profile);
        refreshFusionSources();
      } catch (err) {
        setFusionImportError(
          err instanceof Error ? err.message : "加载紫微盘失败, 请稍后重试.",
        );
      } finally {
        setLoadingProfileId(null);
        setLoadingModuleId(null);
      }
    },
    [refreshFusionSources],
  );

  const handleLoadAllProfileBazi = useCallback(async () => {
    setBulkProfileLoading(true);
    setFusionImportError("");
    try {
      await hydrateAllBaziProfilesFromSaved();
      refreshFusionSources();
    } catch (err) {
      setFusionImportError(
        err instanceof Error ? err.message : "批量加载八字盘失败, 请稍后重试.",
      );
    } finally {
      setBulkProfileLoading(false);
    }
  }, [refreshFusionSources]);

  useEffect(() => {
    if (!chatEnabled || activeSession || sessionBusy || pendingSession) {
      return;
    }
    const stored = loadRecentSessions();
    if (stored.length > 0) {
      setActiveSession(stored[0]);
      setRecentSessions(stored);
      return;
    }
    void createSession("general");
  }, [activeSession, chatEnabled, createSession, pendingSession, sessionBusy]);

  const handleNewChat = () => {
    void createSession("general");
  };

  const handleSelectScenario = (scenario: GeneralChatScenario) => {
    void createSession(scenario);
  };

  const handleSelectSession = (session: AiChatSession) => {
    setActiveSession(session);
    setInitError("");
    setPendingMessage(null);
  };

  const handleDeleteSession = (agentId: string) => {
    clearThreadMessages(agentId);
    const nextSessions = removeRecentSession(agentId);
    setRecentSessions(nextSessions);
    if (activeSession?.agentId !== agentId) {
      return;
    }
    setPendingMessage(null);
    setInitError("");
    if (nextSessions.length > 0) {
      setActiveSession(nextSessions[0]);
      return;
    }
    setActiveSession(null);
    if (chatEnabled && !sessionBusy) {
      void createSession("general");
    }
  };

  const handleToggleFusionSource = (sourceId: string) => {
    setSelectedFusionIds((prev) =>
      prev.includes(sourceId)
        ? prev.filter((id) => id !== sourceId)
        : [...prev, sourceId],
    );
  };

  const handleRemoveFusionSource = (sourceId: string) => {
    setFusionSources(removeFusionSource(sourceId));
    setSelectedFusionIds((prev) => prev.filter((id) => id !== sourceId));
  };

  const handleQuickPrompt = (prompt: string) => {
    if (!chatEnabled || sessionBusy) {
      return;
    }
    if (!activeSession) {
      setPendingMessage(prompt);
      void createSession("general", { initialPrompt: prompt }).then((session) => {
        if (session) {
          setPendingMessage(prompt);
        }
      });
      return;
    }
    setPendingMessage(prompt);
  };

  const welcomeHint = useMemo(() => {
    if (activeSession?.source !== "fusion" || !activeSession.fusionSourceLabels?.length) {
      return undefined;
    }
    return buildFusionWelcomeMessage(activeSession.fusionSourceLabels);
  }, [activeSession]);

  if (!chatEnabled) {
    return (
      <div className="ai-chat-disabled">
        <section className="ai-chat-disabled-card">
          <h3>AI 服务未启用</h3>
          <p>
            请检查云托管 bazi-api 与 DeepSeek 或 Cursor 配置, 启用后刷新页面即可使用通用术数对话.
          </p>
          <InterpretModelPicker
            models={chatModels}
            value={selectedModel}
            onChange={onModelChange}
            chatEnabled={false}
          />
          <button type="button" className="product-gold-button" onClick={onGoModules}>
            前往预测模块
          </button>
        </section>
      </div>
    );
  }

  return (
    <div className="ai-chat-workspace">
      <AiChatSidebar
        activeScenario={activeSession?.scenario ?? "general"}
        recentSessions={recentSessions}
        activeAgentId={activeSession?.agentId ?? null}
        disabled={sessionBusy}
        savedProfiles={savedProfiles}
        loadingProfileId={loadingProfileId}
        loadingModuleId={loadingModuleId}
        bulkProfileLoading={bulkProfileLoading}
        onNewChat={handleNewChat}
        onSelectScenario={handleSelectScenario}
        onSelectSession={handleSelectSession}
        onDeleteSession={handleDeleteSession}
        onLoadProfileBazi={(profile) => void handleLoadProfileBazi(profile)}
        onLoadProfileZiwei={(profile) => void handleLoadProfileZiwei(profile)}
        onLoadAllProfileBazi={() => void handleLoadAllProfileBazi()}
      />

      <main className="ai-chat-main">
        <header className="ai-chat-main-header">
          <div>
            <p className="product-eyebrow">AI Oracle Desk</p>
            <h2>{activeSession?.title ?? "AI 对话工作台"}</h2>
          </div>
          {sessionBusy ? <span className="ai-chat-main-status">准备会话中...</span> : null}
        </header>
        {initError ? <p className="ai-chat-init-error">{initError}</p> : null}
        {fusionImportError ? <p className="ai-chat-init-error">{fusionImportError}</p> : null}
        <AssistantChatRuntime
          agentId={activeSession?.agentId ?? null}
          chatEnabled={chatEnabled}
          selectedModel={selectedModel}
          sessionTitle={activeSession?.title ?? "通用术数顾问"}
          welcomeHint={welcomeHint}
          pendingMessage={pendingMessage}
          onPendingMessageConsumed={() => setPendingMessage(null)}
        />
      </main>

      <AiChatContextPanel
        chatEnabled={chatEnabled}
        chatModels={chatModels}
        selectedModel={selectedModel}
        onModelChange={onModelChange}
        activeScenario={activeSession?.scenario ?? "general"}
        sessionTitle={activeSession?.title ?? "通用术数顾问"}
        sessionSource={activeSession?.source ?? "general"}
        sessionBusy={sessionBusy}
        fusionSources={fusionSources}
        selectedFusionIds={selectedFusionIds}
        fusionImportBusy={bulkProfileLoading || Boolean(loadingProfileId)}
        onToggleFusionSource={handleToggleFusionSource}
        onRemoveFusionSource={handleRemoveFusionSource}
        onCreateFusionSession={() => void handleCreateFusionSession()}
        onQuickPrompt={handleQuickPrompt}
        onGoModules={onGoModules}
      />
    </div>
  );
}
