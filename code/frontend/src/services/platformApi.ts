import { API_BASE } from "./config";
import type { PricingTier } from "../config/pricingTiers";

export interface ModuleBlueprint {
  version: string;
  layers: Record<string, { label: string; description: string; modules: string[] }>;
  modules: Record<
    string,
    { id: string; label: string; input: string[]; output: string[]; fusionRole: string }
  >;
}

export async function fetchModuleBlueprint(): Promise<ModuleBlueprint> {
  const response = await fetch(`${API_BASE}/platform/blueprint`);
  if (!response.ok) {
    throw new Error(`blueprint failed: ${response.status}`);
  }
  return response.json();
}

export async function fetchPricingTiers(): Promise<{ tiers: PricingTier[] }> {
  const response = await fetch(`${API_BASE}/platform/pricing-tiers`);
  if (!response.ok) {
    throw new Error(`pricing failed: ${response.status}`);
  }
  return response.json();
}
