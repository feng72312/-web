import { useEffect, useRef, useState } from "react";
import { AnalysisPanels } from "../components/AnalysisPanels";
import { BirthForm } from "../components/BirthForm";
import { AppViewNav, type AppView } from "../components/AppViewNav";
import { InterpretModelPicker } from "../components/InterpretModelPicker";
import { InterpretStyleButtons } from "../components/InterpretStyleButtons";
import { ChatPanel } from "../components/ChatPanel";
import { InterpretBlock } from "../components/InterpretBlock";
import { RagExcerptList } from "../components/RagExcerptList";
import { FourPillars } from "../components/FourPillars";
import { LuckTimelineView } from "../components/LuckTimelineView";
import { PillarDetailView } from "../components/PillarDetailView";
import {
  fetchInterpret,
  fetchLuckTimeline,
  fetchPaipan,
  fetchRagSearch,
} from "../services/api";
import { fetchRagStatus, type RagStatus } from "../services/ragApi";
import { fetchChatStatus, initChatSession } from "../services/chatApi";
import { saveBaziChartRef } from "../utils/baziChartCache";
import { mergeInterpretSummary, type InterpretStyle } from "../utils/interpretStyle";
import type {
  ChatModelOption,
  Interpretation,
  LuckTimeline,
  PaipanRequest,
  PaipanResponse,
} from "../types/bazi";


