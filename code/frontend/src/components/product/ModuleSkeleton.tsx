export function ModuleSkeleton() {
  return (
    <div className="bazi-report-card module-skeleton" aria-busy="true" aria-live="polite">
      <p className="bazi-card-eyebrow">加载模块</p>
      <div className="module-skeleton-block" />
      <div className="module-skeleton-block short" />
      <div className="module-skeleton-block" />
    </div>
  );
}
