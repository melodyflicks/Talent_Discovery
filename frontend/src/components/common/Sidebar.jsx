import { useState, useRef, useEffect } from "react";
import { NavLink, useNavigate, useLocation } from "react-router-dom";
import { useAuth } from "../../context/AuthContext";

const employeeLinks = [
  { to: "/dashboard", label: "Dashboard", icon: "📊" },
  { to: "/profile", label: "My Profile", icon: "👤" },
  { to: "/skills", label: "Skills", icon: "⚡" },
  { to: "/roles", label: "Role Matches", icon: "🎯" },
  { to: "/skill-gaps", label: "Skill Gaps", icon: "📈" },
  { to: "/roadmap", label: "Learning Roadmap", icon: "🗺️" },
  { to: "/career-assistant", label: "Career Assistant", icon: "🤖" },
];

const hrLinks = [
  { to: "/hr", label: "HR Dashboard", icon: "🏢" },
  { to: "/hr/employees", label: "Employees", icon: "👥" },
  { to: "/hr/analytics", label: "Analytics", icon: "📊" },
];

export default function Sidebar() {
  const { user, signOut } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [dropdownOpen, setDropdownOpen] = useState(false);
  const dropRef = useRef(null);

  const isHR = ["hr", "admin"].includes(user?.role);
  const links = isHR ? hrLinks : employeeLinks;

  const initials = user?.full_name
    ? user.full_name.split(" ").map((n) => n[0]).join("").slice(0, 2).toUpperCase()
    : "U";

  useEffect(() => {
    const handler = (e) => {
      if (dropRef.current && !dropRef.current.contains(e.target)) {
        setDropdownOpen(false);
      }
    };
    document.addEventListener("mousedown", handler);
    return () => document.removeEventListener("mousedown", handler);
  }, []);

  const handleLogout = () => {
    signOut();
    navigate("/login");
  };

  return (
    <aside className="sidebar">
      {/* Logo */}
      <div className="sidebar-logo">
        <div className="sidebar-logo-icon">🧠</div>
        <div className="sidebar-title">TalentIQ</div>
        <div className="sidebar-subtitle">AI Employee Intelligence</div>
      </div>

      {/* Navigation */}
      <div className="sidebar-section">
        <div className="sidebar-section-label">Navigation</div>
        {links.map(({ to, label, icon }) => (
          <NavLink
            key={to}
            to={to}
            end={to === "/dashboard" || to === "/hr"}
            className={({ isActive }) =>
              `sidebar-link${isActive || location.pathname === to ? " active" : ""}`
            }
          >
            <span style={{ fontSize: 15 }}>{icon}</span>
            {label}
          </NavLink>
        ))}
      </div>

      {/* User footer */}
      <div className="sidebar-user relative" ref={dropRef}>
        <div
          className="sidebar-avatar"
          style={{ cursor: "pointer" }}
          onClick={() => setDropdownOpen((v) => !v)}
        >
          {initials}
        </div>
        <div style={{ flex: 1, minWidth: 0 }}>
          <div className="sidebar-user-name" style={{ whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis" }}>
            {user?.full_name || user?.email}
          </div>
          <div className="sidebar-user-role">{user?.role}</div>
        </div>
        {dropdownOpen && (
          <div className="dropdown-menu-custom" style={{ bottom: "calc(100% + 6px)", top: "auto" }}>
            <div className="dropdown-item-custom" onClick={() => { setDropdownOpen(false); navigate("/profile"); }}>
              My Profile
            </div>
            <div className="dropdown-divider" />
            <div className="dropdown-item-custom" style={{ color: "var(--danger)" }} onClick={handleLogout}>
              Sign out
            </div>
          </div>
        )}
      </div>
    </aside>
  );
}
