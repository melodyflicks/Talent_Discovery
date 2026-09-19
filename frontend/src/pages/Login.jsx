import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

const DOTS = [
  { size: 80, left: "10%", delay: 0, duration: 18 },
  { size: 120, left: "25%", delay: 4, duration: 22 },
  { size: 60, left: "50%", delay: 2, duration: 16 },
  { size: 100, left: "70%", delay: 6, duration: 20 },
  { size: 50, left: "85%", delay: 1, duration: 14 },
  { size: 90, left: "40%", delay: 8, duration: 24 },
];

const DEMO_ACCOUNTS = [
  { email: "hr1@talent.local", password: "12345", role: "HR Lead" },
  { email: "admin1@talent.local", password: "12345", role: "Admin" },
  { email: "maya.patel@talent.local", password: "EmployeePassword123!", role: "Employee" },
  { email: "alex.chen@talent.local", password: "EmployeePassword123!", role: "Employee" },
];

export default function Login() {
  const [email, setEmail] = useState("hr1@talent.local");
  const [password, setPassword] = useState("12345");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const { signIn } = useAuth();
  const navigate = useNavigate();

  const submit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError("");
    try {
      const person = await signIn({ email, password });
      navigate(["hr", "admin"].includes(person.role) ? "/hr" : "/dashboard");
    } catch (err) {
      const msg = err?.response?.data?.detail || "Invalid email or password.";
      setError(msg);
    } finally {
      setLoading(false);
    }
  };

  const handleDemoClick = (acc) => {
    setEmail(acc.email);
    setPassword(acc.password);
  };

  return (
    <div className="login-page">
      {/* Floating dots */}
      <div className="login-dots">
        {DOTS.map((d, i) => (
          <div
            key={i}
            className="login-dot"
            style={{
              width: d.size,
              height: d.size,
              left: d.left,
              animationDelay: `${d.delay}s`,
              animationDuration: `${d.duration}s`,
              bottom: "-150px",
            }}
          />
        ))}
      </div>

      <div className="login-card">
        {/* Logo */}
        <div className="login-logo">🧠</div>

        <h1 className="login-title">Welcome back</h1>
        <p className="login-subtitle">Sign in to your TalentIQ workspace to continue.</p>

        {error && (
          <div className="error-banner" role="alert">
            {error}
          </div>
        )}

        <form onSubmit={submit}>
          <div style={{ marginBottom: 18 }}>
            <label className="form-label" htmlFor="email">Email address</label>
            <input
              id="email"
              type="email"
              className="form-input"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="you@talent.local"
              required
              autoComplete="email"
            />
          </div>

          <div style={{ marginBottom: 26 }}>
            <label className="form-label" htmlFor="password">Password</label>
            <input
              id="password"
              type="password"
              className="form-input"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Enter your password"
              required
              autoComplete="current-password"
            />
          </div>

          <button
            id="login-submit"
            type="submit"
            className="btn-primary"
            disabled={loading}
            style={{ width: "100%", justifyContent: "center", padding: "12px 20px", fontSize: 15 }}
          >
            {loading ? (
              <>
                <span style={{ width: 16, height: 16, border: "2px solid rgba(255,255,255,0.4)", borderTopColor: "white", borderRadius: "50%", display: "inline-block", animation: "spin 0.7s linear infinite" }} />
                Signing in…
              </>
            ) : "Sign in →"}
          </button>
        </form>

        <div style={{ marginTop: 24, padding: "14px 16px", background: "var(--surface-2)", borderRadius: 10, border: "1px solid var(--border)" }}>
          <p style={{ fontSize: 12, fontWeight: 600, color: "var(--text-muted)", margin: "0 0 8px", textTransform: "uppercase", letterSpacing: "0.05em" }}>
            Demo Quick Login
          </p>
          <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
            {DEMO_ACCOUNTS.map((acc) => (
              <button
                key={acc.email}
                type="button"
                onClick={() => handleDemoClick(acc)}
                style={{
                  background: "none",
                  border: "1px solid var(--border)",
                  borderRadius: 6,
                  padding: "7px 12px",
                  fontSize: 12,
                  textAlign: "left",
                  cursor: "pointer",
                  transition: "var(--transition)",
                  color: "var(--text-secondary)",
                  display: "flex",
                  justifyContent: "space-between",
                }}
              >
                <span style={{ fontFamily: "monospace" }}>{acc.email}</span>
                <span style={{ fontWeight: 600, color: "var(--accent-500)" }}>{acc.role}</span>
              </button>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
