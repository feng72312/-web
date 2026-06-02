import { useCallback, useEffect, useState } from "react";
import {
  fetchQuotaPersistence,
  fetchQuotaStatus,
  redeemLicenseKey,
  type QuotaStatus,
} from "../services/quotaApi";

export function QuotaBar() {
  const [status, setStatus] = useState<QuotaStatus | null>(null);
  const [keyInput, setKeyInput] = useState("");
  const [showRedeem, setShowRedeem] = useState(false);
  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState(false);
  const [storageWarning, setStorageWarning] = useState("");

  const refresh = useCallback(() => {
    fetchQuotaStatus()
      .then(setStatus)
      .catch(() => setStatus(null));
    fetchQuotaPersistence().then((info) => {
      if (info && !info.likelyPersistent) {
        setStorageWarning(
          "提示: 服务端数据尚未持久化, 发版后免费次数与秘钥余额可能重置. 请联系运营配置云存储挂载.",
        );
      } else {
        setStorageWarning("");
      }
    });
  }, []);

  useEffect(() => {
    refresh();
    const timer = window.setInterval(refresh, 60_000);
    const onRefresh = () => refresh();
    window.addEventListener("quota-refresh", onRefresh);
    return () => {
      window.clearInterval(timer);
      window.removeEventListener("quota-refresh", onRefresh);
    };
  }, [refresh]);

  const handleRedeem = async () => {
    if (!keyInput.trim()) {
      return;
    }
    setLoading(true);
    setMessage("");
    try {
      const result = await redeemLicenseKey(keyInput);
      setMessage(`已兑换 +${result.addedCredits} 次, 余额 ${result.creditBalance} 次`);
      setKeyInput("");
      refresh();
    } catch (err) {
      setMessage(err instanceof Error ? err.message : "兑换失败");
    } finally {
      setLoading(false);
    }
  };

  const freeText = status ? `${status.freeRemaining}/${status.freeDailyLimit}` : "--";
  const paidText = status ? String(status.creditBalance) : "--";
  const tierHint = status?.tierQuotas
    ?.map((item) => `${item.tier}${item.remaining}`)
    .join(" ");

  return (
    <div className="quota-bar">
      <div className="quota-bar-summary">
        <span className="quota-bar-item">共享免费 AI: {freeText}</span>
        <span className="quota-bar-sep">|</span>
        <span className="quota-bar-item">次数包: {paidText}</span>
        <button
          type="button"
          className="secondary quota-bar-toggle"
          onClick={() => setShowRedeem((v) => !v)}
        >
          {showRedeem ? "收起" : "兑换秘钥"}
        </button>
      </div>
      {tierHint && (
        <p className="quota-bar-tier-hint">
          等级免费剩余(次): {tierHint}. 先用等级免费, 再用共享免费, 最后用次数包.
        </p>
      )}
      {storageWarning && <p className="quota-bar-message quota-bar-warning">{storageWarning}</p>}
      {showRedeem && (
        <div className="quota-bar-panel">
          <p className="hint">
            10元20次 / 20元50次 / 50元150次 / 100元500次. 人工付款后向运营索取秘钥.
          </p>
          <div className="quota-bar-row">
            <input
              className="text-input"
              type="text"
              placeholder="输入秘钥 ZY-XXXX-XXXX-XXXX"
              value={keyInput}
              onChange={(e) => setKeyInput(e.target.value)}
            />
            <button
              type="button"
              className="primary-btn"
              disabled={loading}
              onClick={handleRedeem}
            >
              兑换
            </button>
          </div>
          {message && <p className="quota-bar-message">{message}</p>}
        </div>
      )}
    </div>
  );
}

/** Call after AI action to refresh quota display */
export { refreshQuotaBar } from "../utils/quotaEvents";
