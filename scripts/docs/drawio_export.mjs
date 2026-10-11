// Draw.io source -> transparent PNG in both themes, rendered by its mxGraph model.
import fs from "node:fs/promises";
import path from "node:path";
import http from "node:http";
import crypto from "node:crypto";
import { chromium } from "playwright";
const args = process.argv.slice(2);
const opt = (n, d) => {
  let i = args.indexOf(n);
  return i < 0 ? d : args[i + 1];
};
const root = path.resolve(opt("--root", "."));
const target = path.resolve(root, opt("--path", "docs/diagrams"));
const browserPath = opt("--browser-executable", null);
const check = args.includes("--check");
async function walk(p) {
  const st = await fs.stat(p);
  if (st.isFile()) return p.endsWith(".drawio") ? [p] : [];
  let result = [];
  for (const e of await fs.readdir(p, { withFileTypes: true }))
    if (e.isDirectory() || e.name.endsWith(".drawio")) result.push(...(await walk(path.join(p, e.name))));
  return result.sort();
}
const files = await walk(target);
if (!files.length) throw new Error("No Draw.io sources");
const html = `<!doctype html><meta charset="utf-8"><style>html,body{margin:0;background:transparent}#graph{position:relative;overflow:visible;width:12000px;height:12000px}svg{overflow:visible}</style><script>var mxBasePath='/scripts/docs/node_modules/mxgraph/javascript/src';var mxLoadResources=false;var mxLoadStylesheets=false;</script><script src="/scripts/docs/node_modules/mxgraph/javascript/mxClient.js"></script><div id="graph"></div><script>window.ready=true;</script>`;
const server = http.createServer(async (req, res) => {
  try {
    if (req.url === "/") {
      res.setHeader("Content-Type", "text/html");
      res.end(html);
      return;
    }
    const requested = path.resolve(root, "." + decodeURIComponent(req.url.split("?")[0]));
    const real = await fs.realpath(requested);
    if (!real.startsWith(root + path.sep)) throw Error("outside root");
    res.setHeader("Content-Type", requested.endsWith(".js") ? "text/javascript" : "application/octet-stream");
    res.end(await fs.readFile(real));
  } catch {
    res.writeHead(404);
    res.end();
  }
});
await new Promise((r) => server.listen(0, "127.0.0.1", r));
let browser;
const evidence = [];
try {
  browser = await chromium.launch({
    headless: true,
    ...(browserPath ? { executablePath: browserPath } : {}),
  });
  const page = await browser.newPage({ viewport: { width: 1600, height: 1000 }, deviceScaleFactor: 2 });
  const origin = "http://127.0.0.1:" + server.address().port;
  await page.route("**/*", (r) => (new URL(r.request().url()).origin === origin ? r.continue() : r.abort()));
  for (const file of files) {
    const xml = await fs.readFile(file, "utf8");
    for (const theme of ["light", "dark"]) {
      await page.goto(origin);
      await page.waitForFunction(() => window.ready && window.mxGraph);
      const report = await page.evaluate(
        ({ xml, theme }) => {
          const doc = mxUtils.parseXml(xml);
          if (doc.getElementsByTagName("parsererror").length) throw Error("Invalid XML");
          const model = doc.getElementsByTagName("mxGraphModel")[0];
          if (!model) throw Error("Uncompressed mxGraphModel required");
          const vertices = [...model.querySelectorAll('mxCell[vertex="1"]')];
          if (
            !vertices.length ||
            vertices.every((c) => (c.getAttribute("style") || "").includes("shape=image"))
          )
            throw Error("Image-only source is not editable diagram");
          const graph = new mxGraph(document.getElementById("graph"));
          graph.setEnabled(false);
          graph.setHtmlLabels(false);
          new mxCodec(doc).decode(model, graph.getModel());
          const palette =
            theme === "dark"
              ? { fill: "#172554", stroke: "#93c5fd", font: "#e2e8f0", edge: "#cbd5e1" }
              : { fill: "#eff6ff", stroke: "#2563eb", font: "#172554", edge: "#475569" };
          const cells = Object.values(graph.model.cells).filter((c) => c.vertex || c.edge);
          graph.model.beginUpdate();
          try {
            for (const c of cells) {
              let style = c.style || "";
              const put = (k, v) => {
                style = mxUtils.setStyle(style, k, v);
              };
              const role = /janeRole=([^;]+)/.exec(style)?.[1] || "default";
              const roles =
                theme === "dark"
                  ? {
                      control: ["#2e1065", "#c4b5fd", "#ede9fe"],
                      process: ["#431407", "#fb923c", "#ffedd5"],
                      data: ["#052e16", "#4ade80", "#dcfce7"],
                    }
                  : {
                      control: ["#ede9fe", "#7c3aed", "#2e1065"],
                      process: ["#ffedd5", "#c2410c", "#431407"],
                      data: ["#dcfce7", "#15803d", "#052e16"],
                    };
              const color = roles[role] || [palette.fill, palette.stroke, palette.font];
              put("fontColor", color[2]);
              put("strokeColor", c.edge ? palette.edge : color[1]);
              if (c.vertex && !/fillColor=none/.test(style)) put("fillColor", color[0]);
              if (c.edge) {
                put("labelBackgroundColor", theme === "dark" ? "#0f172a" : "#ffffff");
                put("labelBorderColor", "none");
              }
              put("fontFamily", "Arial");
              graph.model.setStyle(c, style);
            }
          } finally {
            graph.model.endUpdate();
          }
          graph.refresh();
          const bounds = graph.getGraphBounds();
          graph.view.setTranslate(24 - bounds.x, 24 - bounds.y);
          graph.refresh();
          const result = graph.getGraphBounds();
          const width = Math.ceil(result.x + result.width + 24),
            height = Math.ceil(result.y + result.height + 24);
          if (width < 40 || height < 40 || width > 12000 || height > 12000)
            throw Error("Invalid diagram bounds");
          const container = document.getElementById("graph");
          container.style.width = width + "px";
          container.style.height = height + "px";
          return {
            width,
            height,
            vertices: cells.filter((c) => c.vertex).length,
            edges: cells.filter((c) => c.edge).length,
            textLabels: cells.filter((c) => c.value).length,
          };
        },
        { xml, theme },
      );
      const output = file.replace(/\.drawio$/, `.${theme}.png`);
      const png = await page.locator("#graph").screenshot({ omitBackground: true });
      const pixels = await page.evaluate(async (data) => {
        const img = new Image();
        img.src = "data:image/png;base64," + data;
        await img.decode();
        const canvas = document.createElement("canvas");
        canvas.width = img.width;
        canvas.height = img.height;
        const ctx = canvas.getContext("2d");
        ctx.drawImage(img, 0, 0);
        const bytes = ctx.getImageData(0, 0, img.width, img.height).data;
        let transparentPixels = 0,
          visiblePixels = 0;
        for (let i = 3; i < bytes.length; i += 4) {
          if (bytes[i] === 0) transparentPixels++;
          else visiblePixels++;
        }
        return { transparentPixels, visiblePixels };
      }, png.toString("base64"));
      if (!pixels.transparentPixels || !pixels.visiblePixels)
        throw Error("Missing transparency or empty PNG");
      if (check) {
        const old = await fs.readFile(output);
        if (!old.equals(png)) throw Error("PNG drift: " + path.relative(root, output));
      } else await fs.writeFile(output, png);
      evidence.push({
        source: path.relative(root, file).replaceAll("\\", "/"),
        theme,
        png: path.relative(root, output).replaceAll("\\", "/"),
        source_sha256: crypto.createHash("sha256").update(xml).digest("hex"),
        png_sha256: crypto.createHash("sha256").update(png).digest("hex"),
        ...report,
        ...pixels,
      });
      console.log(
        `OK ${path.relative(root, file)} ${theme}: ${report.vertices} vertices, ${report.edges} edges, ${report.width}x${report.height}`,
      );
    }
  }
  await fs.mkdir(root + "/.jane/doc-render", { recursive: true });
  await fs.writeFile(
    root + "/.jane/doc-render/drawio-evidence.json",
    JSON.stringify(
      {
        browser: browser.version(),
        engine: "mxgraph@4.2.2",
        transparent: true,
        scale: 2,
        mode: check ? "drift-check" : "actual-export",
        diagrams: evidence,
      },
      null,
      2,
    ) + "\n",
  );
  if (!check && target === path.join(root, "docs/diagrams"))
    await fs.writeFile(
      root + "/docs/diagrams/manifest.json",
      JSON.stringify({ engine: "mxgraph@4.2.2", scale: 2, transparent: true, diagrams: evidence }, null, 2) +
        "\n",
    );
} finally {
  if (browser) await browser.close();
  await new Promise((r) => server.close(r));
}
