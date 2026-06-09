import { useEffect, useState } from "react";
import { useAuth } from "../context/AuthContext";
import { DualInterpretSummary } from "../components/DualInterpretSummary";
import { RagExcerptList } from "../components/RagExcerptList";
import { InterpretModelPicker } from "../components/InterpretModelPicker";
import { InterpretStyleButtons } from "../components/InterpretStyleButtons";
import { ChatPanel } from "../components/ChatPanel";
import { MeihuaBoard } from "../components/meihua/MeihuaBoard";
import { TiYongPanel } from "../components/meihua/TiYongPanel";
import { NumberCastForm } from "../components/liuyao/NumberCastForm";
import { TimeCastForm } from "../components/liuyao/TimeCastForm";
import { fetchChatStatus } from "../services/chatApi";
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

export function MeihuaTab() {
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
  const [chatAgentId, setChatAgentId] = useState<string | null>(null);
  const [chatEnabled, setChatEnabled] = useState(false);
  const [chatModels, setChatModels] = useState<ChatModelOption[]>([]);
  const [selectedModel, setSelectedModel] = useState("deepseek-chat");
  const [showChat, setShowChat] = useState(false);

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
    setChatAgentId(null);
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
      if (full.interpretation.agentId) {
        setChatAgentId(full.interpretation.agentId);
      }
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
        const session = await initMeihuaChatSession(
          chart,
          interpretation?.excerpts,
          interpretation?.knowledgeHits,
        );
        setChatAgentId(session.agentId);
        setShowChat(true);
      } catch (err) {
        setError(err instanceof Error ? err.message : "对话连接失败");
      }
    });
  };

  if (showChat && chart) {
    return (
      <div className="meihua-tab chat-mode">
        <ChatPanel
          layout="page"
          agentId={chatAgentId}
          chartName={chart.benGua.name}
          dayMaster={`体${chart.tiGua.name}用${chart.yongGua.name}`}
          chatEnabled={chatEnabled}
          chatModels={chatModels}
          selectedModel={selectedModel}
          onModelChange={setSelectedModel}
          sessionLoading={false}
          connectError=""
          onConnect={() => {}}
          onBack={() => setShowChat(false)}
        />
      </div>
    );
  }

  return (
    <div className="meihua-tab discipline-page">
      <section className="panel panel-cast">
        <div className="panel-head">
          <div>
            <h2>梅花起卦</h2>
            <p className="hint">数字或时间起卦, 自动排体用卦与动爻.</p>
          </div>
        </div>
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
      </section>

      {error && <div className="error-box">{error}</div>}

      {chart && (
        <>
          <section className="panel panel-chart">
            <div className="panel-head">
              <h2>梅花卦象</h2>
              {chart.meta?.castNote && (
                <p className="hint">{chart.meta.castNote}</p>
              )}
            </div>
            <MeihuaBoard chart={chart} />
          </section>

          <TiYongPanel
            chart={chart}
            loading={tiYongLoading}
            onApplyMoving={handleApplyMoving}
          />

          <section className="panel action-panel">
            <h2>典籍与 AI</h2>
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
          </section>

          {(interpretation?.summaryProfessional ||
            interpretation?.summaryPlain ||
            interpretation?.summary) && (
            <DualInterpretSummary title="梅花解读" interpretation={interpretation}>
              {interpretation.knowledgeHits && interpretation.knowledgeHits.length > 0 && (
                <details>
                  <summary>结构化典籍</summary>
                  <ul>
                    {interpretation.knowledgeHits.map((hit, idx) => (
                      <li key={idx}>
                        [{hit.topic}] {hit.summary}
                      </li>
                    ))}
                  </ul>
                </details>
              )}
              {interpretation.query && (
                <details>
                  <summary>古籍索引</summary>
                  <p className="mono">{interpretation.query}</p>
                </details>
              )}
              <RagExcerptList excerpts={interpretation.excerpts ?? []} />
            </DualInterpretSummary>
          )}
        </>
      )}
    </div>
  );
}
