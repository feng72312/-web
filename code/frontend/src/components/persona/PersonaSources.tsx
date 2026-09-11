import { BookMarked, ExternalLink } from "lucide-react";
import type { PersonaDetail } from "../../types/persona";

const SOURCE_LABELS = {
  primary: "原典",
  research: "研究",
  upstream: "上游",
  critical: "边界",
} as const;

interface PersonaSourcesProps {
  persona: PersonaDetail;
}

export function PersonaSources({ persona }: PersonaSourcesProps) {
  return (
    <div className="persona-sources-content">
      <header>
        <BookMarked size={18} aria-hidden="true" />
        <div>
          <p>Sources & Boundaries</p>
          <h3>据何而谈</h3>
        </div>
      </header>
      <p className="persona-source-rule">
        只有目录内可核验的文字才作为原典引用；其余内容会明确视为思想框架下的模拟分析。
      </p>
      <ol className="persona-source-list">
        {persona.sources.map((source) => (
          <li key={source.id}>
            <span>{SOURCE_LABELS[source.kind]}</span>
            <strong>{source.title}</strong>
            <p>{source.note}</p>
            {source.citation ? <small>{source.citation}</small> : null}
            {source.url ? (
              <a href={source.url} target="_blank" rel="noreferrer">
                查看来源 <ExternalLink size={12} />
              </a>
            ) : null}
          </li>
        ))}
      </ol>
      <div className="persona-source-license">
        <strong>{persona.license.name} 人物包</strong>
        <span>{persona.license.attribution}</span>
      </div>
    </div>
  );
}
