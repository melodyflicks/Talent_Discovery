import { useEffect, useMemo, useState } from "react";
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
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  Radar,
} from "recharts";
import PageHeader from "../components/common/PageHeader";
import StatCard from "../components/common/StatCard";
import LoadingSpinner from "../components/common/LoadingSpinner";
import { getHRAnalytics, getHREmployees } from "../services/api";

const COLORS = ["#167d9a", "#173b67", "#10b981", "#f59e0b", "#8b5cf6", "#ef4444", "#ec4899"];

const TABS = ["Overview", "Employees", "Skill Gaps", "Role Demand", "Learning"];

export default function HRDashboard() {
  const [analytics, setAnalytics] = useState(null);
  const [employees, setEmployees] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [tab, setTab] = useState("Overview");
  const [search, setSearch] = useState("");
  const [deptFilter, setDeptFilter] = useState("All");
  const [selectedEmp, setSelectedEmp] = useState(null);

  useEffect(() => {
    const load = async () => {
      try {
        const [a, e] = await Promise.all([getHRAnalytics(), getHREmployees()]);
        setAnalytics(a);
        setEmployees(e);
      } catch {
        setError("Failed to load HR analytics. Make sure you have HR or Admin access.");
      } finally {
        setLoading(false);
      }
    };
    load();
  }, []);

  const departments = useMemo(() => {
    const depts = [...new Set(employees.map((e) => e.department))].filter(Boolean);
    return ["All", ...depts];
  }, [employees]);

  const filteredEmployees = useMemo(() =>
    employees.filter((emp) => {
      const matchDept = deptFilter === "All" || emp.department === deptFilter;
      const q = search.toLowerCase();
      const matchSearch = !q || [emp.employee_code, emp.department, emp.designation]
        .join(" ").toLowerCase().includes(q);
      return matchDept && matchSearch;
    }),
    [employees, deptFilter, search]
  );

  if (loading) return <LoadingSpinner message="Loading HR analytics…" />;
  if (error) return <div className="error-banner">{error}</div>;

  const skillDistData = (analytics.skill_distribution || []).map((d) => ({
    name: d.skill || d.name || "—",
    count: d.count || 0,
    avg: d.avg_proficiency || 0,
  }));

  const deptData = (analytics.department_skills || []).map((d) => ({
    name: d.department,
    employees: d.headcount,
    skills: d.total_skills,
    completion: d.avg_completion,
  }));

  const gapData = (analytics.skill_gaps || []).slice(0, 10).map((g) => ({
    name: g.skill,
    affected: g.affected_employees,
    gap: g.avg_gap_size,
  }));

  const roleData = (analytics.role_demand || []).map((r) => ({
    name: r.role,
    candidates: r.evaluated_candidates,
    score: Math.round(r.avg_match_score),
  }));

  const learningData = (analytics.learning_categories || []).map((l) => ({
    name: l.provider,
    courses: l.course_count,
    assigned: l.assigned_count,
  }));

  const kpiData = [
    { label: "Total Employees", value: analytics.total_employees, accent: "accent" },
    { label: "Avg Profile Completion", value: `${analytics.profile_completion_rate}%`, accent: analytics.profile_completion_rate >= 80 ? "success" : "warning" },
    { label: "Skills in Catalog", value: analytics.total_skills },
    { label: "Critical Gaps", value: analytics.emerging_skill_gaps, accent: analytics.emerging_skill_gaps > 0 ? "danger" : "success" },
    { label: "Role Evaluations", value: analytics.total_role_matches },
    { label: "Learning Plans", value: analytics.learning_recommendations, accent: "accent" },
  ];

  return (
    <>
      <PageHeader
        title="HR Analytics"
        subtitle="Organization-wide talent intelligence: skills, gaps, role readiness, and learning insights."
      />

      {/* KPIs */}
      <div className="stat-grid" style={{ marginBottom: 24 }}>
        {kpiData.map(({ label, value, accent }) => (
          <StatCard key={label} label={label} value={value} accent={accent} />
        ))}
      </div>

      {/* Tab Navigation */}
      <div style={{ display: "flex", gap: 4, marginBottom: 24, borderBottom: "2px solid var(--border)", paddingBottom: 0 }}>
        {TABS.map((t) => (
          <button
            key={t}
            onClick={() => setTab(t)}
            style={{
              padding: "9px 18px",
              border: "none",
              background: "none",
              fontWeight: 700,
              fontSize: 13.5,
              color: tab === t ? "var(--accent-500)" : "var(--text-muted)",
              borderBottom: `2px solid ${tab === t ? "var(--accent-500)" : "transparent"}`,
              cursor: "pointer",
              marginBottom: -2,
              transition: "var(--transition)",
            }}
          >
            {t}
          </button>
        ))}
      </div>

      {/* OVERVIEW TAB */}
      {tab === "Overview" && (
        <div>
          <div className="grid-2" style={{ marginBottom: 20 }}>
            <div className="chart-card">
              <h3 className="card-title" style={{ marginBottom: 16 }}>Top Skills Across Organization</h3>
              <ResponsiveContainer width="100%" height={260}>
                <BarChart data={skillDistData.slice(0, 8)} barSize={22}>
                  <XAxis dataKey="name" tick={{ fontSize: 10 }} />
                  <YAxis tick={{ fontSize: 10 }} />
                  <Tooltip formatter={(v, n) => [v, n === "count" ? "Employees" : "Avg Prof."]} />
                  <Bar dataKey="count" fill="#167d9a" radius={[4, 4, 0, 0]} name="count" />
                </BarChart>
              </ResponsiveContainer>
            </div>
            <div className="chart-card">
              <h3 className="card-title" style={{ marginBottom: 16 }}>Department Headcount</h3>
              <ResponsiveContainer width="100%" height={260}>
                <PieChart>
                  <Pie data={deptData} dataKey="employees" nameKey="name" outerRadius={100} label={({ name, value }) => `${name} (${value})`} fontSize={11}>
                    {deptData.map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
                  </Pie>
                  <Tooltip />
                  <Legend />
                </PieChart>
              </ResponsiveContainer>
            </div>
          </div>
          <div className="grid-2">
            <div className="chart-card">
              <h3 className="card-title" style={{ marginBottom: 16 }}>Department Skills Overview</h3>
              <ResponsiveContainer width="100%" height={220}>
                <BarChart data={deptData} barSize={20}>
                  <XAxis dataKey="name" tick={{ fontSize: 10 }} />
                  <YAxis tick={{ fontSize: 10 }} />
                  <Tooltip />
                  <Bar dataKey="skills" fill="#173b67" radius={[3, 3, 0, 0]} name="Total Skills" />
                  <Bar dataKey="completion" fill="#10b981" radius={[3, 3, 0, 0]} name="Avg Completion %" />
                </BarChart>
              </ResponsiveContainer>
            </div>
            <div className="chart-card">
              <h3 className="card-title" style={{ marginBottom: 16 }}>Learning Activity</h3>
              <ResponsiveContainer width="100%" height={220}>
                <BarChart data={learningData} barSize={20}>
                  <XAxis dataKey="name" tick={{ fontSize: 10 }} />
                  <YAxis tick={{ fontSize: 10 }} />
                  <Tooltip />
                  <Bar dataKey="courses" fill="#8b5cf6" radius={[3, 3, 0, 0]} name="Courses" />
                  <Bar dataKey="assigned" fill="#f59e0b" radius={[3, 3, 0, 0]} name="Assigned" />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>
      )}

      {/* EMPLOYEES TAB */}
      {tab === "Employees" && (
        <div>
          <div style={{ display: "flex", gap: 10, marginBottom: 16, flexWrap: "wrap" }}>
            <input
              className="form-input"
              style={{ maxWidth: 260, padding: "8px 13px" }}
              placeholder="Search employees…"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
            />
            <select
              className="form-input"
              style={{ maxWidth: 200 }}
              value={deptFilter}
              onChange={(e) => setDeptFilter(e.target.value)}
            >
              {departments.map((d) => <option key={d}>{d}</option>)}
            </select>
          </div>
          <div className="card">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Employee Code</th>
                  <th>Department</th>
                  <th>Designation</th>
                  <th>Experience</th>
                  <th>Profile %</th>
                  <th>Location</th>
                </tr>
              </thead>
              <tbody>
                {filteredEmployees.map((emp) => (
                  <tr key={emp.id} style={{ cursor: "pointer" }} onClick={() => setSelectedEmp(emp)} className="hr-employee-row">
                    <td style={{ fontWeight: 700, color: "var(--accent-600)" }}>{emp.employee_code}</td>
                    <td>{emp.department}</td>
                    <td>{emp.designation}</td>
                    <td>{emp.years_of_experience}y</td>
                    <td>
                      <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                        <div style={{ width: 60, height: 6, background: "var(--border)", borderRadius: 999, overflow: "hidden" }}>
                          <div style={{ height: "100%", width: `${emp.profile_completion}%`, background: emp.profile_completion >= 80 ? "#10b981" : "#f59e0b", borderRadius: 999 }} />
                        </div>
                        <span style={{ fontSize: 12, fontWeight: 600 }}>{emp.profile_completion}%</span>
                      </div>
                    </td>
                    <td style={{ color: "var(--text-secondary)" }}>{emp.location || "—"}</td>
                  </tr>
                ))}
                {filteredEmployees.length === 0 && (
                  <tr><td colSpan={6} style={{ textAlign: "center", padding: 32, color: "var(--text-muted)" }}>No employees match your search.</td></tr>
                )}
              </tbody>
            </table>
          </div>

          {/* Employee detail modal */}
          {selectedEmp && (
            <div style={{
              position: "fixed", inset: 0, background: "rgba(0,0,0,0.4)", zIndex: 1000,
              display: "flex", alignItems: "center", justifyContent: "center", padding: 24,
            }} onClick={() => setSelectedEmp(null)}>
              <div style={{ background: "white", borderRadius: 16, width: "100%", maxWidth: 540, padding: 28, boxShadow: "0 24px 80px rgba(0,0,0,0.2)" }} onClick={(e) => e.stopPropagation()}>
                <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 20 }}>
                  <div>
                    <div style={{ fontWeight: 800, fontSize: 18 }}>{selectedEmp.employee_code}</div>
                    <div style={{ color: "var(--text-secondary)", fontSize: 14 }}>{selectedEmp.designation} · {selectedEmp.department}</div>
                  </div>
                  <button onClick={() => setSelectedEmp(null)} style={{ background: "none", border: "none", fontSize: 20, cursor: "pointer", color: "var(--text-muted)" }}>✕</button>
                </div>
                <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12 }}>
                  {[
                    ["Department", selectedEmp.department],
                    ["Designation", selectedEmp.designation],
                    ["Experience", `${selectedEmp.years_of_experience} years`],
                    ["Profile Completion", `${selectedEmp.profile_completion}%`],
                    ["Location", selectedEmp.location || "—"],
                    ["Education", selectedEmp.education || "—"],
                  ].map(([k, v]) => (
                    <div key={k} style={{ padding: 12, background: "var(--surface-2)", borderRadius: 8 }}>
                      <div style={{ fontSize: 11, fontWeight: 700, color: "var(--text-muted)", textTransform: "uppercase", letterSpacing: "0.05em" }}>{k}</div>
                      <div style={{ fontSize: 14, fontWeight: 600, marginTop: 4 }}>{v}</div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      {/* SKILL GAPS TAB */}
      {tab === "Skill Gaps" && (
        <div>
          <div className="grid-2">
            <div className="chart-card">
              <h3 className="card-title" style={{ marginBottom: 16 }}>Top Skill Gaps by Affected Employees</h3>
              <ResponsiveContainer width="100%" height={320}>
                <BarChart data={gapData} layout="vertical" barSize={16}>
                  <XAxis type="number" tick={{ fontSize: 10 }} />
                  <YAxis type="category" dataKey="name" width={110} tick={{ fontSize: 11 }} />
                  <Tooltip formatter={(v, n) => [v, n === "affected" ? "Affected employees" : "Avg gap size"]} />
                  <Bar dataKey="affected" fill="#ef4444" radius={[0, 4, 4, 0]} name="affected" />
                </BarChart>
              </ResponsiveContainer>
            </div>
            <div className="card">
              <div className="card-header-custom"><h3 className="card-title">Skill Gap Details</h3></div>
              <table className="data-table">
                <thead>
                  <tr>
                    <th>Skill</th>
                    <th>Affected</th>
                    <th>Avg Gap</th>
                    <th>Severity</th>
                  </tr>
                </thead>
                <tbody>
                  {(analytics.skill_gaps || []).map((g, i) => (
                    <tr key={i}>
                      <td style={{ fontWeight: 600 }}>{g.skill}</td>
                      <td>{g.affected_employees}</td>
                      <td>{g.avg_gap_size}</td>
                      <td>
                        <span style={{
                          padding: "2px 8px",
                          borderRadius: 999,
                          fontSize: 11.5,
                          fontWeight: 700,
                          background: g.avg_gap_size >= 3 ? "#fef2f2" : g.avg_gap_size >= 2 ? "#fffbeb" : "#ecfdf5",
                          color: g.avg_gap_size >= 3 ? "#dc2626" : g.avg_gap_size >= 2 ? "#b45309" : "#059669",
                        }}>
                          {g.avg_gap_size >= 3 ? "Critical" : g.avg_gap_size >= 2 ? "Medium" : "Low"}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}

      {/* ROLE DEMAND TAB */}
      {tab === "Role Demand" && (
        <div>
          <div className="grid-2">
            <div className="chart-card">
              <h3 className="card-title" style={{ marginBottom: 16 }}>Role Evaluation Activity</h3>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={roleData} barSize={24}>
                  <XAxis dataKey="name" tick={{ fontSize: 10 }} />
                  <YAxis tick={{ fontSize: 10 }} />
                  <Tooltip />
                  <Bar dataKey="candidates" fill="#173b67" radius={[4, 4, 0, 0]} name="Candidates Evaluated" />
                  <Bar dataKey="score" fill="#10b981" radius={[4, 4, 0, 0]} name="Avg Match %" />
                </BarChart>
              </ResponsiveContainer>
            </div>
            <div className="card">
              <div className="card-header-custom"><h3 className="card-title">Role Readiness Table</h3></div>
              <table className="data-table">
                <thead>
                  <tr>
                    <th>Role</th>
                    <th>Department</th>
                    <th>Level</th>
                    <th>Candidates</th>
                    <th>Avg Match</th>
                  </tr>
                </thead>
                <tbody>
                  {(analytics.role_demand || []).map((r, i) => (
                    <tr key={i}>
                      <td style={{ fontWeight: 600 }}>{r.role}</td>
                      <td style={{ color: "var(--text-secondary)" }}>{r.department}</td>
                      <td>
                        <span style={{ fontSize: 12, padding: "2px 8px", borderRadius: 999, background: "var(--surface-2)", border: "1px solid var(--border)" }}>
                          {r.level}
                        </span>
                      </td>
                      <td>{r.evaluated_candidates}</td>
                      <td>
                        <span style={{
                          fontWeight: 800,
                          color: r.avg_match_score >= 70 ? "var(--success)" : r.avg_match_score >= 50 ? "#d97706" : "var(--danger)"
                        }}>
                          {Math.round(r.avg_match_score)}%
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}

      {/* LEARNING TAB */}
      {tab === "Learning" && (
        <div>
          <div className="grid-2">
            <div className="chart-card">
              <h3 className="card-title" style={{ marginBottom: 16 }}>Learning by Provider</h3>
              <ResponsiveContainer width="100%" height={280}>
                <BarChart data={learningData} barSize={24}>
                  <XAxis dataKey="name" tick={{ fontSize: 10 }} />
                  <YAxis tick={{ fontSize: 10 }} />
                  <Tooltip />
                  <Bar dataKey="courses" fill="#8b5cf6" radius={[4, 4, 0, 0]} name="Total Courses" />
                  <Bar dataKey="assigned" fill="#167d9a" radius={[4, 4, 0, 0]} name="Assigned" />
                </BarChart>
              </ResponsiveContainer>
            </div>
            <div className="card">
              <div className="card-header-custom"><h3 className="card-title">Provider Summary</h3></div>
              <table className="data-table">
                <thead>
                  <tr>
                    <th>Provider</th>
                    <th>Total Courses</th>
                    <th>Assignments</th>
                    <th>Coverage</th>
                  </tr>
                </thead>
                <tbody>
                  {(analytics.learning_categories || []).map((l, i) => {
                    const coverage = l.course_count > 0 ? Math.round((l.assigned_count / l.course_count) * 100) : 0;
                    return (
                      <tr key={i}>
                        <td style={{ fontWeight: 600 }}>{l.provider}</td>
                        <td>{l.course_count}</td>
                        <td>{l.assigned_count}</td>
                        <td>
                          <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                            <div style={{ width: 60, height: 6, background: "var(--border)", borderRadius: 999, overflow: "hidden" }}>
                              <div style={{ height: "100%", width: `${coverage}%`, background: "#8b5cf6", borderRadius: 999 }} />
                            </div>
                            <span style={{ fontSize: 12, fontWeight: 600 }}>{coverage}%</span>
                          </div>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
