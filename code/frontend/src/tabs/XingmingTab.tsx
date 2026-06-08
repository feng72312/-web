import { useEffect, useState } from "react";
import { useAuth } from "../context/AuthContext";
import { BirthForm } from "../components/BirthForm";
import { DualInterpretSummary } from "../components/DualInterpretSummary";
import { RagExcerptList } from "../components/RagExcerptList";
import { InterpretModelPicker } from "../components/InterpretModelPicker";
import { InterpretStyleButtons } from "../components/InterpretStyleButtons";
import { ChatPanel } from "../components/ChatPanel";
import { XingmingBoard } from "../components/xingming/XingmingBoard";
import { fetchChatStatus } from "../services/chatApi";
import {
  fetchXingmingChart,
  fetchXingmingInterpret,
  initXingmingChatSession,
} from "../services/xingmingApi";
import {
  hasAnyInterpretSummary,
  mergeInterpretSummary,
  type InterpretStyle,
} from "../utils/interpretStyle";
import type { ChatModelOption, PaipanRequest, PaipanResponse } from "../types/bazi";
import type { XingmingChart, XingmingChartRequest, XingmingInterpretation } from "../types/xingming";
import "../styles/xingming.css";

const BAZI_CHART_KEY = "bazi_last_chart_v1";
const ZIWEI_CHART_KEY = "ziwei:lastChart";

function buildXingmingRequest(birth: PaipanRequest, question: string, targetYear: number): XingmingChartRequest {
  return {
    name: birth.name,
    calendarType: birth.calendarType,
    year: birth.year,
    month: birth.month,
    day: birth.day,
    isLeapMonth: birth.isLeapMonth,
    hour: birth.hour,
    minute: birth.minute,
    gender: birth.gender,
    useTrueSolarTime: true,
    longitude: 120,
    latitude: 35,
    targetYear,
    question: question.trim(),
    rules: { school: "guolao_v1", ziHourRule: "combined", dayNightRule: "auto" },
  };
}

function loadSessionChart<T>(key: string): T | undefined {
  try {
    const raw = sessionStorage.getItem(key);
    if (!raw) return undefined;
    return JSON.parse(raw) as T;
  } catch {
    return undefined;
  }
}

