import { useEffect, useMemo, useState } from "react";
import { fetchLiuri } from "../services/api";
import type { FlowPillar, LiuriDay, LuckTimeline } from "../types/bazi";
import { wuxingClass } from "../utils/wuxing";

interface Props {
  timeline: LuckTimeline;
  onBack: () => void;
}

const GRID_HEADERS = [
  "日期",
  "流日",
  "流月",
  "流年",
  "大运",
  "年柱",
  "月柱",
  "日柱",
  "时柱",
];

function PillarCell({ pillar, tag }: { pillar: FlowPillar; tag?: string }) {
  return (
    <div className="flow-cell">
      {tag && <span className="flow-tag">{tag}</span>}
      <div className="flow-gan">
        <span className={wuxingClass(pillar.ganWuxing)}>{pillar.gan}</span>
        <span className="flow-shishen">{pillar.shishenGan}</span>
      </div>
      <div className="flow-zhi">
        <span className={wuxingClass(pillar.zhiWuxing)}>{pillar.zhi}</span>
        <div className="flow-hide">
          {pillar.hideStems.map((item) => (
            <span key={item}>{item}</span>
          ))}
        </div>
      </div>
      <div className="flow-xunkong">{pillar.xunkong}</div>
    </div>
  );
}

export function LuckTimelineView({ timeline, onBack }: Props) {
  const [dayunIndex, setDayunIndex] = useState(timeline.current.dayunIndex);
  const [liunianYear, setLiunianYear] = useState(timeline.current.liunianYear);
  const [liuyueIndex, setLiuyueIndex] = useState(timeline.current.liuyueIndex);
  const [liuriDate, setLiuriDate] = useState(timeline.current.liuriDate);
  const [liuriByYear, setLiuriByYear] = useState(timeline.liuriByYear);

  const dayun = useMemo(
    () => timeline.dayun.find((item) => item.index === dayunIndex) || timeline.dayun[0],
    [timeline.dayun, dayunIndex],
  );

  const liunian = useMemo(
    () => dayun?.liunian.find((item) => item.year === liunianYear) || dayun?.liunian[0],
    [dayun, liunianYear],
  );

  const liuyue = useMemo(
    () => liunian?.liuyue.find((item) => item.index === liuyueIndex) || liunian?.liuyue[0],
    [liunian, liuyueIndex],
  );

  useEffect(() => {
    const yearKey = String(liunianYear);
    let cancelled = false;
    fetchLiuri(liunianYear, timeline.dayMaster).then((payload) => {
      if (cancelled) {
        return;
      }
      setLiuriByYear((prev) => {
        if (prev[yearKey]) {
          return prev;
        }
        return { ...prev, [yearKey]: payload.months };
      });
    });
    return () => {
      cancelled = true;
    };
  }, [liunianYear, timeline.dayMaster]);

  useEffect(() => {
    setLiuriDate((prev) => `${liunianYear}${prev.slice(4)}`);
  }, [liunianYear]);

  const monthKey = liuriDate.slice(0, 7);
  const monthDays: LiuriDay[] = liuriByYear[String(liunianYear)]?.[monthKey] || [];
  const liuri = monthDays.find((item) => item.date === liuriDate) || monthDays[0];

  const liuriFlow: FlowPillar | undefined = liuri
    ? {
        gan: liuri.gan,
        zhi: liuri.zhi,
        ganzhi: liuri.ganzhi,
        shishenGan: liuri.shishenGan,
        hideStems: liuri.hideStems,
        xunkong: liuri.xunkong,
        ganWuxing: liuri.ganWuxing,
        zhiWuxing: liuri.zhiWuxing,
      }
    : undefined;

  const ageText = liunian ? `${liunian.age}岁 ${liunian.year}` : "";

  return (
    <section className="chart-detail panel luck-panel">
      <div className="chart-detail-header">
        <button type="button" className="secondary back-btn" onClick={onBack}>
          返回
        </button>
        <h2>大运流年</h2>
      </div>

      <div className="luck-grid-wrap">
        <table className="luck-grid">
          <thead>
            <tr>
              {GRID_HEADERS.map((head) => (
                <th key={head}>{head}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            <tr>
              <td className="luck-meta">{ageText}</td>
              <td className="luck-meta">{liuri?.day || "-"}日</td>
              <td className="luck-meta">{liuyue?.monthLabel || "-"}月</td>
              <td className="luck-meta">{liunian?.year || "-"}</td>
              <td className="luck-meta">
                {dayun ? `${dayun.startAge}-${dayun.endAge}岁` : "-"}
              </td>
              <td className="luck-meta">*</td>
              <td className="luck-meta">*</td>
              <td className="luck-meta">*</td>
              <td className="luck-meta">*</td>
            </tr>
            <tr>
              <td className="luck-label">天干</td>
              <td>{liuriFlow && <PillarCell pillar={liuriFlow} tag={liuriFlow.shishenGan} />}</td>
              <td>{liuyue && <PillarCell pillar={liuyue.pillar} tag={liuyue.pillar.shishenGan} />}</td>
              <td>{liunian && <PillarCell pillar={liunian.pillar} tag={liunian.pillar.shishenGan} />}</td>
              <td>{dayun && <PillarCell pillar={dayun.pillar} tag={dayun.pillar.shishenGan} />}</td>
              <td>
                <PillarCell pillar={timeline.birthPillars.year} tag={timeline.birthPillars.year.shishenGan} />
              </td>
              <td>
                <PillarCell pillar={timeline.birthPillars.month} tag={timeline.birthPillars.month.shishenGan} />
              </td>
              <td>
                <PillarCell pillar={timeline.birthPillars.day} tag={timeline.genderRole} />
              </td>
              <td>
                <PillarCell pillar={timeline.birthPillars.hour} tag={timeline.birthPillars.hour.shishenGan} />
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <div className="luck-section">
        <div className="luck-section-title">大运</div>
        <div className="luck-track">
          {timeline.dayun.map((item) => (
            <button
              key={item.index}
              type="button"
              className={`luck-chip ${item.index === dayunIndex ? "active" : ""}`}
              onClick={() => {
                setDayunIndex(item.index);
                const first = item.liunian[0];
                if (first) {
                  setLiunianYear(first.year);
                  setLiuyueIndex(0);
                }
              }}
            >
              <span>
                {item.startAge}岁 {item.startYear}
              </span>
              <strong>{item.ganzhi}</strong>
            </button>
          ))}
        </div>
      </div>

      <div className="luck-section">
        <div className="luck-section-title">流年</div>
        <div className="luck-track">
          {dayun?.liunian.map((item) => (
            <button
              key={item.year}
              type="button"
              className={`luck-chip ${item.year === liunianYear ? "active" : ""}`}
              onClick={() => {
                setLiunianYear(item.year);
                setLiuyueIndex(0);
              }}
            >
              <span>{item.year}</span>
              <strong>{item.ganzhi}</strong>
            </button>
          ))}
        </div>
      </div>

      <div className="luck-section">
        <div className="luck-section-title">节气</div>
        <div className="luck-jieqi">
          {timeline.jieqi.map((name) => (
            <span key={name}>{name}</span>
          ))}
        </div>
      </div>

      <div className="luck-section">
        <div className="luck-section-title">流月</div>
        <div className="luck-track">
          {liunian?.liuyue.map((item) => (
            <button
              key={item.index}
              type="button"
              className={`luck-chip ${item.index === liuyueIndex ? "active" : ""}`}
              onClick={() => setLiuyueIndex(item.index)}
            >
              <span>{item.monthLabel}月</span>
              <strong>{item.ganzhi}</strong>
            </button>
          ))}
        </div>
      </div>

      <div className="luck-section">
        <div className="luck-section-title">流日</div>
        <div className="luck-track luck-track-days">
          {monthDays.map((item) => (
            <button
              key={item.date}
              type="button"
              className={`luck-chip ${item.date === liuriDate ? "active" : ""}`}
              onClick={() => setLiuriDate(item.date)}
            >
              <span>{item.day}日</span>
              <strong>{item.ganzhi}</strong>
            </button>
          ))}
        </div>
      </div>
    </section>
  );
}
