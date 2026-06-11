export interface HomeImageMeta {
  src: string;
  alt: string;
  credit: string;
}

/** Project SVG covers - see public/images/home/ATTRIBUTIONS.md */
const MODULE_IMAGES: Record<string, HomeImageMeta> = {
  "01": {
    src: "/images/home/modules/01-bazi.svg",
    alt: "太极八卦与命理象征",
    credit: "Project SVG cover",
  },
  "11": {
    src: "/images/home/modules/11-ziwei.svg",
    alt: "星空与紫微斗数意象",
    credit: "Project SVG cover",
  },
  "09": {
    src: "/images/home/modules/09-xingming.svg",
    alt: "七政四余天象占验",
    credit: "Project SVG cover",
  },
  "02": {
    src: "/images/home/modules/02-liuyao.svg",
    alt: "铜钱摇卦六爻卜筮",
    credit: "Project SVG cover",
  },
  "03": {
    src: "/images/home/modules/03-meihua.svg",
    alt: "梅花易数与初春梅枝",
    credit: "Project SVG cover",
  },
  "04": {
    src: "/images/home/modules/04-qimen.svg",
    alt: "奇门遁甲九宫时空",
    credit: "Project SVG cover",
  },
  "05": {
    src: "/images/home/modules/05-liuren.svg",
    alt: "大六壬典籍与课式",
    credit: "Project SVG cover",
  },
  "13": {
    src: "/images/home/modules/13-tarot.svg",
    alt: "塔罗牌阵与象征解读",
    credit: "Project SVG cover",
  },
  "06": {
    src: "/images/home/modules/06-fengshui.svg",
    alt: "园林宅院风水堪舆",
    credit: "Project SVG cover",
  },
  hepan: {
    src: "/images/home/modules/util-hepan.svg",
    alt: "双人合盘婚恋合作",
    credit: "Project SVG cover",
  },
  zhuge: {
    src: "/images/home/modules/util-zhuge.svg",
    alt: "诸葛神数签文竹简",
    credit: "Project SVG cover",
  },
  jiemeng: {
    src: "/images/home/modules/util-jiemeng.svg",
    alt: "周公解梦与夜色梦境",
    credit: "Project SVG cover",
  },
  cewen: {
    src: "/images/home/modules/util-cewen.svg",
    alt: "测字拆形汉字象意",
    credit: "Project SVG cover",
  },
  naming: {
    src: "/images/home/modules/util-naming.svg",
    alt: "起名五格与文房",
    credit: "Project SVG cover",
  },
  "name-analysis": {
    src: "/images/home/modules/util-name-analysis.svg",
    alt: "姓名笔画五行分析",
    credit: "Project SVG cover",
  },
  phone: {
    src: "/images/home/modules/util-phone.svg",
    alt: "号码数理五行倾向",
    credit: "Project SVG cover",
  },
};

const SECTION_IMAGES: Record<string, HomeImageMeta> = {
  chart: {
    src: "/images/home/sections/chart.svg",
    alt: "命盘层: 八字紫微星命",
    credit: "Project SVG cover",
  },
  divination: {
    src: "/images/home/sections/divination.svg",
    alt: "卜筮层: 六爻梅花奇门六壬塔罗",
    credit: "Project SVG cover",
  },
  environment: {
    src: "/images/home/sections/environment.svg",
    alt: "环境关系: 风水堪舆",
    credit: "Project SVG cover",
  },
  utility: {
    src: "/images/home/sections/utility.svg",
    alt: "实用专区: 合盘测字解梦起名",
    credit: "Project SVG cover",
  },
};

export const HOME_HERO_IMAGE: HomeImageMeta = {
  src: "/images/home/hero.svg",
  alt: "东方玄学天文馆",
  credit: "Project SVG cover",
};

export function getModuleHomeImage(id: string): HomeImageMeta | undefined {
  return MODULE_IMAGES[id];
}

export function getSectionHomeImage(theme: string): HomeImageMeta | undefined {
  return SECTION_IMAGES[theme];
}
