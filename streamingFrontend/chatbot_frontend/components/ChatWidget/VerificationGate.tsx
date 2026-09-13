"use client";

import { useState } from "react";

import { submitLead, verifyOtp } from "@/lib/chatbot-api";
import type { AccessStatus } from "@/lib/types";

type VerificationGateProps = {
  apiUrl: string;
  sessionId: string;
  access: AccessStatus;
  onVerified: (access: AccessStatus) => void;
};

export default function VerificationGate({
  apiUrl,
  sessionId,
  access,
  onVerified,
}: VerificationGateProps) {
  const [step, setStep] = useState<"details" | "otp">(
    access.lead_submitted ? "otp" : "details",
  );
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [company, setCompany] = useState("");
  const [designation, setDesignation] = useState("");
  const [otp, setOtp] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [info, setInfo] = useState<string | null>(null);

  async function handleLeadSubmit(event: React.FormEvent) {
    event.preventDefault();
    setIsSubmitting(true);
    setError(null);
    setInfo(null);

    try {
      const result = await submitLead(apiUrl, {
        session_id: sessionId,
        name,
        email,
        company,
        designation,
      });
      setInfo(result.message);
      setStep("otp");
      onVerified(result.access);
    } catch (submitError) {
      setError(
        submitError instanceof Error
          ? submitError.message
          : "Could not submit your details.",
      );
    } finally {
      setIsSubmitting(false);
    }
  }

  async function handleOtpSubmit(event: React.FormEvent) {
    event.preventDefault();
    setIsSubmitting(true);
    setError(null);
    setInfo(null);

    try {
      const result = await verifyOtp(apiUrl, {
        session_id: sessionId,
        otp,
      });
      setInfo(result.message);
      onVerified(result.access);
    } catch (verifyError) {
      setError(
        verifyError instanceof Error
          ? verifyError.message
          : "Could not verify OTP.",
      );
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <div className="rounded-2xl border border-amber-200/25 bg-[#14141f]/95 p-4 shadow-lg">
      <p className="text-[15px] font-semibold text-white">
        Continue the conversation
      </p>
      <p className="mt-1 text-[14px] font-medium leading-7 text-zinc-100">
        You have used your {access.free_limit} free messages. Share a few details
        and verify your email to keep chatting.
      </p>

      {step === "details" ? (
        <form onSubmit={handleLeadSubmit} className="mt-4 space-y-3">
          <input
            value={name}
            onChange={(event) => setName(event.target.value)}
            placeholder="Your name"
            required
            className="chatbot-input w-full rounded-xl border border-zinc-500/40 bg-[#1a1a24] px-3 py-2.5 text-sm font-medium text-white outline-none placeholder:text-zinc-300 focus:border-amber-300/50"
          />
          <input
            value={email}
            onChange={(event) => setEmail(event.target.value)}
            placeholder="Email address"
            type="email"
            required
            className="chatbot-input w-full rounded-xl border border-zinc-500/40 bg-[#1a1a24] px-3 py-2.5 text-sm font-medium text-white outline-none placeholder:text-zinc-300 focus:border-amber-300/50"
          />
          <input
            value={company}
            onChange={(event) => setCompany(event.target.value)}
            placeholder="Company"
            required
            className="chatbot-input w-full rounded-xl border border-zinc-500/40 bg-[#1a1a24] px-3 py-2.5 text-sm font-medium text-white outline-none placeholder:text-zinc-300 focus:border-amber-300/50"
          />
          <input
            value={designation}
            onChange={(event) => setDesignation(event.target.value)}
            placeholder="Designation you are looking for"
            required
            className="chatbot-input w-full rounded-xl border border-zinc-500/40 bg-[#1a1a24] px-3 py-2.5 text-sm font-medium text-white outline-none placeholder:text-zinc-300 focus:border-amber-300/50"
          />
          <button
            type="submit"
            disabled={isSubmitting}
            className="w-full rounded-full border border-amber-300/45 bg-[#4a3f24] px-4 py-2.5 text-sm font-semibold text-white transition hover:bg-[#5c4f2c] disabled:opacity-50"
          >
            {isSubmitting ? "Sending OTP..." : "Send OTP"}
          </button>
        </form>
      ) : (
        <form onSubmit={handleOtpSubmit} className="mt-4 space-y-3">
          <input
            value={otp}
            onChange={(event) => setOtp(event.target.value)}
            placeholder="Enter 6-digit OTP"
            inputMode="numeric"
            maxLength={6}
            required
            className="chatbot-input w-full rounded-xl border border-zinc-500/40 bg-[#1a1a24] px-3 py-2.5 text-sm font-medium tracking-[0.3em] text-white outline-none placeholder:text-zinc-300 focus:border-amber-300/50"
          />
          <button
            type="submit"
            disabled={isSubmitting}
            className="w-full rounded-full border border-amber-300/45 bg-[#4a3f24] px-4 py-2.5 text-sm font-semibold text-white transition hover:bg-[#5c4f2c] disabled:opacity-50"
          >
            {isSubmitting ? "Verifying..." : "Verify OTP"}
          </button>
          <button
            type="button"
            onClick={() => setStep("details")}
            className="w-full text-sm font-medium text-amber-100/80 transition hover:text-amber-50"
          >
            Edit details and resend OTP
          </button>
        </form>
      )}

      {info && <p className="mt-3 text-sm font-medium text-emerald-300">{info}</p>}
      {error && <p className="mt-3 text-sm font-medium text-red-300">{error}</p>}
    </div>
  );
}
