// Evidence run: bun run.mjs <label> <base url> <out dir>
import { chromium } from "playwright";
import { mkdirSync, writeFileSync } from "node:fs";

const [label, base, out] = process.argv.slice(2);
mkdirSync(out, { recursive: true });
const launch = (args) => chromium.launch({ channel: "chrome", headless: true, args: ["--enable-unsafe-webgpu", ...args] });
const open = async (browser, query) => {
  const page = await browser.newPage({ viewport: { width: 1280, height: 760 } });
  await page.goto(`${base}/examples/evidence.html${query}`);
  await page.waitForFunction(() => window.ready, null, { timeout: 300000 });
  await page.waitForTimeout(3000);
  return page;
};
const lines = (timeline) =>
  timeline
    .toSorted((a, b) => a.ms - b.ms)
    .map(({ ms, kind, detail }) => `${String(ms).padStart(6)} ms  ${kind}: ${detail}`)
    .join("\n");
const settled = (page, busy) =>
  page.waitForFunction(
    (busy) => {
      const drawn = window.timeline.filter(({ kind }) => kind === "frame painted with status");
      return drawn.length > 0 && !drawn.at(-1).detail.startsWith(busy);
    },
    busy,
    { timeout: 300000 },
  );

if (!process.env.SKIP_E1)
// E1: element labels with the page's Arial added through `fonts` (addFont).
{
  const browser = await launch(["--force-device-scale-factor=2"]);
  const page = await open(browser, "?arial&smiles=" + encodeURIComponent("[RaH2].[GaH3].[AtH].[RgH].[TaH5]"));
  await page.screenshot({ path: `${out}/e1-${label}-arial-added.png`, clip: { x: 250, y: 340, width: 660, height: 140 } });
  await browser.close();
}

// E5: open a large drawing by dropping its file, then export it as a PDF figure.
{
  const browser = await launch([]);
  const page = await open(browser, "?smiles=" + encodeURIComponent("NC(C)C(=O)".repeat(100) + "O"));
  await page.evaluate(() => window.dropSaved("evidence-big.rsk", 20));
  await page.waitForFunction(() => window.timeline.some(({ kind }) => kind === "long task"), null, { timeout: 120000 });
  await page.waitForTimeout(6000);
  const opened = await page.evaluate(() => window.timeline);
  writeFileSync(`${out}/e5-${label}-open.txt`, `${label}: drop evidence-big.rsk (20 copies of a 100-residue peptide, 10 020 atoms) on the editor\n${lines(opened)}\n`);

  // Export tab, then "Export PDF…".
  await page.mouse.move(1248, 123, { steps: 5 });
  await page.mouse.down();
  await page.mouse.up();
  await page.waitForTimeout(4000);
  await page.evaluate(() => window.restart());
  await page.mouse.move(1120, 624, { steps: 5 });
  await page.mouse.down();
  await page.mouse.up();
  await page.waitForFunction(() => window.timeline.some(({ kind }) => kind === "long task" || kind === "status set"), null, { timeout: 60000 });
  await page.waitForTimeout(8000);
  const exported = await page.evaluate(() => window.timeline);
  writeFileSync(`${out}/e5-${label}-export.txt`, `${label}: click Export PDF… for the same drawing\n${lines(exported)}\n`);
  await page.screenshot({ path: `${out}/e5-${label}-after-export.png` });
  await browser.close();
}
