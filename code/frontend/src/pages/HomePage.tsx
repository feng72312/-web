import { useMemo } from "react";
import { getModuleGuideItems } from "../config/moduleGuideContent";
import { buildModuleShowcaseList, getUtilityShowcaseList } from "../config/productModules";
import { HomeKnowledgeAiPanel } from "../components/product/home/HomeKnowledgeAiPanel";
import { HomeProductHero } from "../components/product/home/HomeProductHero";
import { HomeSelectedEntrances } from "../components/product/home/HomeSelectedEntrances";
import { HomeWorkflowStory } from "../components/product/home/HomeWorkflowStory";
import type { UtilityId } from "../utilities/registry";

interface HomePageProps {
  onEnterModule: (moduleId: string, utilityId?: UtilityId) => void;
  onGoModules?: () => void;
  onGoChat?: () => void;
}

export function HomePage({ onEnterModule, onGoModules, onGoChat }: HomePageProps) {
  const moduleCount = buildModuleShowcaseList().length;
  const utilityCount = getUtilityShowcaseList().filter((u) => u.enabled).length;
  const guideItems = useMemo(() => getModuleGuideItems(), []);

  const handleEnterModules = () => {
    if (onGoModules) {
      onGoModules();
    } else {
      onEnterModule("01");
    }
  };

  const handleEnterChat = () => {
    if (onGoChat) {
      onGoChat();
    }
  };

  return (
    <div className="home-product-page">
      <HomeProductHero
        moduleCount={moduleCount}
        utilityCount={utilityCount}
        onEnterModules={handleEnterModules}
        onEnterChat={handleEnterChat}
      />
      <HomeSelectedEntrances
        items={guideItems}
        onEnterModule={(id) => onEnterModule(id)}
        onEnterModules={handleEnterModules}
      />
      <HomeKnowledgeAiPanel />
      <HomeWorkflowStory />
    </div>
  );
}
