import { useEffect, useState } from "react";
import type { BirthFormState, PaipanRequest, SavedProfile } from "../types/bazi";
import {
  defaultFormState,
  deleteProfile,
  formToPaipanRequest,
  listProfiles,
  profileToFormState,
  saveNewProfile,
  updateProfile,
} from "../services/profileStorage";
import { HOUR_SLOTS } from "../utils/timeSlots";
import { SavedProfiles } from "./SavedProfiles";

interface Props {
  loading: boolean;
  onSubmit: (data: PaipanRequest) => void;
}

export function BirthForm({ loading, onSubmit }: Props) {
  const [form, setForm] = useState<BirthFormState>(defaultFormState);
  const [profiles, setProfiles] = useState<SavedProfile[]>([]);
  const [saveMessage, setSaveMessage] = useState("");

  useEffect(() => {
    setProfiles(listProfiles());
  }, []);

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
    setProfiles(listProfiles());
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
      setProfiles(listProfiles());
      return;
    }
    setProfiles(listProfiles());
    setSaveMessage(`已更新: ${saved.name}`);
  };

  const handleNewForm = () => {
    setForm(defaultFormState());
    setSaveMessage("已清空表单, 可填写新的出生信息");
  };

  const handleLoadProfile = (profile: SavedProfile) => {
    setForm(profileToFormState(profile));
    setSaveMessage(`已载入: ${profile.name}`);
  };

  const handleDeleteProfile = (profileId: string) => {
    const target = profiles.find((item) => item.id === profileId);
    const label = target?.name || "未命名";
    if (!window.confirm(`确定删除 ${label} 的出生信息吗?`)) {
      return;
    }
    deleteProfile(profileId);
    setProfiles(listProfiles());
    if (form.activeProfileId === profileId) {
      updateForm({ activeProfileId: null });
    }
    setSaveMessage(`已删除: ${label}`);
  };

  const calendarLabel = form.calendarType === "lunar" ? "农历" : "公历";

  return (
    <div className="birth-section">
      <form className="birth-form panel" onSubmit={handleSubmit}>
        <h2>出生信息</h2>

        <label className="full-width">
          姓名
          <input
            type="text"
            value={form.name}
            maxLength={32}
            placeholder="请输入姓名"
            onChange={(e) => updateForm({ name: e.target.value })}
          />
        </label>

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

        <div className="form-row">
          <label>
            年
            <input
              type="number"
              value={form.year}
              min={1900}
              max={2100}
              onChange={(e) => updateForm({ year: Number(e.target.value) })}
            />
          </label>
          <label>
            月
            <input
              type="number"
              value={form.month}
              min={1}
              max={12}
              onChange={(e) => updateForm({ month: Number(e.target.value) })}
            />
          </label>
          <label>
            日
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
          <label className="leap-row">
            <input
              type="checkbox"
              checked={form.isLeapMonth}
              onChange={(e) => updateForm({ isLeapMonth: e.target.checked })}
            />
            闰月
          </label>
        )}

        <div className="form-row">
          <label className="grow">
            时辰
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
          <label>
            分
            <input
              type="number"
              value={form.minute}
              min={0}
              max={59}
              onChange={(e) => updateForm({ minute: Number(e.target.value) })}
            />
          </label>
        </div>

        <div className="form-row gender-row">
          <span>性别</span>
          <label>
            <input
              type="radio"
              name="gender"
              checked={form.gender === 1}
              onChange={() => updateForm({ gender: 1 })}
            />
            男
          </label>
          <label>
            <input
              type="radio"
              name="gender"
              checked={form.gender === 0}
              onChange={() => updateForm({ gender: 0 })}
            />
            女
          </label>
        </div>

        {form.activeProfileId && (
          <p className="hint editing-profile-hint">
            正在编辑已选档案. 改完后可「更新当前档案」, 或填新人信息后点「另存为新档案」.
          </p>
        )}

        <div className="form-actions">
          <button type="submit" disabled={loading}>
            {loading ? "排盘中..." : "开始排盘"}
          </button>
          <button
            type="button"
            className="secondary"
            onClick={handleSaveNew}
            disabled={loading}
          >
            另存为新档案
          </button>
          {form.activeProfileId && (
            <button
              type="button"
              className="secondary"
              onClick={handleUpdate}
              disabled={loading}
            >
              更新当前档案
            </button>
          )}
          <button
            type="button"
            className="secondary"
            onClick={handleNewForm}
            disabled={loading}
          >
            新建空白
          </button>
        </div>

        {saveMessage && <p className="save-message">{saveMessage}</p>}
      </form>

      <div className="panel saved-panel">
        <SavedProfiles
          profiles={profiles}
          activeProfileId={form.activeProfileId}
          onLoad={handleLoadProfile}
          onDelete={handleDeleteProfile}
        />
      </div>
    </div>
  );
}
