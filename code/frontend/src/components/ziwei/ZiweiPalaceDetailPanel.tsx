import type { ZiweiChart, ZiweiPalace, ZiweiRuntimeLayer } from "../../types/ziwei";
import { findPalaceByBranch, getOppositeBranch } from "./ziweiLayout";
import { MALEFIC_STAR_NAMES } from "./ziweiLayout";
import {
  collectAllStars,
  formatAges,
  formatStar,
  getActiveLayer,
  isRuntimePalace,
  majorStarSummary,
  mutagenClass,
  palaceHasMalefic,
} from "./ziweiDisplay";

interface ZiweiPalaceDetailPanelProps {
  chart: ZiweiChart;
  palace: ZiweiPalace;
  runtimeLayer: ZiweiRuntimeLayer;
}

function RelatedPalaceBlock({ title, palace }: { title: string; palace?: ZiweiPalace }) {
  if (!palace) {
    return null;
  }
  return (
    <div className="ziwei-detail-related">
      <strong>{title}</strong>
      <span>
        {palace.name} {palace.stemBranch}
      </span>
      <span>{majorStarSummary(palace)}</span>
    </div>
  );
}

export function ZiweiPalaceDetailPanel({
  chart,
  palace,
  runtimeLayer,
}: ZiweiPalaceDetailPanelProps) {
  const oppositeBranch = palace.oppositeBranch || getOppositeBranch(palace.earthlyBranch);
  const oppositePalace = findPalaceByBranch(chart.palaces, oppositeBranch);
  const triadPalaces = (palace.triadBranches ?? [])
    .map((branch) => findPalaceByBranch(chart.palaces, branch))
    .filter((item): item is ZiweiPalace => Boolean(item));
  const runtime = getActiveLayer(chart, runtimeLayer);
  const maleficStars = collectAllStars(palace).filter((star) =>
    MALEFIC_STAR_NAMES.has(star.name),
  );

  return (
    <aside className="ziwei-detail-panel">
      <h3>宫位详情</h3>
      <section className="ziwei-detail-block">
        <h4>概览</h4>
        <p>
          {palace.name} {palace.stemBranch}
        </p>
        <p>
          {palace.isSoul ? "命宫 " : ""}
          {palace.isBody ? "身宫 " : ""}
          {palace.decadalRange ? `大限 ${palace.decadalRange}` : ""}
        </p>
        {runtime?.available && isRuntimePalace(palace, runtime) ? (
          <p className="ziwei-detail-runtime">当前 {runtime.layer} 相关宫</p>
        ) : null}
      </section>

      <section className="ziwei-detail-block">
        <h4>主星</h4>
        <p>{majorStarSummary(palace)}</p>
        {palace.brightnessSummary ? <p className="hint">{palace.brightnessSummary}</p> : null}
      </section>

      <section className="ziwei-detail-block">
        <h4>辅星</h4>
        <p>
          {(palace.starGroups?.minor ?? palace.minorStars).map(formatStar).join(" ") || "无"}
        </p>
      </section>

      <section className="ziwei-detail-block">
        <h4>杂曜</h4>
        <p>{(palace.starGroups?.adj ?? palace.adjStars).map(formatStar).join(" ") || "无"}</p>
      </section>

      <section className="ziwei-detail-block">
        <h4>生年四化</h4>
        {palace.mutagenStars?.length ? (
          <ul className="ziwei-detail-list">
            {palace.mutagenStars.map((item) => (
              <li key={`${item.name}-${item.mutagen}`} className={mutagenClass(item.mutagen)}>
                {item.name} {item.mutagen}
              </li>
            ))}
          </ul>
        ) : (
          <p>本宫无生年四化星</p>
        )}
      </section>

      {chart.meta.chartSchool === "feixing" && palace.flyingMutagens ? (
        <section className="ziwei-detail-block">
          <h4>宫干飞化</h4>
          {palace.flyingMutagens.outbound.length ? (
            <>
              <p className="hint">本宫 {palace.heavenlyStem} 干飞出</p>
              <ul className="ziwei-detail-list">
                {palace.flyingMutagens.outbound.map((item) => (
                  <li
                    key={`out-${item.mutagen}-${item.star}-${item.targetPalace}`}
                    className={mutagenClass(item.mutagen)}
                  >
                    {item.star}
                    {item.mutagen} 入 {item.targetPalace}
                  </li>
                ))}
              </ul>
            </>
          ) : (
            <p>本宫无飞出四化</p>
          )}
          {palace.flyingMutagens.inbound.length ? (
            <>
              <p className="hint">飞入本宫</p>
              <ul className="ziwei-detail-list">
                {palace.flyingMutagens.inbound.map((item) => (
                  <li
                    key={`in-${item.mutagen}-${item.star}-${item.sourcePalace}`}
                    className={mutagenClass(item.mutagen)}
                  >
                    {item.sourcePalace} {item.sourceStem} 干 {item.star}
                    {item.mutagen}
                  </li>
                ))}
              </ul>
            </>
          ) : (
            <p>无其它宫飞入</p>
          )}
        </section>
      ) : null}

      <section className="ziwei-detail-block">
        <h4>煞曜</h4>
        <p>{palaceHasMalefic(palace) ? maleficStars.map((s) => s.name).join(" ") : "本宫无突出煞曜"}</p>
      </section>

      <section className="ziwei-detail-block">
        <h4>小限年龄</h4>
        <p>{formatAges(palace.minorAges) || "无"}</p>
      </section>

      <section className="ziwei-detail-block">
        <h4>三方四正</h4>
        <RelatedPalaceBlock title="本宫" palace={palace} />
        <RelatedPalaceBlock title="对宫" palace={oppositePalace} />
        {triadPalaces.map((item) => (
          <RelatedPalaceBlock key={item.earthlyBranch} title="三方" palace={item} />
        ))}
      </section>
    </aside>
  );
}
