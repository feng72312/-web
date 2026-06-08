import {
  DISCIPLINE_SELECTION_TIPS,
  getDisciplineIntro,
} from "../config/disciplineIntros";

interface DisciplineIntroPanelProps {
  tabId: string;
  label?: string;
}

export function DisciplineIntroPanel({ tabId, label }: DisciplineIntroPanelProps) {
  const intro = getDisciplineIntro(tabId);
  if (!intro) {
    return null;
  }

  const title = label
    ? intro.subtitle
      ? `${label} (${intro.subtitle})`
      : label
    : "术数简介";

  return (
    <section className="panel discipline-intro-panel">
      <div className="discipline-intro-header">
        <h2>{title}</h2>
      </div>

      <div className="discipline-intro-fields">
        <div className="discipline-intro-field">
          <h3>预测类别</h3>
          <p>{intro.category}</p>
        </div>
        <div className="discipline-intro-field">
          <h3>核心方法</h3>
          <p>{intro.coreMethod}</p>
        </div>
        <div className="discipline-intro-field">
          <h3>特点</h3>
          <p>{intro.characteristics}</p>
          {intro.advantages.length > 0 && (
            <ul className="discipline-intro-questions discipline-intro-traits">
              {intro.advantages.map((item) => (
                <li key={item}>{item}</li>
              ))}
            </ul>
          )}
        </div>
        <div className="discipline-intro-field">
          <h3>推荐测算</h3>
          <ul className="discipline-intro-questions">
            {intro.recommendedFor.map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ul>
        </div>
        <div className="discipline-intro-field">
          <h3>典型问题</h3>
          <ul className="discipline-intro-questions">
            {intro.typicalQuestions.map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ul>
        </div>
      </div>

      <div className="discipline-intro-selection">
        <h3>如何选择</h3>
        <ul>
          {DISCIPLINE_SELECTION_TIPS.map((item) => (
            <li key={item}>{item}</li>
          ))}
        </ul>
      </div>
    </section>
  );
}
