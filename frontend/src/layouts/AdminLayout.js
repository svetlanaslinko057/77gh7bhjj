import { Outlet, NavLink, useNavigate, Link } from 'react-router-dom';
import { useAuth } from '@/App';
import { ConnectionStatusBadge } from '@/components/ConnectionStatus';
import NotificationBell from '@/components/NotificationBell';
import ThemeToggle from '@/components/ThemeToggle';
import Logo from '@/components/Logo';
import MobileNav from '@/components/MobileNav';
import {
  LayoutDashboard,
  Users,
  ShieldCheck,
  Building2,
  CircleDollarSign,
  CreditCard,
  FileText,
  FileSignature,
  Inbox,
  BarChart3,
  Settings,
  LogOut,
  MessageCircleQuestion,
  Landmark,
  BookOpen,
  ArrowUpFromLine,
  Coins,
  Gauge,
  HeartPulse,
  ScrollText,
  Banknote,
  FileDown,
  Repeat,
  ArrowLeft,
  Activity,
  BookOpenCheck,
  Boxes,
  Award,
} from 'lucide-react';

/** Lumen admin panel — investment fund operations console. */
const AdminLayout = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = async () => {
    await logout();
    navigate('/');
  };

  return (
    <div className="h-screen overflow-hidden bg-app text-token-primary flex" data-testid="admin-layout">
      <MobileNav role="admin" />
      <aside
        className="app-sidebar w-[244px] flex flex-col sticky top-0 h-screen bg-app-surface app-safe-top"
        style={{ borderRight: '1px solid var(--token-border)' }}
      >
        <div className="px-4 pt-6 pb-4">
          <div className="flex items-center">
            <Logo height={32} className="max-w-full" />
          </div>
          <p className="text-[11px] text-token-muted mt-3 leading-relaxed">Панель фонду · v1</p>
          <div className="mt-2 flex items-center gap-2">
            <ConnectionStatusBadge />
            <NotificationBell />
          </div>
          <Link to="/" data-testid="back-to-site" className="mt-3 inline-flex items-center gap-1.5 text-[12px] font-medium text-token-muted hover:text-token-primary transition">
            <ArrowLeft className="w-3.5 h-3.5" /> На сайт
          </Link>
        </div>

        <nav className="flex-1 p-3 space-y-1 overflow-y-auto" data-testid="admin-sidebar-nav">
          <div className="px-3 py-2 text-token-kicker">Операції</div>
          <NavItem to="/admin/dashboard" icon={<LayoutDashboard className="w-[18px] h-[18px]" />} label="Огляд" testid="nav-dashboard" />
          <NavItem to="/admin/operations" icon={<Activity className="w-[18px] h-[18px]" />} label="Центр операцій" testid="nav-operations" />
          <NavItem to="/admin/fund" icon={<Gauge className="w-[18px] h-[18px]" />} label="Аналітика фонду" testid="nav-fund" />
          <NavItem to="/admin/investors" icon={<Users className="w-[18px] h-[18px]" />} label="Інвестори" testid="nav-investors" />
          <NavItem to="/admin/intents" icon={<Inbox className="w-[18px] h-[18px]" />} label="Заявки" testid="nav-intents" />
          <NavItem to="/admin/kyc" icon={<ShieldCheck className="w-[18px] h-[18px]" />} label="KYC" testid="nav-kyc" />
          <NavItem to="/admin/assets" icon={<Building2 className="w-[18px] h-[18px]" />} label="Активи" testid="nav-assets" />
          <NavItem to="/admin/registry" icon={<Boxes className="w-[18px] h-[18px]" />} label="Реєстр одиниць" testid="nav-registry" />
          <NavItem to="/admin/certificates" icon={<Award className="w-[18px] h-[18px]" />} label="Сертифікати" testid="nav-certificates" />
          <NavItem to="/admin/rounds" icon={<CircleDollarSign className="w-[18px] h-[18px]" />} label="Раунди" testid="nav-rounds" />
          <NavItem to="/admin/questions" icon={<MessageCircleQuestion className="w-[18px] h-[18px]" />} label="Питання (Q&A)" testid="nav-questions" />

          <div className="px-3 py-2 mt-4 text-token-kicker">Фінанси</div>
          <NavItem to="/admin/payments" icon={<CreditCard className="w-[18px] h-[18px]" />} label="Платежі" testid="nav-payments" />
          <NavItem to="/admin/withdrawals" icon={<ArrowUpFromLine className="w-[18px] h-[18px]" />} label="Виводи" testid="nav-withdrawals" />
          <NavItem to="/admin/payouts" icon={<Coins className="w-[18px] h-[18px]" />} label="Виплати доходу" testid="nav-payouts" />
          <NavItem to="/admin/bank-transactions" icon={<Banknote className="w-[18px] h-[18px]" />} label="Банк-транзакції" testid="nav-bank-transactions" />
          <NavItem to="/admin/payout-export" icon={<FileDown className="w-[18px] h-[18px]" />} label="Експорт виплат" testid="nav-payout-export" />
          <NavItem to="/admin/secondary-market" icon={<Repeat className="w-[18px] h-[18px]" />} label="Вторинний ринок" testid="nav-secondary-market" />
          <NavItem to="/admin/funding-accounts" icon={<Landmark className="w-[18px] h-[18px]" />} label="Реквізити" testid="nav-funding-accounts" />
          <NavItem to="/admin/ledger" icon={<BookOpen className="w-[18px] h-[18px]" />} label="Реєстр (Ledger)" testid="nav-ledger" />
          <NavItem to="/admin/contracts" icon={<FileSignature className="w-[18px] h-[18px]" />} label="Договори" testid="nav-contracts" />
          <NavItem to="/admin/documents" icon={<FileText className="w-[18px] h-[18px]" />} label="Документи" testid="nav-documents" />
          <NavItem to="/admin/reports" icon={<BarChart3 className="w-[18px] h-[18px]" />} label="Звіти" testid="nav-reports" />

          <div className="px-3 py-2 mt-4 text-token-kicker">Система</div>
          <NavItem to="/admin/sop" icon={<BookOpenCheck className="w-[18px] h-[18px]" />} label="Регламенти (SOP)" testid="nav-sop" />
          <NavItem to="/admin/system-health" icon={<HeartPulse className="w-[18px] h-[18px]" />} label="System Health" testid="nav-system-health" />
          <NavItem to="/admin/audit-log" icon={<ScrollText className="w-[18px] h-[18px]" />} label="Audit Log" testid="nav-audit-log" />
          <NavItem to="/admin/settings" icon={<Settings className="w-[18px] h-[18px]" />} label="Налаштування" testid="nav-settings" />
        </nav>

        <div className="p-3" style={{ borderTop: '1px solid var(--token-border)' }}>
          <div className="mb-2 flex items-center justify-between gap-2">
            <span className="text-[10px] uppercase tracking-wider text-token-muted font-semibold">Тема</span>
            <ThemeToggle />
          </div>
          <div
            className="flex items-center gap-3 p-3 rounded-xl"
            style={{ background: 'var(--token-surface-elevated)', border: '1px solid var(--token-border)' }}
          >
            <div
              className="w-9 h-9 rounded-lg flex items-center justify-center font-semibold text-sm"
              style={{
                background: 'var(--token-success-tint)',
                color: 'var(--token-primary)',
                border: '1px solid var(--token-success-border)',
              }}
            >
              {user?.name?.[0]?.toUpperCase() || 'A'}
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium truncate text-token-primary">{user?.name || 'Адмін'}</p>
              <p className="text-[11px] text-token-muted capitalize">{user?.role || 'admin'}</p>
            </div>
            <button
              onClick={handleLogout}
              className="p-2 rounded-lg transition-colors text-token-muted hover:text-token-primary"
              style={{ background: 'transparent' }}
              onMouseEnter={(e) => { e.currentTarget.style.background = 'var(--token-border)'; }}
              onMouseLeave={(e) => { e.currentTarget.style.background = 'transparent'; }}
              data-testid="admin-logout-btn"
              title="Вийти"
            >
              <LogOut className="w-4 h-4" />
            </button>
          </div>
        </div>
      </aside>

      <main className="app-main flex-1 min-h-0 overflow-y-auto bg-app">
        <Outlet />
      </main>
    </div>
  );
};

const NavItem = ({ to, icon, label, badge, testid }) => (
  <NavLink
    to={to}
    data-testid={testid}
    className={({ isActive }) =>
      `flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition-all ${
        isActive ? 'nav-item-active' : 'nav-item-idle'
      }`
    }
  >
    {icon}
    <span className="flex-1">{label}</span>
    {badge && <span className="status-badge badge-danger">{badge}</span>}
  </NavLink>
);

export default AdminLayout;
