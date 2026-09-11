import type { OnAuthStateChangeCallback } from "@cloudbase/auth";
import {
  createContext,
  lazy,
  Suspense,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useRef,
  useState,
  type ReactNode,
} from "react";

import { cloudbaseAuthEnabled } from "../config/cloudbase";
import { mergeDeviceQuota } from "../services/authApi";
import { fetchQuotaStatus } from "../services/quotaApi";
import { clearAccessTokenCache, getAccessToken, getCloudbaseAuth } from "../services/cloudbaseClient";
import { hasFreeAiQuota } from "../utils/quotaHelpers";
import { refreshQuotaBar } from "../utils/quotaEvents";

const AuthLoginModal = lazy(() =>
  import("../components/AuthLoginModal").then((module) => ({
    default: module.AuthLoginModal,
  })),
);

const UserCenterModal = lazy(() =>
  import("../components/UserCenterModal").then((module) => ({
    default: module.UserCenterModal,
  })),
);

type AuthUser = {
  id: string;
  username?: string;
  phone?: string;
};

type AuthContextValue = {
  enabled: boolean;
  loading: boolean;
  user: AuthUser | null;
  loginOpen: boolean;
  userCenterOpen: boolean;
  openLogin: (afterLogin?: () => void) => void;
  closeLogin: () => void;
  openUserCenter: () => void;
  closeUserCenter: () => void;
  runWithAuth: (action: () => void | Promise<void>) => void;
  refreshSession: () => Promise<void>;
  signOut: () => Promise<void>;
};

type AuthStateEvent = Parameters<OnAuthStateChangeCallback>[0];

const AuthContext = createContext<AuthContextValue | null>(null);

function mapUser(raw: Record<string, unknown> | undefined | null): AuthUser | null {
  if (!raw?.id || typeof raw.id !== "string") {
    return null;
  }
  const meta = raw.user_metadata;
  const username =
    typeof raw.username === "string"
      ? raw.username
      : meta && typeof meta === "object" && typeof (meta as { username?: string }).username === "string"
        ? (meta as { username: string }).username
        : undefined;
  const phone = typeof raw.phone === "string" ? raw.phone : undefined;
  return { id: raw.id, username, phone };
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const enabled = cloudbaseAuthEnabled();
  const [loading, setLoading] = useState(enabled);
  const [user, setUser] = useState<AuthUser | null>(null);
  const [loginOpen, setLoginOpen] = useState(false);
  const [userCenterOpen, setUserCenterOpen] = useState(false);
  const [pendingAction, setPendingAction] = useState<(() => void | Promise<void>) | null>(null);
  const postLoginRunning = useRef(false);

  const refreshSession = useCallback(async () => {
    if (!enabled) {
      setUser(null);
      setLoading(false);
      return;
    }
    setLoading(true);
    try {
      const auth = await getCloudbaseAuth();
      const { data } = await auth.getSession();
      const session = data?.session as { user?: Record<string, unknown>; access_token?: string } | undefined;
      if (!session?.access_token || session.user?.is_anonymous) {
        setUser(null);
        return;
      }
      setUser(mapUser(session.user ?? null));
    } catch {
      setUser(null);
    } finally {
      setLoading(false);
    }
  }, [enabled]);

  const runPostLogin = useCallback(async () => {
    if (postLoginRunning.current) {
      return;
    }
    postLoginRunning.current = true;
    try {
      await refreshSession();
      void mergeDeviceQuota()
        .then(() => refreshQuotaBar())
        .catch(() => undefined);
    } finally {
      window.setTimeout(() => {
        postLoginRunning.current = false;
      }, 2000);
    }
  }, [refreshSession]);

  useEffect(() => {
    void refreshSession();
    if (!enabled) {
      return;
    }
    let disposed = false;
    let unsubscribe: (() => void) | null = null;
    void getCloudbaseAuth()
      .then((auth) => {
        if (disposed) {
          return;
        }
        const sub = auth.onAuthStateChange((event: AuthStateEvent) => {
          if (event === "SIGNED_IN" || event === "TOKEN_REFRESHED" || event === "USER_UPDATED") {
            void runPostLogin();
          }
          if (event === "SIGNED_OUT") {
            setUser(null);
          }
        });
        unsubscribe = () => sub?.data?.subscription?.unsubscribe?.();
      })
      .catch(() => {
        if (!disposed) {
          setUser(null);
        }
      });
    return () => {
      disposed = true;
      if (unsubscribe) {
        unsubscribe();
      }
    };
  }, [enabled, refreshSession, runPostLogin]);

  const openLogin = useCallback((afterLoginAction?: () => void) => {
    if (afterLoginAction) {
      setPendingAction(() => afterLoginAction);
    }
    setLoginOpen(true);
  }, []);

  const closeLogin = useCallback(() => {
    const hadPending = pendingAction !== null;
    setLoginOpen(false);
    setPendingAction(null);
    if (hadPending) {
      window.dispatchEvent(new CustomEvent("zy-auth-cancelled"));
    }
  }, [pendingAction]);

  const finishLogin = useCallback(async () => {
    setLoginOpen(false);
    const action = pendingAction;
    setPendingAction(null);
    void runPostLogin();
    if (action) {
      await action();
    }
  }, [pendingAction, runPostLogin]);

  const runWithAuth = useCallback(
    (action: () => void | Promise<void>) => {
      void (async () => {
        const token = await getAccessToken();
        if (token) {
          await action();
          return;
        }
        try {
          const status = await fetchQuotaStatus();
          if (hasFreeAiQuota(status)) {
            await action();
            return;
          }
        } catch {
          // fall through to login when quota status unavailable
        }
        openLogin(() => {
          void action();
        });
      })();
    },
    [openLogin],
  );

  const signOut = useCallback(async () => {
    if (!enabled) {
      return;
    }
    const auth = await getCloudbaseAuth();
    await auth.signOut();
    clearAccessTokenCache();
    setUser(null);
    refreshQuotaBar();
  }, [enabled]);

  const value = useMemo<AuthContextValue>(
    () => ({
      enabled,
      loading,
      user,
      loginOpen,
      userCenterOpen,
      openLogin,
      closeLogin,
      openUserCenter: () => setUserCenterOpen(true),
      closeUserCenter: () => setUserCenterOpen(false),
      runWithAuth,
      refreshSession,
      signOut,
    }),
    [
      closeLogin,
      enabled,
      loading,
      loginOpen,
      openLogin,
      runWithAuth,
      refreshSession,
      signOut,
      user,
      userCenterOpen,
    ],
  );

  return (
    <AuthContext.Provider value={value}>
      {children}
      {enabled && loginOpen ? (
        <Suspense fallback={<div className="auth-modal-loading" role="status">正在载入登录面板...</div>}>
          <AuthLoginModal onClose={closeLogin} onSuccess={finishLogin} />
        </Suspense>
      ) : null}
      {enabled && userCenterOpen && user ? (
        <Suspense fallback={<div className="auth-modal-loading" role="status">正在载入个人中心...</div>}>
          <UserCenterModal user={user} onClose={() => setUserCenterOpen(false)} />
        </Suspense>
      ) : null}
    </AuthContext.Provider>
  );
}

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext);
  if (!ctx) {
    throw new Error("useAuth must be used within AuthProvider");
  }
  return ctx;
}
