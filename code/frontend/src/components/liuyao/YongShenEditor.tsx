import { LIUQIN_OPTIONS, type LiuyaoChart, type YongShenResult } from "../../types/liuyao";

interface Props {
  chart: LiuyaoChart;
  yongShen: YongShenResult | null;
  loading?: boolean;
  onApply: (yongShen: string) => void;
}

export function YongShenEditor({ chart, yongShen, loading, onApply }: Props) {
  const options = LIUQIN_OPTIONS.filter((name) =>
    chart.lines.some((line) => line.liuqin === name),
  );

  return (
    <section className="panel yongshen-panel">
      <h3>用神</h3>
      {yongShen ? (
        <>
          <p>
            当前用神: {yongShen.yongShen}爻 (第{yongShen.position}爻) [{yongShen.source}]
          </p>
          <p className="hint">{yongShen.reason}</p>
        </>
      ) : (
        <p className="hint">完成排盘后可 AI 推断用神, 也可手动指定.</p>
      )}
      <div className="yongshen-edit-row">
        <label>
          修改用神
          <select
            defaultValue={yongShen?.yongShen ?? ""}
            id="yongshen-select"
            disabled={loading}
          >
            <option value="" disabled>
              选择六亲
            </option>
            {(options.length ? options : LIUQIN_OPTIONS).map((name) => (
              <option key={name} value={name}>
                {name}
              </option>
            ))}
          </select>
        </label>
        <button
          type="button"
          className="secondary"
          disabled={loading}
          onClick={() => {
            const select = document.getElementById("yongshen-select") as HTMLSelectElement | null;
            if (select?.value) {
              onApply(select.value);
            }
          }}
        >
          确认修改
        </button>
      </div>
    </section>
  );
}
