export type ZiHourPhase = "early" | "late";

export const HOUR_SLOTS = [
  { value: 0, label: "子时 23:00-01:00" },
  { value: 1, label: "丑时 01:00-03:00" },
  { value: 2, label: "寅时 03:00-05:00" },
  { value: 3, label: "卯时 05:00-07:00" },
  { value: 4, label: "辰时 07:00-09:00" },
  { value: 5, label: "巳时 09:00-11:00" },
  { value: 6, label: "午时 11:00-13:00" },
  { value: 7, label: "未时 13:00-15:00" },
  { value: 8, label: "申时 15:00-17:00" },
  { value: 9, label: "酉时 17:00-19:00" },
  { value: 10, label: "戌时 19:00-21:00" },
  { value: 11, label: "亥时 21:00-23:00" },
];

export function hourFromSlot(
  slotIndex: number,
  ziHourPhase: ZiHourPhase = "late",
): number {
  const slot = HOUR_SLOTS[slotIndex] || HOUR_SLOTS[0];
  if (slot.value === 0) {
    return ziHourPhase === "early" ? 0 : 23;
  }
  return slot.value * 2 - 1;
}

export function slotFromHour(hour: number): {
  slotIndex: number;
  ziHourPhase: ZiHourPhase;
} {
  if (hour === 0) {
    return { slotIndex: 0, ziHourPhase: "early" };
  }
  if (hour === 23) {
    return { slotIndex: 0, ziHourPhase: "late" };
  }
  return {
    slotIndex: Math.min(11, Math.max(1, Math.floor((hour + 1) / 2))),
    ziHourPhase: "late",
  };
}

export function ziHourLabel(phase: ZiHourPhase): string {
  return phase === "early" ? "早子时" : "晚子时";
}

export function formatHourSlotLabel(slotIndex: number, ziHourPhase: ZiHourPhase): string {
  if (slotIndex === 0) {
    return ziHourLabel(ziHourPhase);
  }
  return HOUR_SLOTS[slotIndex]?.label.split(" ")[0] || "";
}
