import { ADVISOR_TAGS, type AdvisorTagId } from "../../../config/moduleGuideContent";

interface AdvisorQuestionTabsProps {
  activeTag: AdvisorTagId;
  onChange: (tag: AdvisorTagId) => void;
}

export function AdvisorQuestionTabs({ activeTag, onChange }: AdvisorQuestionTabsProps) {
  return (
    <div className="advisor-question-tabs" role="tablist" aria-label="问题类型">
      {ADVISOR_TAGS.map((tag, index) => (
        <button
          key={tag.id}
          type="button"
          role="tab"
          aria-selected={activeTag === tag.id}
          className={activeTag === tag.id ? "advisor-tab active" : "advisor-tab"}
          onClick={() => onChange(tag.id)}
        >
          <span className="advisor-tab-index">0{index + 1}</span>
          <span className="advisor-tab-copy">
            <strong>{tag.label}</strong>
            <span>{tag.hint}</span>
          </span>
        </button>
      ))}
    </div>
  );
}
