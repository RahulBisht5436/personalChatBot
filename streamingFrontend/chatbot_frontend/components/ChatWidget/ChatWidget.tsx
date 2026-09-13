"use client";

import { useEffect, useRef, useState } from "react";
import { createPortal } from "react-dom";

import {
  fetchAccessStatus,
  fetchChatHistory,
  getDefaultApiUrl,
  sendChatMessage,
} from "@/lib/chatbot-api";
import { getSessionId } from "@/lib/session";
import type { AccessStatus, ChatMessage } from "@/lib/types";
import { widgetConfig } from "@/lib/widget-config";
import StarlightBackground from "./StarlightBackground";
import { MessageContent } from "./MessageContent";
import VerificationGate from "./VerificationGate";
import "./chat-widget.css";

type ChatWidgetProps = {
  apiUrl?: string;
  embedded?: boolean;
  inIframeEmbed?: boolean;
};

const LAUNCHER_BOTTOM = 20;
const LAUNCHER_SIZE = 64;
const PANEL_ANIM_MS = 340;

const PANEL_SHELL: React.CSSProperties = {
  overflow: "hidden",
  borderRadius: 22,
  border: "1px solid rgba(212, 175, 55, 0.28)",
  boxShadow:
    "0 28px 90px rgba(0, 0, 0, 0.55), inset 0 1px 0 rgba(255, 255, 255, 0.08)",
  background:
    "linear-gradient(165deg, rgba(18, 18, 28, 0.98) 0%, rgba(8, 8, 14, 0.99) 100%)",
};

function getPanelStyle(embedded: boolean): React.CSSProperties {
  if (embedded) {
    return {
      ...PANEL_SHELL,
      display: "flex",
      flexDirection: "column",
      width: "100%",
      maxWidth: 390,
      height: 580,
      position: "relative",
    };
  }

  return {
    ...PANEL_SHELL,
    position: "relative",
    width: 370,
    height: 540,
    maxHeight: "calc(100vh - 120px)",
    display: "flex",
    flexDirection: "column",
  };
}

function SparkleIcon() {
  return (
    <svg viewBox="0 0 24 24" fill="none" className="h-7 w-7" aria-hidden="true">
      <path
        d="M12 2l1.4 4.3L18 8l-4.6 1.7L12 14l-1.4-4.3L6 8l4.6-1.7L12 2Z"
        fill="currentColor"
      />
    </svg>
  );
}

function CloseIcon() {
  return (
    <svg viewBox="0 0 24 24" fill="none" className="h-7 w-7" aria-hidden="true">
      <path
        d="M7 7l10 10M17 7L7 17"
        stroke="currentColor"
        strokeWidth="2"
        strokeLinecap="round"
      />
    </svg>
  );
}

function LauncherIcons({ isOpen }: { isOpen: boolean }) {
  return (
    <span className="chatbot-launcher-icon-stack" aria-hidden="true">
      <span
        className={`chatbot-launcher-sparkle ${
          isOpen ? "is-hidden" : "is-visible chatbot-launcher-sparkle--enter"
        }`}
      >
        <SparkleIcon />
      </span>
      <span className={`chatbot-launcher-close ${isOpen ? "is-visible" : "is-hidden"}`}>
        <CloseIcon />
      </span>
    </span>
  );
}

function TypingIndicator() {
  return (
    <div className="chatbot-message flex justify-start">
      <div className="flex items-center gap-1.5 rounded-2xl rounded-bl-md border border-zinc-500/40 bg-[#232330] px-4 py-3 shadow-lg">
        <span className="chatbot-typing-dot inline-block h-2 w-2 rounded-full bg-amber-100" />
        <span className="chatbot-typing-dot inline-block h-2 w-2 rounded-full bg-amber-100" />
        <span className="chatbot-typing-dot inline-block h-2 w-2 rounded-full bg-amber-100" />
      </div>
    </div>
  );
}

