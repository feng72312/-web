import { useMemo, useState } from "react";
import { AI_CHAT_SCENARIOS, getScenarioConfig } from "./scenarioConfig";
import type { SavedProfile } from "../../types/bazi";
import { formatHourSlotLabel } from "../../utils/timeSlots";
import { hasProfileFusionSource } from "./fusionProfileImporter";
import type { AiChatSession } from "./types";
import type { GeneralChatScenario } from "../../services/chatApi";

interface AiChatSidebarProps {
  activeScenario: GeneralChatScenario;
  recentSessions: AiChatSession[];
  activeAgentId: string | null;
  disabled?: boolean;
  savedProfiles: SavedProfile[];
  loadingProfileId: string | null;
  loadingModuleId: string | null;
  bulkProfileLoading?: boolean;
  onNewChat: () => void;
  onSelectScenario: (scenario: GeneralChatScenario) => void;
  onSelectSession: (session: AiChatSession) => void;
  onDeleteSession: (agentId: string) => void;
  onLoadProfileBazi: (profile: SavedProfile) => void;
  onLoadProfileZiwei: (profile: SavedProfile) => void;
  onLoadAllProfileBazi: () => void;
}

function formatProfile(profile: SavedProfile): string {
  const calendar = profile.calendarType === "lunar" ? "农历" : "公历";
  const leap = profile.isLeapMonth ? " 闰月" : "";
  const gender = profile.gender === 1 ? "男" : "女";
  const hour = formatHourSlotLabel(
    profile.hourSlot,
    profile.ziHourPhase === "early" ? "early" : "late",
  );
  return `${calendar} ${profile.year}-${profile.month}-${profile.day}${leap} ${hour} ${gender}`;
}

