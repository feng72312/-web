import { useEffect, useRef, useState } from "react";
import { AnalysisPanels } from "./components/AnalysisPanels";
import { BirthForm } from "./components/BirthForm";
import { AppViewNav, type AppView } from "./components/AppViewNav";
import { ChatPanel } from "./components/ChatPanel";
import { FourPillars } from "./components/FourPillars";
import { LuckTimelineView } from "./components/LuckTimelineView";
import { PillarDetailView } from "./components/PillarDetailView";
import {
  fetchInterpret,
  fetchLuckTimeline,
  fetchPaipan,
  fetchRagSearch,
} from "./services/api";
import { fetchChatStatus, initChatSession } from "./services/chatApi";
import type {
  Interpretation,
  LuckTimeline,
  PaipanRequest,
  PaipanResponse,
} from "./types/bazi";
import "./styles/app.css";
import "./styles/chart-detail.css";


export default function App() {
  const [paipanLoading, setPaipanLoading] = useState(false);
  const [luckLoading, setLuckLoading] = useState(false);
  const [luckTimeline, setLuckTimeline] = useState<LuckTimeline | null>(null);
  const [ragLoading, setRagLoading] = useState(false);
  const [interpretLoading, setInterpretLoading] = useState(false);
  const [chatInitLoading, setChatInitLoading] = useState(false);
  const [chatConnectError, setChatConnectError] = useState("");
  const chatAutoConnectDone = useRef(false);
  const [error, setError] = useState("");
  const [result, setResult] = useState<PaipanResponse | null>(null);
  const [lastRequest, setLastRequest] = useState<PaipanRequest | null>(null);
  const [interpretation, setInterpretation] = useState<Interpretation | null>(
    null,
  );
  const [chatAgentId, setChatAgentId] = useState<string | null>(null);
  const [appView, setAppView] = useState<AppView>("summary");
  const [cursorEnabled, setCursorEnabled] = useState(false);
  const [cursorModel, setCursorModel] = useState("composer-2.5");

  useEffect(() => {
    fetchChatStatus()
      .then((status) => {
        setCursorEnabled(status.enabled);
        setCursorModel(status.model);
      })
      .catch(() => {
        setCursorEnabled(false);
      });
  }, []);

  const startChatSession = (paipan: PaipanResponse) => {
    if (!cursorEnabled) {
      return;
    }
    setChatInitLoading(true);
    setChatConnectError("");
    initChatSession(
      paipan.chart as unknown as Record<string, unknown>,
      paipan.sections as unknown as Array<Record<string, unknown>>,
    )
      .then((id) => {
        setChatAgentId(id);
        setChatConnectError("");
      })
      .catch((err) => {
        const msg =
          err instanceof Error ? err.message : "AI 对话连接失败";
        setChatConnectError(msg);
      })
      .finally(() => setChatInitLoading(false));
  };

  const handleConnectChat = () => {
    if (!result) {
      return;
    }
    startChatSession(result);
  };

  useEffect(() => {
    if (
      appView !== "chat" ||
      !result ||
      !cursorEnabled ||
      chatAgentId ||
      chatInitLoading ||
      chatAutoConnectDone.current
    ) {
      return;
    }
    chatAutoConnectDone.current = true;
    handleConnectChat();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [appView, result, cursorEnabled, chatAgentId, chatInitLoading]);

  const handleSubmit = async (data: PaipanRequest) => {
    setPaipanLoading(true);
    setError("");
    setAppView("summary");
    setInterpretation(null);
    setChatAgentId(null);
    setChatConnectError("");
    chatAutoConnectDone.current = false;
    setLuckTimeline(null);
    try {
      const paipan = await fetchPaipan(data);
      setResult(paipan);
      setLastRequest(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "请求失败");
      setResult(null);
      setLastRequest(null);
      setInterpretation(null);
      setChatAgentId(null);
      setLuckTimeline(null);
    } finally {
      setPaipanLoading(false);
    }
  };

  const handleRagSearch = async () => {
    if (!lastRequest) {
      return;
    }
    setRagLoading(true);
    setError("");
    try {
      const rag = await fetchRagSearch(lastRequest);
      setInterpretation((prev) => ({
        query: rag.query,
        excerpts: rag.excerpts,
        summary: prev?.summary ?? "",
        agentId: prev?.agentId ?? chatAgentId ?? undefined,
      }));
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "知识库检索失败",
      );
    } finally {
      setRagLoading(false);
    }
  };

  const handleInterpret = async () => {
    if (!lastRequest) {
      return;
    }
    setInterpretLoading(true);
    setError("");
    try {
      const full = await fetchInterpret(
        lastRequest,
        interpretation?.excerpts,
      );
      setInterpretation(full.interpretation);
      if (full.interpretation.agentId) {
        setChatAgentId(full.interpretation.agentId);
      }
    } catch (err) {
      setError(
        err instanceof Error
          ? `AI 解读失败: ${err.message}`
          : "AI 解读失败",
      );
    } finally {
      setInterpretLoading(false);
    }
  };

  const handleOpenLuck = async () => {
    if (luckTimeline) {
      setAppView("luck");
      return;
    }
    if (!lastRequest) {
      return;
    }
    setLuckLoading(true);
    setError("");
    try {
      const payload = await fetchLuckTimeline(lastRequest);
      setLuckTimeline(payload.luckTimeline);
      setAppView("luck");
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "大运流年加载失败",
      );
    } finally {
      setLuckLoading(false);
    }
  };

  const chart = result?.chart;
  const pillarDetail = chart?.pillarDetail;
  const activeAgentId = chatAgentId ?? interpretation?.agentId ?? null;
  const hasRagExcerpts =
    interpretation != null && interpretation.excerpts.length > 0;

  const chatReady = Boolean(activeAgentId) && cursorEnabled;

  return (
    <div className={`app-shell ${appView === "chat" ? "app-shell-chat" : ""}`}>
      <header className="app-header">
        <div>
          <p className="eyebrow">Bazi Platform MVP</p>
          <h1>八字排盘</h1>
          <p className="subtitle">模块化架构, 便于后续扩展典籍解读与更多分析模块</p>
        </div>
      </header>

      <main className="app-main">
        <BirthForm loading={paipanLoading} onSubmit={handleSubmit} />

        {error && <div className="error-box">{error}</div>}

        {result && (
          <AppViewNav
            activeView={appView}
            chatReady={chatReady}
            chatLoading={chatInitLoading}
            onSelectSummary={() => setAppView("summary")}
            onSelectChat={() => setAppView("chat")}
          />
        )}

        {result && appView === "chat" && (
          <ChatPanel
            layout="page"
            agentId={activeAgentId}
            chartName={chart?.input.name}
            dayMaster={chart?.dayMaster}
            cursorEnabled={cursorEnabled}
            cursorModel={cursorModel}
            sessionLoading={chatInitLoading}
            connectError={chatConnectError}
            onConnect={handleConnectChat}
            onBack={() => setAppView("summary")}
          />
        )}

        {result && appView === "pillars" && pillarDetail && (
          <PillarDetailView detail={pillarDetail} onBack={() => setAppView("summary")} />
        )}

        {result && appView === "luck" && luckLoading && (
          <section className="panel chart-detail">
            <p className="hint">正在加载大运流年, 首次约需 1 秒...</p>
          </section>
        )}

        {result && appView === "luck" && luckTimeline && !luckLoading && (
          <LuckTimelineView timeline={luckTimeline} onBack={() => setAppView("summary")} />
        )}

        {result && appView === "summary" && (
          <div className="result-area">
            {chart?.input.name && (
              <p className="result-name">命主: {chart.input.name}</p>
            )}

            <section className="panel action-panel">
              <h2>典籍与 AI</h2>
              <p className="action-hint">
                开始排盘仅计算命盘. 知识库检索与 AI 解读需单独触发, 避免阻塞排盘与对话.
              </p>
              <div className="action-row">
                <button
                  type="button"
                  className="secondary"
                  disabled={ragLoading || !lastRequest}
                  onClick={handleRagSearch}
                >
                  {ragLoading ? "检索中..." : "检索知识库"}
                </button>
                <button
                  type="button"
                  className="primary-btn"
                  disabled={interpretLoading || !lastRequest}
                  onClick={handleInterpret}
                >
                  {interpretLoading ? "生成中..." : "生成 AI 解读"}
                </button>
                <button
                  type="button"
                  className="secondary"
                  onClick={() => setAppView("chat")}
                >
                  打开 AI 对话
                </button>
              </div>
              {hasRagExcerpts && interpretation?.query && (
                <p className="action-status">
                  已检索 {interpretation.excerpts.length} 条摘录
                  {interpretation.summary ? ", 已生成解读" : ""}
                </p>
              )}
            </section>

            <section className="panel chart-panel">
              <h2>四柱排盘</h2>
              <FourPillars
                chart={chart}
                luckLoading={luckLoading}
                onOpenDetail={() => pillarDetail && setAppView("pillars")}
                onOpenLuck={handleOpenLuck}
              />
            </section>

            <AnalysisPanels chart={chart} sections={result.sections} />

            {interpretation?.summary && (
              <section className="panel interpret-panel">
                <div className="interpret-header">
                  <h2>命理解读</h2>
                  <span className="interpret-badge">
                    {cursorEnabled && interpretation.agentId ? "AI 解读" : "演示模式"}
                  </span>
                </div>
                <p className="interpret-summary">{interpretation.summary}</p>
                {interpretation.query && (
                  <details>
                    <summary>RAG 检索词</summary>
                    <p className="mono">{interpretation.query}</p>
                  </details>
                )}
                {interpretation.excerpts.map((item, idx) => (
                  <blockquote key={idx} className="excerpt">
                    <cite>{item.source}</cite>
                    <p>{item.excerpt}</p>
                  </blockquote>
                ))}
              </section>
            )}

            {interpretation && !interpretation.summary && hasRagExcerpts && (
              <section className="panel interpret-panel">
                <h2>典籍摘录</h2>
                {interpretation.query && (
                  <details open>
                    <summary>RAG 检索词</summary>
                    <p className="mono">{interpretation.query}</p>
                  </details>
                )}
                {interpretation.excerpts.map((item, idx) => (
                  <blockquote key={idx} className="excerpt">
                    <cite>{item.source}</cite>
                    <p>{item.excerpt}</p>
                  </blockquote>
                ))}
              </section>
            )}

          </div>
        )}
      </main>
    </div>
  );
}
