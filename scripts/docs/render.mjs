// Render active Markdown using stored Draw.io PNG exports, with theme-aware preview.
import fs from "node:fs/promises";
import path from "node:path";
import http from "node:http";
import { createRequire } from "node:module";
import { pathToFileURL } from "node:url";
const args = process.argv.slice(2);
const opt = (n, d) => {
  const i = args.indexOf(n);
  return i < 0 ? d : args[i + 1];
};
const root = path.resolve(opt("--root", "."));
const deps = path.resolve(root, opt("--dependency-root", "scripts/docs"));
const out = path.resolve(root, opt("--output", ".jane/doc-render/pages"));
if (!out.startsWith(root + path.sep + ".jane" + path.sep)) throw Error("Output must be under .jane");
const require = createRequire(path.join(deps, "package.json"));
const { marked } = await import(pathToFileURL(require.resolve("marked")).href);
const { default: hljs } = await import(pathToFileURL(require.resolve("highlight.js")).href);
const { chromium } = require("playwright");
async function walk(p) {
  const st = await fs.stat(p);
  if (st.isFile()) return p.endsWith(".md") ? [p] : [];
  let result = [];
  for (const e of await fs.readdir(p, { withFileTypes: true }))
    if (e.isDirectory() || e.name.endsWith(".md")) result.push(...(await walk(path.join(p, e.name))));
  return result.sort();
}
const index = args.indexOf("--paths");
let selected =
  index < 0
    ? ["README.md", "docs/development/documentation-style.md"]
    : args
        .slice(index + 1)
        .filter((x, i, a) => !x.startsWith("--") && !a.slice(0, i).some((v) => v.startsWith("--")));
let files = [];
for (const name of selected) files.push(...(await walk(path.resolve(root, name))));
if (args.includes("--all-diagrams"))
  for (const p of await walk(root + "/docs"))
    if ((await fs.readFile(p, "utf8")).includes(".light.png")) files.push(p);
files = [...new Set(files)];
await fs.mkdir(out, { recursive: true });
const esc = (s) =>
  String(s)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;");
