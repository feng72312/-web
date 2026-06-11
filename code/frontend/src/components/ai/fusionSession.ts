import type { AiChatSession } from "./types";
import type { FusionChartSource } from "./fusionTypes";
import { buildFusionSessionTitle } from "./fusionSourceBuilder";

export function createFusionChatSessionRecord(
  agentId: string,
  sources: FusionChartSource[],
  title?: string,
): AiChatSession {
  const sessionTitle = title ?? buildFusionSessionTitle(sources);
  return {
    agentId,
    title: sessionTitle,
    scenario: "review_result",
    createdAt: new Date().toISOString(),
    source: "fusion",
    fusionSourceIds: sources.map((item) => item.sourceId),
    fusionSourceLabels: sources.map((item) => item.moduleLabel),
    subtitle: sources.map((item) => item.moduleLabel).join(" / "),
  };
}
