export type TarotDeckId = "rws" | "marseille" | "thoth";

export interface TarotDeckInfo {
  id: TarotDeckId;
  nameZh: string;
  desc: string;
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
  orientation: "upright" | "reversed";
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
  meta?: { drawNote?: string; cardCount?: number };
}

export interface TarotDrawRequest {
  question: string;
  deck: TarotDeckId;
  spread: string;
  allowReversed?: boolean;
}

export interface TarotInterpretation {
  query: string;
  excerpts: Array<{ source: string; excerpt: string }>;
  summary: string;
  summaryProfessional?: string;
  summaryPlain?: string;
  agentId?: string;
}
