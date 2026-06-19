import { useEffect, useState } from "react";
import { useAuth } from "../../context/AuthContext";
import { InterpretModelPicker } from "../../components/InterpretModelPicker";
import { InterpretStyleButtons } from "../../components/InterpretStyleButtons";
import { DualInterpretSummary } from "../../components/DualInterpretSummary";
import { ClassicIndexPanel } from "../../components/ClassicIndexPanel";
import { VisualWorkbench } from "../../components/visual/VisualWorkbench";
import { VisualPanel } from "../../components/visual/VisualPanel";
import { VisualEmptyState } from "../../components/visual/VisualEmptyState";
import { fetchChatStatus } from "../../services/chatApi";
import { fetchJiemengSearch, fetchUtilsInterpret } from "../../services/utilsApi";
import {
  hasAnyInterpretSummary,
  mergeInterpretSummary,
  type InterpretStyle,
} from "../../utils/interpretStyle";
import type { ChatModelOption } from "../../types/bazi";
import type { JiemengMatch, UtilsInterpretation } from "../../types/utils";

export function JiemengTool() {
  const { runWithAuth } = useAuth();
  const [dream, setDream] = useState("");
  const [question, setQuestion] = useState("");
  const [loading, setLoading] = useState(false);
  const [interpretLoading, setInterpretLoading] = useState<InterpretStyle | null>(null);
  const [error, setError] = useState("");
  const [matches, setMatches] = useState<JiemengMatch[]>([]);
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

  const runSearch = async () => {
    if (dream.trim().length < 2) {
      setError("请至少输入两个字的梦境描述");
      return;
    }
    setLoading(true);
    setError("");
    try {
      const data = await fetchJiemengSearch(dream.trim());
      setMatches(data.matches ?? []);
      setInterpretation(null);
      if (!data.matches?.length) {
        setError("未匹配到条目, 请换关键词再试");
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "解梦检索失败");
      setMatches([]);
    } finally {
      setLoading(false);
    }
  };

  const runInterpret = async (style: InterpretStyle) => {
    if (!matches.length) {
      setError("请先检索梦境条目");
      return;
    }
    setInterpretLoading(style);
    setError("");
    try {
      const res = await fetchUtilsInterpret(
        "jiemeng",
        { dream: dream.trim(), matches },
        { question: question || dream, style, model: selectedModel },
      );
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

  const stageContent =
    matches.length > 0 ? (
      <VisualPanel title="匹配条目">
        <ul className="utils-match-list">
          {matches.map((row, index) => (
            <li key={`${row.text}-${index}`}>
              {row.section && <span className="utils-match-section">{row.section}</span>}
              <p>{row.text}</p>
            </li>
          ))}
        </ul>
      </VisualPanel>
    ) : (
      <VisualEmptyState
        theme="dream"
        title="梦境待检索"
        description="描述梦境关键词或景象, 系统从《周公解梦》条目中检索象意断语."
      />
    );

  return (
    <div className="jiemeng-tool">
      <VisualWorkbench
        moduleId="jiemeng"
        title="周公解梦"
        subtitle="梦境象意、条目检索、AI串联"
        theme="dream"
        error={error || undefined}
        input={
          <VisualPanel
            title="周公解梦"
            hint="描述梦境关键词或景象, 系统从《周公解梦》条目中检索象意断语, 可再 AI 串联解读."
          >
            <label className="field field-grow">
              <span>梦境描述</span>
              <textarea
                rows={4}
                value={dream}
                maxLength={500}
                placeholder="例如: 梦见天门开, 乘龙上天"
                onChange={(e) => setDream(e.target.value)}
              />
            </label>

            <label className="field field-grow">
              <span>问事 (解读用)</span>
              <input
                type="text"
                maxLength={200}
                value={question}
                placeholder="例如: 问事业吉凶"
                onChange={(e) => setQuestion(e.target.value)}
              />
            </label>

            <div className="form-actions">
              <button type="button" className="primary-btn" disabled={loading} onClick={() => void runSearch()}>
                {loading ? "检索中..." : "检索条目"}
              </button>
            </div>
          </VisualPanel>
        }
        stage={stageContent}
        oracle={
          matches.length > 0 ? (
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
            <DualInterpretSummary title="梦境解读" interpretation={interpretation}>
              <ClassicIndexPanel
                query={interpretation.query}
                excerpts={interpretation.excerpts}
              />
            </DualInterpretSummary>
          ) : undefined
        }
      />
    </div>
  );
}
