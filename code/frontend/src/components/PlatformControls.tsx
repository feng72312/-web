import { Moon, Sun, LayoutGrid, Rows3, Briefcase, Sparkles } from "lucide-react";
import { useTheme } from "../context/ThemeContext";

export function PlatformControls() {
  const { theme, toggleTheme, density, toggleDensity, lane, setLane } = useTheme();

  return (
    <div className="platform-controls">
      <button
        type="button"
        className="icon-btn"
        onClick={toggleTheme}
        title={theme === "light" ? "切换暗色" : "切换亮色"}
        aria-label="切换主题"
      >
        {theme === "light" ? (
          <Moon size={16} strokeWidth={2} className="platform-control-icon" />
        ) : (
          <Sun size={16} strokeWidth={2} className="platform-control-icon" />
        )}
      </button>
      <button
        type="button"
        className="icon-btn"
        onClick={toggleDensity}
        title={density === "comfortable" ? "紧凑视图" : "舒适视图"}
        aria-label="切换密度"
      >
        {density === "comfortable" ? (
          <Rows3 size={16} strokeWidth={2} className="platform-control-icon" />
        ) : (
          <LayoutGrid size={16} strokeWidth={2} className="platform-control-icon" />
        )}
      </button>
      <button
        type="button"
        className={lane === "consumer" ? "icon-btn active" : "icon-btn"}
        onClick={() => setLane("consumer")}
        title="简版体验"
        aria-label="简版体验"
      >
        <Sparkles size={16} strokeWidth={2} className="platform-control-icon" />
      </button>
      <button
        type="button"
        className={lane === "professional" ? "icon-btn active" : "icon-btn"}
        onClick={() => setLane("professional")}
        title="专业视图"
        aria-label="专业视图"
      >
        <Briefcase size={16} strokeWidth={2} className="platform-control-icon" />
      </button>
    </div>
  );
}
