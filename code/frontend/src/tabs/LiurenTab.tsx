import { useEffect, useState } from "react";
import { useAuth } from "../context/AuthContext";
import { DualInterpretSummary } from "../components/DualInterpretSummary";
import { ClassicIndexPanel } from "../components/ClassicIndexPanel";
import { InterpretModelPicker } from "../components/InterpretModelPicker";
import { InterpretStyleButtons } from "../components/InterpretStyleButtons";
import { JinkouPanel } from "../components/liuren/JinkouPanel";
import { LiurenCastForm } from "../components/liuren/LiurenCastForm";
import { ShenShaPanel } from "../components/liuren/ShenShaPanel";
import { SiKeSanChuanPanel } from "../components/liuren/SiKeSanChuanPanel";
import { TianDiPanGrid } from "../components/liuren/TianDiPanGrid";
import { fetchChatStatus } from "../services/chatApi";
import { openModuleAiChatSession } from "../components/ai/moduleChatBridge";
import { createModuleChatSessionRecord } from "../components/ai/moduleSession";
import type { AiChatSession } from "../components/ai/types";
import {
  fetchLiurenChart,
  fetchLiurenInterpret,
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
import { VisualWorkbench } from "../components/visual/VisualWorkbench";
import { VisualPanel } from "../components/visual/VisualPanel";
import { VisualEmptyState } from "../components/visual/VisualEmptyState";

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

interface LiurenTabProps {
  onOpenAiChatSession: (session: AiChatSession) => void;
}

export function LiurenTab({ onOpenAiChatSession }: LiurenTabProps) {
  const { runWithAuth } = useAuth();
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
  const [interpretStyleLoading, setInterpretStyleLoading] = useState<InterpretStyle | null>(null);
  const [, setLastInterpretStyle] = useState<InterpretStyle | null>(null);
  const [error, setError] = useState("");
  const [chart, setChart] = useState<LiurenChart | null>(null);
  const [interpretation, setInterpretation] = useState<LiurenInterpretation | null>(null);
  const [chatEnabled, setChatEnabled] = useState(false);
  const [chatModels, setChatModels] = useState<ChatModelOption[]>([]);
  const [selectedModel, setSelectedModel] = useState("deepseek-chat");

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
    } catch (err) {
      setError(err instanceof Error ? err.message : "解读失败");
    } finally {
      setInterpretStyleLoading(null);
    }
  };

  const handleOpenChat = () => {
    runWithAuth(async () => {
      if (!chart) {
        setError("请先完成起课");
        return;
      }
      try {
        let agentId = interpretation?.agentId ?? null;
        if (!agentId) {
          const session = await initLiurenChatSession(
            chart,
            interpretation?.excerpts,
            interpretation?.knowledgeHits,
          );
          agentId = session.agentId;
        }
        const title = chart.liuren?.geJu.name || chart.jinkou?.renYuan || "大六壬";
        await openModuleAiChatSession(
          createModuleChatSessionRecord({
            agentId,
            moduleId: "05",
            moduleLabel: "六壬",
            question: chart.input.question,
            chartName: title,
            subtitle: chart.liuren?.yueJiang ?? chart.jinkou?.difen ?? "",
          }),
          interpretation,
          onOpenAiChatSession,
        );
      } catch (err) {
        setError(err instanceof Error ? err.message : "对话连接失败");
      }
    });
  };

  const lr = chart?.liuren;
  const jk = chart?.jinkou;

  const hasInterpretation =
    interpretation?.summaryProfessional ||
    interpretation?.summaryPlain ||
    interpretation?.summary ||
    (interpretation?.excerpts && interpretation.excerpts.length > 0);

  const stageContent = chart ? (
    <>
      {lr && (
        <VisualPanel
          title="六壬课盘"
          actions={
            <div className="meta-pills">
              <span className="meta-pill">
                {lr.fourPillars.year} {lr.fourPillars.month}{" "}
                {lr.fourPillars.day} {lr.fourPillars.hour}
              </span>
              {chart.trueSolarTime && (
                <span className="meta-pill meta-pill-accent">
                  真太阳 {chart.trueSolarTime}
                </span>
              )}
              <span className="meta-pill">{lr.geJu.name}</span>
            </div>
          }
        >
          <div className="liuren-chart-body">
            <SiKeSanChuanPanel pan={lr} />
            <TianDiPanGrid pan={lr} />
            <ShenShaPanel shenSha={lr.shenSha} />
          </div>
        </VisualPanel>
      )}
      {jk && (
        <VisualPanel title="金口诀">
          <JinkouPanel jinkou={jk} />
        </VisualPanel>
      )}
    </>
  ) : (
    <VisualEmptyState
      theme="liuren"
      title="课盘待起课"
      description="填写问事与占时四柱后, 生成天地盘、四课三传与神将课盘."
    />
  );

  return (
    <div className="liuren-tab">
      <VisualWorkbench
        moduleId="liuren"
        title="大六壬"
        subtitle="天地盘、四课三传、神将、人事推演"
        theme="liuren"
        error={error || undefined}
        input={
          <VisualPanel
            title="大六壬起课"
            hint="以占时四柱起课, 不引用用户八字. 支持正六壬、金口诀或二者同排."
          >
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
            <div className="form-actions form-actions-end">
              <button
                type="button"
                className="primary-btn"
                disabled={loading}
                onClick={handleChart}
              >
                {loading ? "起课中..." : "完成起课"}
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
            </VisualPanel>
          ) : undefined
        }
        interpretation={
          hasInterpretation ? (
            <DualInterpretSummary title="六壬解读" interpretation={interpretation!}>
              <ClassicIndexPanel
                query={interpretation?.query}
                excerpts={interpretation?.excerpts}
              />
            </DualInterpretSummary>
          ) : undefined
        }
      />
    </div>
  );
}
