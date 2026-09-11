import { ArrowRight, BookOpen, MessageCircleMore } from "lucide-react";

interface HomeProductHeroProps {
  moduleCount: number;
  utilityCount: number;
  onEnterModules: () => void;
  onEnterChat: () => void;
}

export function HomeProductHero({
  moduleCount,
  utilityCount,
  onEnterModules,
  onEnterChat,
}: HomeProductHeroProps) {
  return (
    <section className="home-product-hero">
      <div className="home-product-hero-copy">
        <p className="home-light-eyebrow">ZIYUN Destiny Observatory</p>
        <h1>
          从一张命盘
          <span>看清人生的起承转合</span>
        </h1>
        <p className="home-product-lead">
          以八字、紫微、六爻等东方术数为骨架，以典籍证据和 AI 顾问为脉络，
          把复杂的命盘、眼前的选择与未来的节奏讲清楚。
        </p>
        <div className="home-product-actions">
          <button type="button" className="home-btn-primary" onClick={onEnterModules}>
            开始推演
            <ArrowRight size={17} strokeWidth={1.8} aria-hidden="true" />
          </button>
          <button type="button" className="home-btn-secondary" onClick={onEnterChat}>
            <MessageCircleMore size={17} strokeWidth={1.8} aria-hidden="true" />
            先问 AI 顾问
          </button>
        </div>
        <div className="home-hero-facts" aria-label="平台能力">
          <span><strong>{moduleCount}</strong> 门术数</span>
          <span><strong>{utilityCount}</strong> 项工具</span>
          <span><strong>典籍</strong> 证据可溯源</span>
        </div>
      </div>
      <div className="home-chart-stage" aria-label="命盘与典籍解读预览">
        <span className="home-hero-seal" aria-hidden="true">紫云</span>
        <div className="home-chart-orbit" aria-hidden="true">
          <span className="home-chart-orbit-ring ring-one" />
          <span className="home-chart-orbit-ring ring-two" />
          <span className="home-chart-axis axis-x" />
          <span className="home-chart-axis axis-y" />
          <strong>命</strong>
        </div>
        <div className="home-pillar-preview" aria-label="四柱示意">
          {[
            ["年柱", "甲子"],
            ["月柱", "丙寅"],
            ["日柱", "辛巳"],
            ["时柱", "壬辰"],
          ].map(([label, value]) => (
            <div key={label}>
              <span>{label}</span>
              <strong>{value}</strong>
            </div>
          ))}
        </div>
        <blockquote className="home-classic-note">
          <BookOpen size={18} strokeWidth={1.7} aria-hidden="true" />
          <div>
            <p>“论命先观月令，察其旺衰，再取用神。”</p>
            <cite>典籍证据 · 解读时标注来源</cite>
          </div>
        </blockquote>
        <div className="home-chart-caption">
          <span>命盘预览</span>
          <span>格局 · 岁运 · 证据链</span>
        </div>
      </div>
    </section>
  );
}
