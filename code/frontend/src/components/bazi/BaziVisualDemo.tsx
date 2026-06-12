import { useEffect, useState } from "react";
import { BirthForm } from "../BirthForm";
import type { RagStatus } from "../../services/ragApi";
import type {
  ChatModelOption,
  Interpretation,
  LuckTimeline,
  PaipanRequest,
  PaipanResponse,
} from "../../types/bazi";
import type { InterpretStyle } from "../../utils/interpretStyle";
import { BaziReportView } from "./BaziReportView";
import "../../styles/bazi-visual-demo.css";

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
  const [birthFormOpen, setBirthFormOpen] = useState(true);

  useEffect(() => {
    document.body.classList.add("bazi-visual-immersive");
    return () => document.body.classList.remove("bazi-visual-immersive");
  }, []);

  useEffect(() => {
    if (result) {
      setBirthFormOpen(false);
    }
  }, [result]);

  const chart = result?.chart;

  return (
    <div className="bazi-visual-demo bazi-report-shell">
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

      <section className="bazi-report-input-card">
        <button
          type="button"
          className="bazi-report-input-toggle"
          onClick={() => setBirthFormOpen((open) => !open)}
        >
          <span className="bazi-card-eyebrow">Birth Record</span>
          <strong>{birthFormOpen ? "收起出生信息" : "出生信息 / 重新排盘"}</strong>
        </button>
        {birthFormOpen && (
          <div className="bazi-report-input-body">
            <BirthForm embedded loading={paipanLoading} onSubmit={onSubmit} />
          </div>
        )}
      </section>

      {!chart || !result ? (
        <div className="bazi-report-empty">
          <span>等待排盘</span>
          <p>填写真实出生信息并点击「开始排盘」后, 下方会展开报表式命盘。</p>
        </div>
      ) : (
        <BaziReportView
          result={result}
          lastRequest={lastRequest}
          luckLoading={luckLoading}
          luckTimeline={luckTimeline}
          interpretation={interpretation}
          ragStatus={ragStatus}
          chatEnabled={chatEnabled}
          chatModels={chatModels}
          selectedModel={selectedModel}
          interpretStyleLoading={interpretStyleLoading}
          interpretQuestion={interpretQuestion}
          onModelChange={onModelChange}
          onInterpretQuestionChange={onInterpretQuestionChange}
          onOpenAiChat={onOpenAiChat}
          onOpenLuck={onOpenLuck}
          onInterpret={onInterpret}
          onInterpretStyleLoading={onInterpretStyleLoading}
          buildProfessionalCopyText={buildProfessionalCopyText}
        />
      )}
    </div>
  );
}
