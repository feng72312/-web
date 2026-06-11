import type { ZiweiPalace } from "../../types/ziwei";

export const BRANCH_GRID_POSITIONS: Record<string, { row: number; col: number }> = {
  巳: { row: 1, col: 1 },
  午: { row: 1, col: 2 },
  未: { row: 1, col: 3 },
  申: { row: 1, col: 4 },
  辰: { row: 2, col: 1 },
  酉: { row: 2, col: 4 },
  卯: { row: 3, col: 1 },
  戌: { row: 3, col: 4 },
  寅: { row: 4, col: 1 },
  丑: { row: 4, col: 2 },
  子: { row: 4, col: 3 },
  亥: { row: 4, col: 4 },
};

export const OPPOSITE_BRANCHES: Record<string, string> = {
  子: "午",
  丑: "未",
  寅: "申",
  卯: "酉",
  辰: "戌",
  巳: "亥",
  午: "子",
  未: "丑",
  申: "寅",
  酉: "卯",
  戌: "辰",
  亥: "巳",
};

export const TRIAD_GROUPS: string[][] = [
  ["申", "子", "辰"],
  ["寅", "午", "戌"],
  ["巳", "酉", "丑"],
  ["亥", "卯", "未"],
];

export const MALEFIC_STAR_NAMES = new Set([
  "擎羊",
  "陀罗",
  "火星",
  "铃星",
  "地空",
  "地劫",
  "天空",
  "天刑",
  "大耗",
  "劫煞",
  "灾煞",
  "天姚",
  "天哭",
  "天虚",
  "阴煞",
  "白虎",
  "贯索",
]);

export const MUTAGEN_CLASS_MAP: Record<string, string> = {
  禄: "ziwei-mutagen-lu",
  权: "ziwei-mutagen-quan",
  科: "ziwei-mutagen-ke",
  忌: "ziwei-mutagen-ji",
};

export function getPalacePosition(palace: ZiweiPalace): { row: number; col: number } | null {
  if (palace.position?.row && palace.position?.col) {
    return { row: palace.position.row, col: palace.position.col };
  }
  const branch = palace.earthlyBranch;
  if (!branch) {
    return null;
  }
  return BRANCH_GRID_POSITIONS[branch] ?? null;
}

export function getOppositeBranch(branch: string): string {
  return palaceBranchOrFallback(branch, OPPOSITE_BRANCHES);
}

function palaceBranchOrFallback(
  branch: string,
  map: Record<string, string>,
): string {
  return map[branch] ?? "";
}

export function getTriadBranches(branch: string): string[] {
  for (const group of TRIAD_GROUPS) {
    if (group.includes(branch)) {
      return group.filter((item) => item !== branch);
    }
  }
  return [];
}

export function findPalaceByBranch(
  palaces: ZiweiPalace[],
  branch: string,
): ZiweiPalace | undefined {
  return palaces.find((palace) => palace.earthlyBranch === branch);
}

export function findSoulPalace(palaces: ZiweiPalace[]): ZiweiPalace | undefined {
  return palaces.find((palace) => palace.isSoul || palace.name === "命宫") ?? palaces[0];
}
