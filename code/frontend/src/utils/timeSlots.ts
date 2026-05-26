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

export function hourFromSlot(slotIndex: number): number {
  const slot = HOUR_SLOTS[slotIndex] || HOUR_SLOTS[0];
  return slot.value === 0 ? 0 : slot.value * 2 - 1;
}

export function slotFromHour(hour: number): number {
  if (hour === 0 || hour === 23) {
    return 0;
  }
  return Math.min(11, Math.max(1, Math.floor((hour + 1) / 2)));
}
