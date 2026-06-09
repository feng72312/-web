import { useEffect, useState } from "react";
import { useAuth } from "../../context/AuthContext";
import { BirthForm } from "../../components/BirthForm";
import { ChatPanel } from "../../components/ChatPanel";
import { InterpretModelPicker } from "../../components/InterpretModelPicker";
import { InterpretStyleButtons } from "../../components/InterpretStyleButtons";
import { RagExcerptList } from "../../components/RagExcerptList";
import { DualInterpretSummary } from "../../components/DualInterpretSummary";
import { ZiweiAdvancedSettings } from "../../components/ziwei/ZiweiAdvancedSettings";
import { fetchChatStatus } from "../../services/chatApi";
import {
  DEFAULT_ZIWEI_SETTINGS,
  profileToZiweiSettings,
  updateProfileZiweiSettings,
} from "../../services/profileStorage";
import {
  fetchHepanChart,
  fetchHepanInterpret,
  fetchHepanScenes,
  initHepanChatSession,
} from "../../services/hepanApi";
import {
  hasAnyInterpretSummary,
  mergeInterpretSummary,
  type InterpretStyle,
} from "../../utils/interpretStyle";
import type { ChatModelOption, PaipanRequest, ZiweiProfileSettings } from "../../types/bazi";
import type {
  HepanChartRequest,
  HepanChartResponse,
  HepanDiscipline,
  HepanInterpretation,
  HepanScene,
  HepanSceneOption,
} from "../../types/hepan";
import { HepanCrossNotesPanel, HepanPersonSummary } from "./HepanCrossNotesPanel";

function toHepanPerson(data: PaipanRequest) {
  return {
    name: data.name,
    calendarType: data.calendarType,
    year: data.year,
    month: data.month,
    day: data.day,
    isLeapMonth: data.isLeapMonth,
    hour: data.hour,
    minute: data.minute,
    gender: data.gender,
  };
}

