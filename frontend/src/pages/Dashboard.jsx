import { useEffect, useState } from "react";
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  PieChart,
  Pie,
  Cell,
  Legend,
} from "recharts";
import PageHeader from "../components/common/PageHeader";
import StatCard from "../components/common/StatCard";
import LoadingSpinner from "../components/common/LoadingSpinner";
import { getMyProfile, getEmployeeSkills, getEmployeeMatches, getSkillGaps } from "../services/api";

const COLORS = ["#167d9a", "#173b67", "#1a9ab8", "#10b981", "#f59e0b", "#8b5cf6"];

const skillTypeColor = { explicit: "#167d9a", inferred: "#f59e0b", transferable: "#10b981" };

export default function Dashboard() {
  const [profile, setProfile] = useState(null);
  const [skills, setSkills] = useState([]);
  const [matches, setMatches] = useState([]);
  const [gaps, setGaps] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const load = async () => {
      try {
        const p = await getMyProfile();
        setProfile(p);
        const [s, m, g] = await Promise.all([
          getEmployeeSkills(p.id),
          getEmployeeMatches(p.id),
          getSkillGaps(p.id),
        ]);
        setSkills(s);
        setMatches(m);
        setGaps(g);
      } catch (err) {
        setError("Failed to load dashboard data.");
      } finally {
        setLoading(false);
      }
    };
    load();
  }, []);

  if (loading) return <LoadingSpinner message="Loading your dashboard…" />;
  if (error) return <div className="error-banner">{error}</div>;

  // Chart data
  const skillProfData = skills.slice(0, 8).map((s) => ({
    name: s.skill?.name || "—",
    proficiency: s.proficiency,
    fill: skillTypeColor[s.skill_type] || "#167d9a",
  }));

  const skillTypeDist = ["explicit", "inferred", "transferable"].map((type) => ({
    name: type.charAt(0).toUpperCase() + type.slice(1),
    value: skills.filter((s) => s.skill_type === type).length,
  }));

  const matchData = matches.slice(0, 6).map((m) => ({
    name: m.role?.title || "—",
    match: Math.round(m.match_score),
  }));

  const topMatch = matches[0];
  const criticalGaps = gaps.filter((g) => ["critical", "high"].includes(g.gap_level)).length;

  return (
    <>
      <PageHeader
        title="My Dashboard"
        subtitle={`Welcome back, ${profile?.user?.full_name?.split(" ")[0] || "there"} · ${profile?.designation || ""} in ${profile?.department || ""}`}
      />

      {/* KPI Row */}
      <div className="stat-grid">
        <StatCard label="Total Skills" value={skills.length} accent="accent" />
        <StatCard label="Verified Skills" value={skills.filter((s) => s.skill_type === "explicit").length} accent="success" />
        <StatCard label="Inferred Skills" value={skills.filter((s) => s.skill_type === "inferred").length} />
        <StatCard label="Role Matches" value={matches.length} />
        <StatCard label="Skill Gaps" value={gaps.length} sub={criticalGaps > 0 ? `${criticalGaps} critical` : null} accent={criticalGaps > 0 ? "danger" : null} />
        <StatCard label="Profile" value={`${profile?.profile_completion ?? 0}%`} sub="Completion" accent="accent" />
      </div>

      {/* Charts Row 1 */}
      <div className="grid-2" style={{ marginBottom: 20 }}>
        <div className="chart-card">
          <div style={{ marginBottom: 16 }}>
            <h3 className="card-title">Skill Proficiency</h3>
            <p style={{ fontSize: 12, color: "var(--text-muted)", margin: "4px 0 0" }}>
              Top {skillProfData.length} skills by proficiency level (1–5)
            </p>
          </div>
          <ResponsiveContainer width="100%" height={240}>
            <BarChart data={skillProfData} barSize={28}>
              <XAxis dataKey="name" tick={{ fontSize: 11 }} />
              <YAxis domain={[0, 5]} tick={{ fontSize: 11 }} />
              <Tooltip formatter={(v) => [`${v}/5`, "Proficiency"]} />
              <Bar dataKey="proficiency" radius={[4, 4, 0, 0]}>
                {skillProfData.map((entry, i) => (
                  <Cell key={i} fill={entry.fill} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="chart-card">
          <div style={{ marginBottom: 16 }}>
            <h3 className="card-title">Role Match Scores</h3>
            <p style={{ fontSize: 12, color: "var(--text-muted)", margin: "4px 0 0" }}>
              Top role matches by compatibility score
            </p>
          </div>
          <ResponsiveContainer width="100%" height={240}>
            <BarChart data={matchData} barSize={28} layout="vertical">
              <XAxis type="number" domain={[0, 100]} tick={{ fontSize: 11 }} />
              <YAxis type="category" dataKey="name" width={120} tick={{ fontSize: 11 }} />
              <Tooltip formatter={(v) => [`${v}%`, "Match"]} />
              <Bar dataKey="match" fill="#167d9a" radius={[0, 4, 4, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Row 2 */}
      <div className="grid-2">
        {/* Skill type breakdown */}
        <div className="chart-card">
          <div style={{ marginBottom: 16 }}>
            <h3 className="card-title">Skill Type Distribution</h3>
          </div>
          <ResponsiveContainer width="100%" height={200}>
            <PieChart>
              <Pie data={skillTypeDist} dataKey="value" nameKey="name" outerRadius={80} label={({ name, value }) => `${name} (${value})`} labelLine={false} fontSize={11}>
                {skillTypeDist.map((_, i) => (
                  <Cell key={i} fill={COLORS[i]} />
                ))}
              </Pie>
              <Tooltip />
              <Legend />
            </PieChart>
          </ResponsiveContainer>
        </div>

        {/* Top Match Card */}
        <div className="card">
          <div className="card-header-custom">
            <h3 className="card-title">🎯 Top Role Match</h3>
          </div>
          <div className="card-body-custom">
            {topMatch ? (
              <>
                <div style={{ display: "flex", gap: 16, alignItems: "center", marginBottom: 20 }}>
                  <div className={`match-ring ${topMatch.match_score >= 75 ? "match-high" : topMatch.match_score >= 50 ? "match-medium" : "match-low"}`}>
                    {Math.round(topMatch.match_score)}%
                  </div>
                  <div>
                    <div style={{ fontWeight: 700, fontSize: 17 }}>{topMatch.role?.title}</div>
                    <div style={{ color: "var(--text-muted)", fontSize: 13 }}>{topMatch.role?.department} · {topMatch.role?.level}</div>
                  </div>
                </div>
                <div style={{ marginBottom: 12 }}>
                  <div style={{ fontSize: 12, fontWeight: 700, color: "var(--text-muted)", marginBottom: 6, textTransform: "uppercase", letterSpacing: "0.05em" }}>
                    Matching skills
                  </div>
                  <div className="tag-list">
                    {(topMatch.matching_skills || []).slice(0, 6).map((s) => (
                      <span key={s} className="tag tag-match">{s}</span>
                    ))}
                  </div>
                </div>
                {(topMatch.missing_skills || []).length > 0 && (
                  <div>
                    <div style={{ fontSize: 12, fontWeight: 700, color: "var(--text-muted)", marginBottom: 6, textTransform: "uppercase", letterSpacing: "0.05em" }}>
                      Missing skills
                    </div>
                    <div className="tag-list">
                      {(topMatch.missing_skills || []).slice(0, 4).map((s) => (
                        <span key={s} className="tag tag-missing">{s}</span>
                      ))}
                    </div>
                  </div>
                )}
                {topMatch.explanation && (
                  <p style={{ marginTop: 14, fontSize: 13, color: "var(--text-secondary)", lineHeight: 1.55 }}>
                    {topMatch.explanation}
                  </p>
                )}
              </>
            ) : (
              <p style={{ color: "var(--text-muted)" }}>No role matches found yet.</p>
            )}
          </div>
        </div>
      </div>
    </>
  );
}
