import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || '';
export const API = `${BACKEND_URL}/api`;

export const lumen = axios.create({
  baseURL: API,
  withCredentials: true,
  timeout: 15000,
});

/** Format UAH with non-breaking space group separators. */
export const formatUAH = (amount) => {
  if (amount === null || amount === undefined || isNaN(amount)) return '—';
  const n = Number(amount);
  return n.toLocaleString('uk-UA', { maximumFractionDigits: 0 }) + ' ₴';
};

export const formatPercent = (n) => {
  if (n === null || n === undefined || isNaN(n)) return '—';
  return `${Number(n).toFixed(1).replace('.', ',')} %`;
};

export const formatDateUk = (iso) => {
  if (!iso) return '—';
  try {
    const d = new Date(iso);
    return d.toLocaleDateString('uk-UA', { day: '2-digit', month: 'short', year: 'numeric' });
  } catch (_e) { return '—'; }
};

/**
 * Extract a human-readable message from a backend error.
 * The API wraps errors in an envelope: {ok, code, message, status, details}.
 * Falls back to FastAPI's raw `detail` and finally to the provided default.
 */
export const lumenError = (e, fallback = 'Сталася помилка') => {
  const data = e?.response?.data;
  if (!data) return fallback;
  if (typeof data.message === 'string' && data.message) return data.message;
  const d = data.detail;
  if (typeof d === 'string' && d) return d;
  if (d && typeof d.message === 'string') return d.message;
  return fallback;
};

/** Structured details payload from the error envelope (e.g. {missing: [...]}). */
export const lumenErrorDetails = (e) => {
  const data = e?.response?.data;
  if (!data) return null;
  if (data.details && typeof data.details === 'object') return data.details;
  if (data.detail && typeof data.detail === 'object') return data.detail;
  return null;
};
