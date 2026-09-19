import { useEffect, useState } from "react";
import PageHeader from "../components/common/PageHeader";
import LoadingSpinner from "../components/common/LoadingSpinner";
import EmptyState from "../components/common/EmptyState";
import { getMyProfile, getRoadmap } from "../services/api";

const PHASE_ICONS = ["🌱", "📚", "🔨", "🎓", "🚀", "🏆"];
const PHASE_COLORS = [
  "linear-gradient(135deg, #10b981, #059669)",
  "linear-gradient(135deg, #167d9a, #0e6d8a)",
  "linear-gradient(135deg, #f59e0b, #d97706)",
  "linear-gradient(135deg, #8b5cf6, #7c3aed)",
  "linear-gradient(135deg, #ef4444, #dc2626)",
  "linear-gradient(135deg, #173b67, #0d1f3c)",
];

export default function Roadmap() {
  const [roadmap, setRoadmap] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const load = async () => {
      try {
        const profile = await getMyProfile();
        const r = await getRoadmap(profile.id);
        setRoadmap(r);
      } catch {
        setError("No roadmap found. Role matches are needed to generate a roadmap.");
      } finally {
        setLoading(false);
      }
    };
    load();
  }, []);

  if (loading) return <LoadingSpinner message="Loading your learning roadmap…" />;

  return (
    <>
      <PageHeader
        title="Learning Roadmap"
        subtitle={
          roadmap?.target_role
            ? `Personalized career path toward ${roadmap.target_role.title} in ${roadmap.target_role.department}`
            : "Your personalized career development and skill-building roadmap."
        }
      />

      {error && (
        <div className="info-banner" style={{ background: "#fffbeb", borderColor: "#fde68a", color: "#b45309" }}>
          ⚠️ {error}
        </div>
      )}

      {roadmap && (
        <div style={{ display: "grid", gridTemplateColumns: "1fr 340px", gap: 20, alignItems: "start" }}>
          {/* Roadmap timeline */}
          <div>
            {roadmap.target_role && (
              <div className="card" style={{ marginBottom: 20, background: "linear-gradient(135deg, var(--brand-700), var(--brand-900))", border: "none", color: "white" }}>
                <div className="card-body-custom">
                  <div style={{ fontSize: 12, fontWeight: 700, opacity: 0.65, textTransform: "uppercase", letterSpacing: "0.08em", marginBottom: 6 }}>
                    Target role
                  </div>
                  <div style={{ fontSize: 22, fontWeight: 800 }}>{roadmap.target_role.title}</div>
                  <div style={{ opacity: 0.7, fontSize: 14 }}>{roadmap.target_role.department} · {roadmap.target_role.level}</div>
                </div>
              </div>
            )}

            <div className="card">
              <div className="card-header-custom"><h3 className="card-title">Development Phases</h3></div>
              <div className="card-body-custom">
                {roadmap.roadmap_data?.phases?.length > 0 ? (
                  roadmap.roadmap_data.phases.map((phase, i) => (
                    <div key={i} className="roadmap-step">
                      <div className="roadmap-dot" style={{ background: PHASE_COLORS[i % PHASE_COLORS.length] }}>
                        {PHASE_ICONS[i % PHASE_ICONS.length]}
                      </div>
                      <div className="roadmap-content">
                        <div className="roadmap-phase">Phase {i + 1}</div>
                        <div className="roadmap-title">{phase.title || phase.phase || `Phase ${i + 1}`}</div>
                        {phase.description && (
                          <div className="roadmap-desc">{phase.description}</div>
                        )}
                        {phase.actions?.length > 0 && (
                          <ul style={{ marginTop: 8, paddingLeft: 18, marginBottom: 0 }}>
                            {phase.actions.map((a, j) => (
                              <li key={j} style={{ fontSize: 13, color: "var(--text-secondary)", marginBottom: 4, lineHeight: 1.5 }}>{a}</li>
                            ))}
                          </ul>
                        )}
                        {phase.skills?.length > 0 && (
                          <div className="tag-list" style={{ marginTop: 8 }}>
                            {phase.skills.map((s) => (
                              <span key={s} className="tag">{s}</span>
                            ))}
                          </div>
                        )}
                      </div>
                    </div>
                  ))
                ) : roadmap.roadmap_data?.milestones?.length > 0 ? (
                  roadmap.roadmap_data.milestones.map((milestone, i) => (
                    <div key={i} className="roadmap-step">
                      <div className="roadmap-dot" style={{ background: PHASE_COLORS[i % PHASE_COLORS.length] }}>
                        {PHASE_ICONS[i % PHASE_ICONS.length]}
                      </div>
                      <div className="roadmap-content">
                        <div className="roadmap-phase">Milestone {i + 1}</div>
                        <div className="roadmap-title">{milestone.title || milestone}</div>
                        {milestone.description && <div className="roadmap-desc">{milestone.description}</div>}
                      </div>
                    </div>
                  ))
                ) : (
                  <EmptyState icon="🗺️" title="Roadmap data loading" description="Your roadmap phases will appear once generated." />
                )}
              </div>
            </div>
          </div>

          {/* Side info */}
          <div>
            {roadmap.roadmap_data?.summary && (
              <div className="card" style={{ marginBottom: 16 }}>
                <div className="card-header-custom"><h3 className="card-title">📋 Summary</h3></div>
                <div className="card-body-custom">
                  <p style={{ fontSize: 14, color: "var(--text-secondary)", lineHeight: 1.6, margin: 0 }}>
                    {roadmap.roadmap_data.summary}
                  </p>
                </div>
              </div>
            )}

            {roadmap.roadmap_data?.key_skills?.length > 0 && (
              <div className="card" style={{ marginBottom: 16 }}>
                <div className="card-header-custom"><h3 className="card-title">⚡ Key Skills to Build</h3></div>
                <div className="card-body-custom">
                  <div className="tag-list">
                    {roadmap.roadmap_data.key_skills.map((s) => (
                      <span key={s} className="tag">{s}</span>
                    ))}
                  </div>
                </div>
              </div>
            )}

            {roadmap.roadmap_data?.estimated_duration && (
              <div className="card">
                <div className="card-body-custom" style={{ textAlign: "center" }}>
                  <div style={{ fontSize: 36, marginBottom: 8 }}>⏱️</div>
                  <div style={{ fontSize: 13, color: "var(--text-muted)", marginBottom: 4 }}>Estimated timeline</div>
                  <div style={{ fontSize: 20, fontWeight: 800 }}>{roadmap.roadmap_data.estimated_duration}</div>
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {!roadmap && !error && (
        <EmptyState icon="🗺️" title="No roadmap yet" description="Generate role matches first to create your personalized learning roadmap." />
      )}
    </>
  );
}
