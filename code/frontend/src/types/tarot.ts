export type TarotDeckId = "rws" | "marseille" | "thoth";
export type TarotDrawMode = "pick" | "manual" | "auto";
export type TarotOrientation = "upright" | "reversed";

export interface TarotDeckInfo {
  id: TarotDeckId;
  nameZh: string;
  desc: string;
}

export interface TarotCardInfo {
  cardId: string;
  nameZh: string;
  nameEn: string;
  image?: string | null;
  keywordsZh?: string[];
}

export interface SpreadPosition {
  index: number;
  labelZh: string;
  meaningZh: string;
}

export interface SpreadDef {
  id: string;
  nameZh: string;
  cardCount: number;
  complexity: string;
  questionTypes: string[];
  positions: SpreadPosition[];
}

export interface DrawnCard {
  position: number;
  positionLabel: string;
  positionMeaning: string;
  cardId: string;
  nameZh: string;
  nameEn: string;
  orientation: TarotOrientation;
  meaningZh: string;
  meaningEn: string;
  keywords: string[];
  image?: string | null;
}

export interface TarotReading {
  input: {
    question: string;
    deck: TarotDeckId;
    spread: string;
    allowReversed: boolean;
  };
  deck: TarotDeckId;
  deckName: string;
  spreadId: string;
  spreadName: string;
  cards: DrawnCard[];
  meta?: { drawNote?: string; cardCount?: number; drawMode?: TarotDrawMode };
}

export interface TarotDrawRequest {
  question: string;
  deck: TarotDeckId;
  spread: string;
  allowReversed?: boolean;
}

export interface TarotShuffleResponse {
  sessionToken: string;
  deckSize: number;
}

export interface ManualCardSelection {
  position: number;
  cardId: string;
  orientation: TarotOrientation;
}

export interface TarotInterpretation {
  query: string;
  excerpts: Array<{ source: string; excerpt: string }>;
  summary: string;
  summaryProfessional?: string;
  summaryPlain?: string;
  agentId?: string;
}
