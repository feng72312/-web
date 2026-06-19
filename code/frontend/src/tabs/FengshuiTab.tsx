import { useEffect, useState } from "react";
import { useAuth } from "../context/AuthContext";
import { DualInterpretSummary } from "../components/DualInterpretSummary";
import { ClassicIndexPanel } from "../components/ClassicIndexPanel";
import { InterpretModelPicker } from "../components/InterpretModelPicker";
import { InterpretStyleButtons } from "../components/InterpretStyleButtons";
import { BazhaiGrid } from "../components/fengshui/BazhaiGrid";
import { BazhaiSummaryPanel } from "../components/fengshui/BazhaiSummaryPanel";
import { FengshuiCastForm } from "../components/fengshui/FengshuiCastForm";
import { XuankongGrid } from "../components/fengshui/XuankongGrid";
import { XuankongSummaryPanel } from "../components/fengshui/XuankongSummaryPanel";
import { fetchChatStatus } from "../services/chatApi";
import { openModuleAiChatSession } from "../components/ai/moduleChatBridge";
import { createModuleChatSessionRecord } from "../components/ai/moduleSession";
import type { AiChatSession } from "../components/ai/types";
import {
  fetchFengshuiChart,
  fetchFengshuiInterpret,
  fetchFengshuiMountains,
  initFengshuiChatSession,
} from "../services/fengshuiApi";
import { mergeInterpretSummary, type InterpretStyle } from "../utils/interpretStyle";
import type { ChatModelOption } from "../types/bazi";
import type {
  FengshuiChart,
  FengshuiInterpretation,
  FengshuiMethod,
  FengshuiMountain,
  FengshuiScene,
} from "../types/fengshui";
import { VisualWorkbench } from "../components/visual/VisualWorkbench";
import { VisualPanel } from "../components/visual/VisualPanel";
import { VisualEmptyState } from "../components/visual/VisualEmptyState";

interface FengshuiTabProps {
  onOpenAiChatSession: (session: AiChatSession) => void;
}

