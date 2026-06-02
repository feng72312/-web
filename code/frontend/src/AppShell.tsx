import { useState } from "react";
import { AuthAccountBar } from "./components/AuthAccountBar";
import { UsageStatsBar } from "./components/UsageStatsBar";
import { QuotaBar } from "./components/QuotaBar";
import { WorkflowGuide } from "./components/WorkflowGuide";
import { BaziTab } from "./tabs/BaziTab";
import { DISCIPLINE_TABS, DEFAULT_TAB } from "./tabs/disciplines";
import { LiuyaoTab } from "./tabs/LiuyaoTab";
import { MeihuaTab } from "./tabs/MeihuaTab";
import { LiurenTab } from "./tabs/LiurenTab";
import { QimenTab } from "./tabs/QimenTab";
import { ZiweiTab } from "./tabs/ZiweiTab";
import { PlaceholderTab } from "./tabs/PlaceholderTab";
import "./styles/app.css";
import "./styles/chart-detail.css";

const PLACEHOLDER_LABELS: Record<string, string> = {
  "03": "梅花易数",
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
  const [visitedTabs, setVisitedTabs] = useState<string[]>([DEFAULT_TAB]);
  const current = DISCIPLINE_TABS.find((tab) => tab.id === activeTab);

  const handleSelectTab = (tabId: string) => {
    setActiveTab(tabId);
    setVisitedTabs((prev) => (prev.includes(tabId) ? prev : [...prev, tabId]));
  };

  const renderTabContent = (tabId: string) => {
    if (tabId === "01") {
      return <BaziTab />;
    }
    if (tabId === "02") {
      return <LiuyaoTab />;
    }
    if (tabId === "03") {
      return <MeihuaTab />;
    }
    if (tabId === "04") {
      return <QimenTab />;
    }
    if (tabId === "05") {
      return <LiurenTab />;
    }
    if (tabId === "11") {
      return <ZiweiTab />;
    }
    const tab = DISCIPLINE_TABS.find((item) => item.id === tabId);
    return <PlaceholderTab title={PLACEHOLDER_LABELS[tabId] ?? tab?.label ?? ""} />;
  };

  return (
    <div className="app-shell">
      <header className="app-header">
        <div className="app-header-top">
          <div>
            <p className="eyebrow">Shushu Platform MVP</p>
            <h1>术数排盘平台</h1>
            <p className="subtitle">术数 Tab: 八字 / 六爻 / 梅花 / 奇门 / 六壬 / 紫微斗数已可用</p>
          </div>
          <div className="app-header-side">
            <AuthAccountBar />
            <QuotaBar />
            <UsageStatsBar />
          </div>
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
              onClick={() => handleSelectTab(tab.id)}
            >
              {tab.label}
              {!tab.enabled && <span className="view-nav-tag">待开发</span>}
            </button>
          ))}
        </nav>
      </header>

      <div className="app-body">
        <WorkflowGuide activeTab={activeTab} disciplineLabel={current?.label} />
        <main className="app-main">
          {visitedTabs.map((tabId) => (
            <div key={tabId} hidden={activeTab !== tabId}>
              {renderTabContent(tabId)}
            </div>
          ))}
        </main>
      </div>
    </div>
  );
}
