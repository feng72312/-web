import { useEffect, useState } from "react";
import { useAuth } from "../context/AuthContext";
import { DualInterpretSummary } from "../components/DualInterpretSummary";
import { RagExcerptList } from "../components/RagExcerptList";
import { InterpretModelPicker } from "../components/InterpretModelPicker";
import { InterpretStyleButtons } from "../components/InterpretStyleButtons";
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
  initLiuyaoChatSession,
  overrideYongShen,
} from "../services/liuyaoApi";
import { mergeInterpretSummary, type InterpretStyle } from "../utils/interpretStyle";
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
    });
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
              onProfessional={() => runWithAuth(() => handleInterpret("professional"))}
              onPlain={() => runWithAuth(() => handleInterpret("plain"))}
            />
          </section>

          {(interpretation?.summaryProfessional ||
            interpretation?.summaryPlain ||
            interpretation?.summary) && (
            <DualInterpretSummary title="六爻解读" interpretation={interpretation}>
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
