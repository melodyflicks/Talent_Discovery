import { useEffect, useState } from "react";
import PageHeader from "../components/common/PageHeader";
import LoadingSpinner from "../components/common/LoadingSpinner";
import EmptyState from "../components/common/EmptyState";
import { getMyProfile, getEmployeeMatches, generateMatches } from "../services/api";

function MatchCard({ match }) {
  const score = Math.round(match.match_score);
  const cls = score >= 75 ? "match-high" : score >= 50 ? "match-medium" : "match-low";

  return (
    <div className="card" style={{ transition: "var(--transition)" }}>
      <div className="card-body-custom">
        <div style={{ display: "flex", gap: 16, alignItems: "flex-start", marginBottom: 16 }}>
          <div className={`match-ring ${cls}`}>{score}%</div>
          <div style={{ flex: 1 }}>
            <div style={{ fontWeight: 800, fontSize: 17, marginBottom: 2 }}>{match.role?.title || "—"}</div>
            <div style={{ color: "var(--text-secondary)", fontSize: 13 }}>
              {match.role?.department} · {match.role?.level}
            </div>
          </div>
        </div>

        {/* Match bar */}
        <div style={{ marginBottom: 16 }}>
          <div style={{ height: 8, background: "var(--border)", borderRadius: 999, overflow: "hidden" }}>
            <div style={{
              height: "100%",
              width: `${score}%`,
              borderRadius: 999,
              background: score >= 75 ? "linear-gradient(90deg, #10b981, #34d399)" : score >= 50 ? "linear-gradient(90deg, #f59e0b, #fbbf24)" : "linear-gradient(90deg, #ef4444, #f87171)",
              transition: "width 0.8s ease",
            }} />
          </div>
        </div>

        {(match.matching_skills || []).length > 0 && (
          <div style={{ marginBottom: 12 }}>
            <div style={{ fontSize: 11, fontWeight: 700, color: "var(--text-muted)", textTransform: "uppercase", letterSpacing: "0.06em", marginBottom: 6 }}>
              ✅ Matching skills
            </div>
            <div className="tag-list">
              {match.matching_skills.map((s) => (
                <span key={s} className="tag tag-match">{s}</span>
              ))}
            </div>
          </div>
        )}

        {(match.missing_skills || []).length > 0 && (
          <div style={{ marginBottom: 12 }}>
            <div style={{ fontSize: 11, fontWeight: 700, color: "var(--text-muted)", textTransform: "uppercase", letterSpacing: "0.06em", marginBottom: 6 }}>
              ❌ Missing skills
            </div>
            <div className="tag-list">
              {match.missing_skills.map((s) => (
                <span key={s} className="tag tag-missing">{s}</span>
              ))}
            </div>
          </div>
        )}

        {match.explanation && (
          <p style={{ fontSize: 13, color: "var(--text-secondary)", lineHeight: 1.55, margin: 0, paddingTop: 10, borderTop: "1px solid var(--border)" }}>
            {match.explanation}
          </p>
        )}
      </div>
    </div>
  );
}

export default function Roles() {
  const [matches, setMatches] = useState([]);
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    const load = async () => {
      try {
        const p = await getMyProfile();
        setProfile(p);
        const m = await getEmployeeMatches(p.id);
        setMatches(m);
      } catch {
        setError("Failed to load role matches.");
      } finally {
        setLoading(false);
      }
    };
    load();
  }, []);

  const handleGenerate = async () => {
    if (!profile) return;
    setGenerating(true);
    try {
      const m = await generateMatches(profile.id);
      setMatches(m);
    } catch {
      setError("Failed to generate matches.");
    } finally {
      setGenerating(false);
    }
  };

  if (loading) return <LoadingSpinner message="Loading role matches…" />;

  const sorted = [...matches].sort((a, b) => b.match_score - a.match_score);

  return (
    <>
      <PageHeader
        title="Role Matches"
        subtitle="AI-powered internal role compatibility analysis based on your skill profile."
        actions={
          <button className="btn-primary" onClick={handleGenerate} disabled={generating}>
            {generating ? "Refreshing…" : "🔄 Refresh matches"}
          </button>
        }
      />
      {error && <div className="error-banner">{error}</div>}

      {sorted.length === 0 ? (
        <EmptyState
          icon="🎯"
          title="No matches yet"
          description="Generate role matches based on your current skill profile."
          action={
            <button className="btn-primary" onClick={handleGenerate} disabled={generating}>
              {generating ? "Generating…" : "Generate role matches"}
            </button>
          }
        />
      ) : (
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(380px, 1fr))", gap: 20 }}>
          {sorted.map((match) => (
            <MatchCard key={match.id} match={match} />
          ))}
        </div>
      )}
    </>
  );
}
