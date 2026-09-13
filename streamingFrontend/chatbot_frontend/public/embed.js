(function () {
  if (window.StreamingChatbot?.initialized) {
    return;
  }

  var script = document.currentScript;
  if (!script) {
    return;
  }

  var widgetOrigin =
    script.getAttribute("data-widget-origin") || "http://localhost:3000";
  var apiUrl =
    script.getAttribute("data-api-url") || "http://127.0.0.1:8000";

  var closedStyle = {
    container:
      "position:fixed!important;bottom:0!important;right:0!important;top:auto!important;left:auto!important;width:420px!important;height:180px!important;max-width:none!important;max-height:none!important;margin:0!important;padding:0!important;border:0!important;background:transparent!important;z-index:2147483647!important;pointer-events:none!important;overflow:visible!important;",
    iframe:
      "display:block!important;width:100%!important;height:100%!important;max-width:none!important;max-height:none!important;margin:0!important;padding:0!important;border:0!important;background:transparent!important;pointer-events:auto!important;opacity:1!important;visibility:visible!important;",
  };

  var openStyle = {
    container:
      "position:fixed!important;inset:0!important;top:0!important;right:0!important;bottom:0!important;left:0!important;width:100%!important;height:100%!important;max-width:none!important;max-height:none!important;margin:0!important;padding:0!important;border:0!important;background:transparent!important;z-index:2147483647!important;pointer-events:none!important;overflow:visible!important;",
    iframe:
      "display:block!important;width:100%!important;height:100%!important;max-width:none!important;max-height:none!important;margin:0!important;padding:0!important;border:0!important;background:transparent!important;pointer-events:auto!important;opacity:1!important;visibility:visible!important;",
  };

  var protect = document.createElement("style");
  protect.id = "streaming-chatbot-protect";
  protect.textContent =
    "#streaming-chatbot-root,#streaming-chatbot-root iframe{box-sizing:border-box!important;}";
  document.head.appendChild(protect);

  var container = document.createElement("div");
  container.id = "streaming-chatbot-root";
  container.style.cssText = closedStyle.container;

  var iframe = document.createElement("iframe");
  iframe.title = "Streaming Chatbot";
  iframe.src =
    widgetOrigin +
    "/embed/chat?apiUrl=" +
    encodeURIComponent(apiUrl) +
    "&v=5";
  iframe.setAttribute("allowtransparency", "true");
  iframe.style.cssText = closedStyle.iframe;
  iframe.allow = "clipboard-write";

  container.appendChild(iframe);
  document.body.appendChild(container);

  function setIframeSize(isOpen) {
    var styles = isOpen ? openStyle : closedStyle;
    container.style.cssText = styles.container;
    iframe.style.cssText = styles.iframe;
  }

  window.addEventListener("message", function (event) {
    if (event.origin !== new URL(widgetOrigin).origin) {
      return;
    }

    if (
      event.data &&
      event.data.type === "streaming-chatbot-resize" &&
      typeof event.data.open === "boolean"
    ) {
      setIframeSize(event.data.open);
    }
  });

  window.StreamingChatbot = {
    initialized: true,
    widgetOrigin: widgetOrigin,
    apiUrl: apiUrl,
    setOpen: setIframeSize,
  };
})();
