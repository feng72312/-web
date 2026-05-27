import { useState } from "react";
import { UsageStatsBar } from "./components/UsageStatsBar";
import { BaziTab } from "./tabs/BaziTab";
import { DISCIPLINE_TABS, DEFAULT_TAB } from "./tabs/disciplines";
import { LiuyaoTab } from "./tabs/LiuyaoTab";
import { PlaceholderTab } from "./tabs/PlaceholderTab";
import "./styles/app.css";
import "./styles/chart-detail.css";

const PLACEHOLDER_LABELS: Record<string, string> = {
  "03": "梅花易学",
  "04": "奇门遁甲",
  "05": "大六壬",
  "06": "风水堪舆",
  "07": "相术神相",
  "08": "择日历算",
  "09": "星命占验",
  "10": "杂占方术",
};

export default function AppShell() {
  const [activeTab, setActiveTab] = useState(DEFAULT_TAB);
  const current = DISCIPLINE_TABS.find((tab) => tab.id === activeTab);

  return (
    <div className="app-shell">
      <header className="app-header">
        <div className="app-header-top">
          <div>
            <p className="eyebrow">Shushu Platform MVP</p>
            <h1>术数排盘平台</h1>
            <p className="subtitle">十类术数 Tab, 当前优先六爻卜筮</p>
          </div>
          <UsageStatsBar />
        </div>
        <nav className="discipline-tabs" aria-label="术数分类">
          {DISCIPLINE_TABS.map((tab) => (
            <button
              key={tab.id}
              type="button"
              className={
                activeTab === tab.id
                  ? "discipline-tab active"
                  : "discipline-tab"
              }
              onClick={() => setActiveTab(tab.id)}
            >
              {tab.label}
              {!tab.enabled && <span className="view-nav-tag">待开发</span>}
            </button>
          ))}
        </nav>
      </header>

      <main className="app-main">
        {activeTab === "01" && <BaziTab />}
        {activeTab === "02" && <LiuyaoTab />}
        {activeTab !== "01" && activeTab !== "02" && (
          <PlaceholderTab title={PLACEHOLDER_LABELS[activeTab] ?? current?.label ?? ""} />
        )}
      </main>
    </div>
  );
}
