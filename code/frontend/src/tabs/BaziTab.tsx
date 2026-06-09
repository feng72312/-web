import { useEffect, useRef, useState } from "react";
import { useAuth } from "../context/AuthContext";
import { AnalysisPanels } from "../components/AnalysisPanels";
import { BirthForm } from "../components/BirthForm";
import { AppViewNav, type AppView } from "../components/AppViewNav";
import { InterpretModelPicker } from "../components/InterpretModelPicker";
import { InterpretStyleButtons } from "../components/InterpretStyleButtons";
import { SceneTemplatePicker } from "../components/SceneTemplatePicker";
import { ReportTimelinePanel } from "../components/ReportTimelinePanel";
import { GrowthMetricsPanel } from "../components/GrowthMetricsPanel";
import { FusionChannelsPanel } from "../components/FusionChannelsPanel";
import { InterpretMarkdown } from "../components/InterpretMarkdown";
import { appendTimelineEntry } from "../services/reportTimeline";
import { ChatPanel } from "../components/ChatPanel";
import { InterpretBlock } from "../components/InterpretBlock";
import { ChannelRagEvidence } from "../components/ChannelRagEvidence";
import { RagExcerptList } from "../components/RagExcerptList";
import { FourPillars } from "../components/FourPillars";
import { LuckTimelineView } from "../components/LuckTimelineView";
import { PillarDetailView } from "../components/PillarDetailView";
import {
  fetchInterpret,
  fetchLuckTimeline,
  fetchPaipan,
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
  const { runWithAuth } = useAuth();
  const [paipanLoading, setPaipanLoading] = useState(false);
  const [luckLoading, setLuckLoading] = useState(false);
  const [luckTimeline, setLuckTimeline] = useState<LuckTimeline | null>(null);
  const [interpretStyleLoading, setInterpretStyleLoading] = useState<InterpretStyle | null>(null);
  const [, setLastInterpretStyle] = useState<InterpretStyle | null>(null);
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
  const [fusionMode, setFusionMode] = useState<"bazi_liuyao" | "bazi_ziwei" | "triple">(
    "bazi_liuyao",
  );
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
    runWithAuth(() => startChatSession(result));
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

  useEffect(() => {
    const onAuthCancelled = () => setInterpretStyleLoading(null);
    window.addEventListener("zy-auth-cancelled", onAuthCancelled);
    return () => window.removeEventListener("zy-auth-cancelled", onAuthCancelled);
  }, []);

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
        fusionMode,
      });
      setInterpretation((prev) => {
        const mergedInterp = {
          ...full.interpretation,
          ...mergeInterpretSummary(prev, full.interpretation.summary, style),
        };
        appendTimelineEntry({
          moduleId: "01",
          moduleLabel: "八字命理",
          question: interpretQuestion.trim(),
          interpretation: mergedInterp,
        });
        return mergedInterp;
      });
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
  const chatReady = Boolean(activeAgentId) && chatEnabled;

  const buildProfessionalCopyText = (): string => {
    if (!interpretation?.summaryProfessional) {
      return "";
    }
    if (
      interpretation.tripleFusion &&
      interpretation.summaryProfessional === interpretation.tripleFusion.merged.summary
    ) {
      const t = interpretation.tripleFusion;
      return [
        `综合结论\n${t.merged.summary}`,
        `八字 (${t.bazi.stance})\n${t.bazi.summary}`,
        `紫微 (${t.ziwei.stance})\n${t.ziwei.summary}`,
        `星命 (${t.xingming.stance})\n${t.xingming.summary}`,
      ].join("\n\n");
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
    <div className="bazi-tab discipline-page">
        <section className="panel panel-cast">
          <div className="panel-head">
            <div>
              <h2>八字排盘</h2>
              <p className="hint">
                填写出生信息后排盘, 可保存档案. AI 解读与对话在排盘完成后单独触发.
              </p>
            </div>
          </div>
          <BirthForm
            embedded
            loading={paipanLoading}
            onSubmit={handleSubmit}
          />
        </section>

        {error && <div className="error-box">{error}</div>}

        {result && (
          <AppViewNav
            activeView={appView}
            chatReady={chatReady}
            chatLoading={chatInitLoading}
            onSelectSummary={() => setAppView("summary")}
            onSelectChat={() => runWithAuth(() => setAppView("chat"))}
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
                开始排盘仅计算命盘. AI 解读与对话需单独触发, 避免阻塞排盘.
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
              <SceneTemplatePicker
                activeModuleId="01"
                onSelect={(prompt) => setInterpretQuestion(prompt)}
              />
              <label className="field-label" htmlFor="interpret-question">
                问事 (融合解读)
              </label>
              <label className="field-label" htmlFor="fusion-mode">
                联判模式
              </label>
              <select
                id="fusion-mode"
                className="text-input"
                value={fusionMode}
                onChange={(e) =>
                  setFusionMode(
                    e.target.value as "bazi_liuyao" | "bazi_ziwei" | "triple",
                  )
                }
              >
                <option value="bazi_liuyao">八字+六爻 (命盘+问事)</option>
                <option value="bazi_ziwei">八字+紫微 (+塔罗对照)</option>
                <option value="triple">三术融合 (八字+紫微+星命)</option>
              </select>
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
                  onClick={() => runWithAuth(() => setAppView("chat"))}
                >
                  打开 AI 对话
                </button>
              </div>
              <InterpretStyleButtons
                professionalLoading={interpretStyleLoading === "professional"}
                plainLoading={interpretStyleLoading === "plain"}
                disabled={!lastRequest}
                onLoadingStart={setInterpretStyleLoading}
                onProfessional={() => runWithAuth(() => handleInterpret("professional"))}
                onPlain={() => runWithAuth(() => handleInterpret("plain"))}
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
              {chart && (
                <FourPillars
                  chart={chart}
                  luckLoading={luckLoading}
                  onOpenDetail={() => pillarDetail && setAppView("pillars")}
                  onOpenLuck={handleOpenLuck}
                />
              )}
            </section>

            {chart && <AnalysisPanels chart={chart} sections={result.sections} />}

            {(interpretation?.summaryProfessional ||
              interpretation?.summaryPlain ||
              interpretation?.summary) && (
              <section className="panel interpret-panel">
                <div className="interpret-header">
                  <h2>命理解读</h2>
                  <span className="interpret-badge">
                    {interpretation.tripleFusion
                      ? `三术融合 / ${interpretation.tripleFusion.preferredChannel}`
                      : interpretation.fusion
                        ? interpretation.fusion.weightNote
                        : chatEnabled && interpretation.agentId
                          ? "AI 解读"
                          : "演示模式"}
                  </span>
                </div>
                {interpretation.summaryProfessional && (
                  <InterpretBlock title="命理师专用解读" copyText={buildProfessionalCopyText()}>
                    {interpretation.tripleFusion &&
                    interpretation.summaryProfessional ===
                      interpretation.tripleFusion.merged.summary ? (
                      <FusionChannelsPanel tripleFusion={interpretation.tripleFusion} />
                    ) : interpretation.fusion &&
                      interpretation.summaryProfessional ===
                        interpretation.fusion.merged.summary ? (
                      <FusionChannelsPanel fusion={interpretation.fusion} />
                    ) : (
                      <InterpretMarkdown text={interpretation.summaryProfessional} />
                    )}
                  </InterpretBlock>
                )}
                {interpretation.summaryPlain && (
                  <InterpretBlock title="AI深度解读" copyText={interpretation.summaryPlain}>
                    {interpretation.tripleFusion &&
                    interpretation.summaryPlain === interpretation.tripleFusion.merged.summary ? (
                      <FusionChannelsPanel tripleFusion={interpretation.tripleFusion} />
                    ) : interpretation.fusion &&
                      interpretation.summaryPlain === interpretation.fusion.merged.summary ? (
                      <FusionChannelsPanel fusion={interpretation.fusion} />
                    ) : (
                      <InterpretMarkdown text={interpretation.summaryPlain} />
                    )}
                  </InterpretBlock>
                )}
                {!interpretation.summaryProfessional &&
                  !interpretation.summaryPlain &&
                  interpretation.summary && (
                  <p className="interpret-summary">{interpretation.summary}</p>
                )}
                {!interpretation.tripleFusion && !interpretation.fusion && (
                  <ChannelRagEvidence
                    query={interpretation.query}
                    excerpts={ragExcerpts}
                    label="八字"
                  />
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

            <ReportTimelinePanel />
            <GrowthMetricsPanel />
          </div>
        )}
    </div>
  );
}
