import { useRef, useState } from "react";
import { FusionChannelsPanel } from "../FusionChannelsPanel";
import { InterpretBlock } from "../InterpretBlock";
import { InterpretMarkdown } from "../InterpretMarkdown";
import { InterpretModelPicker } from "../InterpretModelPicker";
import { InterpretStyleButtons } from "../InterpretStyleButtons";
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
import { useAuth } from "../../context/AuthContext";
import { BaziClassicReference } from "./BaziClassicReference";
import { BaziInterpretSegments } from "./BaziInterpretSegments";
import { BaziJudgementPanel } from "./BaziJudgementPanel";
import { BaziInteractionNotes } from "./BaziInteractionNotes";
import { BaziLuckReport } from "./BaziLuckReport";
import { BaziPillarReportTable } from "./BaziPillarReportTable";
import { BaziRelationDiagram } from "./BaziRelationDiagram";
import { BaziReportHeader } from "./BaziReportHeader";

interface BaziReportViewProps {
  result: PaipanResponse;
  lastRequest: PaipanRequest | null;
  luckLoading: boolean;
  luckTimeline: LuckTimeline | null;
  interpretation: Interpretation | null;
  ragStatus: RagStatus | null;
  chatEnabled: boolean;
  chatModels: ChatModelOption[];
  selectedModel: string;
  interpretStyleLoading: InterpretStyle | null;
  interpretQuestion: string;
  onModelChange: (modelId: string) => void;
  onInterpretQuestionChange: (value: string) => void;
  onOpenAiChat: () => void;
  onOpenLuck: () => void;
  onInterpret: (style: InterpretStyle) => void;
  onInterpretStyleLoading: (style: InterpretStyle | null) => void;
  buildProfessionalCopyText: () => string;
}

export function BaziReportView({
  result,
  lastRequest,
  luckLoading,
  luckTimeline,
  interpretation,
  ragStatus,
  chatEnabled,
  chatModels,
  selectedModel,
  interpretStyleLoading,
  interpretQuestion,
  onModelChange,
  onInterpretQuestionChange,
  onOpenAiChat,
  onOpenLuck,
  onInterpret,
  onInterpretStyleLoading,
  buildProfessionalCopyText,
}: BaziReportViewProps) {
  const { runWithAuth } = useAuth();
  const judgementPanelRef = useRef<HTMLElement | null>(null);
  const [highlightRuleId, setHighlightRuleId] = useState<string | null>(null);
  const chart = result.chart;

  const handleRuleIdSelect = (ruleId: string) => {
    setHighlightRuleId(ruleId);
    judgementPanelRef.current?.scrollIntoView({ behavior: "smooth", block: "start" });
  };

  const renderInterpretBody = (text: string, segments?: Interpretation["segments"]) => {
    if (segments && segments.length > 0) {
      return <BaziInterpretSegments segments={segments} onRuleIdSelect={handleRuleIdSelect} />;
    }
    return <InterpretMarkdown text={text} />;
  };

  return (
    <div className="bazi-report-view">
      <BaziReportHeader chart={chart} />
      <BaziPillarReportTable chart={chart} />
      <BaziInteractionNotes
        stemNotes={chart.pillarDetail?.stemNotes}
        branchNotes={chart.pillarDetail?.branchNotes}
      />
      <BaziRelationDiagram chart={chart} />

      <BaziJudgementPanel
        panelRef={judgementPanelRef}
        highlightRuleId={highlightRuleId}
        judgement={
          interpretation?.judgement
            ? {
                ...interpretation.judgement,
                ruleIdRefs:
                  interpretation.ruleIdRefs ?? interpretation.judgement.ruleIdRefs,
              }
            : null
        }
      />

      <BaziLuckReport
        luckLoading={luckLoading}
        luckTimeline={luckTimeline}
        onOpenLuck={onOpenLuck}
      />

      <section className="bazi-report-card bazi-ai-card">
        <div className="bazi-report-section-head">
          <span className="bazi-card-eyebrow">AI Reading</span>
          <h3>命理解读</h3>
        </div>
        {ragStatus && !ragStatus.serviceOk && (
          <p className="bazi-rag-hint">典籍库未就绪: {ragStatus.serviceMessage}</p>
        )}
        {ragStatus?.serviceOk && (
          <p className="bazi-rag-hint ok">
            典籍库已连接, 索引约 {ragStatus.chunks || ragStatus.chunksTotal || 0} 条
          </p>
        )}
        <SceneTemplatePicker
          activeModuleId="01"
          onSelect={(prompt) => onInterpretQuestionChange(prompt)}
        />
        <label className="bazi-visual-field" htmlFor="bazi-report-question">
          <span>问事</span>
          <input
            id="bazi-report-question"
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
            disabled={!chatEnabled}
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

      {(interpretation?.summaryProfessional ||
        interpretation?.summaryPlain ||
        interpretation?.summary) && (
        <section className="bazi-interpret-panel panel interpret-panel">
          <div className="interpret-header">
            <h2>解读结果</h2>
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
                renderInterpretBody(interpretation.summaryPlain, interpretation.segments)
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
                renderInterpretBody(interpretation.summaryProfessional, interpretation.segments)
              )}
            </InterpretBlock>
          )}
          {interpretation.confidenceNote && (
            <p className="bazi-interpret-confidence-note">{interpretation.confidenceNote}</p>
          )}
          {interpretation.segmentStats && (
            <p className="bazi-interpret-segment-stats">
              段落锚点: {interpretation.segmentStats.anchored}/{interpretation.segmentStats.total} 有规则支撑
            </p>
          )}
        </section>
      )}

      {interpretation &&
        !interpretation.tripleFusion &&
        !interpretation.fusion && (
          <BaziClassicReference ragStatus={null} interpretation={interpretation} />
        )}
    </div>
  );
}
