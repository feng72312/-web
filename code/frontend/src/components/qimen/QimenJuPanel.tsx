import type { JuInfo, QimenChart, ZhiFuZhiShi } from "../../types/qimen";

interface QimenJuPanelProps {
  ju: JuInfo;
  zhiFuZhiShi: ZhiFuZhiShi;
  fourPillars: QimenChart["fourPillars"];
  trueSolarTime: string;
  meta?: Record<string, unknown>;
}

export function QimenJuPanel({
  ju,
  zhiFuZhiShi,
  fourPillars,
  trueSolarTime,
  meta,
}: QimenJuPanelProps) {
  return (
    <div className="qimen-ju-panel">
      <h3>局信息与值符值使</h3>
      <dl className="qimen-meta-dl">
        <div>
          <dt>排局</dt>
          <dd>{ju.juName}</dd>
        </div>
        <div>
          <dt>节气</dt>
          <dd>{ju.jieqi || "-"}</dd>
        </div>
        <div>
          <dt>旬首</dt>
          <dd>{ju.xunShou || "-"}</dd>
        </div>
        <div>
          <dt>真太阳时</dt>
          <dd>{trueSolarTime}</dd>
        </div>
        <div>
          <dt>四柱</dt>
          <dd>
            {fourPillars.year} {fourPillars.month} {fourPillars.day}{" "}
            {fourPillars.hour}
          </dd>
        </div>
        <div>
          <dt>值符</dt>
          <dd>
            {zhiFuZhiShi.zhiFuStar} / {zhiFuZhiShi.zhiFuGong} (干
            {zhiFuZhiShi.zhiFuGan})
          </dd>
        </div>
        <div>
          <dt>值使</dt>
          <dd>
            {zhiFuZhiShi.zhiShiDoor} / {zhiFuZhiShi.zhiShiGong}
          </dd>
        </div>
        {meta?.methodLabel ? (
          <div>
            <dt>排盘法</dt>
            <dd>{String(meta.methodLabel)}</dd>
          </div>
        ) : null}
      </dl>
    </div>
  );
}
