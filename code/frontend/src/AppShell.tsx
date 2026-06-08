import { useState } from "react";
import { DisciplineIntroPanel } from "./components/DisciplineIntroPanel";
import { AuthAccountBar } from "./components/AuthAccountBar";
import { SiteFooter } from "./components/SiteFooter";
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
import { XingmingTab } from "./tabs/XingmingTab";
import { FengshuiTab } from "./tabs/FengshuiTab";
import { UtilsTab } from "./tabs/UtilsTab";
import type { UtilityId } from "./utilities/registry";
import { DEFAULT_UTILITY } from "./utilities/registry";
import "./styles/app.css";
import "./styles/chart-detail.css";

export default function AppShell() {
  const [activeTab, setActiveTab] = useState(DEFAULT_TAB);
  const [visitedTabs, setVisitedTabs] = useState<string[]>([DEFAULT_TAB]);
  const [activeUtility, setActiveUtility] = useState<UtilityId>(DEFAULT_UTILITY);
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
    if (tabId === "06") {
      return <FengshuiTab />;
    }
    if (tabId === "09") {
      return <XingmingTab />;
    }
    if (tabId === "11") {
      return <ZiweiTab />;
    }
    if (tabId === "12") {
      return (
        <UtilsTab activeUtility={activeUtility} onUtilityChange={setActiveUtility} />
      );
    }
    return null;
  };

  return (
    <div className="app-shell">
      <header className="app-header">
        <div className="app-header-top">
          <div>
            <p className="eyebrow">Shushu Platform MVP</p>
            <h1>术数排盘平台</h1>
            <p className="subtitle">
              术数 Tab: 八字 / 六爻 / 梅花 / 奇门 / 六壬 / 风水 / 星命 / 紫微已可用 | 实用专区: 合盘 / 诸葛神数 / 解梦 / 测字
            </p>
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
        <WorkflowGuide
          activeTab={activeTab}
          disciplineLabel={current?.label}
          utilityId={activeTab === "12" ? activeUtility : undefined}
        />
        <main className="app-main">
          {visitedTabs.map((tabId) => (
            <div key={tabId} hidden={activeTab !== tabId}>
              {renderTabContent(tabId)}
            </div>
          ))}
        </main>
        <aside className="discipline-intro-sidebar" aria-label="术数简介">
          <DisciplineIntroPanel tabId={activeTab} label={current?.label} />
        </aside>
      </div>
      <SiteFooter />
    </div>
  );
}
