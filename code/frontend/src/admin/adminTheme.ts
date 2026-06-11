import { theme as antTheme, type ThemeConfig } from "antd";
import type { ThemeMode } from "../context/ThemeContext";

const sharedTokens = {
  fontFamily:
    '"Segoe UI", "PingFang SC", "Microsoft YaHei", sans-serif',
  borderRadius: 8,
  colorPrimary: "#8b2f2f",
  colorInfo: "#d9a441",
  colorSuccess: "#3d7a4f",
  colorWarning: "#d9a441",
  colorError: "#8b2f2f",
};

export function getAdminThemeConfig(mode: ThemeMode): ThemeConfig {
  if (mode === "dark") {
    return {
      algorithm: antTheme.darkAlgorithm,
      token: {
        ...sharedTokens,
        colorBgBase: "#0c0e14",
        colorBgContainer: "#12141c",
        colorBgElevated: "#1a1420",
        colorText: "#f7ead1",
        colorTextSecondary: "rgba(247, 234, 209, 0.72)",
        colorBorder: "rgba(217, 164, 65, 0.32)",
        colorPrimary: "#c45a5a",
      },
      components: {
        Layout: {
          siderBg: "#0c0e14",
          headerBg: "#12141c",
          bodyBg: "#0c0e14",
        },
        Menu: {
          darkItemBg: "#0c0e14",
          darkSubMenuItemBg: "#12141c",
        },
      },
    };
  }

  return {
    algorithm: antTheme.defaultAlgorithm,
    token: {
      ...sharedTokens,
      colorBgBase: "#f4efe6",
      colorBgContainer: "#fffdf8",
      colorBgElevated: "#faf6ef",
      colorText: "#1f1a17",
      colorTextSecondary: "#4f453c",
      colorBorder: "#c4b5a0",
    },
    components: {
      Layout: {
        siderBg: "#fffdf8",
        headerBg: "#fffdf8",
        bodyBg: "#f4efe6",
      },
    },
  };
}
