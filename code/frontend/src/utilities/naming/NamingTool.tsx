import { useEffect, useState } from "react";
import { useAuth } from "../../context/AuthContext";
import { InterpretModelPicker } from "../../components/InterpretModelPicker";
import { InterpretStyleButtons } from "../../components/InterpretStyleButtons";
import { DualInterpretSummary } from "../../components/DualInterpretSummary";
import { RagExcerptList } from "../../components/RagExcerptList";
import { VisualWorkbench } from "../../components/visual/VisualWorkbench";
import { VisualPanel } from "../../components/visual/VisualPanel";
import { VisualEmptyState } from "../../components/visual/VisualEmptyState";
import { fetchChatStatus } from "../../services/chatApi";
import { fetchNamingAnalyze, fetchUtilsInterpret } from "../../services/utilsApi";
import {
  hasAnyInterpretSummary,
  mergeInterpretSummary,
  type InterpretStyle,
} from "../../utils/interpretStyle";
import type { ChatModelOption } from "../../types/bazi";
import type { NamingAnalysis, NamingBirthInput } from "../../types/naming";
import type { UtilsInterpretation } from "../../types/utils";
import "../../styles/naming.css";

const DEFAULT_BIRTH: NamingBirthInput = {
  calendarType: "solar",
  year: 2000,
  month: 1,
  day: 1,
  hour: 12,
  minute: 0,
  second: 0,
  gender: 1,
  isLeapMonth: false,
};

