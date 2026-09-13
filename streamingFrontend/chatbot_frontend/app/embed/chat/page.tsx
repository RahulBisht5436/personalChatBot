"use client";

import { Suspense } from "react";
import { useSearchParams } from "next/navigation";

import EmbedBodyStyles from "@/components/ChatWidget/EmbedBodyStyles";
import ChatWidgetMount from "@/components/ChatWidget/ChatWidgetMount";
import { getDefaultApiUrl } from "@/lib/chatbot-api";

function EmbedChatContent() {
  const searchParams = useSearchParams();
  const apiUrl = searchParams.get("apiUrl") ?? getDefaultApiUrl();

  return (
    <>
      <EmbedBodyStyles />
      <ChatWidgetMount apiUrl={apiUrl} inIframeEmbed />
    </>
  );
}

export default function EmbedChatPage() {
  return (
    <Suspense fallback={null}>
      <EmbedChatContent />
    </Suspense>
  );
}
