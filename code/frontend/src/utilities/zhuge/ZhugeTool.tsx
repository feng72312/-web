import { useEffect, useState } from "react";
import { useAuth } from "../../context/AuthContext";
import { InterpretModelPicker } from "../../components/InterpretModelPicker";
import { InterpretStyleButtons } from "../../components/InterpretStyleButtons";
import { RagExcerptList } from "../../components/RagExcerptList";
import { DualInterpretSummary } from "../../components/DualInterpretSummary";
import { VisualWorkbench } from "../../components/visual/VisualWorkbench";
import { VisualPanel } from "../../components/visual/VisualPanel";
import { VisualEmptyState } from "../../components/visual/VisualEmptyState";
import { fetchChatStatus } from "../../services/chatApi";
import { fetchUtilsInterpret, fetchZhugeDivine } from "../../services/utilsApi";
import {
  hasAnyInterpretSummary,
  mergeInterpretSummary,
  type InterpretStyle,
} from "../../utils/interpretStyle";
import type { ChatModelOption } from "../../types/bazi";
import type { UtilsInterpretation, ZhugeDivineResult } from "../../types/utils";

export function ZhugeTool() {
  const { runWithAuth } = useAuth();
  const [chars, setChars] = useState("");
  const [strokeInputs, setStrokeInputs] = useState(["", "", ""]);
  const [question, setQuestion] = useState("");
  const [loading, setLoading] = useState(false);
  const [interpretLoading, setInterpretLoading] = useState<InterpretStyle | null>(null);
  const [error, setError] = useState("");
  const [result, setResult] = useState<ZhugeDivineResult | null>(null);
  const [interpretation, setInterpretation] = useState<UtilsInterpretation | null>(null);
  const [chatEnabled, setChatEnabled] = useState(false);
  const [chatModels, setChatModels] = useState<ChatModelOption[]>([]);
  const [selectedModel, setSelectedModel] = useState("deepseek-chat");

  useEffect(() => {
    fetchChatStatus()
      .then((status) => {
        setChatEnabled(status.enabled);
        setChatModels(status.models ?? []);
        if (status.model) {
          setSelectedModel(status.model);
        }
      })
      .catch(() => setChatEnabled(false));
  }, []);

  const normalizedChars = chars.replace(/\s/g, "");
  const strokes =
    strokeInputs.every((s) => s.trim() !== "") && strokeInputs.length === 3
      ? strokeInputs.map((s) => parseInt(s, 10))
      : undefined;

  const runDivine = async () => {
    if (normalizedChars.length !== 3) {
      setError("请准确输入三个汉字");
      return;
    }
    setLoading(true);
    setError("");
    try {
      const data = await fetchZhugeDivine(normalizedChars, strokes, question);
      setResult(data);
      setInterpretation(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : "诸葛神数失败");
    } finally {
      setLoading(false);
    }
  };

  const runInterpret = async (style: InterpretStyle) => {
    if (!result) {
      setError("请先报字查签");
      return;
    }
    setInterpretLoading(style);
    setError("");
    try {
      const res = await fetchUtilsInterpret("zhuge", result as unknown as Record<string, unknown>, {
        question,
        style,
        model: selectedModel,
      });
      const summary = res.interpretation.summary ?? "";
      setInterpretation((prev) => ({
        ...res.interpretation,
        ...mergeInterpretSummary(prev, summary, style),
      }));
    } catch (err) {
      setError(err instanceof Error ? err.message : "解读失败");
    } finally {
      setInterpretLoading(null);
    }
  };

  const stageContent = result ? (
    <VisualPanel title="签文结果">
      <p>
        报字: <strong>{result.chars}</strong> | 签号: <strong>{result.qianNo}</strong>
      </p>
      <p>
        笔画: {result.rawStrokes.join(" / ")} (归约后 {result.reducedStrokes.join(" / ")})
      </p>
      <ul className="utils-steps">
        {result.steps.map((step) => (
          <li key={step}>{step}</li>
        ))}
      </ul>
      <blockquote className="utils-qian-text">{result.qianText}</blockquote>
      {result.missingText && (
        <p className="hint">典籍签条未全覆盖 384 签, 建议结合 RAG 与 AI 解读.</p>
      )}
    </VisualPanel>
  ) : (
    <VisualEmptyState
      theme="zhuge"
      title="签文待查"
      description="报三字, 按百十个位计笔画, 对 384 签查签文."
    />
  );

  return (
    <div className="zhuge-tool">
      <VisualWorkbench
        moduleId="zhuge"
        title="诸葛神数"
        subtitle="三字报卦、384签、笔画归约"
        theme="zhuge"
        error={error || undefined}
        input={
          <VisualPanel
            title="诸葛神数"
            hint="报三字, 按百十个位计笔画 (十笔以上减十, 恰十或二十作零), 对 384 签查签文. 笔画可留空由系统估算, 亦可手动填写校正."
          >
            <label className="field field-grow">
              <span>三字报卦</span>
              <input
                type="text"
                maxLength={6}
                value={chars}
                placeholder="例如: 林山冲"
                onChange={(e) => setChars(e.target.value)}
              />
            </label>

            <div className="utils-stroke-row">
              <span className="field-label">笔画 (可选)</span>
              {strokeInputs.map((value, index) => (
                <label key={index} className="field">
                  <span>第{index + 1}字</span>
                  <input
                    type="number"
                    min={1}
                    max={30}
                    value={value}
                    placeholder="自动"
                    onChange={(e) => {
                      const next = [...strokeInputs];
                      next[index] = e.target.value;
                      setStrokeInputs(next);
                    }}
                  />
                </label>
              ))}
            </div>

            <label className="field field-grow">
              <span>问事 (解读用)</span>
              <input
                type="text"
                maxLength={200}
                value={question}
                placeholder="例如: 问近期求职"
                onChange={(e) => setQuestion(e.target.value)}
              />
            </label>

            <div className="form-actions">
              <button type="button" className="primary-btn" disabled={loading} onClick={() => void runDivine()}>
                {loading ? "计算中..." : "报字查签"}
              </button>
            </div>
          </VisualPanel>
        }
        stage={stageContent}
        oracle={
          result ? (
            <VisualPanel title="典籍与 AI" accent>
              <InterpretModelPicker
                models={chatModels}
                value={selectedModel}
                onChange={setSelectedModel}
                chatEnabled={chatEnabled}
              />
              <InterpretStyleButtons
                professionalLoading={interpretLoading === "professional"}
                plainLoading={interpretLoading === "plain"}
                disabled={!chatEnabled}
                onLoadingStart={setInterpretLoading}
                onProfessional={() => runWithAuth(() => void runInterpret("professional"))}
                onPlain={() => runWithAuth(() => void runInterpret("plain"))}
              />
            </VisualPanel>
          ) : undefined
        }
        interpretation={
          interpretation && hasAnyInterpretSummary(interpretation) ? (
            <DualInterpretSummary title="签解" interpretation={interpretation}>
              <RagExcerptList excerpts={interpretation.excerpts} />
            </DualInterpretSummary>
          ) : undefined
        }
      />
    </div>
  );
}
