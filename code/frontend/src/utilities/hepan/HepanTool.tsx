import { useEffect, useState } from "react";
import { useAuth } from "../../context/AuthContext";
import { SavedProfiles } from "../../components/SavedProfiles";
import { InterpretModelPicker } from "../../components/InterpretModelPicker";
import { InterpretStyleButtons } from "../../components/InterpretStyleButtons";
import { RagExcerptList } from "../../components/RagExcerptList";
import { DualInterpretSummary } from "../../components/DualInterpretSummary";
import { ZiweiAdvancedSettings } from "../../components/ziwei/ZiweiAdvancedSettings";
import { VisualWorkbench } from "../../components/visual/VisualWorkbench";
import { VisualPanel } from "../../components/visual/VisualPanel";
import { VisualEmptyState } from "../../components/visual/VisualEmptyState";
import { fetchChatStatus } from "../../services/chatApi";
import { openModuleAiChatSession } from "../../components/ai/moduleChatBridge";
import { createModuleChatSessionRecord } from "../../components/ai/moduleSession";
import type { AiChatSession } from "../../components/ai/types";
import {
  DEFAULT_ZIWEI_SETTINGS,
  deleteProfile,
  formToPaipanRequest,
  listProfiles,
  profileToFormState,
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
import type {
  ChatModelOption,
  PaipanRequest,
  SavedProfile,
  ZiweiProfileSettings,
} from "../../types/bazi";
import type {
  HepanChartRequest,
  HepanChartResponse,
  HepanDiscipline,
  HepanInterpretation,
  HepanScene,
  HepanSceneOption,
} from "../../types/hepan";
import { HepanCrossNotesPanel, HepanPersonSummary } from "./HepanCrossNotesPanel";
import { HepanPersonSlot } from "./HepanPersonSlot";

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

interface HepanToolProps {
  onOpenAiChatSession: (session: AiChatSession) => void;
}

export function HepanTool({ onOpenAiChatSession }: HepanToolProps) {
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
  const [chatEnabled, setChatEnabled] = useState(false);
  const [chatModels, setChatModels] = useState<ChatModelOption[]>([]);
  const [selectedModel, setSelectedModel] = useState("deepseek-chat");
  const [profiles, setProfiles] = useState<SavedProfile[]>([]);
  const [personTab, setPersonTab] = useState<"a" | "b">("a");
  const [expandedA, setExpandedA] = useState(true);
  const [expandedB, setExpandedB] = useState(true);

  const refreshProfiles = () => {
    setProfiles(listProfiles());
  };

  useEffect(() => {
    refreshProfiles();
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
        chartSchool: ziweiSettings.chartSchool ?? "sanhe",
      },
    };
  };

  const runHepan = async () => {
    const body = buildRequest();
    if (!body) return;
    setLoading(true);
    setError("");
    setInterpretation(null);
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
        let agentId = interpretation?.agentId ?? null;
        if (!agentId) {
          const session = await initHepanChatSession(hepan, interpretation?.excerpts);
          agentId = session.agentId;
        }
        await openModuleAiChatSession(
          createModuleChatSessionRecord({
            agentId,
            moduleId: "12:hepan",
            moduleLabel: "合盘",
            question,
            chartName: scenes.find((item) => item.id === hepan.scene)?.label ?? hepan.scene,
            subtitle: hepan.discipline === "bazi" ? "八字合盘" : "紫微合盘",
          }),
          interpretation,
          onOpenAiChatSession,
        );
      } catch (err) {
        setError(err instanceof Error ? err.message : "对话连接失败");
      }
    });
  };

  const assignProfileToSlot = (profile: SavedProfile, slot: "a" | "b") => {
    const data = formToPaipanRequest(profileToFormState(profile));
    if (slot === "a") {
      setPersonA(data);
      setActiveProfileId(profile.id);
      setZiweiSettings(profileToZiweiSettings(profile));
      setExpandedA(false);
      setPersonTab("a");
    } else {
      setPersonB(data);
      setExpandedB(false);
      setPersonTab("b");
    }
    setError("");
  };

  const handleDeleteProfile = (profileId: string) => {
    const target = profiles.find((item) => item.id === profileId);
    const label = target?.name || "未命名";
    if (!window.confirm(`确定删除 ${label} 的出生信息吗?`)) {
      return;
    }
    deleteProfile(profileId);
    refreshProfiles();
    if (activeProfileId === profileId) {
      setActiveProfileId(null);
    }
  };

  const handleLoadProfile = (profile: SavedProfile) => {
    assignProfileToSlot(profile, personTab);
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

  const hasInterpretation =
    hasAnyInterpretSummary(interpretation) ||
    (interpretation?.excerpts && interpretation.excerpts.length > 0);

  const stageContent = hepan ? (
    <>
      <VisualPanel
        title="合盘结果"
        hint={`场景: ${scenes.find((s) => s.id === hepan.scene)?.label ?? hepan.scene} / 术数: ${hepan.discipline === "bazi" ? "八字" : "紫微"}`}
      >
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
      </VisualPanel>
      <HepanCrossNotesPanel notes={hepan.crossNotes} />
    </>
  ) : (
    <VisualEmptyState
      theme="hepan"
      title="合盘待生成"
      description="选择场景与术数, 录入两人信息后合盘."
    />
  );

  return (
    <div className="hepan-tool">
      <VisualWorkbench
        moduleId="hepan"
        title="合盘工具"
        subtitle="双人命盘、婚恋合作、交叉备注"
        theme="hepan"
        inputPlacement="top"
        error={error || undefined}
        input={
          <VisualPanel
            className="hepan-input-top-panel"
            title="合盘排盘"
            hint="婚恋默认紫微, 合作默认八字. 录入两人信息后点合盘."
          >
            <div className="hepan-top-bar">
              <div className="hepan-top-options">
                <div className="hepan-scene-row hepan-scene-row-inline">
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

                <div className="hepan-scene-row hepan-scene-row-inline">
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
              </div>

              <section className="hepan-shared-profiles hepan-shared-profiles-horizontal">
                <SavedProfiles
                  profiles={profiles}
                  activeProfileId={activeProfileId}
                  onLoad={handleLoadProfile}
                  onDelete={handleDeleteProfile}
                  onAssignSlot={assignProfileToSlot}
                  layout="horizontal"
                />
              </section>

              <div className="hepan-person-tabs" role="tablist" aria-label="合盘当事人">
                <button
                  type="button"
                  role="tab"
                  aria-selected={personTab === "a"}
                  className={personTab === "a" ? "hepan-person-tab active" : "hepan-person-tab"}
                  onClick={() => setPersonTab("a")}
                >
                  甲方{personA ? " (已录入)" : ""}
                </button>
                <button
                  type="button"
                  role="tab"
                  aria-selected={personTab === "b"}
                  className={personTab === "b" ? "hepan-person-tab active" : "hepan-person-tab"}
                  onClick={() => setPersonTab("b")}
                >
                  乙方{personB ? " (已录入)" : ""}
                </button>
              </div>

              <div className="hepan-person-grid hepan-person-grid-top hepan-person-grid-tabs">
                <HepanPersonSlot
                  label="甲方"
                  person={personA}
                  expanded={expandedA}
                  active={personTab === "a"}
                  onExpandedChange={setExpandedA}
                  onSubmit={(data) => {
                    setPersonA(data);
                    setError("");
                  }}
                  onProfileLoad={(profile) => {
                    setActiveProfileId(profile.id);
                    setZiweiSettings(profileToZiweiSettings(profile));
                  }}
                  onProfilesChange={refreshProfiles}
                />
                <HepanPersonSlot
                  label="乙方"
                  person={personB}
                  expanded={expandedB}
                  active={personTab === "b"}
                  onExpandedChange={setExpandedB}
                  onSubmit={(data) => {
                    setPersonB(data);
                    setError("");
                  }}
                  onProfilesChange={refreshProfiles}
                />
              </div>

              {showZiweiSettings && (
                <details className="hepan-advanced-details">
                  <summary>高级排盘规则</summary>
                  <section className="cast-form-section ziwei-extra-section">
                    <ZiweiAdvancedSettings settings={ziweiSettings} onChange={handleZiweiSettingsChange} />
                  </section>
                </details>
              )}

              <div className="hepan-submit-row">
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
                <button
                  type="button"
                  className="primary-btn hepan-submit-btn"
                  disabled={loading}
                  onClick={() => void runHepan()}
                >
                  {loading ? "合盘中..." : "合盘排盘"}
                </button>
              </div>
            </div>
          </VisualPanel>
        }
        stage={stageContent}
        oracle={
          hepan ? (
            <VisualPanel title="典籍与 AI" accent>
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
              {chatEnabled && (
                <div className="form-actions">
                  <button type="button" className="secondary-btn" onClick={handleOpenChat}>
                    打开 AI 对话
                  </button>
                </div>
              )}
            </VisualPanel>
          ) : undefined
        }
        interpretation={
          hasInterpretation ? (
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
          ) : undefined
        }
      />
    </div>
  );
}
