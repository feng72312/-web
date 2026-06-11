import { useEffect, useState } from "react";
import { useAuth } from "../context/AuthContext";
import { DualInterpretSummary } from "../components/DualInterpretSummary";
import { RagExcerptList } from "../components/RagExcerptList";
import { InterpretModelPicker } from "../components/InterpretModelPicker";
import { InterpretStyleButtons } from "../components/InterpretStyleButtons";
import { MeihuaBoard } from "../components/meihua/MeihuaBoard";
import { TiYongPanel } from "../components/meihua/TiYongPanel";
import { VisualWorkbench } from "../components/visual/VisualWorkbench";
import { VisualPanel } from "../components/visual/VisualPanel";
import { VisualEmptyState } from "../components/visual/VisualEmptyState";
import { NumberCastForm } from "../components/liuyao/NumberCastForm";
import { TimeCastForm } from "../components/liuyao/TimeCastForm";
import { fetchChatStatus } from "../services/chatApi";
import { openModuleAiChatSession } from "../components/ai/moduleChatBridge";
import { createModuleChatSessionRecord } from "../components/ai/moduleSession";
import type { AiChatSession } from "../components/ai/types";
import {
  fetchMeihuaDivine,
  fetchMeihuaInterpret,
  fetchMeihuaTiYong,
  initMeihuaChatSession,
} from "../services/meihuaApi";
import { mergeInterpretSummary, type InterpretStyle } from "../utils/interpretStyle";
import type { ChatModelOption } from "../types/bazi";
import type {
  MeihuaCastMethod,
  MeihuaChart,
  MeihuaInterpretation,
} from "../types/meihua";

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

