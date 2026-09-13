import ChatWidgetMount from "@/components/ChatWidget/ChatWidgetMount";

export default function SiteLayout({ children }: LayoutProps<"/">) {
  return (
    <div className="min-h-full bg-zinc-50 text-zinc-950">
      {children}
      <ChatWidgetMount />
    </div>
  );
}
