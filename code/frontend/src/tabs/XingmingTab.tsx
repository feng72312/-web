import { useEffect, useState } from "react";
import { useAuth } from "../context/AuthContext";
import { BirthForm } from "../components/BirthForm";
import { ChannelRagEvidence } from "../components/ChannelRagEvidence";
import { DualInterpretSummary } from "../components/DualInterpretSummary";
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

  useEffect(() => {
    const onAuthCancelled = () => setInterpretStyleLoading(null);
    window.addEventListener("zy-auth-cancelled", onAuthCancelled);
    return () => window.removeEventListener("zy-auth-cancelled", onAuthCancelled);
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

  const handleBirthConfirm = (data: PaipanRequest) => {
    setBirth(data);
    setError("");
  };

  const handleChart = async () => {
    if (!birth) {
      setError("请先填写出生信息并点「确认出生信息」");
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

  const hasBaziSession = Boolean(loadSessionChart(BAZI_CHART_KEY));
  const hasZiweiSession = Boolean(loadSessionChart(ZIWEI_CHART_KEY));

  return (
    <div className="xingming-tab discipline-page">
      <section className="panel panel-cast">
        <div className="panel-head">
          <div>
            <h2>星命占验排盘</h2>
            <p className="hint">
              果老七政四余, 含命限与流年. 与八字、紫微共用出生档案, 可对照会话内已排命盘.
            </p>
          </div>
        </div>

        <BirthForm
          embedded
          loading={loading}
          submitLabel="确认出生信息"
          onSubmit={handleBirthConfirm}
        />

        <section className="cast-form-section xingming-cast-section">
          <h3 className="cast-form-section-title">占验问事</h3>
          <label className="field field-grow">
            <span>问事</span>
            <textarea
              value={question}
              rows={3}
              placeholder="例如: 论今年事业财运与贵人"
              onChange={(e) => setQuestion(e.target.value)}
            />
          </label>
          <div className="field-row field-row-2 xingming-cast-row">
            <label className="field">
              <span>流年参照年</span>
              <input
                type="number"
                min={1900}
                max={2100}
                value={targetYear}
                onChange={(e) => setTargetYear(Number(e.target.value))}
              />
            </label>
          </div>
          <div className="xingming-compare-block">
            <p className="xingming-compare-label">多盘对照</p>
            <div className="cast-form-options xingming-compare-options">
              <label className="field checkbox-field">
                <input
                  type="checkbox"
                  checked={compareBazi}
                  onChange={(e) => setCompareBazi(e.target.checked)}
                />
                <span>对照八字盘{hasBaziSession ? "" : " (未排)"}</span>
              </label>
              <label className="field checkbox-field">
                <input
                  type="checkbox"
                  checked={compareZiwei}
                  onChange={(e) => setCompareZiwei(e.target.checked)}
                />
                <span>对照紫微盘{hasZiweiSession ? "" : " (未排)"}</span>
              </label>
            </div>
            <p className="hint xingming-compare-hint">
              请先在八字、紫微页完成排盘; 对照数据保存在本次浏览器会话中.
            </p>
          </div>
        </section>

        <div className="form-actions form-actions-end xingming-cast-actions">
          <button type="button" className="primary-btn" disabled={loading} onClick={handleChart}>
            {loading ? "排盘中..." : "星命排盘"}
          </button>
        </div>
      </section>

      {error ? <div className="error-box">{error}</div> : null}

      {chart ? (
        <section className="panel panel-chart">
          <div className="panel-head panel-head-compact">
            <h2>星命盘</h2>
          </div>
          <XingmingBoard chart={chart} />
        </section>
      ) : null}

      {chart ? (
        <section className="panel action-panel">
          <div className="panel-head panel-head-compact">
            <h2>典籍与 AI</h2>
          </div>
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
            onLoadingStart={setInterpretStyleLoading}
            onProfessional={() => runWithAuth(() => handleInterpret("professional"))}
            onPlain={() => runWithAuth(() => handleInterpret("plain"))}
          />
          {hasAnyInterpretSummary(interpretation) ? (
            <DualInterpretSummary title="星命解读" interpretation={interpretation}>
              <ChannelRagEvidence
                query={interpretation.query}
                excerpts={interpretation.excerpts}
                knowledgeEvidence={interpretation.knowledgeEvidence}
                label="星命"
              />
            </DualInterpretSummary>
          ) : null}
          {interpretation?.cases?.length ? (
            <section className="xingming-cases">
              <h3>占验课例</h3>
              <ul>
                {interpretation.cases.map((c, i) => (
                  <li key={String(c.id ?? i)}>{String(c.verdict ?? "")}</li>
                ))}
              </ul>
            </section>
          ) : null}
          <div className="form-actions">
            <button type="button" className="secondary" onClick={handleOpenChat}>
              继续对话
            </button>
          </div>
        </section>
      ) : null}
    </div>
  );
}
