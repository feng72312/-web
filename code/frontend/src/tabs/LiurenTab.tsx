import { useEffect, useState } from "react";
import { DualInterpretSummary } from "../components/DualInterpretSummary";
import { RagExcerptList } from "../components/RagExcerptList";
import { InterpretModelPicker } from "../components/InterpretModelPicker";
import { InterpretStyleButtons } from "../components/InterpretStyleButtons";
import { ChatPanel } from "../components/ChatPanel";
import { JinkouPanel } from "../components/liuren/JinkouPanel";
import { LiurenCastForm } from "../components/liuren/LiurenCastForm";
import { ShenShaPanel } from "../components/liuren/ShenShaPanel";
import { SiKeSanChuanPanel } from "../components/liuren/SiKeSanChuanPanel";
import { TianDiPanGrid } from "../components/liuren/TianDiPanGrid";
import { fetchChatStatus } from "../services/chatApi";
import {
  fetchLiurenChart,
  fetchLiurenInterpret,
  fetchLiurenRagSearch,
  initLiurenChatSession,
} from "../services/liurenApi";
import { mergeInterpretSummary, type InterpretStyle } from "../utils/interpretStyle";
import type { ChatModelOption } from "../types/bazi";
import type { CalendarType } from "../types/bazi";
import { todayYmd } from "../utils/castCalendar";
import type {
  LiurenCastMethod,
  LiurenCategory,
  LiurenChart,
  LiurenInterpretation,
} from "../types/liuren";

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

