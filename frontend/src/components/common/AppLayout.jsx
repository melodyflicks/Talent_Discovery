import Sidebar from "./Sidebar";
import { useAuth } from "../../context/AuthContext";

export default function AppLayout({ children }) {
  const { user } = useAuth();
  if (!user) return null;

  return (
    <div className="app-shell">
      <Sidebar />
      <div className="main-area">
        <main className="content">{children}</main>
      </div>
    </div>
  );
}
