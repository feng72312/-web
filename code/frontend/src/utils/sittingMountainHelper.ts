import type { FengshuiMountain } from "../types/fengshui";

/** Door / main window facing (what the user usually knows). */
export type FacingDirection = "N" | "NE" | "E" | "SE" | "S" | "SW" | "W" | "NW";

export interface FacingPreset {
  id: FacingDirection;
  /** e.g. 大门朝南 */
  doorLabel: string;
  /** e.g. 坐北朝南 */
  houseLabel: string;
  /** Default 24-mountain id (middle star of the trigram group). */
  defaultMountainId: string;
  trigram: string;
  /** Three mountains in this sector, left-to-right on the compass ring. */
  sectorMountainIds: [string, string, string];
  /** Approximate compass degrees for the door facing. */
  facingDegrees: number;
}

export const FACING_PRESETS: FacingPreset[] = [
  {
    id: "S",
    doorLabel: "大门朝南",
    houseLabel: "坐北朝南",
    defaultMountainId: "zi",
    trigram: "坎",
    sectorMountainIds: ["ren", "zi", "gui"],
    facingDegrees: 180,
  },
  {
    id: "N",
    doorLabel: "大门朝北",
    houseLabel: "坐南朝北",
    defaultMountainId: "wu",
    trigram: "离",
    sectorMountainIds: ["bing", "wu", "ding"],
    facingDegrees: 0,
  },
  {
    id: "E",
    doorLabel: "大门朝东",
    houseLabel: "坐西朝东",
    defaultMountainId: "you",
    trigram: "兑",
    sectorMountainIds: ["geng", "you", "xin"],
    facingDegrees: 90,
  },
  {
    id: "W",
    doorLabel: "大门朝西",
    houseLabel: "坐东朝西",
    defaultMountainId: "mao",
    trigram: "震",
    sectorMountainIds: ["jia", "mao", "yi"],
    facingDegrees: 270,
  },
  {
    id: "NE",
    doorLabel: "大门朝东北",
    houseLabel: "坐西南朝东北",
    defaultMountainId: "kun",
    trigram: "坤",
    sectorMountainIds: ["wei", "kun", "shen"],
    facingDegrees: 45,
  },
  {
    id: "SW",
    doorLabel: "大门朝西南",
    houseLabel: "坐东北朝西南",
    defaultMountainId: "gen",
    trigram: "艮",
    sectorMountainIds: ["chou", "gen", "yin"],
    facingDegrees: 225,
  },
  {
    id: "SE",
    doorLabel: "大门朝东南",
    houseLabel: "坐西北朝东南",
    defaultMountainId: "qian",
    trigram: "乾",
    sectorMountainIds: ["xu", "qian", "hai"],
    facingDegrees: 135,
  },
  {
    id: "NW",
    doorLabel: "大门朝西北",
    houseLabel: "坐东南朝西北",
    defaultMountainId: "xun",
    trigram: "巽",
    sectorMountainIds: ["chen", "xun", "si"],
    facingDegrees: 315,
  },
];

const PRESET_BY_MOUNTAIN = new Map<string, FacingPreset>();
for (const preset of FACING_PRESETS) {
  for (const mid of preset.sectorMountainIds) {
    PRESET_BY_MOUNTAIN.set(mid, preset);
  }
}

export function findPresetByMountainId(mountainId: string): FacingPreset | undefined {
  return PRESET_BY_MOUNTAIN.get(mountainId);
}

export function findPresetByFacing(facing: FacingDirection): FacingPreset | undefined {
  return FACING_PRESETS.find((item) => item.id === facing);
}

/** Map compass facing degrees (0=北, 90=东) to a preset. */
export function presetFromFacingDegrees(degrees: number): FacingPreset {
  const normalized = ((degrees % 360) + 360) % 360;
  const sectors: Array<{ max: number; preset: FacingPreset }> = [
    { max: 22.5, preset: FACING_PRESETS[1] },
    { max: 67.5, preset: FACING_PRESETS[4] },
    { max: 112.5, preset: FACING_PRESETS[2] },
    { max: 157.5, preset: FACING_PRESETS[6] },
    { max: 202.5, preset: FACING_PRESETS[0] },
    { max: 247.5, preset: FACING_PRESETS[5] },
    { max: 292.5, preset: FACING_PRESETS[3] },
    { max: 337.5, preset: FACING_PRESETS[7] },
    { max: 360, preset: FACING_PRESETS[1] },
  ];
  for (const sector of sectors) {
    if (normalized < sector.max) {
      return sector.preset;
    }
  }
  return FACING_PRESETS[0];
}

export function mountainLabel(mountains: FengshuiMountain[], id: string): string {
  return mountains.find((item) => item.id === id)?.label ?? id;
}

export function describeMountainChoice(
  mountains: FengshuiMountain[],
  mountainId: string,
): string {
  const mountain = mountains.find((item) => item.id === mountainId);
  if (!mountain) {
    return mountainId;
  }
  const preset = findPresetByMountainId(mountainId);
  if (preset) {
    return `${preset.houseLabel} -> ${mountain.label} (${mountain.trigram}卦)`;
  }
  return `${mountain.label} (${mountain.trigram}卦)`;
}

export function groupMountainsByTrigram(
  mountains: FengshuiMountain[],
): Array<{ trigram: string; items: FengshuiMountain[] }> {
  const groups = new Map<string, FengshuiMountain[]>();
  for (const item of mountains) {
    const list = groups.get(item.trigram) ?? [];
    list.push(item);
    groups.set(item.trigram, list);
  }
  return Array.from(groups.entries()).map(([trigram, items]) => ({ trigram, items }));
}

export const SECTOR_FINE_LABELS: Record<string, [string, string, string]> = {
  坎: ["偏西北", "正北(常用)", "偏东北"],
  离: ["偏东南", "正南(常用)", "偏西南"],
  震: ["偏东北", "正东(常用)", "偏东南"],
  兑: ["偏西北", "正西(常用)", "偏西南"],
  坤: ["偏南", "西南(常用)", "偏西北"],
  艮: ["偏东", "东北(常用)", "偏北"],
  乾: ["偏西", "西北(常用)", "偏北"],
  巽: ["偏东", "东南(常用)", "偏南"],
};
