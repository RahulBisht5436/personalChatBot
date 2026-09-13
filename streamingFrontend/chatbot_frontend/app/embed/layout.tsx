import type { Metadata } from "next";

import "@/components/ChatWidget/chat-widget.css";

export const metadata: Metadata = {
  title: "Chatbot Widget",
  description: "Embeddable streaming chatbot widget",
};

export default function EmbedLayout({ children }: LayoutProps<"/embed">) {
  return (
    <div className="h-full min-h-screen overflow-hidden bg-transparent">
      {children}
    </div>
  );
}
