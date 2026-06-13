import { Outlet, NavLink, useNavigate, Link } from 'react-router-dom';
import { useAuth } from '@/App';
import { ConnectionStatusBadge } from '@/components/ConnectionStatus';
import NotificationBell from '@/components/NotificationBell';
import ThemeToggle from '@/components/ThemeToggle';
import Logo from '@/components/Logo';
import MobileNav from '@/components/MobileNav';
import { LayoutDashboard, Briefcase, Building2, Wallet, FileText, FileSignature, User, Bell, LogOut, PiggyBank, TrendingUp, PieChart, Repeat, ArrowLeft, Boxes, Award, Route as RouteIcon } from 'lucide-react';

const InvestorLayout = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = async () => {
    await logout();
    navigate('/');
  };

  return (
    <div className="h-screen overflow-hidden bg-background text-foreground flex" data-testid="investor-layout">
      <MobileNav role="investor" />
      <aside className="app-sidebar w-[244px] border-r border-border flex flex-col sticky top-0 h-screen bg-card app-safe-top">
        <div className="px-4 pt-6 pb-4">
          <div className="flex items-center">
            <Logo height={32} className="max-w-full" />
          </div>
          <p className="text-[11px] text-muted-foreground mt-3 leading-relaxed">
            Кабінет інвестора
          </p>
          <div className="mt-2 flex items-center gap-2">
            <ConnectionStatusBadge />
            <NotificationBell />
          </div>
          <Link to="/" data-testid="back-to-site" className="mt-3 inline-flex items-center gap-1.5 text-[12px] font-medium text-muted-foreground hover:text-foreground transition">
            <ArrowLeft className="w-3.5 h-3.5" /> На сайт
          </Link>
        </div>

        <nav className="flex-1 p-3 space-y-1 overflow-y-auto" data-testid="investor-sidebar-nav">
          <NavItem to="/investor/dashboard" icon={<LayoutDashboard className="w-[18px] h-[18px]" />} label="Огляд" testid="nav-dashboard" />
          <NavItem to="/investor/portfolio" icon={<Briefcase className="w-[18px] h-[18px]" />} label="Портфель" testid="nav-portfolio" />
          <NavItem to="/investor/units" icon={<Boxes className="w-[18px] h-[18px]" />} label="Мої частки" testid="nav-units" />
          <NavItem to="/investor/certificates" icon={<Award className="w-[18px] h-[18px]" />} label="Сертифікати" testid="nav-certificates" />
          <NavItem to="/investor/journey" icon={<RouteIcon className="w-[18px] h-[18px]" />} label="Шлях інвестицій" testid="nav-journey" />
          <NavItem to="/investor/opportunities" icon={<Building2 className="w-[18px] h-[18px]" />} label="Об'єкти" testid="nav-opportunities" />
          <NavItem to="/investor/marketplace" icon={<Repeat className="w-[18px] h-[18px]" />} label="Вторинний ринок" testid="nav-marketplace" />
          <NavItem to="/investor/payments" icon={<Wallet className="w-[18px] h-[18px]" />} label="Платежі та виплати" testid="nav-payments" />
          <NavItem to="/investor/wallet" icon={<PiggyBank className="w-[18px] h-[18px]" />} label="Гаманець" testid="nav-wallet" />
          <NavItem to="/investor/income" icon={<TrendingUp className="w-[18px] h-[18px]" />} label="Доходи" testid="nav-income" />
          <NavItem to="/investor/analytics" icon={<PieChart className="w-[18px] h-[18px]" />} label="Аналітика" testid="nav-analytics" />
          <NavItem to="/investor/contracts" icon={<FileSignature className="w-[18px] h-[18px]" />} label="Договори" testid="nav-contracts" />
          <NavItem to="/investor/documents" icon={<FileText className="w-[18px] h-[18px]" />} label="Документи" testid="nav-documents" />
          <NavItem to="/investor/notifications" icon={<Bell className="w-[18px] h-[18px]" />} label="Сповіщення" testid="nav-notifications" />
          <NavItem to="/investor/notification-preferences" icon={<Bell className="w-[18px] h-[18px]" />} label="Налаштування сповіщень" testid="nav-notif-prefs" />
          <NavItem to="/investor/profile" icon={<User className="w-[18px] h-[18px]" />} label="Профіль" testid="nav-profile" />
        </nav>

        <div className="p-3 border-t border-border">
          <div className="mb-2 flex items-center justify-between gap-2">
            <span className="text-[10px] uppercase tracking-wider text-muted-foreground font-semibold">Тема</span>
            <ThemeToggle />
          </div>
          <div className="flex items-center gap-3 p-3 rounded-xl bg-muted border border-border">
            <div className="w-9 h-9 rounded-lg bg-signal/10 flex items-center justify-center font-semibold text-sm border border-border">
              {user?.name?.[0]?.toUpperCase() || 'I'}
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium truncate">{user?.name || 'Інвестор'}</p>
              <p className="text-[11px] text-muted-foreground truncate">{user?.email}</p>
            </div>
            <button
              onClick={handleLogout}
              className="p-2 hover:bg-muted rounded-lg transition-colors text-muted-foreground hover:text-foreground"
              data-testid="logout-btn"
              title="Вийти"
            >
              <LogOut className="w-4 h-4" />
            </button>
          </div>
        </div>
      </aside>

      <main className="app-main flex-1 min-h-0 overflow-y-auto bg-background">
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
        isActive
          ? 'bg-signal/10 text-foreground border border-signal/30'
          : 'text-muted-foreground hover:text-foreground hover:bg-muted'
      }`
    }
  >
    {icon}
    <span className="flex-1">{label}</span>
    {badge && <span className="px-2 py-0.5 text-xs bg-signal/15 text-signal rounded-full">{badge}</span>}
  </NavLink>
);

export default InvestorLayout;
