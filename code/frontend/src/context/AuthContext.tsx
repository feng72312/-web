import { AuthLoginModal } from "../components/AuthLoginModal";
import { UserCenterModal } from "../components/UserCenterModal";
import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from "react";

import { cloudbaseAuthEnabled } from "../config/cloudbase";
import { mergeDeviceQuota } from "../services/authApi";
import { fetchQuotaStatus } from "../services/quotaApi";
import { getAccessToken, getCloudbaseAuth } from "../services/cloudbaseClient";
import { hasFreeAiQuota } from "../utils/quotaHelpers";
import { refreshQuotaBar } from "../utils/quotaEvents";

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

  const refreshSession = useCallback(async () => {
    if (!enabled) {
      setUser(null);
      setLoading(false);
      return;
    }
    setLoading(true);
    try {
      const auth = getCloudbaseAuth();
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

  const afterLogin = useCallback(async () => {
    await mergeDeviceQuota().catch(() => undefined);
    await refreshSession();
    refreshQuotaBar();
  }, [refreshSession]);

  useEffect(() => {
    void refreshSession();
    if (!enabled) {
      return;
    }
    const auth = getCloudbaseAuth();
    const sub = auth.onAuthStateChange((event) => {
      if (event === "SIGNED_IN" || event === "TOKEN_REFRESHED" || event === "USER_UPDATED") {
        void afterLogin();
      }
      if (event === "SIGNED_OUT") {
        setUser(null);
      }
    });
    return () => {
      sub?.data?.subscription?.unsubscribe?.();
    };
  }, [afterLogin, enabled, refreshSession]);

  const openLogin = useCallback((afterLoginAction?: () => void) => {
    if (afterLoginAction) {
      setPendingAction(() => afterLoginAction);
    }
    setLoginOpen(true);
  }, []);

  const closeLogin = useCallback(() => {
    setLoginOpen(false);
    setPendingAction(null);
  }, []);

  const finishLogin = useCallback(async () => {
    await afterLogin();
    setLoginOpen(false);
    const action = pendingAction;
    setPendingAction(null);
    if (action) {
      await action();
    }
  }, [afterLogin, pendingAction]);

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
    const auth = getCloudbaseAuth();
    await auth.signOut();
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
        <AuthLoginModal onClose={closeLogin} onSuccess={() => void finishLogin()} />
      ) : null}
      {enabled && userCenterOpen && user ? (
        <UserCenterModal user={user} onClose={() => setUserCenterOpen(false)} />
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
