import { useEffect, useState } from "react";
import { useAuth } from "../context/AuthContext";
import { DualInterpretSummary } from "../components/DualInterpretSummary";
import { ClassicIndexPanel } from "../components/ClassicIndexPanel";
import { InterpretModelPicker } from "../components/InterpretModelPicker";
import { InterpretStyleButtons } from "../components/InterpretStyleButtons";
import { CoinCastPanel, rollCoinLine } from "../components/liuyao/CoinCastPanel";
import { LiuyaoJudgementPanel } from "../components/liuyao/LiuyaoJudgementPanel";
import { HexagramBoard } from "../components/liuyao/HexagramBoard";
import { NumberCastForm } from "../components/liuyao/NumberCastForm";
import { TimeCastForm } from "../components/liuyao/TimeCastForm";
import { YongShenEditor } from "../components/liuyao/YongShenEditor";
import { VisualWorkbench } from "../components/visual/VisualWorkbench";
import { VisualPanel } from "../components/visual/VisualPanel";
import { VisualEmptyState } from "../components/visual/VisualEmptyState";
import { fetchChatStatus } from "../services/chatApi";
import { openModuleAiChatSession } from "../components/ai/moduleChatBridge";
import { createModuleChatSessionRecord } from "../components/ai/moduleSession";
import type { AiChatSession } from "../components/ai/types";
import {
  fetchInferYongShen,
  fetchLiuyaoDivine,
  fetchLiuyaoInterpret,
  fetchLiuyaoJudgement,
  initLiuyaoChatSession,
  overrideYongShen,
} from "../services/liuyaoApi";
import { mergeInterpretSummary, type InterpretStyle } from "../utils/interpretStyle";
import type { ChatModelOption } from "../types/bazi";
import type {
  CastMethod,
  LiuyaoChart,
  LiuyaoInterpretation,
  LiuyaoJudgementReport,
  YongShenResult,
} from "../types/liuyao";

function parseDatetimeLocal(value: string) {
  const date = new Date(value);
  return {
    year: date.getFullYear(),
    month: date.getMonth() + 1,
    day: date.getDate(),
    hour: date.getHours(),
    minute: date.getMinutes(),
    second: date.getSeconds(),
  };
}

function nowParts() {
  const date = new Date();
  return {
    year: date.getFullYear(),
    month: date.getMonth() + 1,
    day: date.getDate(),
    hour: date.getHours(),
    minute: date.getMinutes(),
    second: date.getSeconds(),
  };
}

