export const CLOUDBASE_ENV_ID =
  (import.meta.env.VITE_CLOUDBASE_ENV_ID as string | undefined)?.trim() ||
  "zy-feng-d3glt5d93b1a9f08e";

export const CLOUDBASE_REGION =
  (import.meta.env.VITE_CLOUDBASE_REGION as string | undefined)?.trim() || "ap-shanghai";

export const CLOUDBASE_PUBLISHABLE_KEY =
  (import.meta.env.VITE_CLOUDBASE_PUBLISHABLE_KEY as string | undefined)?.trim() || "";

export function cloudbaseAuthEnabled(): boolean {
  return Boolean(CLOUDBASE_ENV_ID && CLOUDBASE_PUBLISHABLE_KEY);
}
