/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_API_BASE: string;
  readonly VITE_CLOUDBASE_ENV_ID: string;
  readonly VITE_CLOUDBASE_REGION: string;
  readonly VITE_CLOUDBASE_PUBLISHABLE_KEY: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}
