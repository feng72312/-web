import { useEffect, useState } from "react";
import { useAuth } from "../context/AuthContext";
import { BirthForm } from "../components/BirthForm";
import { DualInterpretSummary } from "../components/DualInterpretSummary";
import { ClassicIndexPanel } from "../components/ClassicIndexPanel";
import { InterpretModelPicker } from "../components/InterpretModelPicker";
import { InterpretStyleButtons } from "../components/InterpretStyleButtons";
import { ZiweiAdvancedSettings } from "../components/ziwei/ZiweiAdvancedSettings";
import { ZiweiJudgementPanel } from "../components/ziwei/ZiweiJudgementPanel";
import { ZiweiLimitsPanel } from "../components/ziwei/ZiweiLimitsPanel";
import { ZiweiRulesMetaBar } from "../components/ziwei/ZiweiRulesMetaBar";
import { ZiweiChartModeSwitch } from "../components/ziwei/ZiweiChartModeSwitch";
import { ZiweiPalaceGrid } from "../components/ziwei/ZiweiPalaceGrid";
import { VisualWorkbench } from "../components/visual/VisualWorkbench";
import { VisualPanel } from "../components/visual/VisualPanel";
import { VisualEmptyState } from "../components/visual/VisualEmptyState";
import { fetchChatStatus } from "../services/chatApi";
import { buildZiweiFusionSource } from "../components/ai/fusionSourceBuilder";
import { upsertFusionSource } from "../components/ai/fusionSourceStorage";
import { openModuleAiChatSession } from "../components/ai/moduleChatBridge";
import { createModuleChatSessionRecord } from "../components/ai/moduleSession";
import type { AiChatSession } from "../components/ai/types";
import {
  DEFAULT_ZIWEI_SETTINGS,
  profileToZiweiSettings,
  updateProfileZiweiSettings,
} from "../services/profileStorage";
import { fetchZiweiChart, fetchZiweiInterpret, fetchZiweiJudgement, initZiweiChatSession } from "../services/ziweiApi";
import {
  hasAnyInterpretSummary,
  mergeInterpretSummary,
  type InterpretStyle,
} from "../utils/interpretStyle";
import { deferIdle } from "../utils/deferIdle";
import type { ChatModelOption, PaipanRequest, ZiweiProfileSettings } from "../types/bazi";
import type {
  ZiweiChart,
  ZiweiChartRequest,
  ZiweiDisplayMode,
  ZiweiInterpretation,
  ZiweiJudgementReport,
} from "../types/ziwei";
import "../styles/ziwei.css";

const ZIWEI_CHART_MODE_KEY = "ziwei-chart-mode";

function loadChartMode(): ZiweiDisplayMode {
  try {
    const saved = localStorage.getItem(ZIWEI_CHART_MODE_KEY);
    return saved === "pro" ? "pro" : "simple";
  } catch {
    return "simple";
  }
}

function buildZiweiRequest(
  birth: PaipanRequest,
  settings: ZiweiProfileSettings,
  question: string,
  targetYear: number,
  detailLevel: ZiweiDisplayMode,
): ZiweiChartRequest {
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
    useTrueSolarTime: settings.useTrueSolarTime,
    longitude: settings.longitude,
    targetYear,
    detailLevel,
    question: question.trim(),
    rules: {
      leapMonthRule: settings.leapMonthRule,
      ziHourRule: settings.ziHourRule,
      mutagenTable: settings.mutagenTable ?? "nan_pai",
      chartSchool: settings.chartSchool ?? "sanhe",
    },
  };
}

interface ZiweiTabProps {
  onOpenAiChatSession: (session: AiChatSession) => void;
}

