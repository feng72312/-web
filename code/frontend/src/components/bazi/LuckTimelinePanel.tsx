import { useEffect, useMemo, useState } from "react";
import { fetchLiuri } from "../../services/api";
import type { FlowPillar, LiuriDay, LuckTimeline } from "../../types/bazi";
import { wuxingClass } from "../../utils/wuxing";

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

function ColoredGanzhi({ pillar }: { pillar: FlowPillar }) {
  return (
    <span className="bazi-luck-matrix-gz">
      <span className={wuxingClass(pillar.ganWuxing)}>{pillar.gan}</span>
      <span className={wuxingClass(pillar.zhiWuxing)}>{pillar.zhi}</span>
    </span>
  );
}

interface MatrixItem {
  id: string;
  metaTop: string;
  metaBottom?: string;
  pillar: FlowPillar;
}

function LuckMatrixTrack({
  items,
  activeId,
  onSelect,
}: {
  items: MatrixItem[];
  activeId: string;
  onSelect: (id: string) => void;
}) {
  return (
    <div className="bazi-luck-matrix">
      <div className="bazi-luck-matrix-row meta">
        {items.map((item) => (
          <button
            key={`${item.id}-meta`}
            type="button"
            className={`bazi-luck-matrix-cell ${item.id === activeId ? "active" : ""}`}
            onClick={() => onSelect(item.id)}
          >
            <span>{item.metaTop}</span>
            {item.metaBottom && <span className="bazi-luck-matrix-sub">{item.metaBottom}</span>}
          </button>
        ))}
      </div>
      <div className="bazi-luck-matrix-row gz">
        {items.map((item) => (
          <button
            key={`${item.id}-gz`}
            type="button"
            className={`bazi-luck-matrix-cell ${item.id === activeId ? "active" : ""}`}
            onClick={() => onSelect(item.id)}
          >
            <ColoredGanzhi pillar={item.pillar} />
          </button>
        ))}
      </div>
    </div>
  );
}

function ShenShaRow({ label, items }: { label: string; items: string[] }) {
  const text = items.length ? items.join(", ") : "-";
  return (
    <div className="bazi-luck-shensha-row">
      <span className="bazi-luck-shensha-label">{label}</span>
      <span className="bazi-luck-shensha-value">{text}</span>
    </div>
  );
}

interface LuckTimelinePanelProps {
  timeline: LuckTimeline;
}

export function LuckTimelinePanel({ timeline }: LuckTimelinePanelProps) {
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
    fetchLiuri(liunianYear, timeline.dayMaster, {
      dayZhi: timeline.birthPillars.day.zhi,
      yearGan: timeline.birthPillars.year.gan,
      yearZhi: timeline.birthPillars.year.zhi,
      monthZhi: timeline.birthPillars.month.zhi,
    }).then((payload) => {
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
        shenSha: liuri.shenSha,
      }
    : undefined;

  const ageText = liunian ? `${liunian.age}岁 ${liunian.year}` : "";

  const dayunItems: MatrixItem[] = timeline.dayun.map((item) => ({
    id: String(item.index),
    metaTop: `${String(item.startAge).padStart(2, "0")}岁`,
    metaBottom: String(item.startYear),
    pillar: item.pillar,
  }));

  const liunianItems: MatrixItem[] =
    dayun?.liunian.map((item) => ({
      id: String(item.year),
      metaTop: String(item.year),
      pillar: item.pillar,
    })) ?? [];

  const liuyueItems: MatrixItem[] =
    liunian?.liuyue.map((item) => ({
      id: String(item.index),
      metaTop: `${item.monthLabel}月`,
      pillar: item.pillar,
    })) ?? [];

  return (
    <div className="luck-panel bazi-luck-timeline-panel">
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
              <td className="luck-meta">{liuri?.day ? `${liuri.day}日` : "-"}</td>
              <td className="luck-meta">{liuyue?.monthLabel ? `${liuyue.monthLabel}月` : "-"}</td>
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
                <PillarCell
                  pillar={timeline.birthPillars.year}
                  tag={timeline.birthPillars.year.shishenGan}
                />
              </td>
              <td>
                <PillarCell
                  pillar={timeline.birthPillars.month}
                  tag={timeline.birthPillars.month.shishenGan}
                />
              </td>
              <td>
                <PillarCell pillar={timeline.birthPillars.day} tag={timeline.genderRole} />
              </td>
              <td>
                <PillarCell
                  pillar={timeline.birthPillars.hour}
                  tag={timeline.birthPillars.hour.shishenGan}
                />
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <div className="luck-section">
        <div className="luck-section-title">大运</div>
        <LuckMatrixTrack
          items={dayunItems}
          activeId={String(dayunIndex)}
          onSelect={(id) => {
            const index = Number(id);
            setDayunIndex(index);
            const picked = timeline.dayun.find((item) => item.index === index);
            const first = picked?.liunian[0];
            if (first) {
              setLiunianYear(first.year);
              setLiuyueIndex(0);
            }
          }}
        />
      </div>

      <div className="luck-section">
        <div className="luck-section-title">流年</div>
        <LuckMatrixTrack
          items={liunianItems}
          activeId={String(liunianYear)}
          onSelect={(id) => {
            setLiunianYear(Number(id));
            setLiuyueIndex(0);
          }}
        />
        <div className="luck-jieqi">
          {timeline.jieqi.map((name) => (
            <span key={name}>{name}</span>
          ))}
        </div>
      </div>

      <div className="luck-section">
        <div className="luck-section-title">流月</div>
        <LuckMatrixTrack
          items={liuyueItems}
          activeId={String(liuyueIndex)}
          onSelect={(id) => setLiuyueIndex(Number(id))}
        />
      </div>

      <div className="luck-section">
        <div className="luck-section-title">流日</div>
        <div className="luck-track luck-track-days bazi-luck-ri-track">
          {monthDays.map((item) => (
            <button
              key={item.date}
              type="button"
              className={`luck-chip bazi-luck-ri-chip ${item.date === liuriDate ? "active" : ""}`}
              onClick={() => setLiuriDate(item.date)}
            >
              <span>{item.day}日</span>
              <span className="bazi-luck-matrix-gz">
                <span className={wuxingClass(item.ganWuxing)}>{item.gan}</span>
                <span className={wuxingClass(item.zhiWuxing)}>{item.zhi}</span>
              </span>
            </button>
          ))}
        </div>
      </div>

      <div className="bazi-luck-shensha-block">
        <ShenShaRow label="大运神煞" items={dayun?.pillar.shenSha ?? []} />
        <ShenShaRow label="流年神煞" items={liunian?.pillar.shenSha ?? []} />
        <ShenShaRow label="流月神煞" items={liuyue?.pillar.shenSha ?? []} />
        <ShenShaRow label="流日神煞" items={liuriFlow?.shenSha ?? []} />
      </div>
    </div>
  );
}
