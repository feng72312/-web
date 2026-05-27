type AppView = "summary" | "pillars" | "luck" | "chat";

interface Props {
  activeView: AppView;
  chatReady: boolean;
  chatLoading: boolean;
  onSelectSummary: () => void;
  onSelectChat: () => void;
}

export function AppViewNav({
  activeView,
  chatReady,
  chatLoading,
  onSelectSummary,
  onSelectChat,
}: Props) {
  const onChart = activeView === "summary" || activeView === "pillars" || activeView === "luck";

  return (
    <nav className="app-view-nav" aria-label="主视图切换">
      <button
        type="button"
        className={onChart ? "view-nav-btn active" : "view-nav-btn"}
        onClick={onSelectSummary}
      >
        命盘
      </button>
      <button
        type="button"
        className={activeView === "chat" ? "view-nav-btn active" : "view-nav-btn"}
        onClick={onSelectChat}
      >
        AI 对话
        {chatLoading && <span className="view-nav-tag">连接中</span>}
        {!chatLoading && chatReady && <span className="view-nav-tag ready">就绪</span>}
      </button>
    </nav>
  );
}

export type { AppView };