export function FengshuiTab({ onOpenAiChatSession }: FengshuiTabProps) {
  const { runWithAuth } = useAuth();
  const [question, setQuestion] = useState("");
  const [method, setMethod] = useState<FengshuiMethod>("bazhai");
  const [scene, setScene] = useState<FengshuiScene>("residence");
  const [birthYear, setBirthYear] = useState(1990);
  const [gender, setGender] = useState<0 | 1>(1);
  const [buildYear, setBuildYear] = useState(2020);
  const [flowYear, setFlowYear] = useState("");
  const [sittingMountain, setSittingMountain] = useState("zi");
  const [mountains, setMountains] = useState<FengshuiMountain[]>([]);
  const [loading, setLoading] = useState(false);
  const [interpretStyleLoading, setInterpretStyleLoading] = useState<InterpretStyle | null>(null);
  const [, setLastInterpretStyle] = useState<InterpretStyle | null>(null);
  const [error, setError] = useState("");
  const [chart, setChart] = useState<FengshuiChart | null>(null);
  const [interpretation, setInterpretation] = useState<FengshuiInterpretation | null>(null);
  const [chatEnabled, setChatEnabled] = useState(false);
  const [chatModels, setChatModels] = useState<ChatModelOption[]>([]);
  const [selectedModel, setSelectedModel] = useState("deepseek-chat");

  useEffect(() => {
    fetchFengshuiMountains()
      .then((payload) => setMountains(payload.mountains))
      .catch(() => setMountains([]));
  }, []);

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
    const base = {
      question: question.trim(),
      method,
      scene,
      birthYear,
      gender,
      sittingMountain,
    };
    if (method === "xuankong") {
      const flow = flowYear.trim() ? Number(flowYear) : undefined;
      return { ...base, buildYear, flowYear: flow };
    }
    return base;
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
      const payload = await fetchFengshuiChart(buildRequest());
      setChart(payload.chart);
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
      const full = await fetchFengshuiInterpret(
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
        setError("请先完成排盘");
        return;
      }
      try {
        let agentId = interpretation?.agentId ?? null;
        if (!agentId) {
          const session = await initFengshuiChatSession(
            chart,
            interpretation?.excerpts,
            interpretation?.knowledgeHits,
          );
          agentId = session.agentId;
        }
        await openModuleAiChatSession(
          createModuleChatSessionRecord({
            agentId,
            moduleId: "06",
            moduleLabel: "风水",
            question: chart.input.question,
            chartName: chartTitle,
            subtitle: dayMaster,
          }),
          interpretation,
          onOpenAiChatSession,
        );
      } catch (err) {
        setError(err instanceof Error ? err.message : "对话连接失败");
      }
    });
  };

  const chartTitle =
    chart?.input.method === "xuankong"
      ? chart.xuankong?.label ?? "玄空飞星"
      : chart?.zhaiGua?.label ?? "八宅";
  const dayMaster =
    chart?.input.method === "xuankong"
      ? chart.xuankong?.period.label ?? ""
      : chart?.mingGua?.alias ?? "";

  const isXuankong = method === "xuankong";
  const hasInterpretation =
    interpretation?.summaryProfessional ||
    interpretation?.summaryPlain ||
    interpretation?.summary ||
    (interpretation?.excerpts && interpretation.excerpts.length > 0);

  const stageContent =
    chart && chart.input.method === "bazhai" && chart.mingGua && chart.zhaiGua && chart.palaces ? (
      <VisualPanel
        title="八宅方位盘"
        actions={
          <div className="meta-pills">
            <span className="meta-pill">{chart.mingGua.groupLabel}</span>
            <span className="meta-pill">{chart.zhaiGua.groupLabel}</span>
            <span className={`meta-pill ${chart.compatible ? "meta-pill-accent" : ""}`}>
              {chart.compatible ? "人宅相配" : "人宅不配"}
            </span>
          </div>
        }
      >
        <div className="fengshui-chart-body">
          <BazhaiSummaryPanel chart={chart} />
          <BazhaiGrid palaces={chart.palaces} />
        </div>
      </VisualPanel>
    ) : chart && chart.input.method === "xuankong" && chart.xuankong ? (
      <VisualPanel
        title="玄空飞星盘"
        actions={
          <div className="meta-pills">
            <span className="meta-pill">{chart.xuankong.period.label}</span>
            <span className="meta-pill">{chart.xuankong.period.yuan}</span>
            <span className="meta-pill">{chart.xuankong.label}</span>
          </div>
        }
      >
        <div className="fengshui-chart-body xuankong-chart-body">
          <XuankongSummaryPanel xuankong={chart.xuankong} />
          <div className="xuankong-grids">
            <XuankongGrid cells={chart.xuankong.combinedPan} title="运-山-向合盘" />
            <XuankongGrid cells={chart.xuankong.yunPan} title="运盘" />
            <XuankongGrid cells={chart.xuankong.shanPan} title="山盘" />
            <XuankongGrid cells={chart.xuankong.xiangPan} title="向盘" />
            {chart.xuankong.flowPan && (
              <XuankongGrid cells={chart.xuankong.flowPan} title={`${chart.xuankong.flowYear}流年`} />
            )}
          </div>
        </div>
      </VisualPanel>
    ) : (
      <VisualEmptyState
        theme="fengshui"
        title="罗盘待定向"
        description="填写宅主信息与坐山定向后, 生成八宅或玄空飞星方位盘."
      />
    );

  return (
    <div className="fengshui-tab">
      <VisualWorkbench
        moduleId="fengshui"
        title={isXuankong ? "玄空飞星" : "八宅堪舆"}
        subtitle="罗盘、宅卦、方位、飞星"
        theme="fengshui"
        error={error || undefined}
        input={
          <VisualPanel
            title={isXuankong ? "玄空飞星排盘" : "八宅排盘"}
            hint={
              isXuankong
                ? "按建成/入伙年定元运, 坐山定向排运山向飞星. 可选叠加流年."
                : "按出生年定命卦, 按宅坐山定宅卦, 计算四大吉方与四凶方."
            }
          >
            <FengshuiCastForm
              question={question}
              onQuestionChange={setQuestion}
              method={method}
              onMethodChange={setMethod}
              scene={scene}
              onSceneChange={setScene}
              birthYear={birthYear}
              onBirthYearChange={setBirthYear}
              gender={gender}
              onGenderChange={setGender}
              buildYear={buildYear}
              onBuildYearChange={setBuildYear}
              flowYear={flowYear}
              onFlowYearChange={setFlowYear}
              sittingMountain={sittingMountain}
              onSittingMountainChange={setSittingMountain}
              mountains={mountains}
            />
            <div className="form-actions form-actions-end">
              <button
                type="button"
                className="primary-btn"
                disabled={loading || mountains.length === 0}
                onClick={handleChart}
              >
                {loading ? "排盘中..." : "完成排盘"}
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
            <DualInterpretSummary
              title={isXuankong ? "玄空解读" : "八宅解读"}
              interpretation={interpretation!}
            >
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
