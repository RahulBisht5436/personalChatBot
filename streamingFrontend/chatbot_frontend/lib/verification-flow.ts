export type VerificationStep =
  | "none"
  | "name"
  | "email"
  | "company"
  | "designation"
  | "otp";

export type PendingLead = {
  name: string;
  email: string;
  company: string;
  designation: string;
};

const EMAIL_PATTERN = /^[^@\s]+@[^@\s]+\.[^@\s]+$/;

export function getVerificationPlaceholder(step: VerificationStep): string {
  switch (step) {
    case "name":
      return "Enter your name";
    case "email":
      return "Enter your email address";
    case "company":
      return "Enter your company name";
    case "designation":
      return "Enter your role or designation";
    case "otp":
      return "Enter 6-digit verification code";
    default:
      return "Type your message...";
  }
}

export function getNextVerificationStep(
  step: VerificationStep,
): VerificationStep | null {
  switch (step) {
    case "name":
      return "email";
    case "email":
      return "company";
    case "company":
      return "designation";
    case "designation":
      return "otp";
    default:
      return null;
  }
}

export function getAssistantVerificationReply(
  step: VerificationStep,
  lead: PendingLead,
  freeLimit: number,
): string | null {
  switch (step) {
    case "name":
      return `You've used your ${freeLimit} free messages. To keep chatting, I need a few quick details.\n\nFirst, what's your **name**?`;
    case "email":
      return `Thanks, ${lead.name}! What's your **email address**?`;
    case "company":
      return "Which **company** are you from?";
    case "designation":
      return "And what **role** or designation are you looking for?";
    case "otp":
      return `I've sent a 6-digit verification code to **${lead.email}**. Please enter it here to continue.`;
    default:
      return null;
  }
}

export function validateVerificationInput(
  step: VerificationStep,
  value: string,
): string | null {
  const trimmed = value.trim();

  if (!trimmed) {
    return "Please enter a value to continue.";
  }

  if (step === "email" && !EMAIL_PATTERN.test(trimmed)) {
    return "Please enter a valid email address.";
  }

  if (step === "otp" && !/^\d{4,8}$/.test(trimmed)) {
    return "Please enter the verification code from your email.";
  }

  return null;
}

export function applyVerificationInput(
  step: VerificationStep,
  value: string,
  lead: PendingLead,
): PendingLead {
  const trimmed = value.trim();

  switch (step) {
    case "name":
      return { ...lead, name: trimmed };
    case "email":
      return { ...lead, email: trimmed.toLowerCase() };
    case "company":
      return { ...lead, company: trimmed };
    case "designation":
      return { ...lead, designation: trimmed };
    default:
      return lead;
  }
}
