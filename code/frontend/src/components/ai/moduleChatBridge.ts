import { seedChatInterpretation } from "../../services/chatApi";
import type { FusionChartSource } from "./fusionTypes";
import { upsertFusionSource } from "./fusionSourceStorage";
import { clearThreadMessages } from "./threadStorage";
import type { AiChatSession } from "./types";

export interface ModuleInterpretationSeed {
  summaryPlain?: string | null;
  summaryProfessional?: string | null;
}

export async function openModuleAiChatSession(
  session: AiChatSession,
  interpretation: ModuleInterpretationSeed | null | undefined,
  onOpen: (session: AiChatSession) => void,
  fusionSource?: FusionChartSource | null,
): Promise<void> {
  if (fusionSource) {
    upsertFusionSource(fusionSource);
  }
  const hasPlain = Boolean(interpretation?.summaryPlain?.trim());
  const hasPro = Boolean(interpretation?.summaryProfessional?.trim());
  if (hasPlain || hasPro) {
    const result = await seedChatInterpretation(session.agentId, {
      summaryPlain: interpretation?.summaryPlain ?? undefined,
      summaryProfessional: interpretation?.summaryProfessional ?? undefined,
    });
    if (result.added > 0) {
      clearThreadMessages(session.agentId);
    }
  }
  onOpen(session);
}