const slug = (s) =>
  s
    .replace(/!?\[([^\]]*)\]\([^)]*\)/g, "$1")
    .replace(/[`*~]/g, "")
    .toLowerCase()
    .replace(/[^\p{L}\p{N}\p{M}\-_ ]/gu, "")
    .replaceAll(" ", "-");
let current, theme, headings;
const renderer = new marked.Renderer();
renderer.heading = ({ tokens, depth }) => {
  const raw = tokens.map((t) => t.raw).join("");
  const id = slug(raw),
    n = headings.get(id) || 0;
  headings.set(id, n + 1);
  return `<h${depth} id="${esc(id + (n ? "-" + n : ""))}">${marked.parseInline(raw)}</h${depth}>`;
};
renderer.code = ({ text, lang }) => {
  const language = (lang || "text").split(/\s/)[0];
  if (language === "mermaid") throw Error("Use Draw.io source and PNG exports");
  if (["text", "console"].includes(language)) return `<pre><code>${esc(text)}</code></pre>`;
  if (!hljs.getLanguage(language)) throw Error("Unsupported code language " + language);
  return `<pre><code class="hljs language-${esc(language)}">${hljs.highlight(text, { language }).value}</code></pre>`;
};
renderer.image = ({ href, text }) => {
  if (/^https?:/.test(href)) throw Error("Remote images not allowed in local preview");
  const target = path.resolve(
    path.dirname(current),
    decodeURIComponent(href.split("#")[0]).replace(
      /\.light\.png$/,
      theme === "dark" ? ".dark.png" : ".light.png",
    ),
  );
  if (!target.startsWith(root + path.sep)) throw Error("Image leaves checkout");
  return `<img src="/repo/${encodeURI(path.relative(root, target).split(path.sep).join("/"))}" alt="${esc(text)}">`;
};
marked.use({ renderer });
const mime = { ".html": "text/html", ".js": "text/javascript", ".css": "text/css", ".png": "image/png" };
const server = http.createServer(async (req, res) => {
  try {
    const u = decodeURIComponent(req.url.split("?")[0]);
    const base = u.startsWith("/repo/") ? root : out;
    const file = path.resolve(base, u.startsWith("/repo/") ? u.slice(6) : u.slice(1));
    const real = await fs.realpath(file);
    if (!real.startsWith(base + path.sep)) throw Error("outside root");
    res.setHeader("Content-Type", mime[path.extname(file)] || "application/octet-stream");
    res.end(await fs.readFile(real));
  } catch {
    res.writeHead(404);
    res.end();
  }
});
await new Promise((r) => server.listen(0, "127.0.0.1", r));
let browser;
const reports = [];
try {
  browser = await chromium.launch({
    headless: true,
    ...(opt("--browser-executable", null) ? { executablePath: opt("--browser-executable") } : {}),
  });
  const page = await browser.newPage({ viewport: { width: 1440, height: 1000 } });
  const origin = "http://127.0.0.1:" + server.address().port;
  await page.route("**/*", (r) => (new URL(r.request().url()).origin === origin ? r.continue() : r.abort()));
  for (const [i, file] of files.entries())
    for (const t of args.includes("--both-themes") ? ["light", "dark"] : ["light"]) {
      current = file;
      theme = t;
      headings = new Map();
      const content = await fs.readFile(file, "utf8");
      const css = await fs.readFile(
        path.join(
          deps,
          "node_modules/highlight.js/styles",
          theme === "dark" ? "github-dark.css" : "github.css",
        ),
        "utf8",
      );
      const html = `<!doctype html><meta charset="utf-8"><style>${css}body{font:16px/1.6 system-ui,sans-serif;color:${theme === "dark" ? "#e2e8f0" : "#172554"};background:${theme === "dark" ? "#111827" : "#fff"};max-width:1120px;margin:32px auto;padding:0 32px}h1,h2,h3{line-height:1.25}h2{margin-top:40px}a{color:${theme === "dark" ? "#93c5fd" : "#2563eb"}}table{border-collapse:collapse;width:100%;font-size:14px}td,th{border:1px solid #64748b;padding:8px;text-align:left}pre{padding:18px;background:${theme === "dark" ? "#1f2937" : "#f6f8fa"};overflow:auto}img{display:block;max-width:100%;height:auto;margin:20px auto}code{font-family:Consolas,monospace}</style>${marked.parse(content)}`;
      const stem = String(i).padStart(3, "0") + "-" + theme;
      await fs.writeFile(out + "/" + stem + ".html", html);
      await page.goto(origin + "/" + stem + ".html");
      await page.evaluate(async () =>
        Promise.all([...document.images].map((x) => x.decode().catch(() => {}))),
      );
      const result = await page.evaluate(() => ({
        images: document.images.length,
        missingImages: [...document.images].filter((x) => !x.complete || !x.naturalWidth).map((x) => x.src),
        codeBlocks: document.querySelectorAll("code.hljs").length,
        highlightedTokens: document.querySelectorAll("code.hljs span").length,
        tables: document.querySelectorAll("table").length,
        missingAnchors: [...document.querySelectorAll('a[href^="#"]')]
          .filter((a) => !document.getElementById(decodeURIComponent(a.getAttribute("href").slice(1))))
          .map((a) => a.getAttribute("href")),
        overflow: document.documentElement.scrollWidth > window.innerWidth,
      }));
      await page.screenshot({ path: out + "/" + stem + ".png", fullPage: true });
      reports.push({
        source: path.relative(root, file).replaceAll("\\", "/"),
        theme,
        ...result,
        screenshot: path.relative(root, out + "/" + stem + ".png").replaceAll("\\", "/"),
      });
      console.log(
        `${result.missingImages.length || result.missingAnchors.length || result.overflow ? "FAIL" : "OK"} ${reports.at(-1).source} ${theme}: ${result.images} diagrams, ${result.codeBlocks} code blocks`,
      );
    }
  await fs.writeFile(
    out + "/render-evidence.json",
    JSON.stringify(
      { browser: browser.version(), format: "Draw.io PNG", mode: "actual-render", reports },
      null,
      2,
    ) + "\n",
  );
  if (reports.some((r) => r.missingImages.length || r.missingAnchors.length || r.overflow))
    process.exitCode = 1;
} finally {
  if (browser) await browser.close();
  await new Promise((r) => server.close(r));
}