export function BaziTab() {
  const [paipanLoading, setPaipanLoading] = useState(false);
  const [luckLoading, setLuckLoading] = useState(false);
  const [luckTimeline, setLuckTimeline] = useState<LuckTimeline | null>(null);
  const [ragLoading, setRagLoading] = useState(false);
  const [interpretStyleLoading, setInterpretStyleLoading] = useState<InterpretStyle | null>(null);
  const [lastInterpretStyle, setLastInterpretStyle] = useState<InterpretStyle | null>(null);
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
  const [chatEnabled, setChatEnabled] = useState(false);
  const [chatModels, setChatModels] = useState<ChatModelOption[]>([]);
  const [selectedModel, setSelectedModel] = useState("deepseek-chat");
  const [ragStatus, setRagStatus] = useState<RagStatus | null>(null);
  const [interpretQuestion, setInterpretQuestion] = useState(
    "请论此命主格局、用神喜忌与一生大势",
  );

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
      .catch(() => {
        setChatEnabled(false);
      });
  }, []);

  useEffect(() => {
    if (!result) {
      setRagStatus(null);
      return;
    }
    fetchRagStatus()
      .then(setRagStatus)
      .catch(() => setRagStatus(null));
  }, [result]);

  const startChatSession = (paipan: PaipanResponse) => {
    if (!chatEnabled) {
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
      !chatEnabled ||
      chatAgentId ||
      chatInitLoading ||
      chatAutoConnectDone.current
    ) {
      return;
    }
    chatAutoConnectDone.current = true;
    handleConnectChat();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [appView, result, chatEnabled, chatAgentId, chatInitLoading]);

  const handleSubmit = async (data: PaipanRequest) => {
    setPaipanLoading(true);
    setError("");
    setAppView("summary");
    setInterpretation(null);
    setChatAgentId(null);
    setChatConnectError("");
    chatAutoConnectDone.current = false;
    setLastInterpretStyle(null);
    setLuckTimeline(null);
    try {
      const paipan = await fetchPaipan(data);
      setResult(paipan);
      setLastRequest(data);
      saveBaziChartRef(paipan, data);
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
      fetchRagStatus().then(setRagStatus).catch(() => {});
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "知识库检索失败",
      );
    } finally {
      setRagLoading(false);
    }
  };

  const handleInterpret = async (style: InterpretStyle) => {
    if (!lastRequest) {
      return;
    }
    setInterpretStyleLoading(style);
    setLastInterpretStyle(style);
    setError("");
    try {
      const full = await fetchInterpret(lastRequest, {
        excerpts: interpretation?.excerpts,
        question: interpretQuestion.trim(),
        model: selectedModel,
        style,
      });
      setInterpretation((prev) => ({
        ...full.interpretation,
        ...mergeInterpretSummary(prev, full.interpretation.summary, style),
      }));
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
      setInterpretStyleLoading(null);
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
  const ragExcerpts =
    interpretation?.excerpts?.filter((item) => item.source !== "stub") ?? [];
  const hasRagExcerpts = ragExcerpts.length > 0;
  const ragReady = ragStatus?.serviceOk === true;

  const chatReady = Boolean(activeAgentId) && chatEnabled;

  const buildProfessionalCopyText = (): string => {
    if (!interpretation?.summaryProfessional) {
      return "";
    }
    if (
      interpretation.fusion &&
      interpretation.summaryProfessional === interpretation.fusion.merged.summary
    ) {
      const fusion = interpretation.fusion;
      const liuyaoMeta = [
        fusion.liuyao.benGuaName ? `本卦 ${fusion.liuyao.benGuaName}` : "",
        fusion.liuyao.yongShen ? `用神 ${fusion.liuyao.yongShen.yongShen}` : "",
        `倾向: ${fusion.liuyao.stance}`,
      ]
        .filter(Boolean)
        .join(" ");
      return [
        `综合结论\n${fusion.merged.summary}`,
        `八字判断 (倾向: ${fusion.bazi.stance})\n${fusion.bazi.summary}`,
        `六爻判断 (${liuyaoMeta})\n${fusion.liuyao.summary}`,
      ].join("\n\n");
    }
    return interpretation.summaryProfessional;
  };

  return (
    <>
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
              chatEnabled={chatEnabled}
              chatModels={chatModels}
              selectedModel={selectedModel}
              onModelChange={setSelectedModel}
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
              {ragStatus && !ragStatus.serviceOk && (
                <div className="error-box rag-status-box">
                  典籍库未就绪: {ragStatus.serviceMessage}
                  {ragStatus.provider === "stub" && (
                    <span>
                      {" "}
                      (请在 backend/.env 设置 BAZI_RAG_PROVIDER=http 并重启后端)
                    </span>
                  )}
                </div>
              )}
              {ragStatus?.serviceOk && (
                <p className="action-status">
                  典籍库已连接, 索引约 {ragStatus.chunks} 条
                </p>
              )}
              <label className="field-label" htmlFor="interpret-question">
                问事 (八字+六爻双通道解读)
              </label>
              <input
                id="interpret-question"
                className="text-input"
                type="text"
                value={interpretQuestion}
                onChange={(e) => setInterpretQuestion(e.target.value)}
                placeholder="例: 2010年是否离婚 / 论格局与一生大势"
                maxLength={200}
              />
              <InterpretModelPicker
                models={chatModels}
                value={selectedModel}
                onChange={setSelectedModel}
                chatEnabled={chatEnabled}
                disabled={interpretStyleLoading !== null}
              />
              <div className="action-row">
                <button
                  type="button"
                  className="secondary"
                  disabled={ragLoading || !lastRequest || !ragReady}
                  onClick={handleRagSearch}
                  title={ragReady ? "" : "请先启动 RAG 服务并重启后端"}
                >
                  {ragLoading ? "检索中..." : "检索知识库"}
                </button>
                <button
                  type="button"
                  className="secondary"
                  onClick={() => setAppView("chat")}
                >
                  打开 AI 对话
                </button>
              </div>
              <InterpretStyleButtons
                professionalLoading={interpretStyleLoading === "professional"}
                plainLoading={interpretStyleLoading === "plain"}
                disabled={!lastRequest}
                onProfessional={() => handleInterpret("professional")}
                onPlain={() => handleInterpret("plain")}
              />
              {hasRagExcerpts && interpretation?.query && (
                <p className="action-status">
                  已检索 {interpretation.excerpts.length} 条摘录
                  {interpretation.summaryProfessional || interpretation.summaryPlain
                    ? ", 已生成解读"
                    : ""}
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

            {(interpretation?.summaryProfessional ||
              interpretation?.summaryPlain ||
              interpretation?.summary) && (
              <section className="panel interpret-panel">
                <div className="interpret-header">
                  <h2>命理解读</h2>
                  <span className="interpret-badge">
                    {interpretation.fusion
                      ? interpretation.fusion.weightNote
                      : chatEnabled && interpretation.agentId
                        ? "AI 解读"
                        : "演示模式"}
                  </span>
                </div>
                {interpretation.summaryProfessional && (
                  <InterpretBlock title="命理师专用解读" copyText={buildProfessionalCopyText()}>
                    {interpretation.fusion &&
                    interpretation.summaryProfessional === interpretation.fusion.merged.summary ? (
                      <>
                        <h4 className="interpret-subhead">综合结论</h4>
                        <p className="interpret-summary">
                          {interpretation.fusion.merged.summary}
                        </p>
                        <h4 className="interpret-subhead">八字判断</h4>
                        <p className="interpret-channel-meta">
                          倾向: {interpretation.fusion.bazi.stance}
                        </p>
                        <p className="interpret-summary">
                          {interpretation.fusion.bazi.summary}
                        </p>
                        <h4 className="interpret-subhead">六爻判断</h4>
                        <p className="interpret-channel-meta">
                          {interpretation.fusion.liuyao.benGuaName &&
                            `本卦 ${interpretation.fusion.liuyao.benGuaName} `}
                          {interpretation.fusion.liuyao.yongShen &&
                            `用神 ${interpretation.fusion.liuyao.yongShen.yongShen} `}
                          倾向: {interpretation.fusion.liuyao.stance}
                        </p>
                        <p className="interpret-summary">
                          {interpretation.fusion.liuyao.summary}
                        </p>
                      </>
                    ) : (
                      <p className="interpret-summary">{interpretation.summaryProfessional}</p>
                    )}
                  </InterpretBlock>
                )}
                {interpretation.summaryPlain && (
                  <InterpretBlock title="AI深度解读" copyText={interpretation.summaryPlain}>
                    <p className="interpret-summary">{interpretation.summaryPlain}</p>
                  </InterpretBlock>
                )}
                {!interpretation.summaryProfessional &&
                  !interpretation.summaryPlain &&
                  interpretation.summary && (
                  <p className="interpret-summary">{interpretation.summary}</p>
                )}
                {interpretation.query && (
                  <details>
                    <summary>古籍索引</summary>
                    <p className="mono">{interpretation.query}</p>
                  </details>
                )}
                {ragExcerpts.length > 0 && (
                  <RagExcerptList excerpts={ragExcerpts} />
                )}
              </section>
            )}

            {interpretation && !interpretation.summary && hasRagExcerpts && (
              <section className="panel interpret-panel">
                <h2>典籍摘录</h2>
                {interpretation.query && (
                  <details open>
                    <summary>古籍索引</summary>
                    <p className="mono">{interpretation.query}</p>
                  </details>
                )}
                {ragExcerpts.length > 0 && (
                  <RagExcerptList excerpts={ragExcerpts} />
                )}
              </section>
            )}

          </div>
        )}
    </>
  );
}
