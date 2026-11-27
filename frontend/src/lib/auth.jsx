import { createContext, useContext, useState } from 'react';

// SEMENTARA: sesi demo di sisi klien. Ganti dengan POST /api/v1/auth/login (JWT) saat backend auth siap.
const AuthCtx = createContext(null);
const KEY = 'ks_session';
const read = () => { try { return JSON.parse(sessionStorage.getItem(KEY)); } catch { return null; } };

export function AuthProvider({ children }) {
  const [user, setUser] = useState(read);
  const login = (u) => { setUser(u); try { sessionStorage.setItem(KEY, JSON.stringify(u)); } catch { /* abaikan */ } };
  const logout = () => { setUser(null); try { sessionStorage.removeItem(KEY); } catch { /* abaikan */ } };
  return <AuthCtx.Provider value={{ user, login, logout }}>{children}</AuthCtx.Provider>;
}
export const useAuth = () => useContext(AuthCtx);
