import type { FusionBlock, FusionChannelBlock, TripleFusionBlock } from "../types/bazi";
import { ChannelRagEvidence } from "./ChannelRagEvidence";

const CHANNEL_LABELS: Record<string, string> = {
  bazi: "八字",
  ziwei: "紫微",
  xingming: "星命",
  liuyao: "六爻",
};

function ChannelSection({
  label,
  channel,
  meta,
}: {
  label: string;
  channel: FusionChannelBlock;
  meta?: string;
}) {
  if (!channel.available) {
    return (
      <div className="fusion-channel-section unavailable">
        <h4 className="interpret-subhead">{label}</h4>
        <p className="interpret-channel-meta">
          通道不可用{channel.error ? `: ${channel.error}` : ""}
        </p>
      </div>
    );
  }

  return (
    <div className="fusion-channel-section">
      <h4 className="interpret-subhead">{label}判断</h4>
      {meta && <p className="interpret-channel-meta">{meta}</p>}
      {!meta && (
        <p className="interpret-channel-meta">倾向: {channel.stance || "未定"}</p>
      )}
      {channel.error && (
        <p className="channel-warning">{channel.error}</p>
      )}
      {channel.summary ? (
        <p className="interpret-summary">{channel.summary}</p>
      ) : (
        <p className="interpret-channel-meta">暂无解读内容</p>
      )}
      <ChannelRagEvidence
        query={channel.query}
        excerpts={channel.excerpts}
        knowledgeEvidence={channel.knowledgeEvidence}
        label={label}
      />
    </div>
  );
}

interface FusionChannelsPanelProps {
  fusion?: FusionBlock | null;
  tripleFusion?: TripleFusionBlock | null;
}

export function FusionChannelsPanel({ fusion, tripleFusion }: FusionChannelsPanelProps) {
  if (tripleFusion) {
    return (
      <div className="fusion-channels-panel">
        <h4 className="interpret-subhead">综合结论</h4>
        <p className="interpret-summary">{tripleFusion.merged.summary}</p>
        <ChannelSection label={CHANNEL_LABELS.bazi} channel={tripleFusion.bazi} />
        <ChannelSection label={CHANNEL_LABELS.ziwei} channel={tripleFusion.ziwei} />
        <ChannelSection label={CHANNEL_LABELS.xingming} channel={tripleFusion.xingming} />
      </div>
    );
  }

  if (fusion) {
    const liuyaoMeta = [
      fusion.liuyao.benGuaName ? `本卦 ${fusion.liuyao.benGuaName}` : "",
      fusion.liuyao.yongShen ? `用神 ${fusion.liuyao.yongShen.yongShen}` : "",
      `倾向: ${fusion.liuyao.stance}`,
    ]
      .filter(Boolean)
      .join(" ");

    return (
      <div className="fusion-channels-panel">
        <h4 className="interpret-subhead">综合结论</h4>
        <p className="interpret-summary">{fusion.merged.summary}</p>
        <ChannelSection label={CHANNEL_LABELS.bazi} channel={fusion.bazi} />
        <ChannelSection label={CHANNEL_LABELS.liuyao} channel={fusion.liuyao} meta={liuyaoMeta} />
      </div>
    );
  }

  return null;
}
