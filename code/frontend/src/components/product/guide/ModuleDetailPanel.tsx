import type { ModuleGuideItem } from "../../../config/moduleGuideContent";
import { ModuleWorkflowPreview } from "./ModuleWorkflowPreview";

interface ModuleDetailPanelProps {
  item: ModuleGuideItem | null;
}

export function ModuleDetailPanel({ item }: ModuleDetailPanelProps) {
  if (!item) {
    return (
      <aside className="module-detail-panel empty">
        <p>选择左侧推荐模块查看详情与测算流程.</p>
      </aside>
    );
  }

  return (
    <aside className={`module-detail-panel theme-${item.theme}`}>
      <header>
        <p className="home-light-eyebrow">Module Detail</p>
        <h2>{item.label}</h2>
        {item.category && <p className="module-detail-category">{item.category}</p>}
      </header>

      {item.coreMethod && (
        <section className="module-detail-section">
          <h3>核心方法</h3>
          <p>{item.coreMethod}</p>
        </section>
      )}

      {item.characteristics && (
        <section className="module-detail-section">
          <h3>特点</h3>
          <p>{item.characteristics}</p>
        </section>
      )}

      {item.advantages.length > 0 && (
        <section className="module-detail-section">
          <h3>优势</h3>
          <ul>
            {item.advantages.slice(0, 3).map((a) => (
              <li key={a}>{a}</li>
            ))}
          </ul>
        </section>
      )}

      {item.recommendedFor.length > 0 && (
        <section className="module-detail-section">
          <h3>适合测算</h3>
          <ul>
            {item.recommendedFor.slice(0, 3).map((r) => (
              <li key={r}>{r}</li>
            ))}
          </ul>
        </section>
      )}

      {item.typicalQuestions.length > 0 && (
        <section className="module-detail-section">
          <h3>典型问题</h3>
          <ul>
            {item.typicalQuestions.slice(0, 2).map((q) => (
              <li key={q}>{q}</li>
            ))}
          </ul>
        </section>
      )}

      <ModuleWorkflowPreview workflow={item.workflow} previewCount={3} />
    </aside>
  );
}
