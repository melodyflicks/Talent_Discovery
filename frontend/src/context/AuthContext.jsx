import { createContext, useContext, useMemo, useState } from "react";
import { login as requestLogin } from "../services/api";

const AuthContext = createContext(null);

const stored = () => {
  try {
    return JSON.parse(sessionStorage.getItem("talent_user"));
  } catch {
    return null;
  }
};

export function AuthProvider({ children }) {
  const [user, setUser] = useState(stored);

  const signIn = async (credentials) => {
    const result = await requestLogin(credentials);
    sessionStorage.setItem("talent_token", result.access_token);
    sessionStorage.setItem("talent_user", JSON.stringify(result.user));
    setUser(result.user);
    return result.user;
  };

  const signOut = () => {
    sessionStorage.removeItem("talent_token");
    sessionStorage.removeItem("talent_user");
    setUser(null);
  };

  const value = useMemo(() => ({ user, signIn, signOut }), [user]);
  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export const useAuth = () => useContext(AuthContext);
