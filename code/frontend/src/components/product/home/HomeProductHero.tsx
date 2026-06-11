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
        <h1>东方术数智能工作台</h1>
        <p className="home-product-lead">
          汇聚千年命理智慧与现代智能顾问, 为你把人生起伏、眼前抉择、关系与环境
          讲得透彻、说得明白. 不问生辰也能找到方向, 问得越深, 答得越准.
        </p>
        <div className="home-product-actions">
          <button type="button" className="home-btn-primary" onClick={onEnterModules}>
            开始选择术数
          </button>
          <button type="button" className="home-btn-secondary" onClick={onEnterChat}>
            与 AI 顾问聊聊
          </button>
        </div>
      </div>
      <div className="home-product-metrics">
        <div className="home-metric-card">
          <strong>{moduleCount}</strong>
          <span>术数门类</span>
        </div>
        <div className="home-metric-card">
          <strong>{utilityCount}</strong>
          <span>实用工具</span>
        </div>
        <div className="home-metric-card">
          <strong>典籍</strong>
          <span>千年智慧护航</span>
        </div>
        <div className="home-metric-card">
          <strong>双档</strong>
          <span>专业与白话解读</span>
        </div>
        <div className="home-metric-card">
          <strong>24h</strong>
          <span>随时问事解惑</span>
        </div>
        <div className="home-metric-card">
          <strong>多轮</strong>
          <span>聊到心里踏实</span>
        </div>
      </div>
    </section>
  );
}
