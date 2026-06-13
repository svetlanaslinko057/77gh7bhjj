import { useEffect, useState, useCallback, lazy, Suspense } from "react";
import "@/App.css";
import { BrowserRouter, Routes, Route, useLocation, Navigate } from "react-router-dom";
import axios from "axios";
import { createContext, useContext } from "react";
import { GoogleOAuthProvider } from "@react-oauth/google";
import { getDeviceFingerprint } from "@/lib/deviceFingerprint";

import { ToastProvider } from "@/components/Toast";
import ToastBridgeMount from "@/components/ToastBridgeMount";
import RootErrorBoundary from "@/components/RootErrorBoundary";
import { ThemeProvider, useTheme } from "@/contexts/ThemeContext";
import { LegalSettingsProvider } from "@/contexts/LegalSettingsContext";
import { LanguageProvider } from "@/contexts/LanguageContext";
import { ContactModalProvider } from "@/contexts/ContactModalContext";
import CookieBanner from "@/components/CookieBanner";
import EvaCompanion from "@/components/EvaCompanion";

import LandingPage from "@/pages/LandingPage";
const PublicAssetDetail = lazy(() => import("@/pages/PublicAssetDetail"));
const LegalIndexPage = lazy(() => import("@/pages/legal/LegalIndexPage"));
const LegalDocPage = lazy(() => import("@/pages/legal/LegalDocPage"));
import UnifiedAuthPage from "@/pages/UnifiedAuthPage";
import AdminLoginPage from "@/pages/AdminLoginPage";
const TwoFactorChallengePage = lazy(() => import("@/pages/TwoFactorChallengePage"));
const TwoFactorSetupPage = lazy(() => import("@/pages/TwoFactorSetupPage"));
const TwoFactorRecoveryPage = lazy(() => import("@/pages/TwoFactorRecoveryPage"));

import InvestorLayout from "@/layouts/InvestorLayout";
const InvestorDashboard = lazy(() => import("@/pages/investor/InvestorDashboard"));
const InvestorPortfolio = lazy(() => import("@/pages/investor/InvestorPortfolio"));
const InvestorOpportunities = lazy(() => import("@/pages/investor/InvestorOpportunities"));
const InvestorAssetDetail = lazy(() => import("@/pages/investor/InvestorAssetDetail"));
const InvestorPayments = lazy(() => import("@/pages/investor/InvestorPayments"));
const InvestorWallet = lazy(() => import("@/pages/investor/InvestorWallet"));
const InvestorIncome = lazy(() => import("@/pages/investor/InvestorIncome"));
const InvestorAnalytics = lazy(() => import("@/pages/investor/InvestorAnalytics"));
const InvestorContracts = lazy(() => import("@/pages/investor/InvestorContracts"));
const InvestorDocuments = lazy(() => import("@/pages/investor/InvestorDocuments"));
const InvestorProfile = lazy(() => import("@/pages/investor/InvestorProfile"));
const InvestorNotifications = lazy(() => import("@/pages/investor/InvestorNotifications"));
const InvestorNotificationPreferences = lazy(() => import("@/pages/investor/InvestorNotificationPreferences"));
const InvestorMarketplace = lazy(() => import("@/pages/investor/InvestorMarketplace"));
const AdminSecondaryMarket = lazy(() => import("@/pages/admin/AdminSecondaryMarket"));

