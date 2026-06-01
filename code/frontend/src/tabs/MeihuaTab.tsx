import { useEffect, useState } from "react";
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
  fetchMeihuaRagSearch,
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
  const [question, setQuestion] = useState("");
  const [method, setMethod] = useState<MeihuaCastMethod>("number");
  const [numberCount, setNumberCount] = useState<1 | 2 | 3>(1);
  const [numberValues, setNumberValues] = useState<string[]>(["", "", ""]);
  const [useNow, setUseNow] = useState(true);
  const [datetime, setDatetime] = useState(toDatetimeLocal(new Date()));
  const [loading, setLoading] = useState(false);
  const [tiYongLoading, setTiYongLoading] = useState(false);
  const [ragLoading, setRagLoading] = useState(false);
  const [interpretStyleLoading, setInterpretStyleLoading] = useState<InterpretStyle | null>(null);
  const [lastInterpretStyle, setLastInterpretStyle] = useState<InterpretStyle | null>(null);
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

  const handleRagSearch = async () => {
    if (!chart) return;
    setRagLoading(true);
    setError("");
    try {
      const rag = await fetchMeihuaRagSearch(chart, question);
      setInterpretation((prev) => ({
        query: rag.query,
        tiYong: {
          tiGua: chart.tiGua,
          yongGua: chart.yongGua,
          relation: chart.tiYongRelation,
          isStatic: chart.isStatic,
        },
        excerpts: rag.excerpts,
        summary: prev?.summary ?? "",
      }));
    } catch (err) {
      setError(err instanceof Error ? err.message : "检索失败");
    } finally {
      setRagLoading(false);
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

  const handleOpenChat = async () => {
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
    <div className="meihua-tab">
      <section className="panel">
        <h2>梅花起卦</h2>
        <label className="field-block">
          问事
          <textarea
            value={question}
            onChange={(event) => setQuestion(event.target.value)}
            placeholder="例如: 这次合作能成吗?"
            rows={2}
          />
        </label>

        <div className="method-switch discipline-method-switch">
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

        <button type="button" className="primary-btn" disabled={loading} onClick={handleDivine}>
          {loading ? "起卦中..." : "完成起卦"}
        </button>
      </section>

      {error && <div className="error-box">{error}</div>}

      {chart && (
        <>
          <section className="panel">
            <h2>梅花卦象</h2>
            {chart.meta?.castNote && <p className="hint">{chart.meta.castNote}</p>}
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
              <button type="button" className="secondary" disabled={ragLoading} onClick={handleRagSearch}>
                {ragLoading ? "检索中..." : "检索知识库"}
              </button>
              <button type="button" className="secondary" disabled={!chatEnabled} onClick={handleOpenChat}>
                打开 AI 对话
              </button>
            </div>
            <InterpretStyleButtons
              professionalLoading={interpretStyleLoading === "professional"}
              plainLoading={interpretStyleLoading === "plain"}
              onProfessional={() => handleInterpret("professional")}
              onPlain={() => handleInterpret("plain")}
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