export function ZiweiTab({ onOpenAiChatSession }: ZiweiTabProps) {
  const { runWithAuth } = useAuth();
  const [ziweiSettings, setZiweiSettings] = useState<ZiweiProfileSettings>(DEFAULT_ZIWEI_SETTINGS);
  const [question, setQuestion] = useState("请论此命命宫格局、性情与当前大限流年");
  const [targetYear, setTargetYear] = useState(new Date().getFullYear());
  const [chartMode, setChartMode] = useState<ZiweiDisplayMode>(loadChartMode);
  const [loading, setLoading] = useState(false);
  const [interpretStyleLoading, setInterpretStyleLoading] = useState<InterpretStyle | null>(null);
  const [, setLastInterpretStyle] = useState<InterpretStyle | null>(null);
  const [error, setError] = useState("");
  const [chart, setChart] = useState<ZiweiChart | null>(null);
  const [lastBirth, setLastBirth] = useState<PaipanRequest | null>(null);
  const [activeProfileId, setActiveProfileId] = useState<string | null>(null);
  const [interpretation, setInterpretation] = useState<ZiweiInterpretation | null>(null);
  const [judgement, setJudgement] = useState<ZiweiJudgementReport | null>(null);
  const [judgementLoading, setJudgementLoading] = useState(false);
  const [chatEnabled, setChatEnabled] = useState(false);
  const [chatModels, setChatModels] = useState<ChatModelOption[]>([]);
  const [selectedModel, setSelectedModel] = useState("deepseek-chat");

  useEffect(() => {
    fetchChatStatus()
      .then((status) => {
        setChatEnabled(status.enabled);
        setChatModels(status.models ?? []);
        if (status.model) setSelectedModel(status.model);
      })
      .catch(() => setChatEnabled(false));
  }, []);

  const loadJudgement = async (nextChart: ZiweiChart, year = targetYear, useRag = false) => {
    setJudgementLoading(true);
    try {
      const result = await fetchZiweiJudgement(
        nextChart,
        nextChart.input.question ?? question,
        year,
        nextChart.rulesMeta?.chartSchool,
        useRag,
      );
      setJudgement(result.judgement);
    } catch {
      setJudgement(null);
    } finally {
      setJudgementLoading(false);
    }
  };

  const runChart = async (
    birth: PaipanRequest,
    year = targetYear,
    mode: ZiweiDisplayMode = chartMode,
  ) => {
    setLoading(true);
    setError("");
    setInterpretation(null);
    setJudgement(null);
    try {
      const payload = await fetchZiweiChart(
        buildZiweiRequest(birth, ziweiSettings, question, year, mode),
      );
      setChart(payload.chart);
      setLastBirth(birth);
      await loadJudgement(payload.chart, year, false);
      window.requestAnimationFrame(() => {
        document
          .querySelector(".ziwei-tab .visual-workbench-stage")
          ?.scrollIntoView({ behavior: "smooth", block: "nearest" });
      });
      deferIdle(() => {
        upsertFusionSource(
          buildZiweiFusionSource({
            chart: payload.chart as unknown as Record<string, unknown>,
            question: payload.chart.input.question ?? question,
            chartName: payload.chart.meta.bureau,
            subtitle: payload.chart.palaces[0]?.stemBranch ?? "",
          }),
        );
      });
    } catch (err) {
      const message = err instanceof Error ? err.message : "排盘失败";
      setError(message);
      setChart(null);
    } finally {
      setLoading(false);
    }
  };

  const handleBirthSubmit = (birth: PaipanRequest) => {
    void runChart(birth);
  };

  const handleTargetYearChange = (year: number) => {
    setTargetYear(year);
    if (lastBirth && chartMode === "pro") {
      void runChart(lastBirth, year, "pro");
    }
  };

  const handleChartModeChange = (mode: ZiweiDisplayMode) => {
    setChartMode(mode);
    try {
      localStorage.setItem(ZIWEI_CHART_MODE_KEY, mode);
    } catch {
      /* ignore storage errors */
    }
    if (lastBirth) {
      void runChart(lastBirth, targetYear, mode);
    }
  };

  const handleZiweiSettingsChange = (patch: Partial<ZiweiProfileSettings>) => {
    setZiweiSettings((prev) => {
      const next = { ...prev, ...patch };
      if (activeProfileId) {
        updateProfileZiweiSettings(activeProfileId, next);
      }
      return next;
    });
  };

  const handleInterpret = async (style: InterpretStyle) => {
    if (!chart) return;
    setInterpretStyleLoading(style);
    setLastInterpretStyle(style);
    setError("");
    try {
      const full = await fetchZiweiInterpret(
        chart,
        interpretation?.excerpts,
        selectedModel,
        style,
        question,
      );
      setInterpretation((prev) => {
        const merged = {
          ...full.interpretation,
          ...mergeInterpretSummary(prev, full.interpretation.summary, style),
        };
        if (full.interpretation.judgement) {
          setJudgement(full.interpretation.judgement);
        }
        if (chart) {
          upsertFusionSource(
            buildZiweiFusionSource({
              chart: chart as unknown as Record<string, unknown>,
              question: chart.input.question ?? question,
              chartName: chart.meta.bureau,
              subtitle: chart.palaces[0]?.stemBranch ?? "",
              summaryPlain: merged.summaryPlain,
              summaryProfessional: merged.summaryProfessional,
              agentId: merged.agentId,
            }),
          );
        }
        return merged;
      });
    } catch (err) {
      setError(err instanceof Error ? err.message : "解读失败");
    } finally {
      setInterpretStyleLoading(null);
    }
  };

  const handleOpenChat = () => {
    runWithAuth(async () => {
      if (!chart) {
        setError("请先排盘");
        return;
      }
      try {
        let agentId = interpretation?.agentId ?? null;
        if (!agentId) {
          const session = await initZiweiChatSession(
            chart,
            interpretation?.excerpts,
            interpretation?.knowledgeHits,
          );
          agentId = session.agentId;
        }
        const fusionSource = buildZiweiFusionSource({
          chart: chart as unknown as Record<string, unknown>,
          question: chart.input.question ?? question,
          chartName: chart.meta.bureau,
          subtitle: chart.palaces[0]?.stemBranch ?? "",
          summaryPlain: interpretation?.summaryPlain,
          summaryProfessional: interpretation?.summaryProfessional,
          agentId,
        });
        await openModuleAiChatSession(
          createModuleChatSessionRecord({
            agentId,
            moduleId: "11",
            moduleLabel: "紫微",
            question: chart.input.question ?? question,
            chartName: chart.meta.bureau,
            subtitle: chart.palaces[0]?.stemBranch ?? "",
          }),
          interpretation,
          onOpenAiChatSession,
          fusionSource,
        );
      } catch (err) {
        setError(err instanceof Error ? err.message : "对话连接失败");
      }
    });
  };

  const hasInterpretation =
    hasAnyInterpretSummary(interpretation) ||
    (interpretation?.excerpts && interpretation.excerpts.length > 0);

  const displayChart = judgement?.enrichedChart ?? chart;

  const stageContent = chart ? (
    <>
      <VisualPanel title={chartMode === "simple" ? "紫微简易盘" : "紫微专业盘"}>
        <ZiweiRulesMetaBar chart={displayChart ?? chart} />
        <ZiweiChartModeSwitch mode={chartMode} loading={loading} onChange={handleChartModeChange} />
        <ZiweiPalaceGrid
          chart={displayChart ?? chart}
          mode={chartMode}
          targetYear={targetYear}
          onTargetYearChange={handleTargetYearChange}
          judgement={judgement}
        />
      </VisualPanel>
      <ZiweiJudgementPanel judgement={judgement} loading={judgementLoading} />
    </>
  ) : (
    <VisualEmptyState
      theme="astro"
      title="命盘待生成"
      description="填写出生信息后生成十二宫星曜盘"
    />
  );

  return (
    <div className="ziwei-tab">
      <VisualWorkbench
        moduleId="ziwei"
        title="紫微斗数"
        subtitle="十二宫、四化飞星、大限流年"
        theme="astro"
        inputPlacement="top"
        error={error || undefined}
        input={
          <VisualPanel
            title="紫微斗数排盘"
            hint="默认简易排盘更快; 需要流年/流月/层级高亮时再切专业排盘."
          >
            <BirthForm
              embedded
              loading={loading}
              onSubmit={handleBirthSubmit}
              onProfileLoad={(profile) => {
                setActiveProfileId(profile.id);
                setZiweiSettings(profileToZiweiSettings(profile));
              }}
            />
            <section className="cast-form-section ziwei-extra-section">
              <ZiweiAdvancedSettings
                settings={ziweiSettings}
                onChange={handleZiweiSettingsChange}
              />
              <label className="field field-grow">
                <span>问事 (解读用)</span>
                <input
                  type="text"
                  value={question}
                  maxLength={200}
                  placeholder="例如: 论事业与财运大势"
                  onChange={(e) => setQuestion(e.target.value)}
                />
              </label>
            </section>
          </VisualPanel>
        }
        stage={stageContent}
        oracle={
          chart ? (
            <VisualPanel title="典籍与解读" accent>
              <details className="ziwei-limits-fold">
                <summary>展开传统运限列表</summary>
                <ZiweiLimitsPanel
                  chart={chart}
                  targetYear={targetYear}
                  onTargetYearChange={handleTargetYearChange}
                />
              </details>
              <InterpretModelPicker
                models={chatModels}
                value={selectedModel}
                onChange={setSelectedModel}
                chatEnabled={chatEnabled}
                disabled={interpretStyleLoading !== null}
              />
              <InterpretStyleButtons
                professionalLoading={interpretStyleLoading === "professional"}
                plainLoading={interpretStyleLoading === "plain"}
                disabled={!chart}
                onLoadingStart={setInterpretStyleLoading}
                onProfessional={() => runWithAuth(() => handleInterpret("professional"))}
                onPlain={() => runWithAuth(() => handleInterpret("plain"))}
              />
              {chatEnabled && (
                <div className="action-row">
                  <button type="button" className="secondary" onClick={handleOpenChat}>
                    打开 AI 对话
                  </button>
                </div>
              )}
            </VisualPanel>
          ) : undefined
        }
        interpretation={
          hasInterpretation ? (
            <DualInterpretSummary title="紫微解读" interpretation={interpretation!}>
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
