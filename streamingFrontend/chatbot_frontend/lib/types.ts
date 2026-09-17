export type ChatMessage = {
  role: string;
  content: string;
};

export type AccessStatus = {
  verified: boolean;
  message_count: number;
  free_limit: number;
  requires_verification: boolean;
  can_chat: boolean;
  lead_submitted: boolean;
  hiring_interest_sent?: boolean;
  remaining_free_messages: number | null;
};

export type UiEvent = {
  type: "hiring_interest_sent";
  launcher_mood: "happy";
};

export type ChatResponse = {
  message: string;
  chat_history: ChatMessage[];
  access?: AccessStatus;
  ui_event?: UiEvent;
};

export type ChatHistoryResponse = {
  chat_history: ChatMessage[];
  access?: AccessStatus;
};

export type LeadRequest = {
  session_id: string;
  name: string;
  email: string;
  company: string;
  designation: string;
};

export type VerifyOtpRequest = {
  session_id: string;
  otp: string;
};

export type LeadResponse = {
  message: string;
  access: AccessStatus;
};

export type AccessResponse = {
  access: AccessStatus;
};

export type ApiErrorDetail = {
  message?: string;
  access?: AccessStatus;
};
