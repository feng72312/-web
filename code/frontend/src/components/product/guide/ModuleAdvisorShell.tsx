import { useEffect, useMemo, useState } from "react";
import {
  getModuleGuideItems,
  getModulesForAdvisorTag,
  getUtilityGuideItems,
  type AdvisorTagId,
  type ModuleGuideItem,
} from "../../../config/moduleGuideContent";
import type { UtilityId } from "../../../utilities/registry";
import { AdvisorQuestionTabs } from "./AdvisorQuestionTabs";
import { ModuleDetailPanel } from "./ModuleDetailPanel";
import { ModuleRecommendationCard } from "./ModuleRecommendationCard";
import { UtilityGuideStrip } from "./UtilityGuideStrip";

interface ModuleAdvisorShellProps {
  onSelectModule: (moduleId: string) => void;
  onSelectUtility: (utilityId: UtilityId) => void;
}

export function ModuleAdvisorShell({
  onSelectModule,
  onSelectUtility,
}: ModuleAdvisorShellProps) {
  const [activeTag, setActiveTag] = useState<AdvisorTagId>("life-pattern");
  const [activeItemId, setActiveItemId] = useState<string | null>(null);

  const utilities = useMemo(() => getUtilityGuideItems(), []);
  const recommended = useMemo(
    () => getModulesForAdvisorTag(activeTag),
    [activeTag],
  );

  useEffect(() => {
    if (activeTag === "quick-tool") {
      setActiveItemId(null);
      return;
    }
    if (recommended.length === 0) {
      setActiveItemId(null);
      return;
    }
    if (!activeItemId || !recommended.some((m) => m.id === activeItemId)) {
      setActiveItemId(recommended[0].id);
    }
  }, [activeTag, recommended, activeItemId]);

  const activeItem: ModuleGuideItem | null = useMemo(() => {
    if (!activeItemId) return null;
    return getModuleGuideItems().find((m) => m.id === activeItemId) ?? null;
  }, [activeItemId]);

  const handleEnterModule = (moduleId: string) => {
    if (moduleId === "12") {
      onSelectUtility("hepan");
      onSelectModule("12");
      return;
    }
    onSelectModule(moduleId);
  };

  return (
    <div className="module-advisor-page">
      <header className="module-advisor-intro">
        <p className="home-light-eyebrow">Discipline Advisor</p>
        <h1>术数选择向导</h1>
        <p>
          先选你的问题类型, 再看推荐术数、适合场景与测算流程, 然后进入对应工作台.
        </p>
      </header>

      <AdvisorQuestionTabs activeTag={activeTag} onChange={setActiveTag} />

      {activeTag === "quick-tool" ? (
        <UtilityGuideStrip
          items={utilities}
          onSelect={(id) => {
            onSelectUtility(id as UtilityId);
            onSelectModule("12");
          }}
        />
      ) : (
        <div className="module-advisor-layout">
          <div className="module-advisor-list">
            {recommended.length === 0 ? (
              <p className="module-advisor-empty">该类型暂无推荐模块.</p>
            ) : (
              recommended.map((item) => (
                <ModuleRecommendationCard
                  key={item.id}
                  item={item}
                  selected={activeItemId === item.id}
                  onSelect={() => setActiveItemId(item.id)}
                  onEnter={() => handleEnterModule(item.id)}
                />
              ))
            )}
          </div>
          <ModuleDetailPanel item={activeItem} />
        </div>
      )}

      {activeTag !== "quick-tool" && (
        <UtilityGuideStrip
          items={utilities}
          onSelect={(id) => {
            onSelectUtility(id as UtilityId);
            onSelectModule("12");
          }}
        />
      )}
    </div>
  );
}
