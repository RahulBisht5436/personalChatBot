import { chromium } from "playwright";

const externalUrl =
  process.env.EMBED_TEST_URL ?? "http://127.0.0.1:5500/main.html";

const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 1280, height: 800 } });
const errors = [];

page.on("pageerror", (error) => errors.push(`page: ${error.message}`));
page.on("console", (msg) => {
  if (msg.type() === "error") {
    errors.push(`console: ${msg.text()}`);
  }
});

await page.goto(externalUrl, { waitUntil: "networkidle", timeout: 60000 });
await page.waitForTimeout(2500);

const parentDiag = await page.evaluate(() => {
  const root = document.getElementById("streaming-chatbot-root");
  const iframe = root?.querySelector("iframe");
  const rootRect = root?.getBoundingClientRect();
  const iframeRect = iframe?.getBoundingClientRect();

  return {
    hasRoot: Boolean(root),
    hasProtect: Boolean(document.getElementById("streaming-chatbot-protect")),
    rootWidth: rootRect?.width ?? 0,
    rootHeight: rootRect?.height ?? 0,
    iframeWidth: iframeRect?.width ?? 0,
    iframeHeight: iframeRect?.height ?? 0,
    viewportWidth: window.innerWidth,
    viewportHeight: window.innerHeight,
    iframeSrc: iframe?.src ?? null,
  };
});

const embedFrame = page
  .frames()
  .find((frame) => frame.url().includes("/embed/chat"));

if (!embedFrame) {
  console.error("FAIL: embed iframe not found");
  console.log(JSON.stringify({ parentDiag, errors }, null, 2));
  await browser.close();
  process.exit(1);
}

const iframeDiag = await embedFrame.evaluate(() => {
  const styles = Array.from(document.styleSheets).map((sheet) => {
    try {
      return sheet.href ?? "inline";
    } catch {
      return "blocked";
    }
  });

  return {
    stylesheetCount: document.styleSheets.length,
    hasChatWidgetCss: styles.some((href) =>
      String(href).includes("chat-widget"),
    ),
    hasGlobalsCss: styles.some((href) => String(href).includes("globals")),
  };
});

const launcher = page
  .frameLocator("#streaming-chatbot-root iframe")
  .getByRole("button", { name: "Open chat widget" });

await launcher.waitFor({ state: "visible", timeout: 10000 });

const closedDiag = {
  rootWidth: parentDiag.rootWidth,
  rootHeight: parentDiag.rootHeight,
};

const helloClickable = await page.locator("h1").click({ timeout: 2000 }).then(
  () => true,
  () => false,
);

await launcher.click();
await page.waitForTimeout(900);

const openParentDiag = await page.evaluate(() => {
  const root = document.getElementById("streaming-chatbot-root");
  const rect = root?.getBoundingClientRect();
  return {
    rootWidth: rect?.width ?? 0,
    rootHeight: rect?.height ?? 0,
    viewportWidth: window.innerWidth,
    viewportHeight: window.innerHeight,
  };
});

const openDiag = await embedFrame.evaluate(() => {
  const title = document.querySelector(".chatbot-title-shimmer");
  const rect = title?.getBoundingClientRect();

  return {
    hasPanelTitle: Boolean(title),
    centeredHorizontally:
      rect != null
        ? Math.abs(rect.left + rect.width / 2 - window.innerWidth / 2) < 80
        : false,
  };
});

await page.screenshot({
  path: "scripts/playwright-external-result.png",
});

await browser.close();

const checks = {
  compactIframeWhenClosed: closedDiag.rootWidth <= 430 && closedDiag.rootHeight <= 200,
  fullScreenIframeWhenOpen:
    Math.abs(openParentDiag.rootWidth - openParentDiag.viewportWidth) < 2 &&
    Math.abs(openParentDiag.rootHeight - openParentDiag.viewportHeight) < 2,
  protectStyles: parentDiag.hasProtect,
  cssLoaded: iframeDiag.hasChatWidgetCss && iframeDiag.hasGlobalsCss,
  launcherVisible: true,
  hostPageClickableWhenClosed: helloClickable,
  panelOpensCentered: openDiag.hasPanelTitle && openDiag.centeredHorizontally,
  noErrors: errors.length === 0,
};

console.log(
  JSON.stringify(
    {
      externalUrl,
      parentDiag,
      closedDiag,
      openParentDiag,
      iframeDiag,
      openDiag,
      checks,
      errors,
    },
    null,
    2,
  ),
);

const passed = Object.values(checks).every(Boolean);
process.exit(passed ? 0 : 1);
