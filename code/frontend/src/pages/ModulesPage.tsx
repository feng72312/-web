import { lazy, Suspense, useEffect, useState } from "react";
import {
  getModuleMeta,
  type VisualThemeId,
} from "../config/productModules";
import { ModuleAdvisorShell } from "../components/product/guide/ModuleAdvisorShell";
import { ModuleSkeleton } from "../components/product/ModuleSkeleton";
import { VisualModuleFrame } from "../components/product/VisualModuleFrame";
import type { UtilityId } from "../utilities/registry";
import { DEFAULT_UTILITY } from "../utilities/registry";
import type { AiChatSession } from "../components/ai/types";

const BaziTab = lazy(() =>
  import("../tabs/BaziTab").then((m) => ({ default: m.BaziTab })),
);
const LiuyaoTab = lazy(() =>
  import("../tabs/LiuyaoTab").then((m) => ({ default: m.LiuyaoTab })),
);
const MeihuaTab = lazy(() =>
  import("../tabs/MeihuaTab").then((m) => ({ default: m.MeihuaTab })),
);
const LiurenTab = lazy(() =>
  import("../tabs/LiurenTab").then((m) => ({ default: m.LiurenTab })),
);
const QimenTab = lazy(() =>
  import("../tabs/QimenTab").then((m) => ({ default: m.QimenTab })),
);
const ZiweiTab = lazy(() =>
  import("../tabs/ZiweiTab").then((m) => ({ default: m.ZiweiTab })),
);
const XingmingTab = lazy(() =>
  import("../tabs/XingmingTab").then((m) => ({ default: m.XingmingTab })),
);
const FengshuiTab = lazy(() =>
  import("../tabs/FengshuiTab").then((m) => ({ default: m.FengshuiTab })),
);
const UtilsTab = lazy(() =>
  import("../tabs/UtilsTab").then((m) => ({ default: m.UtilsTab })),
);
const TarotTab = lazy(() =>
  import("../tabs/TarotTab").then((m) => ({ default: m.TarotTab })),
);

interface ModulesPageProps {
  initialModuleId?: string | null;
  initialUtilityId?: UtilityId | null;
  navigationRequest?: number;
  onOpenAiChatSession: (session: AiChatSession) => void;
}

const NATIVE_VISUAL_MODULES = new Set(["01", "13"]);

function renderModuleContent(
  moduleId: string,
  activeUtility: UtilityId,
  onUtilityChange: (id: UtilityId) => void,
  onOpenAiChatSession: (session: AiChatSession) => void,
) {
  switch (moduleId) {
    case "01":
      return <BaziTab onOpenAiChatSession={onOpenAiChatSession} />;
    case "02":
      return <LiuyaoTab onOpenAiChatSession={onOpenAiChatSession} />;
    case "03":
      return <MeihuaTab onOpenAiChatSession={onOpenAiChatSession} />;
    case "04":
      return <QimenTab onOpenAiChatSession={onOpenAiChatSession} />;
    case "05":
      return <LiurenTab onOpenAiChatSession={onOpenAiChatSession} />;
    case "06":
      return <FengshuiTab onOpenAiChatSession={onOpenAiChatSession} />;
    case "09":
      return <XingmingTab onOpenAiChatSession={onOpenAiChatSession} />;
    case "11":
      return <ZiweiTab onOpenAiChatSession={onOpenAiChatSession} />;
    case "12":
      return (
        <UtilsTab
          activeUtility={activeUtility}
          onUtilityChange={onUtilityChange}
          onOpenAiChatSession={onOpenAiChatSession}
        />
      );
    case "13":
      return <TarotTab onOpenAiChatSession={onOpenAiChatSession} />;
    default:
      return null;
  }
}

export function ModulesPage({
  initialModuleId = null,
  initialUtilityId = null,
  navigationRequest = 0,
  onOpenAiChatSession,
}: ModulesPageProps) {
  const [activeModuleId, setActiveModuleId] = useState<string | null>(
    initialModuleId ?? null,
  );
  const [visitedModules, setVisitedModules] = useState<string[]>(
    initialModuleId ? [initialModuleId] : [],
  );
  const [activeUtility, setActiveUtility] = useState<UtilityId>(
    initialUtilityId ?? DEFAULT_UTILITY,
  );

  useEffect(() => {
    if (!initialModuleId) {
      setActiveModuleId(null);
      return;
    }
    setActiveModuleId(initialModuleId);
    setVisitedModules((prev) =>
      prev.includes(initialModuleId) ? prev : [...prev, initialModuleId],
    );
    if (initialUtilityId) {
      setActiveUtility(initialUtilityId);
    }
  }, [initialModuleId, initialUtilityId, navigationRequest]);

  const resetPagePosition = () => {
    window.requestAnimationFrame(() => {
      window.scrollTo({ top: 0, left: 0, behavior: "auto" });
    });
  };

  const handleSelectModule = (moduleId: string) => {
    setActiveModuleId(moduleId);
    setVisitedModules((prev) => (prev.includes(moduleId) ? prev : [...prev, moduleId]));
    resetPagePosition();
  };

  const handleBack = () => {
    setActiveModuleId(null);
    resetPagePosition();
  };

  const handleUtilityChange = (utilityId: UtilityId) => {
    setActiveUtility(utilityId);
    resetPagePosition();
  };

  return (
    <div className="modules-page">
      <div hidden={activeModuleId !== null}>
        <ModuleAdvisorShell
          onSelectModule={handleSelectModule}
          onSelectUtility={handleUtilityChange}
        />
      </div>

      {visitedModules.map((moduleId) => {
        const hidden = activeModuleId !== moduleId;
        const moduleMeta = getModuleMeta(moduleId);
        const label = moduleMeta?.label ?? "预测模块";
        const theme = moduleMeta?.theme ?? "chart";
        const content = (
          <Suspense fallback={<ModuleSkeleton />}>
            {renderModuleContent(
              moduleId,
              activeUtility,
              handleUtilityChange,
              onOpenAiChatSession,
            )}
          </Suspense>
        );

        if (NATIVE_VISUAL_MODULES.has(moduleId)) {
          return (
            <div key={moduleId} hidden={hidden} className="modules-native-wrap">
              {!hidden && (
                <div className="modules-native-toolbar">
                  <button type="button" className="product-ghost-button" onClick={handleBack}>
                    返回模块列表
                  </button>
                </div>
              )}
              {content}
            </div>
          );
        }

        return (
          <div key={moduleId} hidden={hidden} className="modules-detail">
            <VisualModuleFrame
              moduleId={moduleId}
              label={moduleMeta?.label ?? label}
              theme={(moduleMeta?.theme ?? theme) as VisualThemeId}
              hasVisualDemo={moduleMeta?.hasVisualDemo}
              onBack={handleBack}
            >
              {content}
            </VisualModuleFrame>
          </div>
        );
      })}
    </div>
  );
}
