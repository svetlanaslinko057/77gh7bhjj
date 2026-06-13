import { useState, useEffect } from 'react';
import { useNavigate, useSearchParams, useLocation, Link } from 'react-router-dom';
import { useAuth } from '@/App';
import { runtime } from '@/runtime';
import { Eye, EyeOff, Loader2, ArrowLeft, ShieldCheck, Sparkles, Flame } from 'lucide-react';
import { GoogleLogin } from '@react-oauth/google';
import Logo from '@/components/Logo';
import ThemeToggle from '@/components/ThemeToggle';
import ForgotPasswordModal from '@/components/ForgotPasswordModal';

const GOOGLE_CLIENT_ID = process.env.REACT_APP_GOOGLE_CLIENT_ID || '';

/**
 * Lumen — sign-in / sign-up for investors.
 *
 * Single funnel, single role (investor). The legacy builder/developer/tester
 * paths were removed when EVA-X became Lumen. Quick-login chips are kept for
 * dev/demo access (admin and demo investor) until KYC ramps up.
 */
export default function UnifiedAuthPage() {
  const navigate = useNavigate();
  const location = useLocation();
  const { login, checkAuth } = useAuth();
  const [searchParams] = useSearchParams();

  const initialMode = (() => {
    const m = (searchParams.get('mode') || '').toLowerCase();
    if (m === 'signin' || m === 'register') return m;
    return 'signin';
  })();

  const [mode, setMode] = useState(initialMode);
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [demoLoadingRole, setDemoLoadingRole] = useState(null);
  const [error, setError] = useState('');
  const [forgotOpen, setForgotOpen] = useState(false);
  const [agreed, setAgreed] = useState(false);
  const [demoEnabled, setDemoEnabled] = useState(true);
  const [form, setForm] = useState({ email: '', password: '', name: '' });

  useEffect(() => {
    // Hide demo chips when demo/quick auth is disabled (production flag).
    runtime.get('/api/auth/config')
      .then((r) => {
        const data = r?.data || r;
        if (data && typeof data.demo_auth_enabled === 'boolean') setDemoEnabled(data.demo_auth_enabled);
      })
      .catch(() => { /* keep default (enabled) on failure */ });
  }, []);

  useEffect(() => {
    document.title = mode === 'register'
      ? 'Lumen · Реєстрація інвестора'
      : 'Lumen · Вхід у кабінет';
  }, [mode]);

  const updateField = (k, v) => setForm((p) => ({ ...p, [k]: v }));

  const submit = async (e) => {
    e?.preventDefault();
    setLoading(true);
    setError('');
    try {
      if (mode === 'register') {
        if (!agreed) {
          setError('Щоб продовжити, прийміть Публічну оферту, Політику конфіденційності та Розкриття ризиків.');
          setLoading(false);
          return;
        }
        await runtime.post('/api/auth/register', {
          email: form.email.trim(),
          password: form.password,
          name: form.name.trim() || form.email.split('@')[0],
          role: 'client',
        });
      }
      await login(form.email.trim(), form.password);
      navigate('/investor/dashboard');
    } catch (err) {
      if (err?.requires_2fa) {
        navigate('/two-factor-challenge', {
          state: {
            challenge_token: err.challenge_token,
            email: err.email,
            method: err.method,
            ttl: err.ttl_seconds,
            from: '/investor/dashboard',
          },
        });
        return;
      }
      const msg = err?.response?.data?.detail
        || err?.message
        || 'Не вдалось увійти. Перевірте дані та спробуйте ще раз.';
      setError(typeof msg === 'string' ? msg : 'Помилка авторизації');
    } finally {
      setLoading(false);
    }
  };

  const demoLogin = async (kind) => {
    setError('');
    setDemoLoadingRole(kind);
    try {
      const email = kind === 'admin' ? 'admin@atlas.dev' : 'client@atlas.dev';
      const r = await runtime.post('/api/auth/quick', { email });
      const data = r?.data || r;
      if (data?.user || data?.user_id || data?.session_token) {
        await checkAuth();
        navigate(kind === 'admin' ? '/admin/dashboard' : '/investor/dashboard');
      } else {
        setError('Демо-вхід тимчасово недоступний.');
      }
    } catch (_e) {
      setError('Демо-вхід тимчасово недоступний.');
    } finally {
      setDemoLoadingRole(null);
    }
  };

  const handleGoogle = async (credentialResponse) => {
    setLoading(true);
    setError('');
    try {
      const r = await runtime.post('/api/auth/google', {
        credential: credentialResponse.credential,
        role: 'client',
      });
      const data = r?.data || r;
      if (data) {
        await checkAuth();
        navigate('/investor/dashboard');
      }
    } catch (_e) {
      setError('Не вдалось увійти через Google. Спробуйте email + пароль.');
    } finally {
      setLoading(false);
    }
  };

  const isRegister = mode === 'register';

  return (
    <div className="min-h-screen bg-background text-foreground flex flex-col" data-testid="auth-page">
      {/* Header */}
      <header className="px-6 lg:px-10 py-5 flex items-center justify-between">
        <Link to="/" className="flex items-center gap-2" data-testid="auth-back-home">
          <ArrowLeft className="w-4 h-4 text-muted-foreground" />
          <Logo height={36} />
        </Link>
        <ThemeToggle />
      </header>

      <div className="flex-1 grid lg:grid-cols-2 gap-0">
        {/* Left visual */}
        <aside className="relative hidden lg:flex items-center justify-center overflow-hidden" style={{
          background: 'linear-gradient(160deg, #0E2620 0%, #173B32 50%, #0A1B17 100%)',
        }}>
          <div aria-hidden className="absolute inset-0" style={{
            background: 'radial-gradient(700px 500px at 30% 25%, rgba(229,201,138,0.18), transparent 65%), radial-gradient(600px 400px at 85% 75%, rgba(212,182,117,0.12), transparent 70%)',
          }} />
          <div className="relative z-10 p-12 max-w-md text-[#F4ECDA]">
            <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full border border-white/10 bg-white/5 text-xs uppercase tracking-widest">
              <Flame className="w-3.5 h-3.5 text-[#D4B675]" /> Lumen Capital
            </div>
            <h2 className="mt-6 text-4xl font-bold tracking-tight leading-tight">
              Інвестуйте в реальні активи з прозорою структурою.
            </h2>
            <p className="mt-4 text-[#F4ECDA]/80 leading-relaxed">
              Кожен об'єкт оформлюється через окрему SPV-юр­особу. Ваша частка — це підписаний договір участі з реальними правами на потік доходу.
            </p>
            <ul className="mt-8 space-y-3 text-sm">
              <Bullet text="SPV-структура під кожен актив" />
              <Bullet text="Юридичні договори участі" />
              <Bullet text="Щомісячні прозорі звіти" />
              <Bullet text="Виплати на ваші реквізити" />
            </ul>
            <div className="mt-10 p-4 rounded-2xl border border-white/10 bg-white/5">
              <p className="text-[11px] uppercase tracking-widest text-[#D4B675]">середня доходність</p>
              <p className="mt-1 text-3xl font-bold">17,4% — 22%</p>
              <p className="mt-1 text-xs text-[#F4ECDA]/70">за останні 12 місяців по реалізованих активах</p>
            </div>
          </div>
        </aside>

        {/* Right form */}
        <main className="flex items-center justify-center px-6 py-10 lg:py-16">
          <div className="w-full max-w-md">
            <h1 className="text-3xl font-bold tracking-tight" data-testid="auth-title">
              {isRegister ? 'Створіть кабінет інвестора' : 'Увійдіть у кабінет'}
            </h1>
            <p className="mt-2 text-muted-foreground text-sm">
              {isRegister
                ? 'Безкоштовна реєстрація. KYC можна пройти пізніше.'
                : 'Раді бачити знову. Введіть свої дані.'}
            </p>

            {/* Demo chips */}
            {demoEnabled && (
              <div className="mt-6 flex flex-wrap gap-2" data-testid="auth-demo-chips">
                <DemoChip
                  label="Демо-кабінет інвестора"
                  onClick={() => demoLogin('investor')}
                  loading={demoLoadingRole === 'investor'}
                  testid="demo-investor"
                />
                <DemoChip
                  label="Демо-адмін"
                  onClick={() => demoLogin('admin')}
                  loading={demoLoadingRole === 'admin'}
                  testid="demo-admin"
                  muted
                />
              </div>
            )}

            <form onSubmit={submit} className="mt-6 space-y-3" data-testid="auth-form">
              {isRegister && (
                <Field
                  label="Ваше ім'я"
                  value={form.name}
                  onChange={(v) => updateField('name', v)}
                  placeholder="Іван Петренко"
                  testid="name-input"
                />
              )}
              <Field
                label="Email"
                type="email"
                value={form.email}
                onChange={(v) => updateField('email', v)}
                placeholder="you@example.com"
                required
                testid="email-input"
              />
              <Field
                label="Пароль"
                type={showPassword ? 'text' : 'password'}
                value={form.password}
                onChange={(v) => updateField('password', v)}
                placeholder="мінімум 8 символів"
                required
                testid="password-input"
                suffix={
                  <button
                    type="button"
                    onClick={() => setShowPassword((p) => !p)}
                    className="text-muted-foreground hover:text-foreground transition"
                    aria-label="Показати або сховати пароль"
                  >
                    {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                  </button>
                }
              />

              {error && (
                <div className="text-sm text-red-500 bg-red-500/10 border border-red-500/20 rounded-xl px-3 py-2">
                  {error}
                </div>
              )}

              {!isRegister && (
                <div className="flex justify-end">
                  <button type="button" onClick={() => setForgotOpen(true)} className="text-xs text-[#2E5D4F] hover:underline">
                    Забули пароль?
                  </button>
                </div>
              )}

              {isRegister && (
                <label className="flex items-start gap-2.5 text-xs text-muted-foreground leading-relaxed cursor-pointer" data-testid="auth-consent">
                  <input
                    type="checkbox"
                    checked={agreed}
                    onChange={(e) => setAgreed(e.target.checked)}
                    className="mt-0.5 w-4 h-4 rounded border-border accent-[#2E5D4F] shrink-0"
                    data-testid="auth-consent-checkbox"
                  />
                  <span>
                    Я прийняв(-ла){' '}
                    <Link to="/legal/offer" target="_blank" className="text-[#2E5D4F] hover:underline">Публічну оферту</Link>,{' '}
                    <Link to="/legal/privacy" target="_blank" className="text-[#2E5D4F] hover:underline">Політику конфіденційності</Link>{' '}
                    та{' '}
                    <Link to="/legal/risk" target="_blank" className="text-[#2E5D4F] hover:underline">Розкриття ризиків</Link>.
                  </span>
                </label>
              )}

              <button
                type="submit"
                disabled={loading || (isRegister && !agreed)}
                className="w-full h-12 rounded-full bg-foreground text-background font-medium hover:opacity-90 transition disabled:opacity-50 flex items-center justify-center gap-2"
                data-testid="auth-submit"
              >
                {loading && <Loader2 className="w-4 h-4 animate-spin" />}
                {isRegister ? 'Створити кабінет' : 'Увійти'}
              </button>
            </form>

            {GOOGLE_CLIENT_ID && (
              <div className="mt-5">
                <div className="flex items-center gap-3 text-xs text-muted-foreground my-3">
                  <div className="flex-1 h-px bg-border" />
                  <span>або</span>
                  <div className="flex-1 h-px bg-border" />
                </div>
                <div className="flex justify-center">
                  <GoogleLogin
                    onSuccess={handleGoogle}
                    onError={() => setError('Google вхід не вдався.')}
                    text={isRegister ? 'signup_with' : 'signin_with'}
                    locale="uk"
                    width="320"
                  />
                </div>
              </div>
            )}

            <p className="mt-8 text-sm text-muted-foreground text-center">
              {isRegister ? 'Вже маєте кабінет? ' : 'Новий тут? '}
              <button
                onClick={() => setMode(isRegister ? 'signin' : 'register')}
                className="text-[#2E5D4F] hover:underline font-medium"
                data-testid="auth-mode-toggle"
              >
                {isRegister ? 'Увійти' : 'Створити кабінет'}
              </button>
            </p>

            <div className="mt-8 pt-6 border-t border-border flex items-center gap-2 text-xs text-muted-foreground">
              <ShieldCheck className="w-4 h-4 text-[#2E5D4F]" />
              <span>Захищене з'єднання. Ваші дані шифруються відповідно до GDPR і ЗУ «Про захист персональних даних».</span>
            </div>
          </div>
        </main>
      </div>

      <ForgotPasswordModal open={forgotOpen} onClose={() => setForgotOpen(false)} />
    </div>
  );
}

const Bullet = ({ text }) => (
  <li className="flex items-start gap-2">
    <Sparkles className="w-4 h-4 mt-0.5 text-[#D4B675] shrink-0" />
    <span>{text}</span>
  </li>
);

const Field = ({ label, value, onChange, type = 'text', placeholder, required, testid, suffix }) => (
  <label className="block">
    <span className="text-[11px] uppercase tracking-widest text-muted-foreground">{label}</span>
    <div className="mt-1 relative">
      <input
        type={type}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder={placeholder}
        required={required}
        data-testid={testid}
        className="w-full h-12 px-4 pr-10 rounded-xl border border-border bg-background focus:outline-none focus:border-[#2E5D4F] focus:ring-2 focus:ring-[#2E5D4F]/15 transition"
      />
      {suffix && <div className="absolute right-3 top-1/2 -translate-y-1/2">{suffix}</div>}
    </div>
  </label>
);

const DemoChip = ({ label, onClick, loading, testid, muted }) => (
  <button
    type="button"
    onClick={onClick}
    disabled={loading}
    data-testid={testid}
    className={`inline-flex items-center gap-2 px-4 h-9 rounded-full text-sm font-medium border transition disabled:opacity-50 ${
      muted
        ? 'border-border bg-card text-muted-foreground hover:text-foreground'
        : 'border-[#2E5D4F]/30 bg-[#2E5D4F]/10 text-[#2E5D4F] hover:bg-[#2E5D4F]/15'
    }`}
  >
    {loading && <Loader2 className="w-3.5 h-3.5 animate-spin" />}
    {label}
  </button>
);