import AdminLayout from "@/layouts/AdminLayout";
const AdminDashboard = lazy(() => import("@/pages/admin/AdminDashboard"));
const AdminInvestors = lazy(() => import("@/pages/admin/AdminInvestors"));
const AdminIntents = lazy(() => import("@/pages/admin/AdminIntents"));
const AdminKyc = lazy(() => import("@/pages/admin/AdminKyc"));
const AdminAssets = lazy(() => import("@/pages/admin/AdminAssets"));
const AdminAssetEditor = lazy(() => import("@/pages/admin/AdminAssetEditor"));
const AdminAssetContent = lazy(() => import("@/pages/admin/AdminAssetContent"));
const AdminQuestions = lazy(() => import("@/pages/admin/AdminQuestions"));
const AdminRounds = lazy(() => import("@/pages/admin/AdminRounds"));
const AdminPayments = lazy(() => import("@/pages/admin/AdminPayments"));
const AdminWithdrawals = lazy(() => import("@/pages/admin/AdminWithdrawals"));
const AdminPayouts = lazy(() => import("@/pages/admin/AdminPayouts"));
const AdminFundIntelligence = lazy(() => import("@/pages/admin/AdminFundIntelligence"));
const AdminFundingAccounts = lazy(() => import("@/pages/admin/AdminFundingAccounts"));
const AdminLedger = lazy(() => import("@/pages/admin/AdminLedger"));
const AdminContracts = lazy(() => import("@/pages/admin/AdminContracts"));
const AdminDocuments = lazy(() => import("@/pages/admin/AdminDocuments"));
const AdminReports = lazy(() => import("@/pages/admin/AdminReports"));
const AdminSettings = lazy(() => import("@/pages/admin/AdminSettings"));
const AdminSystemHealth = lazy(() => import("@/pages/admin/AdminSystemHealth"));
const AdminAuditLog = lazy(() => import("@/pages/admin/AdminAuditLog"));
const AdminBankTransactions = lazy(() => import("@/pages/admin/AdminBankTransactions"));
const AdminPayoutExport = lazy(() => import("@/pages/admin/AdminPayoutExport"));
const AdminOperations = lazy(() => import("@/pages/admin/AdminOperations"));
const AdminSOP = lazy(() => import("@/pages/admin/AdminSOP"));
const AdminUnitRegistry = lazy(() => import("@/pages/admin/AdminUnitRegistry"));
const AdminCertificates = lazy(() => import("@/pages/admin/AdminCertificates"));
const InvestorUnits = lazy(() => import("@/pages/investor/InvestorUnits"));
const InvestorCertificates = lazy(() => import("@/pages/investor/InvestorCertificates"));
const InvestorJourney = lazy(() => import("@/pages/investor/InvestorJourney"));
const CertificateVerifyPage = lazy(() => import("@/pages/CertificateVerifyPage"));

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || '';
export const API = `${BACKEND_URL}/api`;

import { runtime } from '@/runtime';
const _runtimeBootPromise = Promise.race([
  runtime.capabilities.refresh().catch(() => null),
  new Promise((res) => setTimeout(res, 1500)),
]);
export const runtimeReady = _runtimeBootPromise;

const AuthContext = createContext(null);
export const useAuth = () => useContext(AuthContext);

const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  const checkAuth = useCallback(async () => {
    try {
      const response = await axios.get(`${API}/auth/me`, { withCredentials: true });
      setUser(response.data);
    } catch (error) {
      setUser(null);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { checkAuth(); }, [checkAuth]);

  const login = async (email, password) => {
    const response = await axios.post(
      `${API}/auth/login`,
      { email, password, device_fingerprint: getDeviceFingerprint() },
      { withCredentials: true }
    );
    if (response.data?.requires_2fa) {
      const err = new Error('TwoFactorRequired');
      err.requires_2fa = true;
      err.challenge_token = response.data.challenge_token;
      err.method = response.data.method || 'totp';
      err.ttl_seconds = response.data.ttl_seconds;
      err.email = email;
      throw err;
    }
    setUser(response.data);
    return response.data;
  };

  const logout = async () => {
    try {
      await axios.post(`${API}/auth/logout`, {}, { withCredentials: true });
    } catch (error) { /* ignore */ }
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, setUser, loading, login, logout, checkAuth }}>
      {children}
    </AuthContext.Provider>
  );
};

const ProtectedRoute = ({ children, allowedRoles }) => {
  const { user, loading } = useAuth();
  const location = useLocation();

  if (loading) {
    return (
      <div className="min-h-screen bg-background flex flex-col items-center justify-center gap-4">
        <div className="w-10 h-10 border-2 border-border border-t-[#2E5D4F] rounded-full animate-spin" />
        <p className="text-sm text-muted-foreground">Перевіряємо сесію…</p>
      </div>
    );
  }

  if (!user) {
    if (location.pathname.startsWith('/admin')) {
      return <Navigate to="/admin/login" state={{ from: location }} replace />;
    }
    return <Navigate to="/auth" state={{ from: location }} replace />;
  }

  if (allowedRoles && !allowedRoles.includes(user.role)) {
    const dashboardRoutes = {
      client: '/investor/dashboard',
      investor: '/investor/dashboard',
      admin: '/admin/dashboard',
    };
    return <Navigate to={dashboardRoutes[user.role] || '/investor/dashboard'} replace />;
  }

  return children;
};