function ChatPanel({
  embedded,
  messages,
  isLoading,
  error,
  input,
  access,
  apiUrl,
  sessionId,
  onAccessChange,
  onInputChange,
  onSend,
  onClose,
  onPromptClick,
  messagesEndRef,
}: {
  embedded: boolean;
  messages: ChatMessage[];
  isLoading: boolean;
  error: string | null;
  input: string;
  access: AccessStatus | null;
  apiUrl: string;
  sessionId: string;
  onAccessChange: (access: AccessStatus) => void;
  onInputChange: (value: string) => void;
  onSend: (event: React.FormEvent) => void;
  onClose: () => void;
  onPromptClick: (prompt: string) => void;
  messagesEndRef: React.RefObject<HTMLDivElement | null>;
}) {
  const requiresVerification =
    access?.requires_verification === true && access.verified === false;
  const canChat = access?.can_chat === true;
  return (
    <div
      className={`chatbot-panel relative ${embedded ? "" : ""}`}
      style={getPanelStyle(embedded)}
    >
      <StarlightBackground className="opacity-80" fallingStarCount={16} />

      <header className="relative z-10 shrink-0 border-b border-amber-200/20 bg-[#0c0c14]/90 px-4 py-4">
        <div className="flex items-start justify-between gap-3">
          <div className="flex items-center gap-3">
            <div className="relative flex h-11 w-11 items-center justify-center overflow-hidden rounded-2xl border border-amber-200/25 bg-black/30 text-sm font-bold text-amber-100 shadow-[inset_0_1px_0_rgba(255,255,255,0.12)]">
              <StarlightBackground starCount={18} fallingStarCount={4} showFallingStars={false} />
              <span className="relative z-10">R</span>
            </div>
            <div>
              <p className="chatbot-title-shimmer text-sm font-semibold">
                {widgetConfig.assistantName}
              </p>
              <p className="text-xs font-medium text-amber-100">{widgetConfig.subtitle}</p>
            </div>
          </div>
          {!embedded && (
            <button
              type="button"
              onClick={onClose}
              className="rounded-full px-2 py-1 text-lg leading-none text-amber-100/70 transition hover:bg-white/10 hover:text-amber-50"
              aria-label="Close chat"
            >
              ×
            </button>
          )}
        </div>
      </header>

      <div className="chatbot-messages-scroll relative z-10 min-h-0 flex-1 px-4 py-4">
        <div
          aria-hidden="true"
          className="pointer-events-none absolute inset-0 bg-[#080810]/68"
        />
        <div className="relative space-y-3">
        {messages.length === 0 && !isLoading && (
          <div className="chatbot-message rounded-2xl border border-amber-200/25 bg-[#14141f]/95 p-4 shadow-lg">
            <p className="text-[15px] font-semibold text-white">
              {widgetConfig.welcomeTitle}
            </p>
            <p className="mt-1 text-[14px] font-medium leading-7 text-zinc-100">
              {widgetConfig.welcomeText}
            </p>

            <div className="mt-4 grid grid-cols-2 gap-2">
              {widgetConfig.highlightStats.map((stat) => (
                <div
                  key={stat.label}
                  className="chatbot-stat-chip rounded-xl border border-amber-200/30 bg-[#1c1c28]/95 px-3 py-2"
                >
                  <p className="text-xs font-semibold text-amber-50">
                    {stat.label}
                  </p>
                  <p className="text-[11px] font-medium text-zinc-200">
                    {stat.detail}
                  </p>
                </div>
              ))}
            </div>

            <div className="mt-3 flex flex-wrap gap-2">
              {widgetConfig.suggestedPrompts.map((prompt) => (
                <button
                  key={prompt}
                  type="button"
                  onClick={() => onPromptClick(prompt)}
                  disabled={!canChat}
                  className="rounded-full border border-amber-200/35 bg-[#1c1c28]/90 px-3 py-1.5 text-left text-xs font-semibold text-amber-50 transition hover:border-amber-200/55 hover:bg-[#252535] disabled:opacity-50"
                >
                  {prompt}
                </button>
              ))}
            </div>
          </div>
        )}

        {requiresVerification && access && (
          <VerificationGate
            apiUrl={apiUrl}
            sessionId={sessionId}
            access={access}
            onVerified={onAccessChange}
          />
        )}

        {messages.map((message, index) => {
          const isUser = message.role === "human";
          return (
            <div
              key={`${message.role}-${index}-${message.content}`}
              className={`chatbot-message flex ${isUser ? "justify-end" : "justify-start"}`}
            >
              <div
                className={
                  isUser
                    ? "max-w-[85%] rounded-2xl rounded-br-md border border-amber-300/45 bg-[#3a3220] px-3.5 py-2.5 text-[15px] font-medium leading-relaxed text-white shadow-[0_8px_24px_rgba(0,0,0,0.35)]"
                    : "max-w-[85%] rounded-2xl rounded-bl-md border border-zinc-500/40 bg-[#232330] px-3.5 py-2.5 text-[15px] font-medium leading-relaxed text-white shadow-[0_8px_24px_rgba(0,0,0,0.35)]"
                }
              >
                {isUser ? message.content : <MessageContent content={message.content} />}
              </div>
            </div>
          );
        })}

        {isLoading && messages.length > 0 && <TypingIndicator />}
        {isLoading && messages.length === 0 && <TypingIndicator />}

        {error && <p className="text-sm font-medium text-red-300">{error}</p>}
        <div ref={messagesEndRef} />
        </div>
      </div>

      <form
        onSubmit={onSend}
        className="relative z-10 shrink-0 border-t border-amber-200/20 bg-[#0c0c14]/95 p-3"
      >
        {!requiresVerification && access && !access.verified && (
          <p className="mb-2 text-xs font-medium text-amber-100/80">
            {access.remaining_free_messages ?? 0} free messages left before email
            verification.
          </p>
        )}
        <div className="flex items-center gap-2">
          <input
            value={input}
            onChange={(event) => onInputChange(event.target.value)}
            placeholder={
              canChat
                ? widgetConfig.placeholder
                : "Verify your email to continue chatting"
            }
            className="chatbot-input flex-1 rounded-full border border-zinc-500/40 bg-[#1a1a24] px-4 py-2.5 text-[15px] font-medium text-white outline-none placeholder:text-zinc-300 focus:border-amber-300/50 focus:bg-[#22222e]"
            disabled={isLoading || !canChat}
          />
          <button
            type="submit"
            disabled={isLoading || !input.trim() || !canChat}
            className="rounded-full border border-amber-300/45 bg-[#4a3f24] px-4 py-2.5 text-sm font-semibold text-white transition hover:bg-[#5c4f2c] disabled:opacity-50"
          >
            Send
          </button>
        </div>
      </form>
    </div>
  );
}

