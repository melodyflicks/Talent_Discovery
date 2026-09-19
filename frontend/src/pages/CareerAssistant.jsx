import { useEffect, useRef, useState } from "react";
import PageHeader from "../components/common/PageHeader";
import { getMyProfile, sendAssistantMessage } from "../services/api";

const SUGGESTIONS = [
  "What skills should I prioritize?",
  "Which roles fit my current profile?",
  "How can I close my critical skill gaps?",
  "What certifications should I pursue?",
  "How do I prepare for a senior role?",
];

export default function CareerAssistant() {
  const [profile, setProfile] = useState(null);
  const [messages, setMessages] = useState([
    {
      type: "assistant",
      text: "Hi there! 👋 I'm your AI Career Assistant. I can help you navigate your career development, understand your skill gaps, and explore internal opportunities. What would you like to know?",
    },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef(null);

  useEffect(() => {
    getMyProfile()
      .then(setProfile)
      .catch(() => {});
  }, []);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const send = async (text = input) => {
    const msg = text.trim();
    if (!msg || loading) return;
    setMessages((prev) => [...prev, { type: "user", text: msg }]);
    setInput("");
    setLoading(true);
    try {
      const result = await sendAssistantMessage({
        message: msg,
        context: profile ? { employee_id: profile.id, name: profile.user?.full_name } : {},
      });
      setMessages((prev) => [
        ...prev,
        { type: "assistant", text: result.reply || "I'm here to help with your career development questions." },
      ]);
    } catch {
      setMessages((prev) => [
        ...prev,
        { type: "assistant", text: "I encountered an issue connecting to the backend. Please try again shortly." },
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <PageHeader
        title="Career Assistant"
        subtitle="AI-powered career guidance tailored to your skill profile and development goals."
      />

      <div className="chat-container">
        {/* Messages */}
        <div className="chat-messages" id="chat-messages">
          {messages.map((msg, i) => (
            <div
              key={i}
              className={`chat-message ${msg.type}`}
              style={{
                animationDelay: `${i * 0.05}s`,
              }}
            >
              {msg.type === "assistant" && (
                <div style={{ fontSize: 11, fontWeight: 700, color: "var(--accent-500)", marginBottom: 4, textTransform: "uppercase", letterSpacing: "0.05em" }}>
                  🤖 AI Assistant
                </div>
              )}
              {msg.text}
            </div>
          ))}
          {loading && (
            <div className="chat-message assistant">
              <div style={{ fontSize: 11, fontWeight: 700, color: "var(--accent-500)", marginBottom: 6, textTransform: "uppercase", letterSpacing: "0.05em" }}>
                🤖 AI Assistant
              </div>
              <div style={{ display: "flex", gap: 4, alignItems: "center" }}>
                {[0, 1, 2].map((i) => (
                  <div
                    key={i}
                    style={{
                      width: 8,
                      height: 8,
                      borderRadius: "50%",
                      background: "var(--accent-400)",
                      animation: "spin 1s ease-in-out infinite",
                      animationDelay: `${i * 0.15}s`,
                      animationName: "typingDot",
                    }}
                  />
                ))}
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Input area */}
        <div className="chat-input-area">
          <div className="chat-suggestions">
            {SUGGESTIONS.map((q) => (
              <button
                key={q}
                className="chat-suggestion"
                onClick={() => send(q)}
                disabled={loading}
              >
                {q}
              </button>
            ))}
          </div>
          <div className="chat-input-row">
            <input
              id="career-assistant-input"
              className="form-input"
              placeholder="Ask about career development, skills, roles…"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && !e.shiftKey && send()}
              disabled={loading}
              autoComplete="off"
            />
            <button
              id="career-assistant-send"
              className="btn-primary"
              onClick={() => send()}
              disabled={loading || !input.trim()}
              style={{ flexShrink: 0 }}
            >
              Send
            </button>
          </div>
        </div>
      </div>

      <style>{`
        @keyframes typingDot {
          0%, 60%, 100% { transform: translateY(0); opacity: 1; }
          30% { transform: translateY(-6px); opacity: 0.4; }
        }
      `}</style>
    </>
  );
}
