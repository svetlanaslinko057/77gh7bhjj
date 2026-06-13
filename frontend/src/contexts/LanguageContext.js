/**
 * LanguageContext — Lumen forces Ukrainian as the only language at this stage.
 * EN is retained as a fallback bucket in the dictionary but no UI toggle is
 * exposed. Once UK is locked in we'll re-introduce additional locales.
 */
import { createContext, useContext, useEffect, useMemo, useCallback } from 'react';
import { DICTIONARY, LANGS } from '@/i18n/dictionary';

const LanguageContext = createContext({
  lang: 'uk',
  setLang: () => {},
  t: (_k, fallback) => fallback,
  tByEn: (en) => en,
  languages: LANGS,
});

export { LanguageContext };
export const useLang = () => useContext(LanguageContext);

const norm = (s) => (typeof s === 'string' ? s.trim().replace(/\s+/g, ' ') : s);

const buildReverseIndex = () => {
  const out = {};
  const en = DICTIONARY.en || {};
  for (const [key, val] of Object.entries(en)) {
    if (typeof val === 'string') out[norm(val)] = key;
  }
  return out;
};

const REVERSE_EN = buildReverseIndex();

export const LanguageProvider = ({ children }) => {
  const lang = 'uk';

  useEffect(() => {
    try { localStorage.setItem('lumen_lang', 'uk'); } catch (_e) { /* noop */ }
    if (typeof document !== 'undefined') {
      document.documentElement.lang = 'uk';
    }
  }, []);

  const setLang = useCallback(() => { /* locked to uk during Lumen rollout */ }, []);

  const t = useCallback((key, fallback) => {
    const dict = DICTIONARY.uk || {};
    if (Object.prototype.hasOwnProperty.call(dict, key)) return dict[key];
    const en = DICTIONARY.en || {};
    if (Object.prototype.hasOwnProperty.call(en, key)) return en[key];
    return fallback !== undefined ? fallback : key;
  }, []);

  const tByEn = useCallback((englishLiteral) => {
    if (typeof englishLiteral !== 'string' || !englishLiteral) return englishLiteral;
    const key = REVERSE_EN[norm(englishLiteral)];
    if (!key) return englishLiteral;
    const dict = DICTIONARY.uk || {};
    return Object.prototype.hasOwnProperty.call(dict, key) ? dict[key] : englishLiteral;
  }, []);

  const value = useMemo(
    () => ({ lang, setLang, t, tByEn, languages: LANGS }),
    [lang, setLang, t, tByEn]
  );

  return <LanguageContext.Provider value={value}>{children}</LanguageContext.Provider>;
};

export default LanguageProvider;
