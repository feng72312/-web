import type { PillarDetailColumn } from "../../types/bazi";

export interface BaziRelationLink {
  id: string;
  layer: "stem" | "branch";
  label: string;
  fromIndex: number;
  toIndex: number;
  fromText: string;
  toText: string;
}

const STEMS = "甲乙丙丁戊己庚辛壬癸";
const BRANCHES = "子丑寅卯辰巳午未申酉戌亥";
const RELATION_TYPES = ["合", "冲", "害", "刑", "破", "暗合"];

function findCharIndex(columns: PillarDetailColumn[], char: string, layer: "stem" | "branch"): number {
  const order: PillarDetailColumn["key"][] = ["year", "month", "day", "hour"];
  for (let i = 0; i < order.length; i += 1) {
    const col = columns.find((item) => item.key === order[i]);
    if (!col) {
      continue;
    }
    const value = layer === "stem" ? col.gan : col.zhi;
    if (value === char) {
      return i;
    }
  }
  return -1;
}

function parseLayer(
  columns: PillarDetailColumn[],
  notes: string | undefined,
  layer: "stem" | "branch",
  links: BaziRelationLink[],
): void {
  if (!notes || notes === "暂无" || notes.includes("暂无")) {
    return;
  }

  const charset = layer === "stem" ? STEMS : BRANCHES;
  const segments = notes.split(/[、,，;；\s]+/).filter(Boolean);

  for (const segment of segments) {
    for (const rel of RELATION_TYPES) {
      const relIdx = segment.indexOf(rel);
      if (relIdx < 2) {
        continue;
      }
      const pair = segment.slice(0, relIdx);
      if (pair.length !== 2) {
        continue;
      }
      const char1 = pair[0];
      const char2 = pair[1];
      if (!charset.includes(char1) || !charset.includes(char2)) {
        continue;
      }
      const fromIndex = findCharIndex(columns, char1, layer);
      const toIndex = findCharIndex(columns, char2, layer);
      if (fromIndex < 0 || toIndex < 0 || fromIndex === toIndex) {
        continue;
      }
      const label = `${char1}${char2}${rel}`;
      const id = `${layer}-${label}-${fromIndex}-${toIndex}`;
      if (links.some((item) => item.id === id)) {
        continue;
      }
      links.push({
        id,
        layer,
        label,
        fromIndex,
        toIndex,
        fromText: char1,
        toText: char2,
      });
    }
  }
}

export function parseBaziRelations(
  columns: PillarDetailColumn[],
  stemNotes?: string,
  branchNotes?: string,
): BaziRelationLink[] {
  const links: BaziRelationLink[] = [];
  parseLayer(columns, stemNotes, "stem", links);
  parseLayer(columns, branchNotes, "branch", links);
  return links;
}
