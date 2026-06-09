import { useEffect, useState } from "react";
import { useAuth } from "../context/AuthContext";
import { DualInterpretSummary } from "../components/DualInterpretSummary";
import { RagExcerptList } from "../components/RagExcerptList";
import { InterpretModelPicker } from "../components/InterpretModelPicker";
import { InterpretStyleButtons } from "../components/InterpretStyleButtons";
import { ChatPanel } from "../components/ChatPanel";
import { QimenCastForm } from "../components/qimen/QimenCastForm";
import { QimenGrid } from "../components/qimen/QimenGrid";
import { QimenJuPanel } from "../components/qimen/QimenJuPanel";
import { fetchChatStatus } from "../services/chatApi";
import {
  fetchQimenChart,
  fetchQimenInterpret,
  initQimenChatSession,
} from "../services/qimenApi";
import { mergeInterpretSummary, type InterpretStyle } from "../utils/interpretStyle";
import type { ChatModelOption } from "../types/bazi";
import { loadBaziBirthProfile } from "../utils/baziChartCache";
import { todayYmd } from "../utils/castCalendar";
import type { CalendarType } from "../types/bazi";
import type {
  BirthProfileSummary,
  QimenCategory,
  QimenChart,
  QimenInterpretation,
  QimenMethod,
} from "../types/qimen";

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

export function QimenTab() {
  const { runWithAuth } = useAuth();
  const [question, setQuestion] = useState("");
  const [category, setCategory] = useState<QimenCategory>("shizhan");
  const [method, setMethod] = useState<QimenMethod>("chaibu");
  const [direction, setDirection] = useState("");
  const [useTrueSolarTime, setUseTrueSolarTime] = useState(false);
  const [longitude, setLongitude] = useState("120");
  const [juOverride, setJuOverride] = useState("");
  const [useNow, setUseNow] = useState(true);
  const [datetime, setDatetime] = useState(toDatetimeLocal(new Date()));
  const [calendarType, setCalendarType] = useState<CalendarType>("solar");
  const [isLeapMonth, setIsLeapMonth] = useState(false);
  const [calYear, setCalYear] = useState(() => todayYmd().year);
  const [calMonth, setCalMonth] = useState(() => todayYmd().month);
  const [calDay, setCalDay] = useState(() => todayYmd().day);
  const [loading, setLoading] = useState(false);
  const [interpretStyleLoading, setInterpretStyleLoading] = useState<InterpretStyle | null>(null);
  const [, setLastInterpretStyle] = useState<InterpretStyle | null>(null);
  const [error, setError] = useState("");
  const [chart, setChart] = useState<QimenChart | null>(null);
  const [interpretation, setInterpretation] = useState<QimenInterpretation | null>(null);
  const [chatAgentId, setChatAgentId] = useState<string | null>(null);
  const [chatEnabled, setChatEnabled] = useState(false);
  const [chatModels, setChatModels] = useState<ChatModelOption[]>([]);
  const [selectedModel, setSelectedModel] = useState("deepseek-chat");
  const [showChat, setShowChat] = useState(false);
  const [useBirthProfile, setUseBirthProfile] = useState(false);
  const [birthProfile, setBirthProfile] = useState<BirthProfileSummary | null>(null);

  useEffect(() => {
    setBirthProfile(loadBaziBirthProfile());
  }, []);

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
    const ju =
      juOverride.trim() !== ""
        ? Number(juOverride)
        : undefined;
    const bp =
      useBirthProfile && birthProfile ? birthProfile : undefined;
    return {
      question: question.trim(),
      category,
      method,
      direction,
      useTrueSolarTime,
      longitude: Number(longitude) || 120,
      juOverride: ju && ju >= 1 && ju <= 9 ? ju : undefined,
      calendarType,
      isLeapMonth,
      year: calYear,
      month: calMonth,
      day: calDay,
      hour: timeParts.hour,
      minute: timeParts.minute,
      second: timeParts.second,
      birthProfile: bp,
    };
  };

  const birthHint = birthProfile
    ? `${birthProfile.summary} ${birthProfile.year} ${birthProfile.month} ${birthProfile.day} ${birthProfile.hour}`
    : "请先在八字 Tab 排盘, 再勾选此项";

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
      const payload = await fetchQimenChart(buildRequest());
      setChart(payload.chart);
    } catch (err) {
      setError(err instanceof Error ? err.message : "起局失败");
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
      const bp =
        useBirthProfile && birthProfile ? birthProfile : chart.birthProfile;
      const full = await fetchQimenInterpret(
        chart,
        interpretation?.excerpts,
        selectedModel,
        bp ?? undefined,
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
        setError("请先完成起局");
        return;
      }
      try {
        const bp =
          useBirthProfile && birthProfile ? birthProfile : chart.birthProfile;
        const session = await initQimenChatSession(
          chart,
          interpretation?.excerpts,
          interpretation?.knowledgeHits,
          bp ?? undefined,
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
      <div className="qimen-tab chat-mode">
        <ChatPanel
          layout="page"
          agentId={chatAgentId}
          chartName={chart.ju.juName}
          dayMaster={`${chart.zhiFuZhiShi.zhiFuStar} ${chart.zhiFuZhiShi.zhiShiDoor}`}
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
    <div className="qimen-tab discipline-page">
      <section className="panel panel-cast">
        <div className="panel-head">
          <div>
            <h2>奇门起局</h2>
            <p className="hint">
              以起局时刻排盘, 不引用用户八字. 默认拆补法, 可选置闰与茅山.
            </p>
          </div>
        </div>
        <QimenCastForm
          question={question}
          onQuestionChange={setQuestion}
          category={category}
          onCategoryChange={setCategory}
          method={method}
          onMethodChange={setMethod}
          direction={direction}
          onDirectionChange={setDirection}
          useTrueSolarTime={useTrueSolarTime}
          onUseTrueSolarTimeChange={setUseTrueSolarTime}
          longitude={longitude}
          onLongitudeChange={setLongitude}
          juOverride={juOverride}
          onJuOverrideChange={setJuOverride}
          useNow={useNow}
          onUseNowChange={setUseNow}
          datetime={datetime}
          onDatetimeChange={setDatetime}
          useBirthProfile={useBirthProfile}
          onUseBirthProfileChange={setUseBirthProfile}
          birthProfileHint={birthHint}
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
        <div className="form-actions form-actions-end">
          <button
            type="button"
            className="primary-btn"
            disabled={loading}
            onClick={handleChart}
          >
            {loading ? "起局中..." : "完成起局"}
          </button>
        </div>
      </section>

      {error && <div className="error-box">{error}</div>}

      {chart && (
        <>
          <section className="panel panel-chart">
            <div className="panel-head">
              <h2>奇门九宫</h2>
            </div>
            <div className="qimen-chart-body">
            <QimenJuPanel
              ju={chart.ju}
              zhiFuZhiShi={chart.zhiFuZhiShi}
              fourPillars={chart.fourPillars}
              trueSolarTime={chart.trueSolarTime}
              meta={chart.meta}
            />
            <QimenGrid palaces={chart.palaces} />
            </div>
          </section>

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
                disabled={!chatEnabled}
                onClick={handleOpenChat}
              >
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
            interpretation?.summary ||
            (interpretation?.excerpts && interpretation.excerpts.length > 0)) && (
            <DualInterpretSummary title="奇门解读" interpretation={interpretation}>
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
