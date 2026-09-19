export default function LoadingSpinner({ message = "Loading…" }) {
  return (
    <div className="spinner-overlay">
      <div style={{ textAlign: "center" }}>
        <div className="spinner" style={{ margin: "0 auto 12px" }} />
        <p style={{ color: "var(--text-muted)", fontSize: 13 }}>{message}</p>
      </div>
    </div>
  );
}
