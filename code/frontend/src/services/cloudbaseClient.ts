import cloudbase from "@cloudbase/js-sdk";

import {
  CLOUDBASE_ENV_ID,
  CLOUDBASE_PUBLISHABLE_KEY,
  CLOUDBASE_REGION,
  cloudbaseAuthEnabled,
} from "../config/cloudbase";

let app: ReturnType<typeof cloudbase.init> | null = null;

export function getCloudbaseApp() {
  if (!cloudbaseAuthEnabled()) {
    throw new Error("CloudBase auth is not configured");
  }
  if (!app) {
    app = cloudbase.init({
      env: CLOUDBASE_ENV_ID,
      region: CLOUDBASE_REGION,
      accessKey: CLOUDBASE_PUBLISHABLE_KEY,
      auth: { detectSessionInUrl: true },
    });
  }
  return app;
}

export function getCloudbaseAuth() {
  return getCloudbaseApp().auth({ persistence: "local" });
}

export type AuthSession = {
  access_token: string;
  refresh_token?: string;
  user?: {
    id?: string;
    phone?: string;
    user_metadata?: { username?: string };
    is_anonymous?: boolean;
  };
};

let accessTokenCache: { token: string | null; at: number } | null = null;
const ACCESS_TOKEN_CACHE_MS = 8000;

export function clearAccessTokenCache(): void {
  accessTokenCache = null;
}

export async function getAccessToken(): Promise<string | null> {
  if (!cloudbaseAuthEnabled()) {
    return null;
  }
  if (
    accessTokenCache &&
    Date.now() - accessTokenCache.at < ACCESS_TOKEN_CACHE_MS
  ) {
    return accessTokenCache.token;
  }
  const auth = getCloudbaseAuth();
  const { data } = await auth.getSession();
  const session = data?.session as AuthSession | undefined;
  if (!session?.access_token) {
    accessTokenCache = { token: null, at: Date.now() };
    return null;
  }
  if (session.user?.is_anonymous) {
    accessTokenCache = { token: null, at: Date.now() };
    return null;
  }
  const userId = session.user?.id;
  if (!userId || userId === "anon") {
    accessTokenCache = { token: null, at: Date.now() };
    return null;
  }
  // Publishable Key is not a logged-in user session; sending it to bazi-api causes 401.
  if (session.access_token === CLOUDBASE_PUBLISHABLE_KEY) {
    accessTokenCache = { token: null, at: Date.now() };
    return null;
  }
  accessTokenCache = { token: session.access_token, at: Date.now() };
  return session.access_token;
}
