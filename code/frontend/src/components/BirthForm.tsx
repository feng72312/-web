import { useEffect, useState } from "react";
import type { BirthFormState, PaipanRequest, SavedProfile } from "../types/bazi";
import {
  defaultFormState,
  deleteProfile,
  formToPaipanRequest,
  listProfiles,
  paipanRequestToFormState,
  profileToFormState,
  saveNewProfile,
  updateProfile,
} from "../services/profileStorage";
import { HOUR_SLOTS } from "../utils/timeSlots";
import { SavedProfiles } from "./SavedProfiles";

interface Props {
  loading: boolean;
  onSubmit: (data: PaipanRequest) => void;
  onProfileLoad?: (profile: SavedProfile) => void;
  /** 嵌入术数 Tab 面板时不重复外层 panel 标题 */
  embedded?: boolean;
  /** 主提交按钮文案, 默认「开始排盘」 */
  submitLabel?: string;
  /** 合盘等嵌入场景: 不重复渲染已保存列表 */
  hideSavedList?: boolean;
  /** 紧凑布局, 减少区块标题与留白 */
  compact?: boolean;
  /** 打开编辑时预填的出生信息 */
  initialRequest?: PaipanRequest | null;
  /** 档案变更后通知父级刷新共用列表 */
  onProfilesChange?: () => void;
}

