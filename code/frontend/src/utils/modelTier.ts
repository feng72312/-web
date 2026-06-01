import type { ChatModelOption } from "../types/bazi";

export const MODEL_DISPLAY_ORDER = [
  "composer-2.5",
  "deepseek-v4-flash",
  "deepseek-chat",
  "deepseek-reasoner",
  "deepseek-v4-pro",
] as const;

/** Display labels only; model id is kept for API calls. */
const MODEL_TIER_BY_ID: Record<string, { tier: string; tierRank: number }> = {
  "composer-2.5": { tier: "小师傅", tierRank: 1 },
  "deepseek-v4-flash": { tier: "小师傅", tierRank: 1 },
  "deepseek-chat": { tier: "大师", tierRank: 2 },
  "deepseek-reasoner": { tier: "宗师", tierRank: 3 },
  "deepseek-v4-pro": { tier: "道长", tierRank: 4 },
};

export type ModelTierKey = "apprentice" | "master" | "grandmaster" | "sage";

export function resolveModelTier(model: Pick<ChatModelOption, "id">) {
  return MODEL_TIER_BY_ID[model.id] ?? { tier: "大师", tierRank: 2 };
}

export function tierClassName(tier: string): ModelTierKey {
  if (tier === "小师傅") return "apprentice";
  if (tier === "宗师") return "grandmaster";
  if (tier === "道长") return "sage";
  return "master";
}

export function sortModelsByTier<T extends Pick<ChatModelOption, "id">>(models: T[]): T[] {
  return [...models].sort((a, b) => {
    const ia = MODEL_DISPLAY_ORDER.indexOf(a.id as (typeof MODEL_DISPLAY_ORDER)[number]);
    const ib = MODEL_DISPLAY_ORDER.indexOf(b.id as (typeof MODEL_DISPLAY_ORDER)[number]);
    return (ia === -1 ? 999 : ia) - (ib === -1 ? 999 : ib);
  });
}
