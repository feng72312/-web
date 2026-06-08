export interface NamingGridRow {
  grid: string;
  strokes: number;
  wuxing: string;
  luck: string;
}

export interface NamingShuowenEntry {
  char: string;
  radical?: string;
  volume?: string;
  pronunciation?: string;
  explanation?: string;
  variants?: Array<{ char: string; note: string }>;
  duanNotes?: Array<{ quote: string; note: string }>;
  xuanNote?: string;
  missing?: boolean;
}

export interface NamingCharWuxing {
  char: string;
  radicalWuxing: string;
  radical: string;
}

export interface NamingBaziProfile {
  dayMasterWuxing: string;
  strength: string;
  weakest: string;
  strongest: string;
  favoredWuxing: string[];
  avoidWuxing: string[];
}

export interface NamingAnalysis {
  fullName: string;
  shuowen: NamingShuowenEntry[];
  charWuxing: NamingCharWuxing[];
  wuge: {
    surname: string;
    givenName: string;
    charStrokes: Array<{ char: string; strokes: number }>;
    grids: NamingGridRow[];
    missingStrokeChars: string[];
  };
  baziProfile: NamingBaziProfile | null;
  chart: Record<string, unknown> | null;
}

export interface NamingBirthInput {
  calendarType: "solar" | "lunar";
  year: number;
  month: number;
  day: number;
  hour: number;
  minute: number;
  second: number;
  gender: number;
  isLeapMonth: boolean;
}
