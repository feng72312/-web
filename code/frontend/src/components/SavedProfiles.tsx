import { useEffect, useState } from "react";

import type { SavedProfile } from "../types/bazi";
import { HOUR_SLOTS } from "../utils/timeSlots";

interface Props {
  profiles: SavedProfile[];
  activeProfileId: string | null;
  onLoad: (profile: SavedProfile) => void;
  onDelete: (profileId: string) => void;
}

function formatProfile(profile: SavedProfile): string {
  const calendar = profile.calendarType === "lunar" ? "农历" : "公历";
  const leap = profile.isLeapMonth ? " 闰月" : "";
  const gender = profile.gender === 1 ? "男" : "女";
  const hour = HOUR_SLOTS[profile.hourSlot]?.label.split(" ")[0] || "";
  return `${calendar} ${profile.year}-${profile.month}-${profile.day}${leap} ${hour} ${gender}`;
}

export function SavedProfiles({
  profiles,
  activeProfileId,
  onLoad,
  onDelete,
}: Props) {
  const [collapsed, setCollapsed] = useState(profiles.length > 2);

  useEffect(() => {
    if (profiles.length === 0) {
      setCollapsed(false);
    }
  }, [profiles.length]);

  if (profiles.length === 0) {
    return (
      <div className="saved-profiles empty">
        <p className="hint">暂无已保存的出生信息。填写后点「另存为新档案」即可保存多人。</p>
      </div>
    );
  }

  return (
    <div className={collapsed ? "saved-profiles collapsed" : "saved-profiles"}>
      <div className="saved-profiles-header">
        <h3>已保存 ({profiles.length})</h3>
        <button
          type="button"
          className="saved-profiles-toggle"
          onClick={() => setCollapsed((prev) => !prev)}
          aria-expanded={!collapsed}
        >
          {collapsed ? "展开" : "收起"}
        </button>
      </div>
      {!collapsed && (
        <ul className="profile-list">
          {profiles.map((profile) => (
            <li
              key={profile.id}
              className={profile.id === activeProfileId ? "profile-item active" : "profile-item"}
            >
              <button
                type="button"
                className="profile-load"
                onClick={() => onLoad(profile)}
              >
                <span className="profile-name">{profile.name || "未命名"}</span>
                <span className="profile-meta">{formatProfile(profile)}</span>
              </button>
              <button
                type="button"
                className="profile-delete"
                onClick={() => onDelete(profile.id)}
              >
                删除
              </button>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
