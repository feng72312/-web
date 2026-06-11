import { AuthAccountBar } from "../AuthAccountBar";
import { PlatformControls } from "../PlatformControls";
import { QuotaBar } from "../QuotaBar";
import { UsageStatsBar } from "../UsageStatsBar";
import type { ProductPageId } from "../../config/productModules";

interface ProductTopNavProps {
  activePage: ProductPageId;
  onPageChange: (page: ProductPageId) => void;
}

const PAGES: { id: ProductPageId; label: string }[] = [
  { id: "home", label: "首页" },
  { id: "modules", label: "预测模块" },
  { id: "chat", label: "AI 对话" },
];

export function ProductTopNav({ activePage, onPageChange }: ProductTopNavProps) {
  return (
    <header className="product-topnav">
      <div className="product-topnav-brand">
        <p className="product-eyebrow">Ziyun Destiny Observatory</p>
        <h1>紫云命理天文馆</h1>
      </div>

      <nav className="product-page-nav" aria-label="产品导航">
        {PAGES.map((page) => (
          <button
            key={page.id}
            type="button"
            className={activePage === page.id ? "product-page-tab active" : "product-page-tab"}
            onClick={() => onPageChange(page.id)}
          >
            {page.label}
          </button>
        ))}
      </nav>

      <div className="product-topnav-side">
        <PlatformControls />
        <AuthAccountBar />
        <QuotaBar />
        <UsageStatsBar />
      </div>
    </header>
  );
}