function HistorySection({
  sessions,
  profiles,
  activeAgentId,
  disabled,
  loadingProfileId,
  loadingModuleId,
  bulkProfileLoading,
  onSelectSession,
  onDeleteSession,
  onLoadProfileBazi,
  onLoadProfileZiwei,
  onLoadAllProfileBazi,
}: {
  sessions: AiChatSession[];
  profiles: SavedProfile[];
  activeAgentId: string | null;
  disabled: boolean;
  loadingProfileId: string | null;
  loadingModuleId: string | null;
  bulkProfileLoading: boolean;
  onSelectSession: (session: AiChatSession) => void;
  onDeleteSession: (agentId: string) => void;
  onLoadProfileBazi: (profile: SavedProfile) => void;
  onLoadProfileZiwei: (profile: SavedProfile) => void;
  onLoadAllProfileBazi: () => void;
}) {
  const [collapsed, setCollapsed] = useState(sessions.length + profiles.length > 5);
  const pendingBaziCount = useMemo(
    () => profiles.filter((profile) => !hasProfileFusionSource(profile.id, "01")).length,
    [profiles],
  );

  if (sessions.length === 0 && profiles.length === 0) {
    return null;
  }

  return (
    <div className="ai-chat-sidebar-section">
      <div className="ai-chat-sidebar-section-head">
        <button
          type="button"
          className="ai-chat-section-toggle"
          aria-expanded={!collapsed}
          onClick={() => setCollapsed((value) => !value)}
        >
          <span className="ai-chat-section-toggle-label">历史记录</span>
          <span className="ai-chat-section-toggle-meta">
            {sessions.length} 对话 / {profiles.length} 档案 / {collapsed ? "展开" : "收起"}
          </span>
        </button>
      </div>
      {!collapsed ? (
        <div className="ai-chat-history-panel">
          {sessions.length > 0 ? (
            <div className="ai-chat-history-block">
              <p className="ai-chat-history-block-title">最近对话</p>
              <div className="ai-chat-session-list ai-chat-session-list-scroll">
                {sessions.map((session) => {
                  const scenarioLabel = getScenarioConfig(session.scenario)?.label;
                  const showScenarioTag =
                    session.source === "general" &&
                    scenarioLabel &&
                    scenarioLabel !== session.title;
                  return (
                    <div key={session.agentId} className="ai-chat-session-row">
                      <button
                        type="button"
                        className={
                          activeAgentId === session.agentId
                            ? "ai-chat-session-card active"
                            : "ai-chat-session-card"
                        }
                        disabled={disabled}
                        onClick={() => onSelectSession(session)}
                      >
                        <span className="ai-chat-session-title">{session.title}</span>
                        {session.source === "module" && session.moduleLabel ? (
                          <span className="ai-chat-session-source">{session.moduleLabel}</span>
                        ) : null}
                        {session.source === "fusion" && session.fusionSourceLabels?.length ? (
                          <span className="ai-chat-session-source fusion">
                            {session.fusionSourceLabels.join(" + ")}
                          </span>
                        ) : null}
                        {showScenarioTag ? (
                          <span className="ai-chat-session-source">{scenarioLabel}</span>
                        ) : null}
                        {session.subtitle && session.subtitle !== scenarioLabel ? (
                          <span className="ai-chat-session-subtitle">{session.subtitle}</span>
                        ) : null}
                        <span className="ai-chat-session-meta">
                          {new Date(session.createdAt).toLocaleString()}
                        </span>
                      </button>
                      <button
                        type="button"
                        className="ai-chat-session-delete"
                        disabled={disabled}
                        title="删除此会话"
                        aria-label="删除此会话"
                        onClick={() => onDeleteSession(session.agentId)}
                      >
                        删除
                      </button>
                    </div>
                  );
                })}
              </div>
            </div>
          ) : null}

          {profiles.length > 0 ? (
            <div className="ai-chat-history-block">
              <p className="ai-chat-history-block-title">排盘档案</p>
              <p className="ai-chat-history-block-desc">
                从已保存出生信息加载盘面, 写入右侧融合素材库后可多盘分析.
              </p>
              {pendingBaziCount > 0 ? (
                <button
                  type="button"
                  className="ai-chat-fusion-bulk-load"
                  disabled={disabled || bulkProfileLoading}
                  onClick={onLoadAllProfileBazi}
                >
                  {bulkProfileLoading
                    ? "正在加载全部八字盘..."
                    : `一键加载全部八字盘 (${pendingBaziCount})`}
                </button>
              ) : null}
              <div className="ai-chat-fusion-saved-list">
                {profiles.map((profile) => {
                  const hasBazi = hasProfileFusionSource(profile.id, "01");
                  const hasZiwei = hasProfileFusionSource(profile.id, "11");
                  const baziLoading =
                    loadingProfileId === profile.id && loadingModuleId === "01";
                  const ziweiLoading =
                    loadingProfileId === profile.id && loadingModuleId === "11";
                  return (
                    <div key={profile.id} className="ai-chat-fusion-saved-card">
                      <div className="ai-chat-fusion-saved-card-body">
                        <span className="ai-chat-fusion-saved-name">
                          {profile.name || "未命名"}
                        </span>
                        <span className="ai-chat-fusion-saved-meta">{formatProfile(profile)}</span>
                      </div>
                      <div className="ai-chat-fusion-saved-actions">
                        <button
                          type="button"
                          className="ai-chat-fusion-load-btn"
                          disabled={disabled || baziLoading || hasBazi}
                          onClick={() => onLoadProfileBazi(profile)}
                        >
                          {hasBazi ? "八字已入库" : baziLoading ? "加载中..." : "加载八字盘"}
                        </button>
                        <button
                          type="button"
                          className="ai-chat-fusion-load-btn"
                          disabled={disabled || ziweiLoading || hasZiwei}
                          onClick={() => onLoadProfileZiwei(profile)}
                        >
                          {hasZiwei ? "紫微已入库" : ziweiLoading ? "加载中..." : "加载紫微盘"}
                        </button>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          ) : null}
        </div>
      ) : null}
    </div>
  );
}

export function AiChatSidebar({
  activeScenario,
  recentSessions,
  activeAgentId,
  disabled = false,
  savedProfiles,
  loadingProfileId,
  loadingModuleId,
  bulkProfileLoading = false,
  onNewChat,
  onSelectScenario,
  onSelectSession,
  onDeleteSession,
  onLoadProfileBazi,
  onLoadProfileZiwei,
  onLoadAllProfileBazi,
}: AiChatSidebarProps) {
  const sortedSessions = useMemo(
    () =>
      [...recentSessions].sort((a, b) => b.createdAt.localeCompare(a.createdAt)),
    [recentSessions],
  );

  return (
    <aside className="ai-chat-sidebar">
      <div className="ai-chat-sidebar-section">
        <button
          type="button"
          className="ai-chat-new-button"
          disabled={disabled}
          onClick={onNewChat}
        >
          新建对话
        </button>
      </div>

      <HistorySection
        sessions={sortedSessions}
        profiles={savedProfiles}
        activeAgentId={activeAgentId}
        disabled={disabled}
        loadingProfileId={loadingProfileId}
        loadingModuleId={loadingModuleId}
        bulkProfileLoading={bulkProfileLoading}
        onSelectSession={onSelectSession}
        onDeleteSession={onDeleteSession}
        onLoadProfileBazi={onLoadProfileBazi}
        onLoadProfileZiwei={onLoadProfileZiwei}
        onLoadAllProfileBazi={onLoadAllProfileBazi}
      />

      <div className="ai-chat-sidebar-section">
        <h3>场景入口</h3>
        <div className="ai-chat-scenario-list">
          {AI_CHAT_SCENARIOS.map((scenario) => (
            <button
              key={scenario.id}
              type="button"
              className={
                activeScenario === scenario.id
                  ? "ai-chat-scenario-item active"
                  : "ai-chat-scenario-item"
              }
              disabled={disabled}
              onClick={() => onSelectScenario(scenario.id)}
            >
              <span className="ai-chat-scenario-label">{scenario.label}</span>
              <span className="ai-chat-scenario-desc">{scenario.description}</span>
            </button>
          ))}
        </div>
      </div>
    </aside>
  );
}
