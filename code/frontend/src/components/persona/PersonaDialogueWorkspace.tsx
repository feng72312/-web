import { lazy, Suspense } from "react";
import {
  ArrowLeft,
  Clock3,
  MessageCircleMore,
  ShieldCheck,
  Trash2,
} from "lucide-react";
import { InterpretModelPicker } from "../InterpretModelPicker";
import { clearThreadMessages } from "../ai/threadStorage";
import type { ChatModelOption } from "../../types/bazi";
import type { PersonaChatSession, PersonaDetail } from "../../types/persona";
import { PersonaSources } from "./PersonaSources";

const AssistantChatRuntime = lazy(() =>
  import("../ai/AssistantChatRuntime").then((module) => ({
    default: module.AssistantChatRuntime,
  })),
);

interface PersonaDialogueWorkspaceProps {
  persona: PersonaDetail;
  session: PersonaChatSession;
  sessions: PersonaChatSession[];
  chatEnabled: boolean;
  chatModels: ChatModelOption[];
  selectedModel: string;
  pendingMessage: string | null;
  onPendingMessageConsumed: () => void;
  onModelChange: (modelId: string) => void;
  onBack: () => void;
  onNewSession: () => void;
  onSelectSession: (session: PersonaChatSession) => void;
  onDeleteSession: (agentId: string) => void;
  onPrompt: (prompt: string) => void;
}

export function PersonaDialogueWorkspace({
  persona,
  session,
  sessions,
  chatEnabled,
  chatModels,
  selectedModel,
  pendingMessage,
  onPendingMessageConsumed,
  onModelChange,
  onBack,
  onNewSession,
  onSelectSession,
  onDeleteSession,
  onPrompt,
}: PersonaDialogueWorkspaceProps) {
  const personaSessions = sessions.filter((item) => item.personaId === persona.id);
  const isHistorical = persona.interactionMode === "historical_simulation";
  const modeLabel = isHistorical ? "AI 历史思想模拟" : "公开思想框架 · 非本人";

  return (
    <div className="persona-dialogue-workspace">
      <aside className="persona-identity-panel">
        <button type="button" className="persona-back-button" onClick={onBack}>
          <ArrowLeft size={15} /> 返回人物馆
        </button>
        <div className="persona-identity-seal" aria-hidden="true">{persona.sealCharacter}</div>
        <p className="persona-kicker">{persona.era} · {persona.lifespan}</p>
        <h2>{persona.name}</h2>
        <p className="persona-identity-formal">{persona.formalName}</p>
        <p className="persona-identity-summary">{persona.summary}</p>
        <div className="persona-simulation-badge">
          <ShieldCheck size={15} /> {modeLabel}
        </div>

        <button type="button" className="persona-new-chat" onClick={onNewSession}>
          <MessageCircleMore size={16} /> 新建一席
        </button>

        <section className="persona-history" aria-labelledby="persona-history-title">
          <h3 id="persona-history-title"><Clock3 size={14} /> 最近对话</h3>
          <div>
            {personaSessions.map((item) => (
              <div className="persona-history-row" key={item.agentId}>
                <button
                  type="button"
                  className={item.agentId === session.agentId ? "is-active" : ""}
                  onClick={() => onSelectSession(item)}
                >
                  <strong>{item.title}</strong>
                  <span>{new Date(item.createdAt).toLocaleDateString("zh-CN")}</span>
                </button>
                <button
                  type="button"
                  className="persona-history-delete"
                  aria-label={`删除${item.title}`}
                  onClick={() => {
                    clearThreadMessages(item.agentId);
                    onDeleteSession(item.agentId);
                  }}
                >
                  <Trash2 size={13} />
                </button>
              </div>
            ))}
          </div>
        </section>
      </aside>

      <main className="persona-conversation-panel">
        <header className="persona-conversation-header">
          <div>
            <p className="persona-kicker">Dialogue · 思想框架讨论</p>
            <h2>{session.title}</h2>
          </div>
          <span><ShieldCheck size={14} /> {modeLabel}</span>
        </header>
        <div className="persona-disclosure compact">
          <ShieldCheck size={17} aria-hidden="true" />
          <span>{persona.disclosure}</span>
        </div>

        <details className="persona-mobile-sources">
          <summary>查看公开来源与引用边界</summary>
          <PersonaSources persona={persona} />
        </details>

        <Suspense
          fallback={<div className="ai-chat-thread-card persona-runtime-loading">正在备好笔墨…</div>}
        >
          <AssistantChatRuntime
            agentId={session.agentId}
            chatEnabled={chatEnabled}
            selectedModel={selectedModel}
            sessionTitle={session.title}
            welcomeHint={`${persona.disclosure}\n\n你可以直接说出眼下真实的难处。我会先辨清处境，再从${persona.themes.slice(0, 3).join("、")}的思想框架与你讨论。`}
            placeholder={isHistorical ? `向${persona.name}的思想模拟提问…` : `用${persona.name}的公开思想框架分析…`}
            scopeHint={isHistorical ? "这是基于史料的 AI 思想模拟；重要现实决策仍需结合事实与专业意见。" : "这是公开思想框架解读，不是本人发言或背书；重要决策请核对最新一手资料。"}
            emptyTitle={`从一个真实困惑开始`}
            emptyDescription="可以描述你的处境，也可以从右侧的开场问题进入。"
            pendingMessage={pendingMessage}
            onPendingMessageConsumed={onPendingMessageConsumed}
          />
        </Suspense>
      </main>

      <aside className="persona-evidence-panel">
        <InterpretModelPicker
          models={chatModels}
          value={selectedModel}
          onChange={onModelChange}
          chatEnabled={chatEnabled}
        />
        <section className="persona-workspace-starters">
          <p className="persona-kicker">Conversation Starters</p>
          <h3>从哪里谈起</h3>
          <div>
            {persona.starters.map((starter) => (
              <button type="button" key={starter.label} onClick={() => onPrompt(starter.prompt)}>
                <span>{starter.theme}</span>
                {starter.label}
              </button>
            ))}
          </div>
        </section>
        <PersonaSources persona={persona} />
      </aside>
    </div>
  );
}
