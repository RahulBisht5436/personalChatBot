"use client";

import dynamic from "next/dynamic";

import "./chat-widget.css";

const ChatWidget = dynamic(() => import("./ChatWidget"), {
  ssr: false,
});

type ChatWidgetMountProps = {
  apiUrl?: string;
  inIframeEmbed?: boolean;
};

export default function ChatWidgetMount({
  apiUrl,
  inIframeEmbed = false,
}: ChatWidgetMountProps) {
  return <ChatWidget apiUrl={apiUrl} inIframeEmbed={inIframeEmbed} />;
}
