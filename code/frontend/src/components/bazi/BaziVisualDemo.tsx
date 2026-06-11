import { useEffect, useState } from "react";
import { useAuth } from "../../context/AuthContext";
import { AnalysisPanels } from "../AnalysisPanels";
import { BirthForm } from "../BirthForm";
import { ChannelRagEvidence } from "../ChannelRagEvidence";
import { FusionChannelsPanel } from "../FusionChannelsPanel";
import { InterpretBlock } from "../InterpretBlock";
import { InterpretMarkdown } from "../InterpretMarkdown";
import { InterpretModelPicker } from "../InterpretModelPicker";
import { InterpretStyleButtons } from "../InterpretStyleButtons";
import { LuckTimelineView } from "../LuckTimelineView";
import { PillarDetailView } from "../PillarDetailView";
import { RagExcerptList } from "../RagExcerptList";
import { SceneTemplatePicker } from "../SceneTemplatePicker";
import type { RagStatus } from "../../services/ragApi";
import type {
  ChatModelOption,
  Interpretation,
  LuckTimeline,
  PaipanRequest,
  PaipanResponse,
} from "../../types/bazi";
import type { InterpretStyle } from "../../utils/interpretStyle";
import { MysticBaziSummary } from "./MysticBaziSummary";
import { MysticFourPillars } from "./MysticFourPillars";
import "../../styles/bazi-visual-demo.css";

type DemoView = "main" | "pillars" | "luck";

interface BaziVisualDemoProps {
  error: string;
  paipanLoading: boolean;
  luckLoading: boolean;
  result: PaipanResponse | null;
  lastRequest: PaipanRequest | null;
  luckTimeline: LuckTimeline | null;
  interpretation: Interpretation | null;
  chatEnabled: boolean;
  chatModels: ChatModelOption[];
  selectedModel: string;
  onModelChange: (modelId: string) => void;
  interpretStyleLoading: InterpretStyle | null;
  interpretQuestion: string;
  onInterpretQuestionChange: (value: string) => void;
  ragStatus: RagStatus | null;
  onOpenAiChat: () => void;
  onSubmit: (data: PaipanRequest) => void;
  onOpenLuck: () => void;
  onInterpret: (style: InterpretStyle) => void;
  onInterpretStyleLoading: (style: InterpretStyle | null) => void;
  buildProfessionalCopyText: () => string;
}

