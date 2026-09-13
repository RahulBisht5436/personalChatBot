const SESSION_STORAGE_KEY = "streaming_chatbot_session_id";

function createSessionId(): string {
  if (typeof crypto !== "undefined" && "randomUUID" in crypto) {
    return crypto.randomUUID();
  }

  return `session-${Date.now()}-${Math.random().toString(36).slice(2, 10)}`;
}

export function getSessionId(): string {
  if (typeof window === "undefined") {
    return "default";
  }

  const existing = window.localStorage.getItem(SESSION_STORAGE_KEY);
  if (existing) {
    return existing;
  }

  const sessionId = createSessionId();
  window.localStorage.setItem(SESSION_STORAGE_KEY, sessionId);
  return sessionId;
}