function toDatetimeLocal(date: Date): string {
  const pad = (n: number) => String(n).padStart(2, "0");
  return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())}T${pad(date.getHours())}:${pad(date.getMinutes())}`;
}

interface MeihuaTabProps {
  onOpenAiChatSession: (session: AiChatSession) => void;
}

export function MeihuaTab({ onOpenAiChatSession }: MeihuaTabProps) {
  const { runWithAuth } = useAuth();
  const [question, setQuestion] = useState("");
  const [method, setMethod] = useState<MeihuaCastMethod>("number");
  const [numberCount, setNumberCount] = useState<1 | 2 | 3>(1);
  const [numberValues, setNumberValues] = useState<string[]>(["", "", ""]);
  const [useNow, setUseNow] = useState(true);
  const [datetime, setDatetime] = useState(toDatetimeLocal(new Date()));
  const [loading, setLoading] = useState(false);
  const [tiYongLoading, setTiYongLoading] = useState(false);
  const [interpretStyleLoading, setInterpretStyleLoading] = useState<InterpretStyle | null>(null);
  const [, setLastInterpretStyle] = useState<InterpretStyle | null>(null);
  const [error, setError] = useState("");
  const [chart, setChart] = useState<MeihuaChart | null>(null);
  const [interpretation, setInterpretation] = useState<MeihuaInterpretation | null>(null);
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
    if (method === "number") {
      const numbers = numberValues
        .slice(0, numberCount)
        .map((value) => Number(value))
        .filter((value) => Number.isFinite(value) && value > 0);
      return { ...base, numbers };
    }
    const parts = useNow
      ? parseDatetimeLocal(toDatetimeLocal(new Date()))
      : parseDatetimeLocal(datetime);
    return { ...base, ...parts };
  };

  const handleDivine = async () => {
    if (!question.trim()) {
      setError("请先输入问事内容");
      return;
    }
    setLoading(true);
    setError("");
    setInterpretation(null);
    try {
      const payload = await fetchMeihuaDivine(buildRequest());
      setChart(payload.chart);
    } catch (err) {
      setError(err instanceof Error ? err.message : "起卦失败");
      setChart(null);
    } finally {
      setLoading(false);
    }
  };

  const handleApplyMoving = async (position: number) => {
    if (!chart) return;
    setTiYongLoading(true);
    setError("");
    try {
      const payload = await fetchMeihuaTiYong(chart, position);
      setChart(payload.chart);
      if (interpretation) {
        setInterpretation({
          ...interpretation,
          tiYong: {
            tiGua: payload.chart.tiGua,
            yongGua: payload.chart.yongGua,
            relation: payload.chart.tiYongRelation,
            isStatic: payload.chart.isStatic,
          },
          summary: "",
        });
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "体用调整失败");
    } finally {
      setTiYongLoading(false);
    }
  };

  const handleInterpret = async (style: InterpretStyle) => {
    if (!chart) return;
    setInterpretStyleLoading(style);
    setLastInterpretStyle(style);
    setError("");
    try {
      const full = await fetchMeihuaInterpret(
        chart,
        interpretation?.excerpts,
        selectedModel,
        style,
      );
      setChart(full.chart);
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

  const handleOpenChat = () => {
    runWithAuth(async () => {
      if (!chart) {
        setError("请先完成起卦");
        return;
      }
      try {
        let agentId = interpretation?.agentId ?? null;
        if (!agentId) {
          const session = await initMeihuaChatSession(
            chart,
            interpretation?.excerpts,
            interpretation?.knowledgeHits,
          );
          agentId = session.agentId;
        }
        await openModuleAiChatSession(
          createModuleChatSessionRecord({
            agentId,
            moduleId: "03",
            moduleLabel: "梅花",
            question: chart.input.question,
            chartName: chart.benGua.name,
            subtitle: `体${chart.tiGua.name}用${chart.yongGua.name}`,
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

  const stageContent = chart ? (
    <VisualPanel title="梅花卦象" hint={chart.meta?.castNote}>
      <MeihuaBoard chart={chart} />
      <TiYongPanel
        chart={chart}
        loading={tiYongLoading}
        onApplyMoving={handleApplyMoving}
      />
    </VisualPanel>
  ) : (
    <VisualEmptyState
      theme="meihua"
      title="卦象待起"
      description="输入问事内容并选择起卦方式, 生成体用卦与动爻."
    />
  );

  return (
    <div className="meihua-tab">
      <VisualWorkbench
        moduleId="meihua"
        title="梅花起卦"
        subtitle="灵机、体用、生克、动爻"
        theme="meihua"
        error={error || undefined}
        input={
          <VisualPanel title="梅花起卦" hint="数字或时间起卦, 自动排体用卦与动爻.">
            <div className="cast-form">
              <section className="cast-form-section">
                <h3 className="cast-form-section-title">问事</h3>
                <label className="field field-grow">
                  <span>问事内容</span>
                  <textarea
                    value={question}
                    onChange={(event) => setQuestion(event.target.value)}
                    placeholder="例如: 这次合作能成吗?"
                    rows={3}
                  />
                </label>
              </section>
              <section className="cast-form-section">
                <h3 className="cast-form-section-title">起卦方式</h3>
                <div className="method-switch segment-switch">
                  {(["number", "time"] as MeihuaCastMethod[]).map((item) => (
                    <button
                      key={item}
                      type="button"
                      className={method === item ? "tab active" : "tab"}
                      onClick={() => setMethod(item)}
                    >
                      {item === "number" ? "数字" : "时间"}
                    </button>
                  ))}
                </div>
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
                {loading ? "起卦中..." : "完成起卦"}
              </button>
            </div>
          </VisualPanel>
        }
        stage={stageContent}
        oracle={
          chart ? (
            <VisualPanel title="典籍与 AI" accent>
              <InterpretModelPicker
                models={chatModels}
                value={selectedModel}
                onChange={setSelectedModel}
                chatEnabled={chatEnabled}
                disabled={interpretStyleLoading !== null}
              />
              <div className="action-row">
                <button type="button" className="secondary" disabled={!chatEnabled} onClick={handleOpenChat}>
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
            <DualInterpretSummary title="梅花解读" interpretation={interpretation!}>
              {interpretation!.knowledgeHits && interpretation!.knowledgeHits.length > 0 && (
                <details>
                  <summary>结构化典籍</summary>
                  <ul>
                    {interpretation!.knowledgeHits.map((hit, idx) => (
                      <li key={idx}>
                        [{hit.topic}] {hit.summary}
                      </li>
                    ))}
                  </ul>
                </details>
              )}
              {interpretation!.query && (
                <details>
                  <summary>古籍索引</summary>
                  <p className="mono">{interpretation!.query}</p>
                </details>
              )}
              <RagExcerptList excerpts={interpretation!.excerpts ?? []} />
            </DualInterpretSummary>
          ) : undefined
        }
      />
    </div>
  );
}
