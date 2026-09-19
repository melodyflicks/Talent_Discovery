import { useEffect, useState } from "react";
import PageHeader from "../components/common/PageHeader";
import LoadingSpinner from "../components/common/LoadingSpinner";
import EmptyState from "../components/common/EmptyState";
import { getMyProfile, getSkillGaps, getRecommendations } from "../services/api";

const GAP_STYLES = {
  critical: { bg: "#fef2f2", color: "#991b1b", label: "Critical" },
  high: { bg: "#fef2f2", color: "#dc2626", label: "High" },
  medium: { bg: "#fffbeb", color: "#b45309", label: "Medium" },
  low: { bg: "#ecfdf5", color: "#059669", label: "Low" },
  none: { bg: "#f0f9ff", color: "#0284c7", label: "None" },
};

export default function SkillGap() {
  const [gaps, setGaps] = useState([]);
  const [recs, setRecs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const load = async () => {
      try {
        const profile = await getMyProfile();
        const [g, r] = await Promise.all([
          getSkillGaps(profile.id),
          getRecommendations(profile.id),
        ]);
        setGaps(g);
        setRecs(r);
      } catch {
        setError("Failed to load skill gap data.");
      } finally {
        setLoading(false);
      }
    };
    load();
  }, []);

  if (loading) return <LoadingSpinner message="Analyzing skill gaps…" />;
  if (error) return <div className="error-banner">{error}</div>;

  const criticalCount = gaps.filter((g) => g.gap_level === "critical").length;
  const highCount = gaps.filter((g) => g.gap_level === "high").length;
  const mediumCount = gaps.filter((g) => g.gap_level === "medium").length;

  return (
    <>
      <PageHeader
        title="Skill Gaps"
        subtitle="Identified gaps between your current skills and target role requirements."
      />

      {/* Summary */}
      <div style={{ display: "flex", gap: 12, marginBottom: 24, flexWrap: "wrap" }}>
        {[
          { label: "Critical gaps", count: criticalCount, style: GAP_STYLES.critical },
          { label: "High priority", count: highCount, style: GAP_STYLES.high },
          { label: "Medium priority", count: mediumCount, style: GAP_STYLES.medium },
          { label: "Total gaps", count: gaps.length, style: { bg: "var(--surface)", color: "var(--text-primary)" } },
        ].map(({ label, count, style }) => (
          <div key={label} style={{
            padding: "10px 18px",
            borderRadius: 10,
            background: style.bg,
            color: style.color,
            fontWeight: 700,
            fontSize: 13,
            border: "1px solid rgba(0,0,0,0.06)",
          }}>
            <span style={{ fontSize: 22, fontWeight: 800, display: "block" }}>{count}</span>
            {label}
          </div>
        ))}
      </div>

      {/* Gaps table */}
      <div className="card" style={{ marginBottom: 28 }}>
        <div className="card-header-custom">
          <h3 className="card-title">Gap Analysis</h3>
        </div>
        {gaps.length === 0 ? (
          <EmptyState icon="🎉" title="No skill gaps found" description="Your profile is fully matched to role requirements." />
        ) : (
          <table className="data-table">
            <thead>
              <tr>
                <th>Skill</th>
                <th>Category</th>
                <th>Target role</th>
                <th>Current level</th>
                <th>Required level</th>
                <th style={{ minWidth: 180 }}>Gap progress</th>
                <th>Priority</th>
              </tr>
            </thead>
            <tbody>
              {gaps.map((gap) => {
                const style = GAP_STYLES[gap.gap_level] || GAP_STYLES.medium;
                const gapPct = Math.min(100, (gap.current_proficiency / Math.max(gap.required_proficiency, 1)) * 100);
                return (
                  <tr key={gap.id}>
                    <td style={{ fontWeight: 700 }}>{gap.skill?.name || "—"}</td>
                    <td style={{ color: "var(--text-secondary)", fontSize: 12.5 }}>{gap.skill?.category || "—"}</td>
                    <td style={{ color: "var(--text-secondary)", fontSize: 12.5 }}>{gap.role?.title || "—"}</td>
                    <td style={{ fontWeight: 700 }}>{gap.current_proficiency}/5</td>
                    <td style={{ fontWeight: 700 }}>{gap.required_proficiency}/5</td>
                    <td>
                      <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                        <div style={{ flex: 1, height: 8, background: "var(--border)", borderRadius: 999, overflow: "hidden" }}>
                          <div style={{
                            height: "100%",
                            width: `${gapPct}%`,
                            background: gapPct >= 80 ? "#10b981" : gapPct >= 50 ? "#f59e0b" : "#ef4444",
                            borderRadius: 999,
                            transition: "width 0.6s ease",
                          }} />
                        </div>
                        <span style={{ fontSize: 11.5, fontWeight: 600, color: "var(--text-muted)", whiteSpace: "nowrap" }}>
                          {Math.round(gapPct)}%
                        </span>
                      </div>
                    </td>
                    <td>
                      <span style={{ background: style.bg, color: style.color, padding: "3px 10px", borderRadius: 999, fontSize: 12, fontWeight: 700 }}>
                        {style.label}
                      </span>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        )}
      </div>

      {/* Course Recommendations */}
      {recs.length > 0 && (
        <>
          <h2 style={{ fontSize: 18, fontWeight: 800, marginBottom: 16 }}>📚 Recommended Learning</h2>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(340px, 1fr))", gap: 16 }}>
            {recs.map((rec) => (
              <div key={rec.id} className="card">
                <div className="card-body-custom">
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 10 }}>
                    <div style={{ flex: 1 }}>
                      <div style={{ fontWeight: 700, fontSize: 15, marginBottom: 3 }}>{rec.course?.title || "—"}</div>
                      <div style={{ fontSize: 12.5, color: "var(--text-muted)" }}>
                        {rec.course?.provider} · {rec.course?.difficulty} · {rec.course?.duration}
                      </div>
                    </div>
                    <span style={{
                      padding: "3px 10px",
                      borderRadius: 999,
                      fontSize: 11.5,
                      fontWeight: 700,
                      background: rec.priority === "high" ? "var(--danger-light)" : rec.priority === "medium" ? "var(--warning-light)" : "var(--success-light)",
                      color: rec.priority === "high" ? "var(--danger)" : rec.priority === "medium" ? "#b45309" : "var(--success)",
                      marginLeft: 10,
                      flexShrink: 0,
                    }}>
                      {rec.priority}
                    </span>
                  </div>
                  {rec.course?.skill?.name && (
                    <div style={{ marginBottom: 10 }}>
                      <span className="skill-badge badge-explicit">📌 {rec.course.skill.name}</span>
                    </div>
                  )}
                  {rec.reason && (
                    <p style={{ fontSize: 13, color: "var(--text-secondary)", lineHeight: 1.55, margin: "0 0 14px" }}>
                      {rec.reason}
                    </p>
                  )}
                  {rec.course?.url && (
                    <a
                      href={rec.course.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="btn-primary"
                      style={{ textDecoration: "none", display: "inline-flex", fontSize: 13 }}
                    >
                      Start learning →
                    </a>
                  )}
                </div>
              </div>
            ))}
          </div>
        </>
      )}
    </>
  );
}
