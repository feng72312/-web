import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import tailwindcss from "@tailwindcss/vite";

export default defineConfig({
  plugins: [react(), tailwindcss()],
  build: {
    target: "esnext",
    rollupOptions: {
      output: {
        manualChunks(id: string) {
          if (!id.includes("node_modules")) {
            return undefined;
          }
          if (
            id.includes("/react/") ||
            id.includes("/react-dom/") ||
            id.includes("/scheduler/") ||
            id.includes("/framer-motion/") ||
            id.includes("/motion/") ||
            id.includes("/@assistant-ui/") ||
            id.includes("/antd/") ||
            id.includes("/@ant-design/") ||
            id.includes("/rc-")
          ) {
            return "vendor-react";
          }
          if (id.includes("/echarts") || id.includes("/zrender")) {
            return "vendor-echarts";
          }
          return undefined;
        },
      },
    },
  },
  server: {
    host: "0.0.0.0",
    allowedHosts: [".trycloudflare.com"],
    port: 5173,
    strictPort: true,
    proxy: {
      "/api": {
        target: "http://127.0.0.1:8002",
        changeOrigin: true,
        timeout: 300000,
        proxyTimeout: 300000,
      },
    },
  },
  preview: {
    host: "0.0.0.0",
    allowedHosts: [".trycloudflare.com"],
    port: 5173,
    strictPort: true,
    proxy: {
      "/api": {
        target: "http://127.0.0.1:8002",
        changeOrigin: true,
        timeout: 300000,
        proxyTimeout: 300000,
      },
    },
  },
});