export function BirthForm({
  loading,
  onSubmit,
  onProfileLoad,
  embedded = false,
  submitLabel = "开始排盘",
  hideSavedList = false,
  compact = false,
  initialRequest = null,
  onProfilesChange,
}: Props) {
  const [form, setForm] = useState<BirthFormState>(() =>
    initialRequest ? paipanRequestToFormState(initialRequest) : defaultFormState(),
  );
  const [profiles, setProfiles] = useState<SavedProfile[]>([]);
  const [saveMessage, setSaveMessage] = useState("");

  const refreshProfiles = () => {
    setProfiles(listProfiles());
    onProfilesChange?.();
  };

  useEffect(() => {
    setProfiles(listProfiles());
  }, []);

  useEffect(() => {
    if (initialRequest) {
      setForm(paipanRequestToFormState(initialRequest));
    }
  }, [initialRequest]);

  const updateForm = (patch: Partial<BirthFormState>) => {
    setForm((prev) => ({ ...prev, ...patch }));
    setSaveMessage("");
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit(formToPaipanRequest(form));
  };

  const handleSaveNew = () => {
    if (!form.name.trim()) {
      setSaveMessage("请先填写姓名再保存");
      return;
    }
    const saved = saveNewProfile(form);
    updateForm({ activeProfileId: saved.id });
    refreshProfiles();
    setSaveMessage(`已另存为新档案: ${saved.name}`);
  };

  const handleUpdate = () => {
    if (!form.name.trim()) {
      setSaveMessage("请先填写姓名再保存");
      return;
    }
    if (!form.activeProfileId) {
      setSaveMessage("请先从下方列表选择要更新的档案, 或点「另存为新档案」");
      return;
    }
    const saved = updateProfile(form);
    if (!saved) {
      setSaveMessage("当前档案不存在, 请重新选择或另存为新档案");
      updateForm({ activeProfileId: null });
      refreshProfiles();
      return;
    }
    refreshProfiles();
    setSaveMessage(`已更新: ${saved.name}`);
  };

  const handleNewForm = () => {
    setForm(defaultFormState());
    setSaveMessage("已清空表单, 可填写新的出生信息");
  };

  const handleLoadProfile = (profile: SavedProfile) => {
    setForm(profileToFormState(profile));
    onProfileLoad?.(profile);
    setSaveMessage(`已载入: ${profile.name}`);
  };

  const handleDeleteProfile = (profileId: string) => {
    const target = profiles.find((item) => item.id === profileId);
    const label = target?.name || "未命名";
    if (!window.confirm(`确定删除 ${label} 的出生信息吗?`)) {
      return;
    }
    deleteProfile(profileId);
    refreshProfiles();
    if (form.activeProfileId === profileId) {
      updateForm({ activeProfileId: null });
    }
    setSaveMessage(`已删除: ${label}`);
  };

  const calendarLabel = form.calendarType === "lunar" ? "农历" : "公历";

  return (
    <div className="birth-section">
      <form
        className={
          embedded
            ? compact
              ? "birth-form cast-form birth-form-compact"
              : "birth-form cast-form"
            : "birth-form panel"
        }
        onSubmit={handleSubmit}
      >
        {!embedded && <h2>出生信息</h2>}

        <section className="cast-form-section">
          <h3 className="cast-form-section-title">
            {embedded ? "出生档案" : "命主信息"}
          </h3>
          <label className="field field-grow">
            <span>姓名</span>
            <input
              type="text"
              value={form.name}
              maxLength={32}
              placeholder="请输入姓名"
              onChange={(e) => updateForm({ name: e.target.value })}
            />
          </label>
          <div className="gender-row cast-form-options">
            <span className="gender-label">性别</span>
            <label className="field checkbox-field">
              <input
                type="radio"
                name="gender"
                checked={form.gender === 1}
                onChange={() => updateForm({ gender: 1 })}
              />
              <span>男</span>
            </label>
            <label className="field checkbox-field">
              <input
                type="radio"
                name="gender"
                checked={form.gender === 0}
                onChange={() => updateForm({ gender: 0 })}
              />
              <span>女</span>
            </label>
          </div>
        </section>

        <section className="cast-form-section">
          <h3 className="cast-form-section-title">出生时间</h3>
        <div className="calendar-tabs">
          <button
            type="button"
            className={form.calendarType === "solar" ? "tab active" : "tab"}
            onClick={() => updateForm({ calendarType: "solar", isLeapMonth: false })}
          >
            公历
          </button>
          <button
            type="button"
            className={form.calendarType === "lunar" ? "tab active" : "tab"}
            onClick={() => updateForm({ calendarType: "lunar" })}
          >
            农历
          </button>
        </div>

        <p className="hint">当前按 {calendarLabel} 输入年月日</p>

        <div className="field-row field-row-3">
          <label className="field">
            <span>年</span>
            <input
              type="number"
              value={form.year}
              min={1900}
              max={2100}
              onChange={(e) => updateForm({ year: Number(e.target.value) })}
            />
          </label>
          <label className="field">
            <span>月</span>
            <input
              type="number"
              value={form.month}
              min={1}
              max={12}
              onChange={(e) => updateForm({ month: Number(e.target.value) })}
            />
          </label>
          <label className="field">
            <span>日</span>
            <input
              type="number"
              value={form.day}
              min={1}
              max={30}
              onChange={(e) => updateForm({ day: Number(e.target.value) })}
            />
          </label>
        </div>

        {form.calendarType === "lunar" && (
          <label className="field checkbox-field">
            <input
              type="checkbox"
              checked={form.isLeapMonth}
              onChange={(e) => updateForm({ isLeapMonth: e.target.checked })}
            />
            <span>闰月</span>
          </label>
        )}

        <div className="field-row field-row-2">
          <label className="field">
            <span>时辰</span>
            <select
              value={form.hourSlot}
              onChange={(e) => updateForm({ hourSlot: Number(e.target.value) })}
            >
              {HOUR_SLOTS.map((h, idx) => (
                <option key={h.label} value={idx}>
                  {h.label}
                </option>
              ))}
            </select>
          </label>
          <label className="field field-narrow">
            <span>分</span>
            <input
              type="number"
              value={form.minute}
              min={0}
              max={59}
              onChange={(e) => updateForm({ minute: Number(e.target.value) })}
            />
          </label>
        </div>
        </section>

        {form.activeProfileId && (
          <p className="hint editing-profile-hint">
            正在编辑已选档案. 改完后可「更新当前档案」, 或填新人信息后点「另存为新档案」.
          </p>
        )}

        <div
          className={
            compact
              ? "form-actions form-actions-end form-actions-compact"
              : "form-actions form-actions-end"
          }
        >
          <button type="submit" className="primary-btn" disabled={loading}>
            {loading ? "处理中..." : submitLabel}
          </button>
          <button
            type="button"
            className="secondary"
            onClick={handleSaveNew}
            disabled={loading}
          >
            另存
          </button>
          {form.activeProfileId && (
            <button
              type="button"
              className="secondary"
              onClick={handleUpdate}
              disabled={loading}
            >
              更新
            </button>
          )}
          <button
            type="button"
            className="secondary"
            onClick={handleNewForm}
            disabled={loading}
          >
            清空
          </button>
        </div>

        {saveMessage && <p className="save-message">{saveMessage}</p>}
      </form>

      {!hideSavedList ? (
        <div className="panel saved-panel">
          <SavedProfiles
            profiles={profiles}
            activeProfileId={form.activeProfileId}
            onLoad={handleLoadProfile}
            onDelete={handleDeleteProfile}
          />
        </div>
      ) : null}
    </div>
  );
}
