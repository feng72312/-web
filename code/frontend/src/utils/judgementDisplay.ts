const CONFIDENCE_BAND_LABELS: Record<string, string> = {
  strong: "较高",
  medium: "中等",
  weak: "偏低",
  high: "较高",
  low: "偏低",
};

const STEP_STATUS_LABELS: Record<string, string> = {
  ok: "完成",
  partial: "部分依据",
  skipped: "未执行",
  pending: "待处理",
};

const STANCE_LABELS: Record<string, string> = {
  favorable: "偏吉",
  unfavorable: "偏凶",
  neutral: "中性",
  mixed: "吉凶参半",
};

const CONCLUSION_KIND_LABELS: Record<string, string> = {
  classic_direct: "典籍直断",
  rule_derived: "规则推导",
  insufficient_evidence: "依据不足",
  case_reference: "命例参考",
};

export const BAZI_JUDGE_ROLE_LABELS: Record<string, string> = {
  month: "月令旺衰",
  tiaohou: "调候",
  geju: "格局",
  qishi: "气势流通",
  shishen: "十神六亲",
  interactions: "刑冲合害",
  suiyun: "岁运",
  boundary: "结论边界",
  case: "案例",
  comprehensive: "综合",
  base: "基础",
};

const TOPIC_ID_LABELS: Record<string, string> = {
  general: "综合",
  career: "事业",
  wealth: "财运",
  marriage: "婚姻",
  health: "健康",
  study: "学业",
  family: "六亲",
  travel: "出行",
  lawsuit: "官非",
  fertility: "子嗣",
};

const ROLE_TOKEN_RE = /\b(month|tiaohou|geju|qishi|shishen|interactions|suiyun|topic|palace|star|mutagen|pattern|limit|cross_school)\b/g;
const TOPIC_ID_RE = /\((general|career|wealth|marriage|health|study|family|travel|lawsuit|fertility)\)/g;

export function formatConfidenceBand(band?: string | null): string {
  if (!band) {
    return "";
  }
  return CONFIDENCE_BAND_LABELS[band] ?? band;
}

export function formatStepStatus(status?: string | null): string {
  if (!status) {
    return "";
  }
  return STEP_STATUS_LABELS[status] ?? status;
}

export function translateJudgeRole(role: string, labels: Record<string, string>): string {
  return labels[role] ?? role;
}

export function localizeJudgementText(text: string): string {
  if (!text) {
    return text;
  }
  let result = text;
  result = result.replace(TOPIC_ID_RE, (_, id: string) => {
    const label = TOPIC_ID_LABELS[id];
    return label ? `(${label})` : `(${id})`;
  });
  result = result.replace(ROLE_TOKEN_RE, (token) => {
    return BAZI_JUDGE_ROLE_LABELS[token] ?? token;
  });
  for (const [key, label] of Object.entries(STANCE_LABELS)) {
    result = result.replace(new RegExp(`\\b${key}\\b`, "g"), label);
  }
  for (const [key, label] of Object.entries(CONCLUSION_KIND_LABELS)) {
    result = result.replace(new RegExp(`\\b${key}\\b`, "g"), label);
  }
  for (const [key, label] of Object.entries(CONFIDENCE_BAND_LABELS)) {
    result = result.replace(new RegExp(`\\b${key}\\b`, "g"), label);
  }
  return result;
}
