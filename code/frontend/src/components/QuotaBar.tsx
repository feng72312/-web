import { useCallback, useEffect, useState } from "react";
import { fetchQuotaStatus, type QuotaStatus } from "../services/quotaApi";

export function QuotaBar() {
  const [status, setStatus] = useState<QuotaStatus | null>(null);

  const refresh = useCallback(() => {
    fetchQuotaStatus()
      .then(setStatus)
      .catch(() => setStatus(null));
  }, []);

  useEffect(() => {
    refresh();
    const timer = window.setInterval(refresh, 300_000);
    const onRefresh = () => refresh();
    window.addEventListener("quota-refresh", onRefresh);
    return () => {
      window.clearInterval(timer);
      window.removeEventListener("quota-refresh", onRefresh);
    };
  }, [refresh]);

  if (!status) {
    return null;
  }

  return (
    <div className="quota-bar">
      <div className="quota-bar-summary">
        <span className="quota-bar-item">今日 AI 剩余 {status.freeRemaining} 次</span>
      </div>
    </div>
  );
}

/** Call after AI action to refresh quota display */
export { refreshQuotaBar } from "../utils/quotaEvents";
