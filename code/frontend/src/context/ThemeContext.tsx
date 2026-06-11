import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from "react";

export type ThemeMode = "light" | "dark";
export type DensityMode = "comfortable" | "compact";
export type ExperienceLane = "consumer" | "professional";

interface ThemeContextValue {
  theme: ThemeMode;
  density: DensityMode;
  lane: ExperienceLane;
  setTheme: (mode: ThemeMode) => void;
  toggleTheme: () => void;
  setDensity: (mode: DensityMode) => void;
  toggleDensity: () => void;
  setLane: (lane: ExperienceLane) => void;
}

const ThemeContext = createContext<ThemeContextValue | null>(null);

const THEME_KEY = "shushu_theme_v1";
const DENSITY_KEY = "shushu_density_v1";
const LANE_KEY = "shushu_lane_v1";

export function ThemeProvider({ children }: { children: ReactNode }) {
  const [theme, setThemeState] = useState<ThemeMode>(() => {
    const saved = localStorage.getItem(THEME_KEY);
    const initial: ThemeMode = saved === "dark" ? "dark" : "light";
    document.documentElement.dataset.theme = initial;
    return initial;
  });
  const [density, setDensityState] = useState<DensityMode>(() => {
    const saved = localStorage.getItem(DENSITY_KEY);
    return saved === "compact" ? "compact" : "comfortable";
  });
  const [lane, setLaneState] = useState<ExperienceLane>(() => {
    const saved = localStorage.getItem(LANE_KEY);
    return saved === "professional" ? "professional" : "consumer";
  });

  useEffect(() => {
    document.documentElement.dataset.theme = theme;
    localStorage.setItem(THEME_KEY, theme);
  }, [theme]);

  useEffect(() => {
    document.documentElement.dataset.density = density;
    localStorage.setItem(DENSITY_KEY, density);
  }, [density]);

  useEffect(() => {
    localStorage.setItem(LANE_KEY, lane);
  }, [lane]);

  const setTheme = useCallback((mode: ThemeMode) => setThemeState(mode), []);
  const toggleTheme = useCallback(
    () => setThemeState((t) => (t === "light" ? "dark" : "light")),
    [],
  );
  const setDensity = useCallback((mode: DensityMode) => setDensityState(mode), []);
  const toggleDensity = useCallback(
    () => setDensityState((d) => (d === "comfortable" ? "compact" : "comfortable")),
    [],
  );
  const setLane = useCallback((next: ExperienceLane) => setLaneState(next), []);

  const value = useMemo(
    () => ({
      theme,
      density,
      lane,
      setTheme,
      toggleTheme,
      setDensity,
      toggleDensity,
      setLane,
    }),
    [theme, density, lane, setTheme, toggleTheme, setDensity, toggleDensity, setLane],
  );

  return <ThemeContext.Provider value={value}>{children}</ThemeContext.Provider>;
}

export function useTheme() {
  const ctx = useContext(ThemeContext);
  if (!ctx) {
    throw new Error("useTheme must be used within ThemeProvider");
  }
  return ctx;
}
