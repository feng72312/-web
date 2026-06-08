import type { FengshuiXuankongPan } from "../../types/fengshui";

interface XuankongSummaryPanelProps {
  xuankong: FengshuiXuankongPan;
}

export function XuankongSummaryPanel({ xuankong }: XuankongSummaryPanelProps) {
  return (
    <div className="fengshui-summary-panel">
      <h3>玄空摘要</h3>
      <dl className="qimen-meta-dl">
        <dt>元运</dt>
        <dd>
          {xuankong.period.label} ({xuankong.period.yuan}, {xuankong.period.rangeStart}-
          {xuankong.period.rangeEnd})
        </dd>
        <dt>坐向</dt>
        <dd>{xuankong.label}</dd>
        <dt>山星</dt>
        <dd>
          入中 {xuankong.sittingStarCenter}, {xuankong.shanFly}
        </dd>
        <dt>向星</dt>
        <dd>
          入中 {xuankong.facingStarCenter}, {xuankong.xiangFly}
        </dd>
        {xuankong.flowYear && (
          <>
            <dt>流年</dt>
            <dd>{xuankong.flowYear}</dd>
          </>
        )}
      </dl>
      <p className="hint">合盘格式为 运-山-向, 例如 9-8-1 表示运星9、山星8、向星1.</p>
    </div>
  );
}
