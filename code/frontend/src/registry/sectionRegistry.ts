import type { SectionModuleDefinition } from "../types/bazi";
import { DayunSection } from "../modules/DayunSection";
import { ShishenSection } from "../modules/ShishenSection";
import { SummarySection } from "../modules/SummarySection";
import { WuxingSection } from "../modules/WuxingSection";

const registry = new Map<string, SectionModuleDefinition>();

function register(def: SectionModuleDefinition): void {
  registry.set(def.id, def);
}

register({ id: "summary", order: 10, Component: SummarySection });
register({ id: "wuxing", order: 20, Component: WuxingSection });
register({ id: "shishen", order: 30, Component: ShishenSection });
register({ id: "dayun", order: 40, Component: DayunSection });

export function getSectionModule(id: string): SectionModuleDefinition | undefined {
  return registry.get(id);
}

export function listRegisteredModules(): SectionModuleDefinition[] {
  return Array.from(registry.values()).sort((a, b) => a.order - b.order);
}

/** Add new UI modules here without touching page layout code. */
export function registerSectionModule(def: SectionModuleDefinition): void {
  register(def);
}