export function XingmingTab() {
  const { runWithAuth } = useAuth();
  const [birth, setBirth] = useState<PaipanRequest | null>(null);
  const [question, setQuestion] = useState("");
  const [targetYear, setTargetYear] = useState(new Date().getFullYear());
  const [chart, setChart] = useState<XingmingChart | null>(null);
  const [interpretation, setInterpretation] = useState<XingmingInterpretation | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [selectedModel, setSelectedModel] = useState("deepseek-chat");
  const [interpretStyleLoading, setInterpretStyleLoading] = useState<InterpretStyle | null>(null);
  const [lastInterpretStyle, setLastInterpretStyle] = useState<InterpretStyle>("professional");
  const [showChat, setShowChat] = useState(false);
  const [chatAgentId, setChatAgentId] = useState<string | null>(null);
  const [compareBazi, setCompareBazi] = useState(true);
  const [compareZiwei, setCompareZiwei] = useState(true);
  const [chatEnabled, setChatEnabled] = useState(false);
  const [models, setModels] = useState<ChatModelOption[]>([]);

  useEffect(() => {
    fetchChatStatus()
      .then((status) => {
        setChatEnabled(status.enabled);
        setModels(status.models ?? []);
        if (status.model) {
          setSelectedModel(status.model);
        }
      })
      .catch(() => setChatEnabled(false));
  }, []);

  const crossCharts = () => {
    const out: { baziChart?: PaipanResponse["chart"]; ziweiChart?: unknown } = {};
    if (compareBazi) {
      const b = loadSessionChart<PaipanResponse["chart"]>(BAZI_CHART_KEY);
      if (b) out.baziChart = b;
    }
    if (compareZiwei) {
      const z = loadSessionChart(ZIWEI_CHART_KEY);
      if (z) out.ziweiChart = z;
    }
    return Object.keys(out).length ? out : undefined;
  };

  const handleChart = async () => {
    if (!birth) {
      setError("请先填写出生信息");
      return;
    }
    if (!question.trim()) {
      setError("请先输入问事内容");
      return;
    }
    setLoading(true);
    setError("");
    setInterpretation(null);
    setChatAgentId(null);
    try {
      const payload = await fetchXingmingChart(buildXingmingRequest(birth, question, targetYear));
      setChart(payload.chart);
      sessionStorage.setItem("xingming:lastChart", JSON.stringify(payload.chart));
    } catch (err) {
      setError(err instanceof Error ? err.message : "排盘失败");
      setChart(null);
    } finally {
      setLoading(false);
    }
  };

  const handleInterpret = async (style: InterpretStyle) => {
    if (!chart) return;
    setInterpretStyleLoading(style);
    setLastInterpretStyle(style);
    setError("");
    try {
      const full = await fetchXingmingInterpret(
        chart,
        interpretation?.excerpts,
        selectedModel,
        style,
        question,
        crossCharts(),
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
        setError("请先完成排盘");
        return;
      }
      try {
        const session = await initXingmingChatSession(
          chart,
          interpretation?.excerpts,
          interpretation?.knowledgeHits,
          interpretation?.cases,
          crossCharts(),
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
      <ChatPanel
        agentId={chatAgentId ?? ""}
        title="星命占验对话"
        onBack={() => setShowChat(false)}
      />
    );
  }

  return (
    <div className="tab-panel xingming-tab">
      <BirthForm onSubmit={setBirth} />
      <label className="field-block">
        问事
        <textarea value={question} onChange={(e) => setQuestion(e.target.value)} rows={2} />
      </label>
      <label className="field-block">
        流年参照年
        <input
          type="number"
          value={targetYear}
          onChange={(e) => setTargetYear(Number(e.target.value))}
        />
      </label>
      <label>
        <input type="checkbox" checked={compareBazi} onChange={(e) => setCompareBazi(e.target.checked)} />
        对照八字盘(session)
      </label>
      <label>
        <input type="checkbox" checked={compareZiwei} onChange={(e) => setCompareZiwei(e.target.checked)} />
        对照紫微盘(session)
      </label>
      <button type="button" className="primary-btn" disabled={loading} onClick={handleChart}>
        {loading ? "排盘中..." : "星命排盘"}
      </button>
      {error ? <p className="error-text">{error}</p> : null}
      {chart ? <XingmingBoard chart={chart} /> : null}
      {chart ? (
        <>
          <InterpretModelPicker
            models={models}
            value={selectedModel}
            onChange={setSelectedModel}
            chatEnabled={chatEnabled}
          />
          <InterpretStyleButtons
            professionalLoading={interpretStyleLoading === "professional"}
            plainLoading={interpretStyleLoading === "plain"}
            disabled={!chart || !chatEnabled}
            onProfessional={() => runWithAuth(() => handleInterpret("professional"))}
            onPlain={() => runWithAuth(() => handleInterpret("plain"))}
          />
          {hasAnyInterpretSummary(interpretation) ? (
            <DualInterpretSummary interpretation={interpretation} style={lastInterpretStyle} />
          ) : null}
          {interpretation?.cases?.length ? (
            <section>
              <h3>占验课例</h3>
              <ul>
                {interpretation.cases.map((c, i) => (
                  <li key={String(c.id ?? i)}>{String(c.verdict ?? "")}</li>
                ))}
              </ul>
            </section>
          ) : null}
          {interpretation ? <RagExcerptList excerpts={interpretation.excerpts} /> : null}
          <button type="button" className="secondary-btn" onClick={handleOpenChat}>
            继续对话
          </button>
        </>
      ) : null}
    </div>
  );
}
