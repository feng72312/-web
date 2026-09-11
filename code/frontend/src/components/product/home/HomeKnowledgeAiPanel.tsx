import { BookOpen, MessagesSquare, ShieldCheck } from "lucide-react";

export function HomeKnowledgeAiPanel() {
  return (
    <section className="home-trust-section">
      <div className="home-trust-lead">
        <p className="home-light-eyebrow">Evidence Before Answer</p>
        <h2>先有命盘与典籍依据，再给判断</h2>
        <p>
          每一份解读先经过确定性排盘、规则判定和典籍检索，再由 AI 整理成专业版与白话版。
        </p>
        <blockquote>
          “不是把玄学说得更玄，而是把依据、边界和不确定性都摆在你面前。”
        </blockquote>
      </div>
      <div className="home-trust-columns">
        <article>
          <BookOpen size={22} strokeWidth={1.6} aria-hidden="true" />
          <h3>典籍证据</h3>
          <p>展示引用来源、规则依据与证据层级，结论不再只有一句“吉或凶”。</p>
        </article>
        <article>
          <ShieldCheck size={22} strokeWidth={1.6} aria-hidden="true" />
          <h3>判断边界</h3>
          <p>标注置信度、冲突意见和适用范围，重要决定仍由你掌握。</p>
        </article>
        <article>
          <MessagesSquare size={22} strokeWidth={1.6} aria-hidden="true" />
          <h3>持续追问</h3>
          <p>看完报告后继续对话，把事业、关系和时间节点逐层问透。</p>
        </article>
      </div>
    </section>
  );
}
