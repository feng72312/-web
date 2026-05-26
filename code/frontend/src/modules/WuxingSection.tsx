import type { SectionModuleProps } from "../types/bazi";

const ORDER = ["\u6728", "\u706b", "\u571f", "\u91d1", "\u6c34"];
const WX_CLASS: Record<string, string> = {
  "\u6728": "wx-wood",
  "\u706b": "wx-fire",
  "\u571f": "wx-earth",
  "\u91d1": "wx-metal",
  "\u6c34": "wx-water",
};

export function WuxingSection({ section }: SectionModuleProps) {
  const data = section.data as {
    items: Array<{ wuxing: string; count: number; ratio: number }>;
    dominant: string;
    weakest: string;
  };

  const max = Math.max(...data.items.map((i) => i.count), 1);

  return (
    <section className="panel">
      <h3>{section.name}</h3>
      <div className="wuxing-bars">
        {ORDER.map((wx) => {
          const item = data.items.find((i) => i.wuxing === wx) || {
            wuxing: wx,
            count: 0,
            ratio: 0,
          };
          return (
            <div key={wx} className="wuxing-row">
              <span className={`wx-label ${WX_CLASS[wx]}`}>{wx}</span>
              <div className="bar-track">
                <div
                  className={`bar-fill ${WX_CLASS[wx]}`}
                  style={{ width: `${(item.count / max) * 100}%` }}
                />
              </div>
              <span className="bar-count">{item.count}</span>
            </div>
          );
        })}
      </div>
      <p className="hint">
        偏旺: {data.dominant} / 偏弱: {data.weakest}
      </p>
    </section>
  );
}
