import { useAuth } from "../../context/AuthContext";
import { ChannelRagEvidence } from "../ChannelRagEvidence";
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
import { BaziClassicReference } from "./BaziClassicReference";
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
  const chart = result.chart;
  const ragExcerpts =
    interpretation?.excerpts?.filter((item) => item.source !== "stub") ?? [];
  const hasRagExcerpts = ragExcerpts.length > 0;

  return (
    <div className="bazi-report-view">
      <BaziReportHeader chart={chart} />
      <BaziPillarReportTable chart={chart} />
      <BaziInteractionNotes
        stemNotes={chart.pillarDetail?.stemNotes}
        branchNotes={chart.pillarDetail?.branchNotes}
      />
      <BaziRelationDiagram chart={chart} />

      <BaziLuckReport
        luckLoading={luckLoading}
        luckTimeline={luckTimeline}
        onOpenLuck={onOpenLuck}
      />

      <BaziClassicReference ragStatus={ragStatus} interpretation={interpretation} />

      <section className="bazi-report-card bazi-ai-card">
        <div className="bazi-report-section-head">
          <span className="bazi-card-eyebrow">AI Reading</span>
          <h3>命理解读</h3>
        </div>
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
            <ChannelRagEvidence query={interpretation.query} excerpts={ragExcerpts} label="八字" />
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
        </section>
      )}
    </div>
  );
}
