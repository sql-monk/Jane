// Contract-shaped stand-in of the package registry (registry.v1) for hybrid runs of the REAL handler-runtime:
// WP-05 (registry) is not in main yet, and handler-runtime loads packages for `POST /v1/test-runs` from the
// registry (`GET /v1/packages/{id}/versions/{v}/archive`, ETag = digest). The stand-in serves ONE real package
// directory (the extractor SDK example by default) through the read operations of registry.v1 the admin and the
// runtime use. The manifest is validated against contracts/schemas/package-manifest.schema.json before serving.
import { createHash } from "node:crypto";
import { readdirSync, readFileSync, statSync } from "node:fs";
import { createServer, type Server } from "node:http";
import path from "node:path";
import { crc32 } from "node:zlib";
import type { Package, PackageManifest, PackageVersion } from "../src/api/types";
import { SCHEMAS, validateAgainst } from "../src/lib/schema";

interface Entry {
  path: string;
  data: Buffer;
}

function collect(root: string, dir = root): Entry[] {
  const out: Entry[] = [];
  for (const name of readdirSync(dir).sort()) {
    if (name === "__pycache__" || name.startsWith(".")) continue;
    const full = path.join(dir, name);
    if (statSync(full).isDirectory()) out.push(...collect(root, full));
    else out.push({ path: path.relative(root, full).split(path.sep).join("/"), data: readFileSync(full) });
  }
  return out;
}

/** Deterministic zip (method 0 = stored, fixed timestamps), so the digest is stable between runs. */
export function buildZip(entries: Entry[]): Buffer {
  const locals: Buffer[] = [];
  const centrals: Buffer[] = [];
  let offset = 0;
  const dosTime = 0;
  const dosDate = ((2026 - 1980) << 9) | (1 << 5) | 1;
  for (const entry of entries) {
    const name = Buffer.from(entry.path, "utf8");
    const crc = crc32(entry.data) >>> 0;
    const local = Buffer.alloc(30);
    local.writeUInt32LE(0x04034b50, 0);
    local.writeUInt16LE(20, 4);
    local.writeUInt16LE(0x0800, 6); // UTF-8 names
    local.writeUInt16LE(0, 8);
    local.writeUInt16LE(dosTime, 10);
    local.writeUInt16LE(dosDate, 12);
    local.writeUInt32LE(crc, 14);
    local.writeUInt32LE(entry.data.length, 18);
    local.writeUInt32LE(entry.data.length, 22);
    local.writeUInt16LE(name.length, 26);
    local.writeUInt16LE(0, 28);
    locals.push(local, name, entry.data);
    const central = Buffer.alloc(46);
    central.writeUInt32LE(0x02014b50, 0);
    central.writeUInt16LE(20, 4);
    central.writeUInt16LE(20, 6);
    central.writeUInt16LE(0x0800, 8);
    central.writeUInt16LE(0, 10);
    central.writeUInt16LE(dosTime, 12);
    central.writeUInt16LE(dosDate, 14);
    central.writeUInt32LE(crc, 16);
    central.writeUInt32LE(entry.data.length, 20);
    central.writeUInt32LE(entry.data.length, 24);
    central.writeUInt16LE(name.length, 28);
    central.writeUInt32LE(offset, 42);
    centrals.push(central, name);
    offset += local.length + name.length + entry.data.length;
  }
  const centralSize = centrals.reduce((n, b) => n + b.length, 0);
  const end = Buffer.alloc(22);
  end.writeUInt32LE(0x06054b50, 0);
  end.writeUInt16LE(entries.length, 8);
  end.writeUInt16LE(entries.length, 10);
  end.writeUInt32LE(centralSize, 12);
  end.writeUInt32LE(offset, 16);
  return Buffer.concat([...locals, ...centrals, end]);
}

export interface Standin {
  url: string;
  pkg: Package;
  version: PackageVersion;
  close: () => Promise<void>;
}

export async function startRegistryStandin(packageDir: string, port: number): Promise<Standin> {
  const entries = collect(packageDir);
  const manifest = JSON.parse(
    readFileSync(path.join(packageDir, "jane-package.json"), "utf8"),
  ) as PackageManifest;
  const issues = validateAgainst(SCHEMAS.manifest, manifest);
  if (issues.length)
    throw new Error(`package manifest does not match the contract: ${JSON.stringify(issues)}`);
  const archive = buildZip(entries);
  const digest = `sha256:${createHash("sha256").update(archive).digest("hex")}`;
  const now = "2026-09-30T00:00:00Z";
  const pkg: Package = {
    package_id: manifest.package_id,
    kind: manifest.kind,
    title: manifest.title,
    latest_version: manifest.version,
    auto_changes_allowed: false,
    deprecated: false,
    created_at: now,
    updated_at: now,
  };
  const version: PackageVersion = {
    package_id: manifest.package_id,
    version: manifest.version,
    digest,
    status: "approved",
    test_status: "unknown",
    manifest,
    files: entries.map((e) => ({
      path: e.path,
      size_bytes: e.data.length,
      sha256: createHash("sha256").update(e.data).digest("hex"),
    })),
    size_bytes: archive.length,
    created_at: now,
    created_by: "human",
  };
  const base = `/v1/packages/${encodeURIComponent(pkg.package_id)}`;
  const vbase = `${base}/versions/${encodeURIComponent(version.version)}`;
  const json = (
    res: import("node:http").ServerResponse,
    status: number,
    body: unknown,
    type = "application/json",
  ) => {
    res.writeHead(status, { "Content-Type": type });
    res.end(JSON.stringify(body));
  };
  const server: Server = createServer((req, res) => {
    const url = new URL(req.url ?? "/", "http://standin");
    if (req.method !== "GET")
      return json(
        res,
        405,
        {
          type: "urn:jane:problem:method_not_allowed",
          title: "Method not allowed",
          status: 405,
          code: "method_not_allowed",
        },
        "application/problem+json",
      );
    if (url.pathname === "/v1/health") return json(res, 200, { status: "ok" });
    if (url.pathname === "/v1/packages")
      return json(res, 200, { items: url.searchParams.get("fork_of") ? [] : [pkg], next_cursor: null });
    if (url.pathname === base) return json(res, 200, pkg);
    if (url.pathname === `${base}/versions`) return json(res, 200, { items: [version], next_cursor: null });
    if (url.pathname === vbase) return json(res, 200, version);
    if (url.pathname === `${vbase}/archive`) {
      res.writeHead(200, {
        "Content-Type": "application/zip",
        ETag: `"${digest}"`,
        "Content-Length": archive.length,
      });
      return res.end(archive);
    }
    if (url.pathname === `${vbase}/file`) {
      const entry = entries.find((e) => e.path === url.searchParams.get("path"));
      if (entry) {
        res.writeHead(200, { "Content-Type": "text/plain; charset=utf-8" });
        return res.end(entry.data);
      }
    }
    return json(
      res,
      404,
      { type: "urn:jane:problem:not_found", title: "Not found", status: 404, code: "not_found" },
      "application/problem+json",
    );
  });
  await new Promise<void>((resolve, reject) => {
    server.once("error", reject);
    server.listen(port, "127.0.0.1", () => resolve());
  });
  return {
    url: `http://127.0.0.1:${port}`,
    pkg,
    version,
    close: () => new Promise((resolve) => server.close(() => resolve())),
  };
}
