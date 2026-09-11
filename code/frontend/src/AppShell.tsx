import { useEffect, useState } from "react";
import { SiteFooter } from "./components/SiteFooter";
import { InterpretQueueBanner } from "./components/InterpretQueueBanner";
import { ProductTopNav } from "./components/product/ProductTopNav";
import { HomePage } from "./pages/HomePage";
import { ModulesPage } from "./pages/ModulesPage";
import { AiChatPage } from "./pages/AiChatPage";
import { PersonaPage } from "./pages/PersonaPage";
import type { ProductPageId } from "./config/productModules";
import type { UtilityId } from "./utilities/registry";
import type { AiChatSession } from "./components/ai/types";

import "./styles/app.css";
import "./styles/chart-detail.css";
import "./styles/product-shell.css";
import "./styles/visual-workbench.css";
import "./styles/theme-modes.css";
import "./styles/ai-chat.css";
import "./styles/persona-dialogue.css";

const PRODUCT_PAGES: ProductPageId[] = ["home", "modules", "personas", "chat"];

function pageFromLocation(): ProductPageId {
  const page = new URLSearchParams(window.location.search).get("page");
  return PRODUCT_PAGES.includes(page as ProductPageId)
    ? (page as ProductPageId)
    : "home";
}

export default function AppShell() {
  const [activePage, setActivePage] = useState<ProductPageId>(pageFromLocation);
  const [moduleEntryId, setModuleEntryId] = useState<string | null>(null);
  const [utilityEntryId, setUtilityEntryId] = useState<UtilityId | null>(null);
  const [modulesNavigationRequest, setModulesNavigationRequest] = useState(0);
  const [pendingAiChatSession, setPendingAiChatSession] =
    useState<AiChatSession | null>(null);

  const resetPagePosition = () => {
    window.requestAnimationFrame(() => {
      window.scrollTo({ top: 0, left: 0, behavior: "auto" });
    });
  };

  useEffect(() => {
    const handleHistoryNavigation = () => {
      setActivePage(pageFromLocation());
      resetPagePosition();
    };
    window.addEventListener("popstate", handleHistoryNavigation);
    return () => window.removeEventListener("popstate", handleHistoryNavigation);
  }, []);

  const handlePageChange = (page: ProductPageId) => {
    if (page === "modules") {
      setModuleEntryId(null);
      setUtilityEntryId(null);
      setModulesNavigationRequest((current) => current + 1);
    }
    const url = new URL(window.location.href);
    if (page === "home") {
      url.searchParams.delete("page");
    } else {
      url.searchParams.set("page", page);
    }
    window.history.pushState(null, "", `${url.pathname}${url.search}${url.hash}`);
    setActivePage(page);
    resetPagePosition();
  };

  const handleEnterModule = (moduleId: string, utilityId?: UtilityId) => {
    setModuleEntryId(moduleId);
    setUtilityEntryId(moduleId === "12" ? (utilityId ?? null) : null);
    setModulesNavigationRequest((current) => current + 1);
    setActivePage("modules");
    resetPagePosition();
  };

  const handleOpenAiChatSession = (session: AiChatSession) => {
    setPendingAiChatSession(session);
    setActivePage("chat");
    resetPagePosition();
  };

  return (
    <div className="product-shell">
      <div className="app-shell">
        <a className="product-skip-link" href="#product-main">
          跳到主要内容
        </a>
        <ProductTopNav activePage={activePage} onPageChange={handlePageChange} />
        <InterpretQueueBanner />

        <main className="product-main" id="product-main" tabIndex={-1}>
          <div hidden={activePage !== "home"}>
            <HomePage
              onEnterModule={handleEnterModule}
              onGoModules={() => handlePageChange("modules")}
              onGoChat={() => handlePageChange("chat")}
            />
          </div>
          <div hidden={activePage !== "modules"}>
            <ModulesPage
              initialModuleId={moduleEntryId}
              initialUtilityId={utilityEntryId}
              navigationRequest={modulesNavigationRequest}
              onOpenAiChatSession={handleOpenAiChatSession}
            />
          </div>
          <div hidden={activePage !== "chat"}>
            <AiChatPage
              onGoModules={() => handlePageChange("modules")}
              pendingSession={pendingAiChatSession}
              onPendingSessionConsumed={() => setPendingAiChatSession(null)}
              isActive={activePage === "chat"}
            />
          </div>
          <div hidden={activePage !== "personas"}>
            <PersonaPage isActive={activePage === "personas"} />
          </div>
        </main>

        <SiteFooter />
      </div>
    </div>
  );
}
