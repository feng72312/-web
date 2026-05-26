import type { AnalysisSection, Chart } from "../types/bazi";
import { getSectionModule } from "../registry/sectionRegistry";

interface Props {
  chart: Chart;
  sections: AnalysisSection[];
}

function FallbackSection({ section }: { section: AnalysisSection }) {
  return (
    <section className="panel">
      <h3>{section.name}</h3>
      <pre className="json-fallback">{JSON.stringify(section.data, null, 2)}</pre>
    </section>
  );
}

export function AnalysisPanels({ chart, sections }: Props) {
  const sorted = [...sections].sort((a, b) => a.order - b.order);

  return (
    <div className="analysis-grid">
      {sorted.map((section) => {
        const mod = getSectionModule(section.id);
        if (mod) {
          const Comp = mod.Component;
          return <Comp key={section.id} section={section} chart={chart} />;
        }
        return <FallbackSection key={section.id} section={section} />;
      })}
    </div>
  );
}
