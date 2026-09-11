import { useCallback, useEffect, useState } from "react";
import { PersonaDialogueWorkspace } from "../components/persona/PersonaDialogueWorkspace";
import { PersonaHall } from "../components/persona/PersonaHall";
import {
  loadPersonaSessions,
  removePersonaSession,
  upsertPersonaSession,
} from "../components/persona/personaSessionStorage";
import { fetchChatStatus } from "../services/chatApi";
import {
  fetchPersona,
  fetchPersonas,
  initPersonaChatSession,
} from "../services/personaApi";
import type { ChatModelOption } from "../types/bazi";
import type {
  PersonaChatSession,
  PersonaCategory,
  PersonaDetail,
  PersonaSummary,
} from "../types/persona";

interface PersonaPageProps {
  isActive?: boolean;
}

export function PersonaPage({ isActive = true }: PersonaPageProps) {
  const [personas, setPersonas] = useState<PersonaSummary[]>([]);
  const [categories, setCategories] = useState<PersonaCategory[]>([]);
  const [catalogTotal, setCatalogTotal] = useState(0);
  const [sourceCommit, setSourceCommit] = useState("");
  const [selectedPersona, setSelectedPersona] = useState<PersonaDetail | null>(null);
  const [sessions, setSessions] = useState<PersonaChatSession[]>(() =>
    loadPersonaSessions(),
  );
  const [activeSession, setActiveSession] = useState<PersonaChatSession | null>(null);
  const [chatEnabled, setChatEnabled] = useState(false);
  const [chatModels, setChatModels] = useState<ChatModelOption[]>([]);
  const [selectedModel, setSelectedModel] = useState("deepseek-chat");
  const [loading, setLoading] = useState(true);
  const [loadingDetail, setLoadingDetail] = useState(false);
  const [sessionBusy, setSessionBusy] = useState(false);
  const [error, setError] = useState("");
  const [pendingMessage, setPendingMessage] = useState<string | null>(null);

  useEffect(() => {
    if (!isActive || personas.length > 0) {
      return;
    }
    setLoading(true);
    Promise.allSettled([fetchPersonas(), fetchChatStatus()])
      .then(([catalogResult, statusResult]) => {
        if (catalogResult.status === "rejected") {
          throw catalogResult.reason;
        }
        const catalog = catalogResult.value;
        setPersonas(catalog.personas);
        setCategories(catalog.categories);
        setCatalogTotal(catalog.total);
        setSourceCommit(catalog.sourceCommit);
        if (statusResult.status === "fulfilled") {
          const status = statusResult.value;
          setChatEnabled(status.enabled);
          setChatModels(status.models ?? []);
          if (status.model) {
            setSelectedModel(status.model);
          }
        } else {
          setChatEnabled(false);
        }
        const first = catalog.personas.find((item) => item.id === "wang-yangming") ?? catalog.personas[0];
        if (first) {
          return fetchPersona(first.id).then(setSelectedPersona);
        }
        return undefined;
      })
      .catch((err) => {
        setError(err instanceof Error ? err.message : "人物馆暂时无法打开，请稍后重试。")
      })
      .finally(() => setLoading(false));
  }, [isActive, personas.length]);

  const selectPersona = useCallback(async (personaId: string) => {
    if (selectedPersona?.id === personaId) {
      document.querySelector(".persona-preview")?.scrollIntoView({ behavior: "smooth" });
      return;
    }
    setLoadingDetail(true);
    setError("");
    try {
      const detail = await fetchPersona(personaId);
      setSelectedPersona(detail);
      window.requestAnimationFrame(() => {
        document.querySelector(".persona-preview")?.scrollIntoView({
          behavior: "smooth",
          block: "start",
        });
      });
    } catch (err) {
      setError(err instanceof Error ? err.message : "人物志读取失败。")
    } finally {
      setLoadingDetail(false);
    }
  }, [selectedPersona?.id]);

  const startSession = useCallback(async (
    persona: PersonaDetail,
    initialPrompt?: string,
  ) => {
    if (!chatEnabled) {
      setError("AI 对话服务尚未启用，人物志与来源仍可浏览。")
      return;
    }
    setSessionBusy(true);
    setError("");
    try {
      const result = await initPersonaChatSession({
        personaId: persona.id,
        initialPrompt,
      });
      const session: PersonaChatSession = {
        ...result,
        personaName: persona.name,
        createdAt: new Date().toISOString(),
      };
      setSelectedPersona(persona);
      setActiveSession(session);
      setSessions(upsertPersonaSession(session));
      setPendingMessage(initialPrompt ?? null);
      window.scrollTo({ top: 0, behavior: "auto" });
    } catch (err) {
      setError(err instanceof Error ? err.message : "对话创建失败，请稍后重试。")
    } finally {
      setSessionBusy(false);
    }
  }, [chatEnabled]);

  const selectSession = useCallback(async (session: PersonaChatSession) => {
    setError("");
    setPendingMessage(null);
    if (selectedPersona?.id !== session.personaId) {
      try {
        setSelectedPersona(await fetchPersona(session.personaId));
      } catch (err) {
        setError(err instanceof Error ? err.message : "人物志读取失败。")
        return;
      }
    }
    setActiveSession(session);
  }, [selectedPersona?.id]);

  const deleteSession = (agentId: string) => {
    const next = removePersonaSession(agentId);
    setSessions(next);
    if (activeSession?.agentId !== agentId) {
      return;
    }
    const replacement = next.find((item) => item.personaId === activeSession.personaId);
    setActiveSession(replacement ?? null);
  };

  if (loading) {
    return <div className="persona-page persona-page-loading" role="status">正在打开思想人物馆…</div>;
  }

  if (activeSession && selectedPersona) {
    return (
      <div className="persona-page">
        <PersonaDialogueWorkspace
          persona={selectedPersona}
          session={activeSession}
          sessions={sessions}
          chatEnabled={chatEnabled}
          chatModels={chatModels}
          selectedModel={selectedModel}
          pendingMessage={pendingMessage}
          onPendingMessageConsumed={() => setPendingMessage(null)}
          onModelChange={setSelectedModel}
          onBack={() => {
            setActiveSession(null);
            setPendingMessage(null);
            window.scrollTo({ top: 0, behavior: "auto" });
          }}
          onNewSession={() => void startSession(selectedPersona)}
          onSelectSession={(session) => void selectSession(session)}
          onDeleteSession={deleteSession}
          onPrompt={setPendingMessage}
        />
      </div>
    );
  }

  return (
    <div className="persona-page">
      <PersonaHall
        personas={personas}
        categories={categories}
        total={catalogTotal}
        sourceCommit={sourceCommit}
        selected={selectedPersona}
        loadingDetail={loadingDetail}
        busy={sessionBusy}
        error={error}
        sessions={sessions}
        onSelect={(personaId) => void selectPersona(personaId)}
        onStart={(persona, prompt) => void startSession(persona, prompt)}
        onResume={(session) => void selectSession(session)}
      />
    </div>
  );
}