export function LiurenTab() {
  const [question, setQuestion] = useState("");
  const [category, setCategory] = useState<LiurenCategory>("shizhan");
  const [castMethod, setCastMethod] = useState<LiurenCastMethod>("both");
  const [jinkouDifen, setJinkouDifen] = useState("");
  const [guiRenMode, setGuiRenMode] = useState(0);
  const [useTrueSolarTime, setUseTrueSolarTime] = useState(false);
  const [longitude, setLongitude] = useState("120");
  const [useNow, setUseNow] = useState(true);
  const [datetime, setDatetime] = useState(toDatetimeLocal(new Date()));
  const [calendarType, setCalendarType] = useState<CalendarType>("solar");
  const [isLeapMonth, setIsLeapMonth] = useState(false);
  const [calYear, setCalYear] = useState(() => todayYmd().year);
  const [calMonth, setCalMonth] = useState(() => todayYmd().month);
  const [calDay, setCalDay] = useState(() => todayYmd().day);
  const [loading, setLoading] = useState(false);
  const [ragLoading, setRagLoading] = useState(false);
  const [interpretStyleLoading, setInterpretStyleLoading] = useState<InterpretStyle | null>(null);
  const [lastInterpretStyle, setLastInterpretStyle] = useState<InterpretStyle | null>(null);
  const [error, setError] = useState("");
  const [chart, setChart] = useState<LiurenChart | null>(null);
  const [interpretation, setInterpretation] = useState<LiurenInterpretation | null>(null);
  const [chatAgentId, setChatAgentId] = useState<string | null>(null);
  const [chatEnabled, setChatEnabled] = useState(false);
  const [chatModels, setChatModels] = useState<ChatModelOption[]>([]);
  const [selectedModel, setSelectedModel] = useState("deepseek-chat");
  const [showChat, setShowChat] = useState(false);

  useEffect(() => {
    if (!useNow) {
      return;
    }
    const today = todayYmd();
    setCalYear(today.year);
    setCalMonth(today.month);
    setCalDay(today.day);
  }, [useNow]);

  useEffect(() => {
    fetchChatStatus()
      .then((status) => {
        setChatEnabled(status.enabled);
        setChatModels(status.models ?? []);
        if (status.model) setSelectedModel(status.model);
      })
      .catch(() => setChatEnabled(false));
  }, []);

  const buildRequest = () => {
    const timeParts = useNow
      ? parseDatetimeLocal(toDatetimeLocal(new Date()))
      : parseDatetimeLocal(datetime);
    return {
      question: question.trim(),
      category,
      castMethod,
      jinkouDifen,
      guiRenMode,
      useTrueSolarTime,
      longitude: Number(longitude) || 120,
      calendarType,
      isLeapMonth,
      year: calYear,
      month: calMonth,
      day: calDay,
      hour: timeParts.hour,
      minute: timeParts.minute,
      second: timeParts.second,
    };
  };

  const handleChart = async () => {
    if (!question.trim()) {
      setError("请先输入问事内容");
      return;
    }
    setLoading(true);
    setError("");
    setInterpretation(null);
    setChatAgentId(null);
    try {
      const payload = await fetchLiurenChart(buildRequest());
      setChart(payload.chart);
    } catch (err) {
      setError(err instanceof Error ? err.message : "起课失败");
      setChart(null);
    } finally {
      setLoading(false);
    }
  };

  const handleRagSearch = async () => {
    if (!chart) return;
    setRagLoading(true);
    setError("");
    try {
      const rag = await fetchLiurenRagSearch(chart, question);
      setInterpretation((prev) => ({
        query: rag.query,
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
      const full = await fetchLiurenInterpret(
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
      setError("请先完成起课");
      return;
    }
    try {
      const session = await initLiurenChatSession(
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

  const lr = chart?.liuren;
  const jk = chart?.jinkou;

  if (showChat && chart) {
    const title = lr?.geJu.name || jk?.renYuan || "大六壬";
    return (
      <div className="liuren-tab chat-mode">
        <ChatPanel
          layout="page"
          agentId={chatAgentId}
          chartName={title}
          dayMaster={lr?.yueJiang ?? jk?.difen ?? ""}
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
    <div className="liuren-tab">
      <section className="panel">
        <h2>大六壬起课</h2>
        <p className="hint">以占时四柱起课, 不引用用户八字. 含正六壬与金口诀.</p>
        <LiurenCastForm
          question={question}
          onQuestionChange={setQuestion}
          category={category}
          onCategoryChange={setCategory}
          castMethod={castMethod}
          onCastMethodChange={setCastMethod}
          jinkouDifen={jinkouDifen}
          onJinkouDifenChange={setJinkouDifen}
          guiRenMode={guiRenMode}
          onGuiRenModeChange={setGuiRenMode}
          useTrueSolarTime={useTrueSolarTime}
          onUseTrueSolarTimeChange={setUseTrueSolarTime}
          longitude={longitude}
          onLongitudeChange={setLongitude}
          useNow={useNow}
          onUseNowChange={setUseNow}
          datetime={datetime}
          onDatetimeChange={setDatetime}
          calendarType={calendarType}
          onCalendarTypeChange={setCalendarType}
          isLeapMonth={isLeapMonth}
          onIsLeapMonthChange={setIsLeapMonth}
          calYear={calYear}
          onCalYearChange={setCalYear}
          calMonth={calMonth}
          onCalMonthChange={setCalMonth}
          calDay={calDay}
          onCalDayChange={setCalDay}
        />
        <button
          type="button"
          className="primary-btn"
          disabled={loading}
          onClick={handleChart}
        >
          {loading ? "起课中..." : "完成起课"}
        </button>
      </section>

      {error && <div className="error-box">{error}</div>}

      {chart && (
        <>
          {lr && (
            <section className="panel">
              <h2>六壬课盘</h2>
              <p className="meta-line">
                占时四柱: {lr.fourPillars.year} {lr.fourPillars.month}{" "}
                {lr.fourPillars.day} {lr.fourPillars.hour}
                {chart.trueSolarTime ? ` | 真太阳 ${chart.trueSolarTime}` : ""}
              </p>
              <SiKeSanChuanPanel pan={lr} />
              <TianDiPanGrid pan={lr} />
              <ShenShaPanel shenSha={lr.shenSha} />
            </section>
          )}
          {jk && (
            <section className="panel">
              <JinkouPanel jinkou={jk} />
            </section>
          )}

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
              <button
                type="button"
                className="secondary"
                disabled={ragLoading}
                onClick={handleRagSearch}
              >
                {ragLoading ? "检索中..." : "检索知识库"}
              </button>
              <button
                type="button"
                className="secondary"
                disabled={!chatEnabled}
                onClick={handleOpenChat}
              >
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
            interpretation?.summary ||
            (interpretation?.excerpts && interpretation.excerpts.length > 0)) && (
            <DualInterpretSummary title="六壬解读" interpretation={interpretation}>
              {interpretation.query && (
                <details open={!interpretation.summaryProfessional && !interpretation.summaryPlain}>
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
