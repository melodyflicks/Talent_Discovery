import { useEffect, useState } from "react";
import PageHeader from "../components/common/PageHeader";
import LoadingSpinner from "../components/common/LoadingSpinner";
import EmptyState from "../components/common/EmptyState";
import { getMyProfile, getEmployeeSkills, getSkillCatalog } from "../services/api";

const TYPE_STYLES = {
  explicit: { bg: "#dbeafe", color: "#1e40af", label: "Verified" },
  inferred: { bg: "#fef3c7", color: "#92400e", label: "Inferred" },
  transferable: { bg: "#d1fae5", color: "#065f46", label: "Transferable" },
};

export default function Skills() {
  const [skills, setSkills] = useState([]);
  const [filter, setFilter] = useState("all");
  const [search, setSearch] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const load = async () => {
      try {
        const profile = await getMyProfile();
        const data = await getEmployeeSkills(profile.id);
        setSkills(data);
      } catch {
        setError("Failed to load skills.");
      } finally {
        setLoading(false);
      }
    };
    load();
  }, []);

  if (loading) return <LoadingSpinner message="Loading skills…" />;
  if (error) return <div className="error-banner">{error}</div>;

  const categories = ["all", ...new Set(skills.map((s) => s.skill?.category).filter(Boolean))];
  const filtered = skills.filter((s) => {
    const matchCat = filter === "all" || s.skill?.category === filter;
    const matchSearch = !search || s.skill?.name?.toLowerCase().includes(search.toLowerCase());
    return matchCat && matchSearch;
  });

  const byType = (type) => skills.filter((s) => s.skill_type === type).length;

  return (
    <>
      <PageHeader
        title="Skills"
        subtitle={`${skills.length} skills identified across your experience and work history.`}
      />

      {/* Summary badges */}
      <div style={{ display: "flex", gap: 10, marginBottom: 24, flexWrap: "wrap" }}>
        {Object.entries(TYPE_STYLES).map(([type, style]) => (
          <div key={type} style={{
            display: "inline-flex",
            alignItems: "center",
            gap: 8,
            padding: "8px 16px",
            borderRadius: 999,
            background: style.bg,
            color: style.color,
            fontWeight: 700,
            fontSize: 13,
            border: `1px solid ${style.color}22`,
          }}>
            <span style={{ fontSize: 18, fontWeight: 800 }}>{byType(type)}</span>
            {style.label}
          </div>
        ))}
      </div>

      {/* Filters */}
      <div style={{ display: "flex", gap: 10, marginBottom: 20, flexWrap: "wrap" }}>
        <input
          className="form-input"
          style={{ maxWidth: 220, padding: "8px 13px" }}
          placeholder="Search skills…"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
        <div style={{ display: "flex", gap: 6, flexWrap: "wrap" }}>
          {categories.map((cat) => (
            <button
              key={cat}
              onClick={() => setFilter(cat)}
              style={{
                padding: "7px 14px",
                borderRadius: 999,
                border: "1px solid var(--border)",
                background: filter === cat ? "var(--brand-700)" : "var(--surface)",
                color: filter === cat ? "white" : "var(--text-secondary)",
                fontWeight: 600,
                fontSize: 12.5,
                cursor: "pointer",
                transition: "var(--transition)",
                textTransform: "capitalize",
              }}
            >
              {cat}
            </button>
          ))}
        </div>
      </div>

      {/* Skills Table */}
      <div className="card">
        {filtered.length === 0 ? (
          <EmptyState icon="⚡" title="No skills found" description="Try adjusting the search or filter." />
        ) : (
          <table className="data-table">
            <thead>
              <tr>
                <th>Skill</th>
                <th>Category</th>
                <th>Type</th>
                <th style={{ minWidth: 160 }}>Proficiency</th>
                <th>Confidence</th>
                <th>Evidence source</th>
              </tr>
            </thead>
            <tbody>
              {filtered.map((es) => {
                const typeStyle = TYPE_STYLES[es.skill_type] || { bg: "#f1f5f9", color: "#64748b", label: es.skill_type };
                return (
                  <tr key={es.id}>
                    <td style={{ fontWeight: 700 }}>{es.skill?.name || "—"}</td>
                    <td>
                      <span style={{ fontSize: 12, color: "var(--text-secondary)", background: "var(--surface-2)", padding: "2px 8px", borderRadius: 999, border: "1px solid var(--border)" }}>
                        {es.skill?.category || "—"}
                      </span>
                    </td>
                    <td>
                      <span style={{ background: typeStyle.bg, color: typeStyle.color, padding: "3px 10px", borderRadius: 999, fontSize: 12, fontWeight: 600 }}>
                        {typeStyle.label}
                      </span>
                    </td>
                    <td>
                      <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
                        <div style={{ flex: 1 }}>
                          <div className="proficiency-bar">
                            <div className="proficiency-fill" style={{ width: `${(es.proficiency / 5) * 100}%` }} />
                          </div>
                        </div>
                        <span style={{ fontSize: 12.5, fontWeight: 700, color: "var(--text-secondary)", whiteSpace: "nowrap" }}>
                          {es.proficiency}/5
                        </span>
                      </div>
                    </td>
                    <td>
                      <span style={{
                        fontSize: 13,
                        fontWeight: 700,
                        color: es.confidence >= 0.8 ? "var(--success)" : es.confidence >= 0.5 ? "#d97706" : "var(--danger)",
                      }}>
                        {Math.round(es.confidence * 100)}%
                      </span>
                    </td>
                    <td style={{ fontSize: 12.5, color: "var(--text-muted)" }}>{es.source}</td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        )}
      </div>
    </>
  );
}
