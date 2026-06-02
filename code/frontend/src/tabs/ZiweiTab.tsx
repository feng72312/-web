import { useEffect, useState } from "react";
import { useAuth } from "../context/AuthContext";
import { BirthForm } from "../components/BirthForm";
import { DualInterpretSummary } from "../components/DualInterpretSummary";
import { RagExcerptList } from "../components/RagExcerptList";
import { InterpretModelPicker } from "../components/InterpretModelPicker";
import { InterpretStyleButtons } from "../components/InterpretStyleButtons";
import { ChatPanel } from "../components/ChatPanel";
import { ZiweiAdvancedSettings } from "../components/ziwei/ZiweiAdvancedSettings";
import { ZiweiLimitsPanel } from "../components/ziwei/ZiweiLimitsPanel";
import { ZiweiPalaceGrid } from "../components/ziwei/ZiweiPalaceGrid";
import { fetchChatStatus } from "../services/chatApi";
import {
  DEFAULT_ZIWEI_SETTINGS,
  profileToZiweiSettings,
  updateProfileZiweiSettings,
} from "../services/profileStorage";
import { fetchZiweiChart, fetchZiweiInterpret, initZiweiChatSession } from "../services/ziweiApi";
import {
  hasAnyInterpretSummary,
  mergeInterpretSummary,
  type InterpretStyle,
} from "../utils/interpretStyle";
import type { ChatModelOption, PaipanRequest, ZiweiProfileSettings } from "../types/bazi";
import type { ZiweiChart, ZiweiChartRequest, ZiweiInterpretation } from "../types/ziwei";
import "../styles/ziwei.css";

function buildZiweiRequest(
  birth: PaipanRequest,
  settings: ZiweiProfileSettings,
  question: string,
  targetYear: number,
): ZiweiChartRequest {
  return {
    name: birth.name,
    calendarType: birth.calendarType,
    year: birth.year,
    month: birth.month,
    day: birth.day,
    isLeapMonth: birth.isLeapMonth,
    hour: birth.hour,
    minute: birth.minute,
    gender: birth.gender,
    useTrueSolarTime: settings.useTrueSolarTime,
    longitude: settings.longitude,
    targetYear,
    question: question.trim(),
    rules: {
      leapMonthRule: settings.leapMonthRule,
      ziHourRule: settings.ziHourRule,
      mutagenTable: settings.mutagenTable ?? "nan_pai",
    },
  };
}

