import { useEffect, useState } from "react";
import { fetchStatsOverview, sendStatsHeartbeat } from "../services/statsApi";

const HEARTBEAT_MS = 30_000;

export function UsageStatsBar() {
  const [online, setOnline] = useState<number | null>(null);
  const [total, setTotal] = useState<number | null>(null);
  const [unavailable, setUnavailable] = useState(false);

  useEffect(() => {
    let cancelled = false;

    const apply = (data: { online: number; total: number }) => {
      if (!cancelled) {
        setOnline(data.online);
        setTotal(data.total);
        setUnavailable(false);
      }
    };

    const markUnavailable = () => {
      if (!cancelled) {
        setUnavailable(true);
      }
    };

    const pulse = () => {
      sendStatsHeartbeat()
        .then(apply)
        .catch(() => {
          fetchStatsOverview()
            .then(apply)
            .catch(markUnavailable);
        });
    };

    pulse();
    const timer = window.setInterval(() => {
      if (document.visibilityState === "visible") {
        pulse();
      }
    }, HEARTBEAT_MS);

    const onVisible = () => {
      if (document.visibilityState === "visible") {
        pulse();
      }
    };
    document.addEventListener("visibilitychange", onVisible);

    return () => {
      cancelled = true;
      window.clearInterval(timer);
      document.removeEventListener("visibilitychange", onVisible);
    };
  }, []);

  const onlineText = online === null ? "--" : String(online);
  const totalText = total === null ? "--" : String(total);

  return (
    <div
      className="usage-stats-bar"
      aria-live="polite"
      title={
        unavailable
          ? "统计服务未连接, 请确认后端已重启并配置 VITE_API_BASE"
          : undefined
      }
    >
      <span className="usage-stats-item">当前在线: {onlineText}</span>
      <span className="usage-stats-sep">|</span>
      <span className="usage-stats-item">累计访客: {totalText}</span>
      {unavailable && <span className="usage-stats-warn">未连接</span>}
    </div>
  );
}
