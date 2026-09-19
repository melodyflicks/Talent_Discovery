import { useEffect, useState } from "react";
import PageHeader from "../components/common/PageHeader";
import LoadingSpinner from "../components/common/LoadingSpinner";
import { getMyProfile } from "../services/api";

const SKILL_TYPE_COLORS = {
  explicit: { bg: "#dbeafe", color: "#1e40af" },
  inferred: { bg: "#fef3c7", color: "#92400e" },
  transferable: { bg: "#d1fae5", color: "#065f46" },
};

export default function Profile() {
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    getMyProfile()
      .then(setProfile)
      .catch(() => setError("Failed to load profile."))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <LoadingSpinner message="Loading your profile…" />;
  if (error) return <div className="error-banner">{error}</div>;
  if (!profile) return null;

  const { user, skills = [], external_profiles = [] } = profile;
  const initials = user?.full_name?.split(" ").map((n) => n[0]).join("").slice(0, 2).toUpperCase() || "U";

  const infoItems = [
    ["Department", profile.department],
    ["Designation", profile.designation],
    ["Experience", `${profile.years_of_experience} year${profile.years_of_experience !== 1 ? "s" : ""}`],
    ["Education", profile.education || "—"],
    ["Location", profile.location || "—"],
    ["Employee Code", profile.employee_code],
    ["Email", user?.email],
  ];

  return (
    <>
      <PageHeader title="My Profile" subtitle="Your talent intelligence profile assembled from all available evidence." />

      <div style={{ display: "grid", gridTemplateColumns: "340px 1fr", gap: 20, alignItems: "start" }}>
        {/* Left: profile card */}
        <div>
          <div className="profile-header-card" style={{ marginBottom: 20 }}>
            <div className="profile-avatar-lg">{initials}</div>
            <h2 style={{ margin: "0 0 4px", fontSize: 20, fontWeight: 800 }}>{user?.full_name}</h2>
            <p style={{ margin: "0 0 16px", opacity: 0.7, fontSize: 14 }}>
              {profile.designation} · {profile.department}
            </p>
            <div style={{ fontSize: 12, opacity: 0.65, marginBottom: 4 }}>
              Profile completion · {profile.profile_completion}%
            </div>
            <div className="profile-completion-bar">
              <div className="profile-completion-fill" style={{ width: `${profile.profile_completion}%` }} />
            </div>
          </div>

          <div className="card">
            <div className="card-header-custom"><h3 className="card-title">Contact & Info</h3></div>
            <div className="card-body-custom" style={{ padding: "12px 22px" }}>
              {infoItems.map(([label, value]) => (
                <div key={label} style={{ padding: "10px 0", borderBottom: "1px solid var(--border)", display: "flex", justifyContent: "space-between", gap: 12 }}>
                  <span style={{ fontSize: 12.5, fontWeight: 600, color: "var(--text-muted)" }}>{label}</span>
                  <span style={{ fontSize: 13, color: "var(--text-primary)", textAlign: "right", maxWidth: "60%" }}>{value}</span>
                </div>
              ))}
              <div style={{ paddingTop: 10 }}>
                <span style={{ fontSize: 12.5, fontWeight: 600, color: "var(--text-muted)" }}>Role</span>
                <span style={{
                  float: "right",
                  padding: "2px 10px",
                  borderRadius: 999,
                  fontSize: 12,
                  fontWeight: 700,
                  background: "rgba(22,125,154,0.15)",
                  color: "#1a9ab8"
                }}>{user?.role}</span>
              </div>
            </div>
          </div>
        </div>

        {/* Right: skills and external */}
        <div>
          <div className="card" style={{ marginBottom: 20 }}>
            <div className="card-header-custom">
              <h3 className="card-title">Skills ({skills.length})</h3>
              <div style={{ display: "flex", gap: 8 }}>
                {["explicit", "inferred", "transferable"].map((t) => (
                  <span key={t} className="skill-badge" style={{ background: SKILL_TYPE_COLORS[t]?.bg, color: SKILL_TYPE_COLORS[t]?.color }}>
                    {t}
                  </span>
                ))}
              </div>
            </div>
            {skills.length === 0 ? (
              <div className="card-body-custom" style={{ color: "var(--text-muted)", fontSize: 14 }}>No skills recorded yet.</div>
            ) : (
              <table className="data-table">
                <thead>
                  <tr>
                    <th>Skill</th>
                    <th>Category</th>
                    <th>Type</th>
                    <th>Proficiency</th>
                    <th>Confidence</th>
                    <th>Evidence</th>
                  </tr>
                </thead>
                <tbody>
                  {skills.map((es) => {
                    const colors = SKILL_TYPE_COLORS[es.skill_type] || { bg: "#f1f5f9", color: "#64748b" };
                    return (
                      <tr key={es.id}>
                        <td style={{ fontWeight: 600 }}>{es.skill?.name || "—"}</td>
                        <td style={{ color: "var(--text-secondary)" }}>{es.skill?.category || "—"}</td>
                        <td>
                          <span className="skill-badge" style={{ background: colors.bg, color: colors.color }}>
                            {es.skill_type}
                          </span>
                        </td>
                        <td>
                          <div style={{ minWidth: 100 }}>
                            <div style={{ display: "flex", justifyContent: "space-between", fontSize: 11, marginBottom: 3 }}>
                              <span style={{ color: "var(--text-muted)" }}>Level {es.proficiency}/5</span>
                            </div>
                            <div className="proficiency-bar">
                              <div className="proficiency-fill" style={{ width: `${(es.proficiency / 5) * 100}%` }} />
                            </div>
                          </div>
                        </td>
                        <td style={{ color: "var(--text-secondary)" }}>{Math.round(es.confidence * 100)}%</td>
                        <td style={{ fontSize: 12, color: "var(--text-muted)" }}>{es.source}</td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            )}
          </div>

          {/* External profiles */}
          {external_profiles.length > 0 && (
            <div className="card">
              <div className="card-header-custom"><h3 className="card-title">External Profiles</h3></div>
              <div className="card-body-custom">
                <div style={{ display: "flex", flexWrap: "wrap", gap: 10 }}>
                  {external_profiles.map((ep) => (
                    <a
                      key={ep.id}
                      href={ep.profile_url || "#"}
                      target="_blank"
                      rel="noopener noreferrer"
                      style={{
                        display: "inline-flex",
                        alignItems: "center",
                        gap: 8,
                        padding: "8px 16px",
                        borderRadius: 999,
                        background: "var(--surface-2)",
                        border: "1px solid var(--border)",
                        fontSize: 13,
                        fontWeight: 600,
                        color: "var(--text-primary)",
                        textDecoration: "none",
                        transition: "var(--transition)",
                      }}
                    >
                      🔗 {ep.platform.charAt(0).toUpperCase() + ep.platform.slice(1)}
                      {ep.username && <span style={{ color: "var(--text-muted)", fontWeight: 400 }}>@{ep.username}</span>}
                    </a>
                  ))}
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </>
  );
}
