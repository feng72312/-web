import { useEffect, useState } from "react";
import { ChatPanel } from "../components/ChatPanel";
import { CoinCastPanel, rollCoinLine } from "../components/liuyao/CoinCastPanel";
import { HexagramBoard } from "../components/liuyao/HexagramBoard";
import { NumberCastForm } from "../components/liuyao/NumberCastForm";
import { TimeCastForm } from "../components/liuyao/TimeCastForm";
import { YongShenEditor } from "../components/liuyao/YongShenEditor";
import { fetchChatStatus } from "../services/chatApi";
import {
  fetchInferYongShen,
  fetchLiuyaoDivine,
  fetchLiuyaoInterpret,
  fetchLiuyaoRagSearch,
  initLiuyaoChatSession,
  overrideYongShen,
} from "../services/liuyaoApi";
import type { ChatModelOption } from "../types/bazi";
import type {
  CastMethod,
  LiuyaoChart,
  LiuyaoInterpretation,
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

export function LiuyaoTab() {
  const [question, setQuestion] = useState("");
  const [method, setMethod] = useState<CastMethod>("coin");
  const [coinLines, setCoinLines] = useState<number[]>([]);
  const [numberCount, setNumberCount] = useState<1 | 2 | 3>(1);
  const [numberValues, setNumberValues] = useState<string[]>(["", "", ""]);
  const [useNow, setUseNow] = useState(true);
  const [datetime, setDatetime] = useState(toDatetimeLocal(new Date()));
  const [loading, setLoading] = useState(false);
  const [ragLoading, setRagLoading] = useState(false);
  const [interpretLoading, setInterpretLoading] = useState(false);
  const [yongShenLoading, setYongShenLoading] = useState(false);
  const [error, setError] = useState("");
  const [chart, setChart] = useState<LiuyaoChart | null>(null);
  const [yongShen, setYongShen] = useState<YongShenResult | null>(null);
  const [interpretation, setInterpretation] = useState<LiuyaoInterpretation | null>(null);
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
    setYongShen(null);
    setChatAgentId(null);
    try {
      const payload = await fetchLiuyaoDivine(buildRequest());
      setChart(payload.chart);
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

  const handleRagSearch = async () => {
    if (!chart) return;
    let current = yongShen;
    if (!current) {
      current = await fetchInferYongShen(chart, question, selectedModel);
      setYongShen(current);
    }
    setRagLoading(true);
    setError("");
    try {
      const rag = await fetchLiuyaoRagSearch(chart, current, question);
      setInterpretation((prev) => ({
        query: rag.query,
        yongShen: current!,
        excerpts: rag.excerpts,
        summary: prev?.summary ?? "",
      }));
    } catch (err) {
      setError(err instanceof Error ? err.message : "检索失败");
    } finally {
      setRagLoading(false);
    }
  };

  const handleInterpret = async () => {
    if (!chart) return;
    setInterpretLoading(true);
    setError("");
    try {
      const full = await fetchLiuyaoInterpret(
        chart,
        yongShen ?? undefined,
        interpretation?.excerpts,
        selectedModel,
      );
      setYongShen(full.interpretation.yongShen);
      setInterpretation(full.interpretation);
      if (full.interpretation.agentId) {
        setChatAgentId(full.interpretation.agentId);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "解读失败");
    } finally {
      setInterpretLoading(false);
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

  const handleOpenChat = async () => {
    if (!chart || !yongShen) {
      setError("请先完成排盘并确定用神");
      return;
    }
    try {
      const session = await initLiuyaoChatSession(
        chart,
        yongShen,
        interpretation?.excerpts,
      );
      setChatAgentId(session.agentId);
      setShowChat(true);
    } catch (err) {
      setError(err instanceof Error ? err.message : "对话连接失败");
    }
  };

  if (showChat && chart) {
    return (
      <div className="liuyao-tab chat-mode">
        <ChatPanel
          layout="page"
          agentId={chatAgentId}
          chartName={chart.benGua.name}
          dayMaster={yongShen?.yongShen}
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
    <div className="liuyao-tab">
      <section className="panel">
        <h2>六爻起卦</h2>
        <label className="field-block">
          问事
          <textarea
            value={question}
            onChange={(event) => setQuestion(event.target.value)}
            placeholder="例如: 这次考试能过吗?"
            rows={2}
          />
        </label>

        <div className="method-switch discipline-method-switch">
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

        <button type="button" className="primary-btn" disabled={loading} onClick={handleDivine}>
          {loading ? "排盘中..." : "完成起卦并排盘"}
        </button>
      </section>

      {error && <div className="error-box">{error}</div>}

      {chart && (
        <>
          <section className="panel">
            <h2>六爻卦象</h2>
            {chart.meta?.castNote && <p className="hint">{chart.meta.castNote}</p>}
            <HexagramBoard chart={chart} highlightPosition={yongShen?.position} />
          </section>

          <YongShenEditor
            chart={chart}
            yongShen={yongShen}
            loading={yongShenLoading}
            onApply={handleOverrideYongShen}
          />

          <section className="panel action-panel">
            <h2>典籍与 AI</h2>
            <div className="action-row">
              <button type="button" className="secondary" disabled={yongShenLoading} onClick={handleInferYongShen}>
                {yongShenLoading ? "推断中..." : "AI 推断用神"}
              </button>
              <button type="button" className="secondary" disabled={ragLoading} onClick={handleRagSearch}>
                {ragLoading ? "检索中..." : "检索典籍"}
              </button>
              <button type="button" className="primary-btn" disabled={interpretLoading} onClick={handleInterpret}>
                {interpretLoading ? "解读中..." : "AI 解读"}
              </button>
              <button type="button" className="secondary" disabled={!yongShen || !chatEnabled} onClick={handleOpenChat}>
                打开 AI 对话
              </button>
            </div>
          </section>

          {interpretation?.summary && (
            <section className="panel interpret-panel">
              <h2>六爻解读</h2>
              <p className="interpret-summary">{interpretation.summary}</p>
              {interpretation.query && (
                <details>
                  <summary>RAG 检索词</summary>
                  <p className="mono">{interpretation.query}</p>
                </details>
              )}
              {interpretation.excerpts?.map((item, idx) => (
                <blockquote key={idx} className="excerpt">
                  <cite>{item.source}</cite>
                  <p>{item.excerpt}</p>
                </blockquote>
              ))}
            </section>
          )}
        </>
      )}
    </div>
  );
}