export function BaziVisualDemo({
  error,
  paipanLoading,
  luckLoading,
  result,
  lastRequest,
  luckTimeline,
  interpretation,
  chatEnabled,
  chatModels,
  selectedModel,
  onModelChange,
  interpretStyleLoading,
  interpretQuestion,
  onInterpretQuestionChange,
  ragStatus,
  onOpenAiChat,
  onSubmit,
  onOpenLuck,
  onInterpret,
  onInterpretStyleLoading,
  buildProfessionalCopyText,
}: BaziVisualDemoProps) {
  const { runWithAuth } = useAuth();
  const [demoView, setDemoView] = useState<DemoView>("main");

  useEffect(() => {
    document.body.classList.add("bazi-visual-immersive");
    return () => document.body.classList.remove("bazi-visual-immersive");
  }, []);

  useEffect(() => {
    if (!result) {
      setDemoView("main");
    }
  }, [result]);

  const chart = result?.chart;
  const pillarDetail = chart?.pillarDetail;
  const ragExcerpts =
    interpretation?.excerpts?.filter((item) => item.source !== "stub") ?? [];
  const hasRagExcerpts = ragExcerpts.length > 0;

  const handleOpenLuck = async () => {
    if (luckTimeline) {
      setDemoView("luck");
      return;
    }
    setDemoView("luck");
    await onOpenLuck();
  };

  if (demoView === "pillars" && pillarDetail) {
    return (
      <div className="bazi-visual-demo bazi-visual-subview">
        <PillarDetailView detail={pillarDetail} onBack={() => setDemoView("main")} />
      </div>
    );
  }

  if (demoView === "luck" && luckLoading) {
    return (
      <div className="bazi-visual-demo bazi-visual-subview">
        <section className="bazi-visual-loading panel">
          <p>正在加载大运流年, 首次约需 1 秒...</p>
          <button type="button" className="bazi-ghost-button" onClick={() => setDemoView("main")}>
            返回
          </button>
        </section>
      </div>
    );
  }

  if (demoView === "luck" && luckTimeline) {
    return (
      <div className="bazi-visual-demo bazi-visual-subview">
        <LuckTimelineView timeline={luckTimeline} onBack={() => setDemoView("main")} />
      </div>
    );
  }

  return (
    <div className="bazi-visual-demo">
      <header className="bazi-visual-topbar">
        <div>
          <p className="bazi-visual-kicker">Ziyun Destiny Observatory</p>
          <h2>八字命理</h2>
        </div>
        <div className="bazi-visual-topmeta">
          {chart?.input.name && <span>{chart.input.name}</span>}
          {chart?.dayMaster && <span>日主 {chart.dayMaster}</span>}
        </div>
      </header>

      {error && <div className="bazi-visual-error">{error}</div>}

      <div className="bazi-visual-grid">
        <aside className="bazi-ritual-panel">
          <section className="bazi-vellum-card">
            <span className="bazi-card-eyebrow">Birth Record</span>
            <BirthForm embedded loading={paipanLoading} onSubmit={onSubmit} />
          </section>
        </aside>

        <main className="bazi-altar">
          <div className="bazi-altar-head">
            <div>
              <p className="bazi-visual-kicker">Four Pillars</p>
              <h3>{chart ? "命盘已立" : "填写出生信息, 开启排盘"}</h3>
            </div>
            {chart && (
              <strong>
                {chart.input.name || "命主"} · {chart.dayMaster}
              </strong>
            )}
          </div>

          {chart ? (
            <MysticFourPillars
              chart={chart}
              luckLoading={luckLoading}
              onOpenDetail={() => pillarDetail && setDemoView("pillars")}
              onOpenLuck={handleOpenLuck}
            />
          ) : (
            <div className="mystic-pillars-empty">
              <span>等待排盘</span>
              <p>左侧填写真实出生信息并点击「开始排盘」后, 这里会展开四柱玉牌命盘。</p>
            </div>
          )}

          {chart && result && (
            <section className="bazi-analysis-wrap">
              <span className="bazi-card-eyebrow">Analysis</span>
              <AnalysisPanels chart={chart} sections={result.sections} />
            </section>
          )}
        </main>

        <aside className="bazi-oracle-panel">
          {chart ? (
            <section className="bazi-oracle-card">
              <span className="bazi-card-eyebrow">Chart Notes</span>
              <MysticBaziSummary chart={chart} />
            </section>
          ) : (
            <section className="bazi-oracle-card">
              <span className="bazi-card-eyebrow">Ritual</span>
              <h3>如何开始</h3>
              <p>先录入真实出生信息。排盘完成后, 中央会亮起四柱玉牌, 右侧展示五行与 AI 解读工作台。</p>
            </section>
          )}

          <section className="bazi-oracle-card bazi-ai-card">
            <span className="bazi-card-eyebrow">AI Reading</span>
            {ragStatus && !ragStatus.serviceOk && (
              <p className="bazi-rag-hint">典籍库未就绪: {ragStatus.serviceMessage}</p>
            )}
            {ragStatus?.serviceOk && (
              <p className="bazi-rag-hint ok">典籍库已连接, 索引约 {ragStatus.chunks} 条</p>
            )}
            <SceneTemplatePicker
              activeModuleId="01"
              onSelect={(prompt) => onInterpretQuestionChange(prompt)}
            />
            <label className="bazi-visual-field" htmlFor="bazi-demo-question">
              <span>问事</span>
              <input
                id="bazi-demo-question"
                type="text"
                value={interpretQuestion}
                onChange={(e) => onInterpretQuestionChange(e.target.value)}
                placeholder="例: 论格局与一生大势"
                maxLength={200}
              />
            </label>
            <InterpretModelPicker
              models={chatModels}
              value={selectedModel}
              onChange={onModelChange}
              chatEnabled={chatEnabled}
              disabled={interpretStyleLoading !== null}
            />
            <div className="bazi-ai-actions">
              <button
                type="button"
                className="bazi-ghost-button"
                disabled={!chatEnabled || !result}
                onClick={() => runWithAuth(onOpenAiChat)}
              >
                打开 AI 对话
              </button>
            </div>
            <InterpretStyleButtons
              professionalLoading={interpretStyleLoading === "professional"}
              plainLoading={interpretStyleLoading === "plain"}
              disabled={!lastRequest}
              onLoadingStart={onInterpretStyleLoading}
              onProfessional={() => runWithAuth(() => onInterpret("professional"))}
              onPlain={() => runWithAuth(() => onInterpret("plain"))}
            />
          </section>
        </aside>
      </div>

      {(interpretation?.summaryProfessional ||
        interpretation?.summaryPlain ||
        interpretation?.summary) && (
        <section className="bazi-interpret-panel panel interpret-panel">
          <div className="interpret-header">
            <h2>命理解读</h2>
          </div>
          {interpretation.summaryPlain && (
            <InterpretBlock title="AI深度解读" copyText={interpretation.summaryPlain}>
              {interpretation.tripleFusion &&
              interpretation.summaryPlain === interpretation.tripleFusion.merged.summary ? (
                <FusionChannelsPanel tripleFusion={interpretation.tripleFusion} />
              ) : interpretation.fusion &&
                interpretation.summaryPlain === interpretation.fusion.merged.summary ? (
                <FusionChannelsPanel fusion={interpretation.fusion} />
              ) : (
                <InterpretMarkdown text={interpretation.summaryPlain} />
              )}
            </InterpretBlock>
          )}
          {interpretation.summaryProfessional && (
            <InterpretBlock title="命理师专用解读" copyText={buildProfessionalCopyText()}>
              {interpretation.tripleFusion &&
              interpretation.summaryProfessional === interpretation.tripleFusion.merged.summary ? (
                <FusionChannelsPanel tripleFusion={interpretation.tripleFusion} />
              ) : interpretation.fusion &&
                interpretation.summaryProfessional === interpretation.fusion.merged.summary ? (
                <FusionChannelsPanel fusion={interpretation.fusion} />
              ) : (
                <InterpretMarkdown text={interpretation.summaryProfessional} />
              )}
            </InterpretBlock>
          )}
          {!interpretation.tripleFusion && !interpretation.fusion && (
            <ChannelRagEvidence
              query={interpretation.query}
              excerpts={ragExcerpts}
              label="八字"
            />
          )}
        </section>
      )}

      {interpretation && !interpretation.summary && hasRagExcerpts && (
        <section className="bazi-interpret-panel panel interpret-panel">
          <h2>典籍摘录</h2>
          {interpretation.query && (
            <details open>
              <summary>古籍索引</summary>
              <p className="mono">{interpretation.query}</p>
            </details>
          )}
          <RagExcerptList excerpts={ragExcerpts} />
        </section>
      )}

    </div>
  );
}
