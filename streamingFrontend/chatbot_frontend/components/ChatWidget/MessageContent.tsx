import React from "react";

const LINK_PATTERN =
  /(\[[^\]]+\]\(https?:\/\/[^\s)]+\)|https?:\/\/[^\s<>"\]]+)/g;
const MARKDOWN_LINK_PATTERN = /^\[([^\]]+)\]\((https?:\/\/[^\s)]+)\)$/;

function renderLink(href: string, label: string, key: string) {
  return (
    <a
      key={key}
      href={href}
      target="_blank"
      rel="noopener noreferrer"
      className="chatbot-message-link font-semibold text-amber-300 underline decoration-amber-300/60 underline-offset-2 transition hover:text-amber-200"
    >
      {label}
    </a>
  );
}

export function MessageContent({ content }: { content: string }) {
  const parts = content.split(LINK_PATTERN);

  return (
    <>
      {parts.map((part, index) => {
        if (!part) {
          return null;
        }

        const markdownMatch = MARKDOWN_LINK_PATTERN.exec(part);
        if (markdownMatch) {
          return renderLink(markdownMatch[2], markdownMatch[1], `md-${index}`);
        }

        if (/^https?:\/\//.test(part)) {
          return renderLink(part, part, `url-${index}`);
        }

        return <React.Fragment key={`text-${index}`}>{part}</React.Fragment>;
      })}
    </>
  );
}