export function HepanTool() {
  const { runWithAuth } = useAuth();
  const [scenes, setScenes] = useState<HepanSceneOption[]>([]);
  const [scene, setScene] = useState<HepanScene>("marriage");
  const [discipline, setDiscipline] = useState<HepanDiscipline>("auto");
  const [question, setQuestion] = useState("");
  const [personA, setPersonA] = useState<PaipanRequest | null>(null);
  const [personB, setPersonB] = useState<PaipanRequest | null>(null);
  const [ziweiSettings, setZiweiSettings] = useState<ZiweiProfileSettings>(DEFAULT_ZIWEI_SETTINGS);
  const [activeProfileId, setActiveProfileId] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [interpretStyleLoading, setInterpretStyleLoading] = useState<InterpretStyle | null>(null);
  const [, setLastInterpretStyle] = useState<InterpretStyle | null>(null);
  const [error, setError] = useState("");
  const [hepan, setHepan] = useState<HepanChartResponse | null>(null);
  const [interpretation, setInterpretation] = useState<HepanInterpretation | null>(null);
  const [chatAgentId, setChatAgentId] = useState<string | null>(null);
  const [chatEnabled, setChatEnabled] = useState(false);
  const [chatModels, setChatModels] = useState<ChatModelOption[]>([]);
  const [selectedModel, setSelectedModel] = useState("deepseek-chat");
  const [showChat, setShowChat] = useState(false);

  useEffect(() => {
    fetchHepanScenes()
      .then((res) => setScenes(res.scenes))
      .catch(() => {});
    fetchChatStatus()
      .then((status) => {
        setChatEnabled(status.enabled);
        setChatModels(status.models ?? []);
        if (status.model) setSelectedModel(status.model);
      })
      .catch(() => setChatEnabled(false));
  }, []);

  useEffect(() => {
    const current = scenes.find((s) => s.id === scene);
    if (current && !question.trim()) {
      setQuestion(current.defaultQuestion);
    }
  }, [scene, scenes, question]);

  const showZiweiSettings =
    discipline === "ziwei" || (discipline === "auto" && scene !== "partnership");

  const buildRequest = (): HepanChartRequest | null => {
    if (!personA || !personB) {
      setError("请先分别录入甲方与乙方出生信息");
      return null;
    }
    return {
      personA: toHepanPerson(personA),
      personB: toHepanPerson(personB),
      scene,
      discipline,
      question: question.trim(),
      useTrueSolarTime: ziweiSettings.useTrueSolarTime,
      longitude: ziweiSettings.longitude,
      ziweiRules: {
        leapMonthRule: ziweiSettings.leapMonthRule,
        ziHourRule: ziweiSettings.ziHourRule,
        mutagenTable: ziweiSettings.mutagenTable ?? "nan_pai",
      },
    };
  };

  const runHepan = async () => {
    const body = buildRequest();
    if (!body) return;
    setLoading(true);
    setError("");
    setInterpretation(null);
    setChatAgentId(null);
    try {
      const result = await fetchHepanChart(body);
      setHepan(result);
      if (!question.trim()) {
        setQuestion(result.question);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "合盘失败");
      setHepan(null);
    } finally {
      setLoading(false);
    }
  };

  const handleInterpret = async (style: InterpretStyle) => {
    if (!hepan) return;
    setInterpretStyleLoading(style);
    setLastInterpretStyle(style);
    setError("");
    try {
      const full = await fetchHepanInterpret(hepan, {
        question,
        excerpts: interpretation?.excerpts,
        model: selectedModel,
        style,
      });
      setHepan(full.hepan);
      setInterpretation((prev) => ({
        ...full.interpretation,
        ...mergeInterpretSummary(prev, full.interpretation.summary, style),
      }));
      if (full.interpretation.agentId) {
        setChatAgentId(full.interpretation.agentId);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "解读失败");
    } finally {
      setInterpretStyleLoading(null);
    }
  };

  const handleOpenChat = () => {
    runWithAuth(async () => {
      if (!hepan) {
        setError("请先合盘排盘");
        return;
      }
      try {
        const session = await initHepanChatSession(hepan, interpretation?.excerpts);
        setChatAgentId(session.agentId);
        setShowChat(true);
      } catch (err) {
        setError(err instanceof Error ? err.message : "对话连接失败");
      }
    });
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

  if (showChat && hepan) {
    const dayMaster = String(
      (hepan.personA.baziChart as { dayMaster?: string } | undefined)?.dayMaster ?? "",
    );
    return (
      <div className="hepan-tool chat-mode">
        <ChatPanel
          layout="page"
          agentId={chatAgentId}
          chartName="合盘"
          dayMaster={dayMaster}
          chatEnabled={chatEnabled}
          chatModels={chatModels}
          selectedModel={selectedModel}
          onModelChange={setSelectedModel}
          sessionLoading={false}
          connectError=""
          onConnect={() => {}}
          onBack={() => setShowChat(false)}
        />
      </div>
    );
  }

  return (
    <div className="hepan-tool discipline-page">
      <section className="panel panel-cast">
        <div className="panel-head">
          <div>
            <h2>合盘工具</h2>
            <p className="hint">选择场景与术数, 录入两人信息后合盘. 婚恋默认紫微, 合作默认八字.</p>
          </div>
        </div>

        <div className="hepan-scene-row">
          <span className="field-label">场景</span>
          <div className="hepan-option-group">
            {scenes.map((item) => (
              <label key={item.id} className="hepan-option">
                <input
                  type="radio"
                  name="hepan-scene"
                  checked={scene === item.id}
                  onChange={() => setScene(item.id)}
                />
                {item.label}
              </label>
            ))}
          </div>
        </div>

        <div className="hepan-scene-row">
          <span className="field-label">术数</span>
          <div className="hepan-option-group">
            {(
              [
                ["auto", "自动"],
                ["bazi", "仅八字"],
                ["ziwei", "仅紫微"],
              ] as const
            ).map(([id, label]) => (
              <label key={id} className="hepan-option">
                <input
                  type="radio"
                  name="hepan-discipline"
                  checked={discipline === id}
                  onChange={() => setDiscipline(id)}
                />
                {label}
              </label>
            ))}
          </div>
        </div>

        <div className="hepan-person-grid">
          <div className="hepan-person-col">
            <h3>甲方 {personA?.name ? `(已录入: ${personA.name})` : ""}</h3>
            <BirthForm
              embedded
              loading={false}
              onSubmit={(data) => {
                setPersonA(data);
                setError("");
              }}
              onProfileLoad={(profile) => {
                setActiveProfileId(profile.id);
                setZiweiSettings(profileToZiweiSettings(profile));
              }}
            />
          </div>
          <div className="hepan-person-col">
            <h3>乙方 {personB?.name ? `(已录入: ${personB.name})` : ""}</h3>
            <BirthForm
              embedded
              loading={false}
              onSubmit={(data) => {
                setPersonB(data);
                setError("");
              }}
            />
          </div>
        </div>

        {showZiweiSettings && (
          <section className="cast-form-section ziwei-extra-section">
            <ZiweiAdvancedSettings settings={ziweiSettings} onChange={handleZiweiSettingsChange} />
          </section>
        )}

        <label className="field field-grow">
          <span>问事 (解读用)</span>
          <input
            type="text"
            value={question}
            maxLength={200}
            placeholder="例如: 论两人婚姻契合度"
            onChange={(e) => setQuestion(e.target.value)}
          />
        </label>

        <div className="form-actions">
          <button type="button" className="primary-btn" disabled={loading} onClick={() => void runHepan()}>
            {loading ? "合盘中..." : "合盘排盘"}
          </button>
        </div>
      </section>

      {error && <div className="error-box">{error}</div>}

      {hepan && (
        <>
          <section className="panel">
            <div className="panel-head">
              <h2>合盘结果</h2>
              <p className="hint">
                场景: {scenes.find((s) => s.id === hepan.scene)?.label ?? hepan.scene} / 术数:{" "}
                {hepan.discipline === "bazi" ? "八字" : "紫微"}
              </p>
            </div>
            {hepan.summaryTags.length > 0 && (
              <div className="hepan-tags">
                {hepan.summaryTags.map((tag) => (
                  <span key={tag} className="hepan-tag">
                    {tag}
                  </span>
                ))}
              </div>
            )}
            <div className="hepan-summary-grid">
              <HepanPersonSummary person={hepan.personA} label="甲方" discipline={hepan.discipline} />
              <HepanPersonSummary person={hepan.personB} label="乙方" discipline={hepan.discipline} />
            </div>
          </section>

          <HepanCrossNotesPanel notes={hepan.crossNotes} />

          <section className="panel panel-interpret">
            <div className="panel-head">
              <h2>典籍与 AI</h2>
            </div>
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
              disabled={!hepan}
              onLoadingStart={setInterpretStyleLoading}
              onProfessional={() => runWithAuth(() => handleInterpret("professional"))}
              onPlain={() => runWithAuth(() => handleInterpret("plain"))}
            />
            {(hasAnyInterpretSummary(interpretation) ||
              (interpretation?.excerpts && interpretation.excerpts.length > 0)) && (
              <DualInterpretSummary title="合盘解读" interpretation={interpretation!}>
                {interpretation?.query && (
                  <details
                    open={
                      !interpretation.summaryProfessional && !interpretation.summaryPlain
                    }
                  >
                    <summary>古籍索引</summary>
                    <p className="mono">{interpretation.query}</p>
                  </details>
                )}
                {interpretation?.excerpts && interpretation.excerpts.length > 0 && (
                  <RagExcerptList excerpts={interpretation.excerpts} />
                )}
              </DualInterpretSummary>
            )}
            {chatEnabled && (
              <div className="form-actions">
                <button type="button" className="secondary-btn" onClick={handleOpenChat}>
                  打开 AI 对话
                </button>
              </div>
            )}
          </section>
        </>
      )}
    </div>
  );
}