export function NamingTool() {
  const { runWithAuth } = useAuth();
  const [surname, setSurname] = useState("");
  const [givenName, setGivenName] = useState("");
  const [question, setQuestion] = useState("");
  const [useBirth, setUseBirth] = useState(false);
  const [birth, setBirth] = useState<NamingBirthInput>(DEFAULT_BIRTH);
  const [loading, setLoading] = useState(false);
  const [interpretLoading, setInterpretLoading] = useState<InterpretStyle | null>(null);
  const [error, setError] = useState("");
  const [analysis, setAnalysis] = useState<NamingAnalysis | null>(null);
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

  const runAnalyze = async () => {
    if (!surname.trim()) {
      setError("请输入姓氏");
      return;
    }
    setLoading(true);
    setError("");
    setInterpretation(null);
    try {
      const res = await fetchNamingAnalyze({
        surname: surname.trim(),
        givenName: givenName.trim(),
        birth: useBirth ? birth : null,
      });
      setAnalysis(res.analysis);
    } catch (err) {
      setError(err instanceof Error ? err.message : "起名分析失败");
      setAnalysis(null);
    } finally {
      setLoading(false);
    }
  };

  const runInterpret = async (style: InterpretStyle) => {
    if (!analysis) {
      setError("请先完成姓名分析");
      return;
    }
    setInterpretLoading(style);
    setError("");
    try {
      const res = await fetchUtilsInterpret(
        "naming",
        { analysis },
        {
          question: question || `请评析「${analysis.fullName}」并给出取名建议`,
          style,
          model: selectedModel,
        },
      );
      const summary = res.interpretation.summary ?? "";
      setInterpretation((prev) => ({
        ...res.interpretation,
        ...mergeInterpretSummary(prev, summary, style),
      }));
    } catch (err) {
      setError(err instanceof Error ? err.message : "AI 解读失败");
    } finally {
      setInterpretLoading(null);
    }
  };

  const stageContent = analysis ? (
    <VisualPanel title={`分析结果: ${analysis.fullName || surname}`} className="naming-analysis-panel">
      {analysis.wuge?.grids?.length > 0 && (
        <div className="naming-block">
          <h3>五格数理</h3>
          <table className="naming-grid-table">
            <thead>
              <tr>
                <th>格</th>
                <th>笔画</th>
                <th>五行</th>
                <th>吉凶</th>
              </tr>
            </thead>
            <tbody>
              {analysis.wuge.grids.map((row) => (
                <tr key={row.grid}>
                  <td>{row.grid}</td>
                  <td>{row.strokes}</td>
                  <td>{row.wuxing}</td>
                  <td className={`luck-${row.luck}`}>{row.luck}</td>
                </tr>
              ))}
            </tbody>
          </table>
          {analysis.wuge.missingStrokeChars?.length > 0 && (
            <p className="hint">
              以下字暂无笔画数据, 五格仅供参考: {analysis.wuge.missingStrokeChars.join(" ")}
            </p>
          )}
        </div>
      )}

      {analysis.baziProfile && (
        <div className="naming-block">
          <h3>八字喜忌 (简析)</h3>
          <p>
            日主 {analysis.baziProfile.dayMasterWuxing}, 身势 {analysis.baziProfile.strength},
            宜补 {analysis.baziProfile.favoredWuxing.join(" ")}
            {analysis.baziProfile.avoidWuxing.length > 0 &&
              `, 忌偏 ${analysis.baziProfile.avoidWuxing.join(" ")}`}
          </p>
        </div>
      )}

      {analysis.shuowen?.length > 0 && (
        <div className="naming-block">
          <h3>《说文解字》字义</h3>
          <ul className="naming-shuowen-list">
            {analysis.shuowen.map((row) => (
              <li key={row.char}>
                <strong>{row.char}</strong>
                {row.radical && <span className="naming-meta"> 部首 {row.radical}</span>}
                {row.pronunciation && <span className="naming-meta"> 反切 {row.pronunciation}</span>}
                <p>{row.explanation || (row.missing ? "未收录于本地说文索引" : "")}</p>
              </li>
            ))}
          </ul>
        </div>
      )}
    </VisualPanel>
  ) : (
    <VisualEmptyState
      theme="naming"
      title="姓名待分析"
      description="结合《说文解字》《释名》等典籍, 五格数理与可选八字喜忌, 提供结构化分析."
    />
  );

  return (
    <div className="naming-tool">
      <VisualWorkbench
        moduleId="naming"
        title="起名"
        subtitle="五格数理、说文字义、八字喜忌"
        theme="naming"
        error={error || undefined}
        input={
          <VisualPanel
            title="起名"
            hint="结合《说文解字》《释名》等典籍, 五格数理与可选八字喜忌, 提供结构化分析与 AI 取名建议."
          >
            <div className="naming-form-grid">
              <label className="field">
                <span>姓氏</span>
                <input
                  type="text"
                  maxLength={8}
                  value={surname}
                  placeholder="例如: 李"
                  onChange={(e) => setSurname(e.target.value)}
                />
              </label>
              <label className="field">
                <span>名字</span>
                <input
                  type="text"
                  maxLength={8}
                  value={givenName}
                  placeholder="例如: 明轩 (可留空仅查字)"
                  onChange={(e) => setGivenName(e.target.value)}
                />
              </label>
            </div>

            <label className="field field-grow">
              <span>问事 (AI 解读用)</span>
              <input
                type="text"
                maxLength={200}
                value={question}
                placeholder="例如: 此名是否合八字喜木?"
                onChange={(e) => setQuestion(e.target.value)}
              />
            </label>

            <label className="naming-toggle">
              <input
                type="checkbox"
                checked={useBirth}
                onChange={(e) => setUseBirth(e.target.checked)}
              />
              <span>结合八字喜忌 (填写出生信息)</span>
            </label>

            {useBirth && (
              <div className="naming-birth-grid">
                <label className="field">
                  <span>历法</span>
                  <select
                    value={birth.calendarType}
                    onChange={(e) =>
                      setBirth((prev) => ({
                        ...prev,
                        calendarType: e.target.value as NamingBirthInput["calendarType"],
                      }))
                    }
                  >
                    <option value="solar">公历</option>
                    <option value="lunar">农历</option>
                  </select>
                </label>
                <label className="field">
                  <span>年</span>
                  <input
                    type="number"
                    min={1900}
                    max={2100}
                    value={birth.year}
                    onChange={(e) => setBirth((prev) => ({ ...prev, year: Number(e.target.value) }))}
                  />
                </label>
                <label className="field">
                  <span>月</span>
                  <input
                    type="number"
                    min={1}
                    max={12}
                    value={birth.month}
                    onChange={(e) => setBirth((prev) => ({ ...prev, month: Number(e.target.value) }))}
                  />
                </label>
                <label className="field">
                  <span>日</span>
                  <input
                    type="number"
                    min={1}
                    max={31}
                    value={birth.day}
                    onChange={(e) => setBirth((prev) => ({ ...prev, day: Number(e.target.value) }))}
                  />
                </label>
                <label className="field">
                  <span>时</span>
                  <input
                    type="number"
                    min={0}
                    max={23}
                    value={birth.hour}
                    onChange={(e) => setBirth((prev) => ({ ...prev, hour: Number(e.target.value) }))}
                  />
                </label>
                <label className="field">
                  <span>性别</span>
                  <select
                    value={birth.gender}
                    onChange={(e) => setBirth((prev) => ({ ...prev, gender: Number(e.target.value) }))}
                  >
                    <option value={1}>男</option>
                    <option value={0}>女</option>
                  </select>
                </label>
              </div>
            )}

            <div className="form-actions">
              <button type="button" className="primary-btn" disabled={loading} onClick={() => void runAnalyze()}>
                {loading ? "分析中..." : "分析姓名"}
              </button>
            </div>
          </VisualPanel>
        }
        stage={stageContent}
        oracle={
          analysis ? (
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
            <DualInterpretSummary title="起名解读" interpretation={interpretation}>
              <RagExcerptList excerpts={interpretation.excerpts} />
            </DualInterpretSummary>
          ) : undefined
        }
      />
    </div>
  );
}