const LoadingFallback = () => (
  <div className="min-h-screen bg-background flex flex-col items-center justify-center gap-4" data-testid="route-loading">
    <div className="w-10 h-10 border-2 border-border border-t-[#2E5D4F] rounded-full animate-spin" />
    <p className="text-sm text-muted-foreground">Завантаження…</p>
  </div>
);

function AppRouter() {
  return (
    <Suspense fallback={<LoadingFallback />}>
      <Routes>
        <Route path="/" element={<LandingPage />} />
        <Route path="/objects/:id" element={<PublicAssetDetail />} />
        <Route path="/legal" element={<LegalIndexPage />} />
        <Route path="/legal/:slug" element={<LegalDocPage />} />
        <Route path="/certificates/verify" element={<CertificateVerifyPage />} />
        <Route path="/certificates/verify/:code" element={<CertificateVerifyPage />} />

        <Route path="/auth" element={<UnifiedAuthPage />} />
        <Route path="/login" element={<Navigate to="/auth" replace />} />
        <Route path="/register" element={<Navigate to="/auth?mode=register" replace />} />
        <Route path="/client/auth" element={<Navigate to="/auth" replace />} />
        <Route path="/builder/auth" element={<Navigate to="/auth" replace />} />
        <Route path="/auth/client" element={<Navigate to="/auth" replace />} />
        <Route path="/auth/builder" element={<Navigate to="/auth" replace />} />
        <Route path="/admin/login" element={<AdminLoginPage />} />

        <Route path="/two-factor-challenge" element={<TwoFactorChallengePage />} />
        <Route path="/account/2fa/setup" element={<ProtectedRoute><TwoFactorSetupPage /></ProtectedRoute>} />
        <Route path="/account/2fa/recovery" element={<ProtectedRoute><TwoFactorRecoveryPage /></ProtectedRoute>} />
        <Route path="/account/2fa" element={<Navigate to="/account/2fa/recovery" replace />} />

        {/* Investor cabinet */}
        <Route
          path="/investor"
          element={
            <ProtectedRoute allowedRoles={['client', 'investor', 'admin']}>
              <InvestorLayout />
            </ProtectedRoute>
          }
        >
          <Route path="dashboard" element={<InvestorDashboard />} />
          <Route path="portfolio" element={<InvestorPortfolio />} />
          <Route path="opportunities" element={<InvestorOpportunities />} />
          <Route path="assets" element={<Navigate to="/investor/opportunities" replace />} />
          <Route path="assets/:assetId" element={<InvestorAssetDetail />} />
          <Route path="payments" element={<InvestorPayments />} />
          <Route path="wallet" element={<InvestorWallet />} />
          <Route path="income" element={<InvestorIncome />} />
          <Route path="analytics" element={<InvestorAnalytics />} />
          <Route path="contracts" element={<InvestorContracts />} />
          <Route path="documents" element={<InvestorDocuments />} />
          <Route path="profile" element={<InvestorProfile />} />
          <Route path="notifications" element={<InvestorNotifications />} />
          <Route path="notification-preferences" element={<InvestorNotificationPreferences />} />
          <Route path="marketplace" element={<InvestorMarketplace />} />
          <Route path="units" element={<InvestorUnits />} />
          <Route path="certificates" element={<InvestorCertificates />} />
          <Route path="journey" element={<InvestorJourney />} />
          <Route index element={<Navigate to="/investor/dashboard" replace />} />
        </Route>

        {/* Legacy /client/* → /investor/* */}
        <Route path="/client" element={<Navigate to="/investor/dashboard" replace />} />
        <Route path="/client/dashboard" element={<Navigate to="/investor/dashboard" replace />} />
        <Route path="/client/projects" element={<Navigate to="/investor/portfolio" replace />} />
        <Route path="/client/documents" element={<Navigate to="/investor/documents" replace />} />
        <Route path="/client/profile" element={<Navigate to="/investor/profile" replace />} />
        <Route path="/client/*" element={<Navigate to="/investor/dashboard" replace />} />

        {/* Old roles → landing */}
        <Route path="/developer/*" element={<Navigate to="/" replace />} />
        <Route path="/tester/*" element={<Navigate to="/" replace />} />
        <Route path="/provider/*" element={<Navigate to="/" replace />} />
        <Route path="/dev/*" element={<Navigate to="/" replace />} />

        {/* Admin */}
        <Route
          path="/admin"
          element={
            <ProtectedRoute allowedRoles={['admin']}>
              <AdminLayout />
            </ProtectedRoute>
          }
        >
          <Route path="dashboard" element={<AdminDashboard />} />
          <Route path="operations" element={<AdminOperations />} />
          <Route path="registry" element={<AdminUnitRegistry />} />
          <Route path="certificates" element={<AdminCertificates />} />
          <Route path="sop" element={<AdminSOP />} />
          <Route path="investors" element={<AdminInvestors />} />
          <Route path="intents" element={<AdminIntents />} />
          <Route path="kyc" element={<AdminKyc />} />
          <Route path="assets" element={<AdminAssets />} />
          <Route path="assets/new" element={<AdminAssetEditor />} />
          <Route path="assets/:assetId" element={<AdminAssetEditor />} />
          <Route path="assets/:assetId/content" element={<AdminAssetContent />} />
          <Route path="questions" element={<AdminQuestions />} />
          <Route path="rounds" element={<AdminRounds />} />
          <Route path="payments" element={<AdminPayments />} />
          <Route path="withdrawals" element={<AdminWithdrawals />} />
          <Route path="payouts" element={<AdminPayouts />} />
          <Route path="fund" element={<AdminFundIntelligence />} />
          <Route path="funding-accounts" element={<AdminFundingAccounts />} />
          <Route path="ledger" element={<AdminLedger />} />
          <Route path="contracts" element={<AdminContracts />} />
          <Route path="documents" element={<AdminDocuments />} />
          <Route path="reports" element={<AdminReports />} />
          <Route path="settings" element={<AdminSettings />} />
          <Route path="system-health" element={<AdminSystemHealth />} />
          <Route path="audit-log" element={<AdminAuditLog />} />
          <Route path="bank-transactions" element={<AdminBankTransactions />} />
          <Route path="payout-export" element={<AdminPayoutExport />} />
          <Route path="secondary-market" element={<AdminSecondaryMarket />} />
          {/* legacy admin paths */}
          <Route path="workflow" element={<Navigate to="/admin/assets" replace />} />
          <Route path="finance" element={<Navigate to="/admin/payments" replace />} />
          <Route path="team" element={<Navigate to="/admin/investors" replace />} />
          <Route path="system" element={<Navigate to="/admin/settings" replace />} />
          <Route path="profile" element={<Navigate to="/admin/settings" replace />} />
          <Route path="qa" element={<Navigate to="/admin/dashboard" replace />} />
          <Route path="validation" element={<Navigate to="/admin/dashboard" replace />} />
          <Route path="leads" element={<Navigate to="/admin/investors" replace />} />
          <Route path="marketing" element={<Navigate to="/admin/dashboard" replace />} />
          <Route path="portfolio" element={<Navigate to="/admin/assets" replace />} />
          <Route path="legal-settings" element={<Navigate to="/admin/settings" replace />} />
          <Route index element={<Navigate to="/admin/dashboard" replace />} />
        </Route>

        <Route path="/dashboard" element={<Navigate to="/investor/dashboard" replace />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </Suspense>
  );
}

function CookieBannerMount() {
  const { theme } = useTheme();
  const location = useLocation();
  // Inside the authenticated cabinets the left sidebar holds the logout/profile
  // control at the bottom-left — offset the banner so it never overlaps it.
  const inApp = /^\/(investor|admin)(\/|$)/.test(location.pathname);
  return <CookieBanner tone={theme === 'light' ? 'light' : 'dark'} inApp={inApp} />;
}

function App() {
  const googleClientId = process.env.REACT_APP_GOOGLE_CLIENT_ID || "";
  return (
    <div className="App">
      <GoogleOAuthProvider clientId={googleClientId}>
        <BrowserRouter basename={process.env.PUBLIC_URL || ""}>
          <ThemeProvider>
            <LanguageProvider>
              <LegalSettingsProvider>
                <AuthProvider>
                  <ToastProvider>
                    <ToastBridgeMount />
                    <ContactModalProvider>
                      <RootErrorBoundary>
                        <AppRouter />
                      </RootErrorBoundary>
                    </ContactModalProvider>
                    <CookieBannerMount />
                    <EvaCompanion />
                  </ToastProvider>
                </AuthProvider>
              </LegalSettingsProvider>
            </LanguageProvider>
          </ThemeProvider>
        </BrowserRouter>
      </GoogleOAuthProvider>
    </div>
  );
}

export default App;
