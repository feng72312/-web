import { BookOpenText, Compass, Home, MessagesSquare, Settings2 } from "lucide-react";
import type { LucideIcon } from "lucide-react";
import { AuthAccountBar } from "../AuthAccountBar";
import { PlatformControls } from "../PlatformControls";
import { QuotaBar } from "../QuotaBar";
import { UsageStatsBar } from "../UsageStatsBar";
import type { ProductPageId } from "../../config/productModules";

interface ProductTopNavProps {
  activePage: ProductPageId;
  onPageChange: (page: ProductPageId) => void;
}

const PAGES: { id: ProductPageId; label: string; icon: LucideIcon }[] = [
  { id: "home", label: "首页", icon: Home },
  { id: "modules", label: "术数推演", icon: Compass },
  { id: "personas", label: "名人对话", icon: BookOpenText },
  { id: "chat", label: "AI 顾问", icon: MessagesSquare },
];

export function ProductTopNav({ activePage, onPageChange }: ProductTopNavProps) {
  return (
    <header className="product-topnav">
      <button
        type="button"
        className="product-topnav-brand"
        onClick={() => onPageChange("home")}
        aria-label="返回首页"
      >
        <p className="product-eyebrow">Ziyun Destiny Observatory</p>
        <h1>紫云命理天文馆</h1>
      </button>

      <nav className="product-page-nav" aria-label="产品导航">
        {PAGES.map((page) => {
          const Icon = page.icon;
          return (
            <button
              key={page.id}
              type="button"
              className={activePage === page.id ? "product-page-tab active" : "product-page-tab"}
              aria-current={activePage === page.id ? "page" : undefined}
              onClick={() => onPageChange(page.id)}
            >
              <Icon size={16} strokeWidth={1.8} aria-hidden="true" />
              {page.label}
            </button>
          );
        })}
      </nav>

      <div className="product-topnav-side">
        <QuotaBar />
        <AuthAccountBar />
        <details className="product-tools-menu">
          <summary aria-label="打开界面设置">
            <Settings2 size={17} strokeWidth={1.8} aria-hidden="true" />
            <span>界面</span>
          </summary>
          <div className="product-tools-popover">
            <section>
              <p>显示设置</p>
              <PlatformControls />
            </section>
            <section>
              <p>运行概览</p>
              <UsageStatsBar />
            </section>
          </div>
        </details>
      </div>
    </header>
  );
}
