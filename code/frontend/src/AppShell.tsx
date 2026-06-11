import { useState } from "react";
import { SiteFooter } from "./components/SiteFooter";
import { ProductTopNav } from "./components/product/ProductTopNav";
import { HomePage } from "./pages/HomePage";
import { ModulesPage } from "./pages/ModulesPage";
import { AiChatPage } from "./pages/AiChatPage";
import type { ProductPageId } from "./config/productModules";
import type { UtilityId } from "./utilities/registry";
import type { AiChatSession } from "./components/ai/types";

import "./styles/app.css";
import "./styles/chart-detail.css";
import "./styles/product-shell.css";
import "./styles/visual-workbench.css";
import "./styles/theme-modes.css";
import "./styles/ai-chat.css";

export default function AppShell() {
  const [activePage, setActivePage] = useState<ProductPageId>("home");
  const [moduleEntryId, setModuleEntryId] = useState<string | null>(null);
  const [utilityEntryId, setUtilityEntryId] = useState<UtilityId | null>(null);
  const [pendingAiChatSession, setPendingAiChatSession] =
    useState<AiChatSession | null>(null);

  const handlePageChange = (page: ProductPageId) => {
    setActivePage(page);
  };

  const handleEnterModule = (moduleId: string, utilityId?: UtilityId) => {
    setModuleEntryId(moduleId);
    setUtilityEntryId(moduleId === "12" ? (utilityId ?? null) : null);
    setActivePage("modules");
  };

  const handleOpenAiChatSession = (session: AiChatSession) => {
    setPendingAiChatSession(session);
    setActivePage("chat");
  };

  return (
    <div className="product-shell">
      <div className="app-shell">
        <ProductTopNav activePage={activePage} onPageChange={handlePageChange} />

        <main className="product-main">
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
        </main>

        <SiteFooter />
      </div>
    </div>
  );
}
