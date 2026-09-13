import type {
  AccessResponse,
  AccessStatus,
  ApiErrorDetail,
  ChatHistoryResponse,
  ChatMessage,
  ChatResponse,
  LeadRequest,
  LeadResponse,
  VerifyOtpRequest,
} from "./types";

const DEFAULT_API_URL = "http://127.0.0.1:8000";

export function getDefaultApiUrl(): string {
  return process.env.NEXT_PUBLIC_API_URL ?? DEFAULT_API_URL;
}

export async function fetchAccessStatus(
  apiUrl: string,
  sessionId: string,
): Promise<AccessStatus> {
  const response = await fetch(
    `${apiUrl}/chatbot/access?session_id=${encodeURIComponent(sessionId)}`,
  );

  if (!response.ok) {
    throw new Error("Failed to load access status");
  }

  const data = (await response.json()) as AccessResponse;
  return data.access;
}

export async function fetchChatHistory(
  apiUrl: string,
  sessionId: string,
): Promise<{ chatHistory: ChatMessage[]; access?: AccessStatus }> {
  const response = await fetch(
    `${apiUrl}/chatbot/history?session_id=${encodeURIComponent(sessionId)}`,
  );

  if (!response.ok) {
    throw new Error("Failed to load chat history");
  }

  const data = (await response.json()) as ChatHistoryResponse;
  return { chatHistory: data.chat_history, access: data.access };
}

export async function sendChatMessage(
  apiUrl: string,
  sessionId: string,
  userMessage: string,
): Promise<ChatResponse> {
  const response = await fetch(`${apiUrl}/chatbot/`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      user_message: userMessage,
      session_id: sessionId,
    }),
  });

  const data = (await response.json()) as ChatResponse | { detail: ApiErrorDetail | string };

  if (!response.ok) {
    const detail = (data as { detail?: ApiErrorDetail | string }).detail;
    const access =
      typeof detail === "object" && detail?.access ? detail.access : undefined;
    const message =
      typeof detail === "object" && detail?.message
        ? detail.message
        : "Failed to send message";
    const error = new Error(message) as Error & { access?: AccessStatus };
    error.access = access;
    throw error;
  }

  return data as ChatResponse;
}

export async function submitLead(
  apiUrl: string,
  payload: LeadRequest,
): Promise<LeadResponse> {
  const response = await fetch(`${apiUrl}/chatbot/lead`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });

  const data = (await response.json()) as LeadResponse | { detail?: string };

  if (!response.ok) {
    throw new Error(
      typeof (data as { detail?: string }).detail === "string"
        ? (data as { detail: string }).detail
        : "Failed to submit details",
    );
  }

  return data as LeadResponse;
}

export async function verifyOtp(
  apiUrl: string,
  payload: VerifyOtpRequest,
): Promise<LeadResponse> {
  const response = await fetch(`${apiUrl}/chatbot/verify-otp`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });

  const data = (await response.json()) as LeadResponse | { detail?: string };

  if (!response.ok) {
    throw new Error(
      typeof (data as { detail?: string }).detail === "string"
        ? (data as { detail: string }).detail
        : "Failed to verify OTP",
    );
  }

  return data as LeadResponse;
}