export default function ChatWidget({
  apiUrl,
  embedded = false,
  inIframeEmbed = false,
}: ChatWidgetProps) {
  const resolvedApiUrl = apiUrl ?? getDefaultApiUrl();
  const sessionIdRef = useRef<string>("");

  const [mounted, setMounted] = useState(false);
  const [isPanelMounted, setIsPanelMounted] = useState(embedded);
  const [panelMotion, setPanelMotion] = useState<"enter" | "exit" | "idle">(
    embedded ? "idle" : "exit",
  );
  const [showGreeting, setShowGreeting] = useState(!embedded);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [access, setAccess] = useState<AccessStatus | null>(null);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [hasLoadedHistory, setHasLoadedHistory] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const closeTimerRef = useRef<number | null>(null);

  function ensureSessionId(): string {
    if (!sessionIdRef.current) {
      sessionIdRef.current = getSessionId();
    }
    return sessionIdRef.current;
  }

  function openChat() {
    if (closeTimerRef.current) {
      window.clearTimeout(closeTimerRef.current);
      closeTimerRef.current = null;
    }

    setShowGreeting(false);
    setIsPanelMounted(true);
    setPanelMotion("enter");

    closeTimerRef.current = window.setTimeout(() => {
      setPanelMotion("idle");
      closeTimerRef.current = null;
    }, 420);
  }

  function closeChat() {
    if (!isPanelMounted || panelMotion === "exit") {
      return;
    }

    setPanelMotion("exit");

    if (closeTimerRef.current) {
      window.clearTimeout(closeTimerRef.current);
    }

    closeTimerRef.current = window.setTimeout(() => {
      setIsPanelMounted(false);
      setPanelMotion("exit");
      closeTimerRef.current = null;
    }, PANEL_ANIM_MS);
  }

  function toggleChat() {
    if (isPanelMounted && panelMotion !== "exit") {
      closeChat();
    } else {
      openChat();
    }
  }

  useEffect(() => {
    return () => {
      if (closeTimerRef.current) {
        window.clearTimeout(closeTimerRef.current);
      }
    };
  }, []);

  useEffect(() => {
    setMounted(true);
  }, []);

  useEffect(() => {
    if (!inIframeEmbed || typeof window === "undefined") {
      return;
    }

    window.parent.postMessage(
      { type: "streaming-chatbot-resize", open: isPanelMounted },
      "*",
    );
  }, [inIframeEmbed, isPanelMounted]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isLoading]);

  useEffect(() => {
    if (!isPanelMounted || embedded) {
      return;
    }

    function handleKeyDown(event: KeyboardEvent) {
      if (event.key === "Escape") {
        closeChat();
      }
    }

    window.addEventListener("keydown", handleKeyDown);

    return () => {
      window.removeEventListener("keydown", handleKeyDown);
    };
  }, [embedded, isPanelMounted]);

  useEffect(() => {
    if ((!isPanelMounted && !embedded) || hasLoadedHistory) {
      return;
    }

    let cancelled = false;
    const sessionId = ensureSessionId();

    async function loadHistory() {
      setIsLoading(true);
      setError(null);

      try {
        const [historyResult, accessStatus] = await Promise.all([
          fetchChatHistory(resolvedApiUrl, sessionId),
          fetchAccessStatus(resolvedApiUrl, sessionId),
        ]);
        if (!cancelled) {
          setMessages(historyResult.chatHistory);
          setAccess(historyResult.access ?? accessStatus);
          setHasLoadedHistory(true);
        }
      } catch {
        if (!cancelled) {
          setError("Could not load chat history.");
        }
      } finally {
        if (!cancelled) {
          setIsLoading(false);
        }
      }
    }

    void loadHistory();

    return () => {
      cancelled = true;
    };
  }, [embedded, hasLoadedHistory, isPanelMounted, resolvedApiUrl]);

  async function sendMessage(message: string) {
    const trimmed = message.trim();
    if (!trimmed || isLoading || !access?.can_chat) {
      return;
    }

    const sessionId = ensureSessionId();

    setInput("");
    setIsLoading(true);
    setError(null);
    setMessages((current) => [
      ...current,
      { role: "human", content: trimmed },
    ]);

    try {
      const result = await sendChatMessage(
        resolvedApiUrl,
        sessionId,
        trimmed,
      );
      setMessages(result.chat_history);
      if (result.access) {
        setAccess(result.access);
      }
      setHasLoadedHistory(true);
    } catch (sendError) {
      const accessError = sendError as Error & { access?: AccessStatus };
      if (accessError.access) {
        setAccess(accessError.access);
      }
      setError(
        accessError.message || "Failed to send message. Is the backend running?",
      );
      setMessages((current) => current.slice(0, -1));
    } finally {
      setIsLoading(false);
    }
  }

  async function handleSend(event: React.FormEvent) {
    event.preventDefault();
    await sendMessage(input);
  }

  const panelProps = {
    embedded,
    messages,
    isLoading,
    error,
    input,
    access,
    apiUrl: resolvedApiUrl,
    sessionId: ensureSessionId(),
    onAccessChange: setAccess,
    onInputChange: setInput,
    onSend: handleSend,
    onClose: closeChat,
    onPromptClick: (prompt: string) => void sendMessage(prompt),
    messagesEndRef,
  };

  if (embedded) {
    return (
      <div className="flex h-full w-full items-end justify-end p-3">
        <ChatPanel {...panelProps} />
      </div>
    );
  }

  if (!mounted) {
    return null;
  }

  return createPortal(
    <>
      {isPanelMounted && (
        <div
          className={`chatbot-backdrop ${panelMotion === "exit" ? "chatbot-backdrop--exit" : "chatbot-backdrop--enter"}`}
          style={{
            position: "fixed",
            inset: 0,
            zIndex: 2147483645,
            pointerEvents: "auto",
          }}
          onClick={closeChat}
          aria-hidden="true"
        />
      )}

      {isPanelMounted && (
        <div
          style={{
            position: "fixed",
            inset: 0,
            zIndex: 2147483646,
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            padding: 20,
            pointerEvents: "none",
          }}
        >
          <div
            className={`chatbot-panel-shell ${
              panelMotion === "exit"
                ? "chatbot-panel-shell--exit"
                : panelMotion === "enter"
                  ? "chatbot-panel-shell--enter"
                  : ""
            }`}
            style={{ pointerEvents: "auto", width: "100%", maxWidth: 370 }}
          >
            <ChatPanel {...panelProps} />
          </div>
        </div>
      )}

      <div
        className="chatbot-launcher-wrap"
        style={{
          position: "fixed",
          bottom: LAUNCHER_BOTTOM,
          zIndex: 2147483647,
          display: "flex",
          flexDirection: "row",
          alignItems: "flex-end",
          gap: 12,
          pointerEvents: "auto",
        }}
      >
        {showGreeting && !isPanelMounted && (
          <button
            type="button"
            onClick={openChat}
            className="chatbot-greeting"
            style={{
              maxWidth: 240,
              borderRadius: 16,
              border: "1px solid rgba(212, 175, 55, 0.25)",
              background:
                "linear-gradient(135deg, rgba(18, 18, 28, 0.95), rgba(8, 8, 14, 0.98))",
              padding: "12px 16px",
              textAlign: "left",
              boxShadow: "0 12px 40px rgba(0, 0, 0, 0.35)",
              cursor: "pointer",
              position: "relative",
              overflow: "hidden",
            }}
          >
            <div
              style={{
                position: "absolute",
                inset: 0,
                background:
                  "radial-gradient(circle at 80% 20%, rgba(212,175,55,0.15), transparent 55%)",
              }}
            />
            <p
              style={{
                margin: 0,
                fontSize: 14,
                fontWeight: 600,
                color: "#f5e6b8",
                position: "relative",
              }}
            >
              {widgetConfig.greeting}
            </p>
            <p
              style={{
                margin: "4px 0 0",
                fontSize: 12,
                lineHeight: "20px",
                color: "#a1a1aa",
                position: "relative",
              }}
            >
              Ask about my education, skills, and projects.
            </p>
          </button>
        )}

        <div style={{ position: "relative", width: LAUNCHER_SIZE, height: LAUNCHER_SIZE }}>
          {!isPanelMounted && <div className="chatbot-launcher-ring" aria-hidden="true" />}
          <button
            type="button"
            onClick={toggleChat}
            aria-label={isPanelMounted ? "Close chat widget" : "Open chat widget"}
            aria-expanded={isPanelMounted}
            className={!isPanelMounted ? "chatbot-launcher" : ""}
            style={{
              position: "relative",
              width: LAUNCHER_SIZE,
              height: LAUNCHER_SIZE,
              borderRadius: "50%",
              border: "1px solid rgba(212, 175, 55, 0.35)",
              background:
                "radial-gradient(circle at 30% 20%, rgba(255,248,231,0.25), transparent 45%), linear-gradient(145deg, #1a1a24, #050508)",
              color: "#f5e6b8",
              cursor: "pointer",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              boxShadow: "0 12px 30px rgba(0, 0, 0, 0.45)",
              flexShrink: 0,
            }}
          >
            <LauncherIcons isOpen={isPanelMounted} />
          </button>
        </div>
      </div>
    </>,
    document.body,
  );
}