export function ZiweiTab() {
  const { runWithAuth } = useAuth();
  const [ziweiSettings, setZiweiSettings] = useState<ZiweiProfileSettings>(DEFAULT_ZIWEI_SETTINGS);
  const [question, setQuestion] = useState("请论此命命宫格局、性情与当前大限流年");
  const [targetYear, setTargetYear] = useState(new Date().getFullYear());
  const [loading, setLoading] = useState(false);
  const [interpretStyleLoading, setInterpretStyleLoading] = useState<InterpretStyle | null>(null);
  const [, setLastInterpretStyle] = useState<InterpretStyle | null>(null);
  const [error, setError] = useState("");
  const [chart, setChart] = useState<ZiweiChart | null>(null);
  const [lastBirth, setLastBirth] = useState<PaipanRequest | null>(null);
  const [activeProfileId, setActiveProfileId] = useState<string | null>(null);
  const [interpretation, setInterpretation] = useState<ZiweiInterpretation | null>(null);
  const [chatAgentId, setChatAgentId] = useState<string | null>(null);
  const [chatEnabled, setChatEnabled] = useState(false);
  const [chatModels, setChatModels] = useState<ChatModelOption[]>([]);
  const [selectedModel, setSelectedModel] = useState("deepseek-chat");
  const [showChat, setShowChat] = useState(false);

  useEffect(() => {
    fetchChatStatus()
      .then((status) => {
        setChatEnabled(status.enabled);
        setChatModels(status.models ?? []);
        if (status.model) setSelectedModel(status.model);
      })
      .catch(() => setChatEnabled(false));
  }, []);

  const runChart = async (birth: PaipanRequest, year = targetYear) => {
    setLoading(true);
    setError("");
    setInterpretation(null);
    setChatAgentId(null);
    try {
      const payload = await fetchZiweiChart(buildZiweiRequest(birth, ziweiSettings, question, year));
      setChart(payload.chart);
      setLastBirth(birth);
    } catch (err) {
      setError(err instanceof Error ? err.message : "排盘失败");
      setChart(null);
    } finally {
      setLoading(false);
    }
  };

  const handleBirthSubmit = (birth: PaipanRequest) => {
    void runChart(birth);
  };

  const handleTargetYearChange = (year: number) => {
    setTargetYear(year);
    if (lastBirth) {
      void runChart(lastBirth, year);
    }
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

  const handleInterpret = async (style: InterpretStyle) => {
    if (!chart) return;
    setInterpretStyleLoading(style);
    setLastInterpretStyle(style);
    setError("");
    try {
      const full = await fetchZiweiInterpret(
        chart,
        interpretation?.excerpts,
        selectedModel,
        style,
        question,
      );
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
      if (!chart) {
        setError("请先排盘");
        return;
      }
      try {
        const session = await initZiweiChatSession(
          chart,
          interpretation?.excerpts,
          interpretation?.knowledgeHits,
        );
        setChatAgentId(session.agentId);
        setShowChat(true);
      } catch (err) {
        setError(err instanceof Error ? err.message : "对话连接失败");
      }
    });
  };

  if (showChat && chart) {
    return (
      <div className="ziwei-tab chat-mode">
        <ChatPanel
          layout="page"
          agentId={chatAgentId}
          chartName={chart.meta.bureau}
          dayMaster={chart.palaces[0]?.stemBranch ?? ""}
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
    <div className="ziwei-tab">
      <section className="panel">
        <h2>紫微斗数排盘</h2>
        <p className="hint">南派三合安星, 含大限/流年/小限. 与八字共用出生档案.</p>
        <BirthForm
          loading={loading}
          onSubmit={handleBirthSubmit}
          onProfileLoad={(profile) => {
            setActiveProfileId(profile.id);
            setZiweiSettings(profileToZiweiSettings(profile));
          }}
        />
        <ZiweiAdvancedSettings settings={ziweiSettings} onChange={handleZiweiSettingsChange} />
        <label className="full-width">
          问事 (解读用)
          <input
            type="text"
            value={question}
            maxLength={200}
            onChange={(e) => setQuestion(e.target.value)}
          />
        </label>
      </section>

      {error && <p className="error">{error}</p>}

      {chart && (
        <>
          <section className="panel">
            <h2>命盘</h2>
            <ZiweiPalaceGrid chart={chart} />
          </section>
          <section className="panel">
            <ZiweiLimitsPanel
              chart={chart}
              targetYear={targetYear}
              onTargetYearChange={handleTargetYearChange}
            />
          </section>
          <section className="panel">
            <h2>典籍与 AI</h2>
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
              disabled={!chart}
              onProfessional={() => runWithAuth(() => handleInterpret("professional"))}
              onPlain={() => runWithAuth(() => handleInterpret("plain"))}
            />
            {(hasAnyInterpretSummary(interpretation) ||
              (interpretation?.excerpts && interpretation.excerpts.length > 0)) && (
              <DualInterpretSummary title="紫微解读" interpretation={interpretation!}>
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
                <RagExcerptList excerpts={interpretation?.excerpts ?? []} />
              </DualInterpretSummary>
            )}
            {chatEnabled && (
              <button type="button" className="primary" onClick={handleOpenChat}>
                打开 AI 对话
              </button>
            )}
          </section>
        </>
      )}
    </div>
  );
}
