// Registry helpers: reading all files of a version and publishing an edited copy as a new immutable version.
import type { ApiClients } from "./client";
import { newIdempotencyKey, unwrap } from "./client";
import { ApiError, toProblem } from "./problem";
import type { PackageManifest, PackageVersion, PublishRequest } from "./types";

export const MANIFEST_FILE = "jane-package.json";

export interface PackageFile {
  encoding: "utf-8" | "base64";
  data: string;
}

function toBase64(bytes: Uint8Array): string {
  let binary = "";
  for (let i = 0; i < bytes.length; i += 0x8000) {
    binary += String.fromCharCode(...bytes.subarray(i, i + 0x8000));
  }
  return btoa(binary);
}

/** Decodes as UTF-8 text when possible, otherwise keeps the bytes as base64. */
export function decodeFile(bytes: ArrayBuffer): PackageFile {
  try {
    return { encoding: "utf-8", data: new TextDecoder("utf-8", { fatal: true }).decode(bytes) };
  } catch {
    return { encoding: "base64", data: toBase64(new Uint8Array(bytes)) };
  }
}

export async function fetchPackageFile(
  api: ApiClients,
  packageId: string,
  version: string,
  path: string,
): Promise<PackageFile> {
  const { data, error, response } = await api.registry.GET(
    "/v1/packages/{package_id}/versions/{version}/file",
    {
      params: { path: { package_id: packageId, version }, query: { path } },
      parseAs: "arrayBuffer",
    },
  );
  if (error !== undefined || !response.ok || !data) {
    throw new ApiError(response.status, toProblem(response.status, error, response.statusText));
  }
  return decodeFile(data as unknown as ArrayBuffer);
}

/** All files of a version except the manifest (the registry builds jane-package.json from `manifest`). */
export async function fetchAllFiles(
  api: ApiClients,
  version: PackageVersion,
): Promise<Record<string, PackageFile>> {
  const files: Record<string, PackageFile> = {};
  for (const entry of version.files ?? []) {
    if (entry.path === MANIFEST_FILE) continue;
    files[entry.path] = await fetchPackageFile(api, version.package_id, version.version, entry.path);
  }
  return files;
}

export function nextManifest(
  base: PackageManifest,
  newVersion: string,
  changeSummary: string,
): PackageManifest {
  return {
    ...base,
    version: newVersion,
    provenance: {
      created_by: "human",
      based_on: { package_id: base.package_id, version: base.version },
      ...(changeSummary ? { change_summary: changeSummary } : {}),
    },
  };
}

/** Publishes a new draft version (JSON form of publishPackageVersion). */
export async function publishVersion(
  api: ApiClients,
  packageId: string,
  manifest: PackageManifest,
  files: Record<string, PackageFile>,
): Promise<PackageVersion> {
  const body: PublishRequest = { manifest, files };
  return unwrap(
    api.registry.POST("/v1/packages/{package_id}/versions", {
      params: { path: { package_id: packageId }, header: { "Idempotency-Key": newIdempotencyKey() } },
      body,
    }),
  );
}
