"use client";

import { useEffect } from "react";

export default function EmbedBodyStyles() {
  useEffect(() => {
    const html = document.documentElement;
    const body = document.body;

    const previous = {
      htmlPointerEvents: html.style.pointerEvents,
      htmlBackground: html.style.background,
      bodyPointerEvents: body.style.pointerEvents,
      bodyBackground: body.style.background,
      bodyOverflow: body.style.overflow,
      bodyMargin: body.style.margin,
    };

    html.style.pointerEvents = "none";
    html.style.background = "transparent";
    html.style.width = "100%";
    html.style.height = "100%";
    html.style.margin = "0";
    html.style.padding = "0";
    body.style.pointerEvents = "none";
    body.style.background = "transparent";
    body.style.overflow = "hidden";
    body.style.margin = "0";
    body.style.padding = "0";
    body.style.width = "100%";
    body.style.height = "100%";

    return () => {
      html.style.pointerEvents = previous.htmlPointerEvents;
      html.style.background = previous.htmlBackground;
      body.style.pointerEvents = previous.bodyPointerEvents;
      body.style.background = previous.bodyBackground;
      body.style.overflow = previous.bodyOverflow;
      body.style.margin = previous.bodyMargin;
    };
  }, []);

  return null;
}
