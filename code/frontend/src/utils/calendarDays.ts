import type { CalendarType } from "../types/bazi";

export function maxDayInMonth(
  year: number,
  month: number,
  calendarType: CalendarType,
): number {
  const safeYear = Number.isFinite(year) ? year : 1990;
  const safeMonth = Math.min(12, Math.max(1, Number(month) || 1));
  if (calendarType === "lunar") {
    return 30;
  }
  return new Date(safeYear, safeMonth, 0).getDate();
}

export function clampDay(
  year: number,
  month: number,
  day: number,
  calendarType: CalendarType,
): number {
  const maxDay = maxDayInMonth(year, month, calendarType);
  return Math.min(maxDay, Math.max(1, Number(day) || 1));
}
