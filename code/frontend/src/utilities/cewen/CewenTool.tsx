import { useEffect, useState } from "react";
import { useAuth } from "../../context/AuthContext";
import { InterpretModelPicker } from "../../components/InterpretModelPicker";
import { InterpretStyleButtons } from "../../components/InterpretStyleButtons";
import { DualInterpretSummary } from "../../components/DualInterpretSummary";
import { RagExcerptList } from "../../components/RagExcerptList";
import { fetchChatStatus } from "../../services/chatApi";
import { fetchUtilsInterpret } from "../../services/utilsApi";
import {
  hasAnyInterpretSummary,
  mergeInterpretSummary,
  type InterpretStyle,
} from "../../utils/interpretStyle";
import type { ChatModelOption } from "../../types/bazi";
import type { UtilsInterpretation } from "../../types/utils";

export function CewenTool() {
  const { runWithAuth } = useAuth();
  const [chars, setChars] = useState("");
  const [question, setQuestion] = useState("");
  const [loading, setLoading] = useState(false);
  const [interpretLoading, setInterpretLoading] = useState<InterpretStyle | null>(null);
  const [error, setError] = useState("");
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

  const runInterpret = async (style: InterpretStyle) => {
    const normalized = chars.replace(/\s/g, "");
    if (!normalized) {
      setError("请输入所测汉字");
      return;
    }
    setLoading(true);
    setInterpretLoading(style);
    setError("");
    try {
      const res = await fetchUtilsInterpret(
        "cewen",
        { chars: normalized },
        { question, style, model: selectedModel },
      );
      const summary = res.interpretation.summary ?? "";
      setInterpretation((prev) => ({
        ...res.interpretation,
        ...mergeInterpretSummary(prev, summary, style),
      }));
    } catch (err) {
      setError(err instanceof Error ? err.message : "测字解读失败");
    } finally {
      setLoading(false);
      setInterpretLoading(null);
    }
  };

  return (
    <div className="cewen-tool discipline-page">
      <section className="panel panel-cast">
        <div className="panel-head">
          <div>
            <h2>测字</h2>
            <p className="hint">输入汉字与问事, 依《测字秘牒》体例经典籍 RAG 与 AI 解读 (非铁板神数).</p>
          </div>
        </div>

        <label className="field field-grow">
          <span>所测字</span>
          <input
            type="text"
            maxLength={20}
            value={chars}
            placeholder="例如: 福"
            onChange={(e) => setChars(e.target.value)}
          />
        </label>

        <label className="field field-grow">
          <span>问事</span>
          <input
            type="text"
            maxLength={200}
            value={question}
            placeholder="例如: 问此次求职是否顺遂"
            onChange={(e) => setQuestion(e.target.value)}
          />
        </label>

        <div className="form-actions">
          <InterpretModelPicker
            models={chatModels}
            value={selectedModel}
            onChange={setSelectedModel}
            chatEnabled={chatEnabled}
          />
          <InterpretStyleButtons
            professionalLoading={interpretLoading === "professional"}
            plainLoading={interpretLoading === "plain"}
            disabled={!chatEnabled || loading}
            onLoadingStart={setInterpretLoading}
            onProfessional={() => runWithAuth(() => void runInterpret("professional"))}
            onPlain={() => runWithAuth(() => void runInterpret("plain"))}
          />
        </div>
      </section>

      {error && <div className="error-box">{error}</div>}

      {interpretation && hasAnyInterpretSummary(interpretation) && (
        <DualInterpretSummary title="测字解读" interpretation={interpretation}>
          <RagExcerptList excerpts={interpretation.excerpts} />
        </DualInterpretSummary>
      )}
    </div>
  );
}