function toDatetimeLocal(date: Date): string {
  const pad = (n: number) => String(n).padStart(2, "0");
  return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())}T${pad(date.getHours())}:${pad(date.getMinutes())}`;
}

interface LiuyaoTabProps {
  onOpenAiChatSession: (session: AiChatSession) => void;
}

export function LiuyaoTab({ onOpenAiChatSession }: LiuyaoTabProps) {
  const { runWithAuth } = useAuth();
  const [question, setQuestion] = useState("");
  const [method, setMethod] = useState<CastMethod>("coin");
  const [coinLines, setCoinLines] = useState<number[]>([]);
  const [numberCount, setNumberCount] = useState<1 | 2 | 3>(1);
  const [numberValues, setNumberValues] = useState<string[]>(["", "", ""]);
  const [useNow, setUseNow] = useState(true);
  const [datetime, setDatetime] = useState(toDatetimeLocal(new Date()));
  const [loading, setLoading] = useState(false);
  const [interpretStyleLoading, setInterpretStyleLoading] = useState<InterpretStyle | null>(null);
  const [, setLastInterpretStyle] = useState<InterpretStyle | null>(null);
  const [yongShenLoading, setYongShenLoading] = useState(false);
  const [error, setError] = useState("");
  const [chart, setChart] = useState<LiuyaoChart | null>(null);
  const [yongShen, setYongShen] = useState<YongShenResult | null>(null);
  const [interpretation, setInterpretation] = useState<LiuyaoInterpretation | null>(null);
  const [judgement, setJudgement] = useState<LiuyaoJudgementReport | null>(null);
  const [judgementLoading, setJudgementLoading] = useState(false);
  const [chatEnabled, setChatEnabled] = useState(false);
  const [chatModels, setChatModels] = useState<ChatModelOption[]>([]);
  const [selectedModel, setSelectedModel] = useState("deepseek-chat");

  useEffect(() => {
    fetchChatStatus()
      .then((status) => {
        setChatEnabled(status.enabled);
        setChatModels(status.models ?? []);
        if (status.model) {
          setSelectedModel(status.model);
        }
      })
      .catch(() => setChatEnabled(false));
  }, []);

  const buildRequest = () => {
    const base = {
      question: question.trim(),
      method,
      calendarType: "solar" as const,
    };
    if (method === "coin") {
      return { ...base, coinLines };
    }
    if (method === "number") {
      const numbers = numberValues
        .slice(0, numberCount)
        .map((value) => Number(value))
        .filter((value) => Number.isFinite(value) && value > 0);
      return { ...base, numbers };
    }
    const parts = useNow ? nowParts() : parseDatetimeLocal(datetime);
    return { ...base, ...parts };
  };

  const loadJudgement = async (nextChart: LiuyaoChart, useRag = false) => {
    setJudgementLoading(true);
    try {
      const result = await fetchLiuyaoJudgement(
        nextChart,
        nextChart.input.question,
        yongShen ?? undefined,
        useRag,
      );
      setJudgement(result.judgement);
      if (result.judgement.yongShen) {
        setYongShen(result.judgement.yongShen);
      }
    } catch {
      setJudgement(null);
    } finally {
      setJudgementLoading(false);
    }
  };

  const handleDivine = async () => {
    if (!question.trim()) {
      setError("请先输入问事内容");
      return;
    }
    if (method === "coin" && coinLines.length !== 6) {
      setError("请完成六次摇卦");
      return;
    }
    setLoading(true);
    setError("");
    setInterpretation(null);
    setJudgement(null);
    setYongShen(null);
    try {
      const payload = await fetchLiuyaoDivine(buildRequest());
      setChart(payload.chart);
      await loadJudgement(payload.chart, false);
    } catch (err) {
      setError(err instanceof Error ? err.message : "起卦失败");
      setChart(null);
    } finally {
      setLoading(false);
    }
  };

  const handleInferYongShen = async () => {
    if (!chart) return;
    setYongShenLoading(true);
    setError("");
    try {
      const result = await fetchInferYongShen(chart, question, selectedModel);
      setYongShen(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : "用神推断失败");
    } finally {
      setYongShenLoading(false);
    }
  };

  const handleInterpret = async (style: InterpretStyle) => {
    if (!chart) return;
    setInterpretStyleLoading(style);
    setLastInterpretStyle(style);
    setError("");
    try {
      const full = await fetchLiuyaoInterpret(
        chart,
        yongShen ?? undefined,
        interpretation?.excerpts,
        selectedModel,
        style,
      );
      setYongShen(full.interpretation.yongShen);
      if (full.interpretation.judgement) {
        setJudgement(full.interpretation.judgement);
      }
      setInterpretation((prev) => ({
        ...full.interpretation,
        ...mergeInterpretSummary(prev, full.interpretation.summary, style),
      }));
    } catch (err) {
      setError(err instanceof Error ? err.message : "解读失败");
    } finally {
      setInterpretStyleLoading(null);
    }
  };

  const handleOverrideYongShen = async (name: string) => {
    if (!chart) return;
    setYongShenLoading(true);
    setError("");
    try {
      const result = await overrideYongShen(chart, name);
      setYongShen(result);
      if (interpretation) {
        setInterpretation({ ...interpretation, yongShen: result, summary: "" });
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "修改用神失败");
    } finally {
      setYongShenLoading(false);
    }
  };

  const handleOpenChat = () => {
    runWithAuth(async () => {
      if (!chart || !yongShen) {
        setError("请先完成排盘并确定用神");
        return;
      }
      try {
        let agentId = interpretation?.agentId ?? null;
        if (!agentId) {
          const session = await initLiuyaoChatSession(
            chart,
            yongShen,
            interpretation?.excerpts,
          );
          agentId = session.agentId;
        }
        await openModuleAiChatSession(
          createModuleChatSessionRecord({
            agentId,
            moduleId: "02",
            moduleLabel: "六爻",
            question: chart.input.question,
            chartName: chart.benGua.name,
            subtitle: yongShen.yongShen,
          }),
          interpretation,
          onOpenAiChatSession,
        );
      } catch (err) {
        setError(err instanceof Error ? err.message : "对话连接失败");
      }
    });
  };

  const hasInterpretation =
    interpretation?.summaryProfessional ||
    interpretation?.summaryPlain ||
    interpretation?.summary;

  const displayChart = judgement?.enrichedChart ?? chart;
  const highlightPosition = judgement?.yongShen?.position ?? yongShen?.position;

  const stageContent = chart ? (
    <>
      <VisualPanel title="六爻卦象" hint={chart.meta?.castNote}>
        <HexagramBoard chart={displayChart ?? chart} highlightPosition={highlightPosition} />
      </VisualPanel>
      {judgementLoading ? (
        <p className="liuyao-judgement-loading">判盘链加载中...</p>
      ) : (
        <LiuyaoJudgementPanel judgement={judgement} />
      )}
    </>
  ) : (
    <VisualEmptyState
      theme="hexagram"
      title="卦象待排"
      description="输入问事内容并起卦, 排盘后确定用神."
    />
  );

  return (
    <div className="liuyao-tab">
      <VisualWorkbench
        moduleId="liuyao"
        title="六爻起卦"
        subtitle="六爻、动爻、用神、世应"
        theme="hexagram"
        error={error || undefined}
        input={
          <VisualPanel title="六爻起卦" hint="支持摇卦、数字、时间三种起卦方式, 排盘后可选定用神.">
            <div className="cast-form">
              <section className="cast-form-section">
                <h3 className="cast-form-section-title">问事</h3>
                <label className="field field-grow">
                  <span>问事内容</span>
                  <textarea
                    value={question}
                    onChange={(event) => setQuestion(event.target.value)}
                    placeholder="例如: 这次考试能过吗?"
                    rows={3}
                  />
                </label>
              </section>
              <section className="cast-form-section">
                <h3 className="cast-form-section-title">起卦方式</h3>
                <div className="method-switch segment-switch">
                  {(["coin", "number", "time"] as CastMethod[]).map((item) => (
                    <button
                      key={item}
                      type="button"
                      className={method === item ? "tab active" : "tab"}
                      onClick={() => setMethod(item)}
                    >
                      {item === "coin" ? "摇卦" : item === "number" ? "数字" : "时间"}
                    </button>
                  ))}
                </div>
                {method === "coin" && (
                  <CoinCastPanel
                    lines={coinLines}
                    onThrow={() => setCoinLines((prev) => [...prev, rollCoinLine()])}
                    onReset={() => setCoinLines([])}
                    disabled={loading}
                  />
                )}
                {method === "number" && (
                  <NumberCastForm
                    count={numberCount}
                    values={numberValues}
                    onCountChange={setNumberCount}
                    onChange={(index, value) => {
                      setNumberValues((prev) => {
                        const next = [...prev];
                        next[index] = value;
                        return next;
                      });
                    }}
                  />
                )}
                {method === "time" && (
                  <TimeCastForm
                    useNow={useNow}
                    onUseNowChange={setUseNow}
                    datetime={datetime}
                    onDatetimeChange={setDatetime}
                  />
                )}
              </section>
            </div>
            <div className="form-actions form-actions-end">
              <button
                type="button"
                className="primary-btn"
                disabled={loading}
                onClick={handleDivine}
              >
                {loading ? "排盘中..." : "完成起卦并排盘"}
              </button>
            </div>
          </VisualPanel>
        }
        stage={stageContent}
        oracle={
          chart ? (
            <VisualPanel title="典籍与 AI" accent>
              <YongShenEditor
                chart={chart}
                yongShen={yongShen}
                loading={yongShenLoading}
                onApply={handleOverrideYongShen}
              />
              <InterpretModelPicker
                models={chatModels}
                value={selectedModel}
                onChange={setSelectedModel}
                chatEnabled={chatEnabled}
                disabled={interpretStyleLoading !== null || yongShenLoading}
              />
              <div className="action-row">
                <button type="button" className="secondary" disabled={yongShenLoading} onClick={handleInferYongShen}>
                  {yongShenLoading ? "推断中..." : "AI 推断用神"}
                </button>
                <button type="button" className="secondary" disabled={!yongShen || !chatEnabled} onClick={handleOpenChat}>
                  打开 AI 对话
                </button>
              </div>
              <InterpretStyleButtons
                professionalLoading={interpretStyleLoading === "professional"}
                plainLoading={interpretStyleLoading === "plain"}
                onLoadingStart={setInterpretStyleLoading}
                onProfessional={() => runWithAuth(() => handleInterpret("professional"))}
                onPlain={() => runWithAuth(() => handleInterpret("plain"))}
              />
            </VisualPanel>
          ) : undefined
        }
        interpretation={
          hasInterpretation ? (
            <DualInterpretSummary title="六爻解读" interpretation={interpretation!}>
              <ClassicIndexPanel
                query={interpretation!.query}
                excerpts={interpretation!.excerpts}
              />
            </DualInterpretSummary>
          ) : undefined
        }
      />
    </div>
  );
}
