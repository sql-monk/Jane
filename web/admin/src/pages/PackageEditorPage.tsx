// Code editor for a package version: edits are published as a new immutable draft version (ТЗ §10).
import { useEffect, useMemo, useState } from "react";
import { useMutation, useQuery } from "@tanstack/react-query";
import { Link, useNavigate, useParams } from "react-router-dom";
import { createTwoFilesPatch } from "diff";
import { useApi } from "../app/context";
import { unwrap } from "../api/client";
import { fetchAllFiles, nextManifest, publishVersion, type PackageFile } from "../api/packages";
import type { PackageManifest } from "../api/types";
import { CodeEditor, languageOfPath } from "../components/CodeEditor";
import { JsonEditor, checkJson, toJsonText } from "../components/JsonEditor";
import { UnifiedDiff } from "../components/UnifiedDiff";
import { ErrorBox, Field, Loading, Notice, Page, Section } from "../components/ui";
import { SCHEMAS } from "../lib/schema";
import { SEMVER_PATTERN, bumpVersion } from "../lib/format";

const MANIFEST_TAB = "jane-package.json";
const PACKAGE_PATH = /^(?!\/)(?!.*(^|\/)\.\.(\/|$))[A-Za-z0-9._/-]{1,300}$/;

export function PackageEditorPage() {
  const { packageId = "", version = "" } = useParams();
  const api = useApi();
  const navigate = useNavigate();
  const source = useQuery({
    queryKey: ["package-edit", packageId, version],
    queryFn: async () => {
      const v = await unwrap(
        api.registry.GET("/v1/packages/{package_id}/versions/{version}", {
          params: { path: { package_id: packageId, version } },
        }),
      );
      const files = await fetchAllFiles(api, v);
      return { version: v, files };
    },
    staleTime: Infinity,
  });

  const [files, setFiles] = useState<Record<string, PackageFile>>({});
  const [manifestText, setManifestText] = useState("");
  const [active, setActive] = useState<string>(MANIFEST_TAB);
  const [newPath, setNewPath] = useState("");
  const [newVersion, setNewVersion] = useState("");
  const [summary, setSummary] = useState("");

  useEffect(() => {
    if (!source.data) return;
    setFiles(source.data.files);
    setManifestText(toJsonText(source.data.version.manifest));
    setNewVersion(bumpVersion(version));
    const first = Object.keys(source.data.files).find((p) => p.endsWith(".py"));
    setActive(first ?? MANIFEST_TAB);
  }, [source.data, version]);

  const original = useMemo<Record<string, PackageFile>>(() => source.data?.files ?? {}, [source.data]);
  const changed = useMemo(() => {
    const paths = new Set([...Object.keys(original), ...Object.keys(files)]);
    return [...paths].filter((p) => original[p]?.data !== files[p]?.data).sort();
  }, [original, files]);

  const patch = useMemo(
    () =>
      changed
        .filter(
          (p) =>
            (original[p]?.encoding ?? "utf-8") === "utf-8" && (files[p]?.encoding ?? "utf-8") === "utf-8",
        )
        .map((p) =>
          createTwoFilesPatch(
            `a/${p}`,
            `b/${p}`,
            original[p]?.data ?? "",
            files[p]?.data ?? "",
            version,
            "draft",
          ),
        )
        .join(""),
    [changed, original, files, version],
  );

  const manifestCheck = checkJson(manifestText, SCHEMAS.manifest);

  const publish = useMutation({
    mutationFn: () => {
      const manifest = nextManifest(manifestCheck.value as PackageManifest, newVersion, summary);
      return publishVersion(api, packageId, manifest, files);
    },
    onSuccess: (published) =>
      navigate(`/packages/${encodeURIComponent(packageId)}?version=${encodeURIComponent(published.version)}`),
  });

  if (source.isLoading) return <Loading what="Завантаження файлів пакета" />;

  const current = files[active];
  const paths = Object.keys(files).sort();

  return (
    <Page title={`Редактор ${packageId}@${version}`}>
      <ErrorBox error={source.error} />
      <Notice>
        Вихідна версія незмінна. Після публікації нова версія має статус draft: запустіть тести (без запису в
        робочі дані), порівняйте відмінності, погодьте й активуйте в етапі завдання.{" "}
        <Link to={`/packages/${encodeURIComponent(packageId)}`}>До пакета</Link>
      </Notice>
      <div className="editor-layout">
        <nav className="file-tree" aria-label="Файли пакета">
          <button
            type="button"
            className={active === MANIFEST_TAB ? "file file-active" : "file"}
            onClick={() => setActive(MANIFEST_TAB)}
          >
            {MANIFEST_TAB}
          </button>
          {paths.map((p) => (
            <button
              key={p}
              type="button"
              className={active === p ? "file file-active" : "file"}
              onClick={() => setActive(p)}
            >
              {changed.includes(p) ? "● " : ""}
              {p}
            </button>
          ))}
          <div className="inline-form">
            <input
              aria-label="Новий файл"
              placeholder="src/new_module.py"
              value={newPath}
              onChange={(e) => setNewPath(e.target.value)}
            />
            <button
              type="button"
              className="btn btn-small"
              disabled={!PACKAGE_PATH.test(newPath) || newPath in files || newPath === MANIFEST_TAB}
              onClick={() => {
                setFiles((f) => ({ ...f, [newPath]: { encoding: "utf-8", data: "" } }));
                setActive(newPath);
                setNewPath("");
              }}
            >
              Додати
            </button>
          </div>
        </nav>
        <div className="editor-main">
          {active === MANIFEST_TAB ? (
            <JsonEditor
              text={manifestText}
              onChange={setManifestText}
              schema={SCHEMAS.manifest}
              label="Маніфест"
              minHeight="28rem"
            />
          ) : current ? (
            current.encoding === "base64" ? (
              <p className="muted">
                Бінарний файл ({active}) — редагування недоступне, файл буде збережено без змін.
              </p>
            ) : (
              <>
                <div className="editor-head">
                  <code>{active}</code>
                  <button
                    type="button"
                    className="btn btn-small btn-danger"
                    onClick={() => {
                      setFiles((f) => {
                        const next = { ...f };
                        delete next[active];
                        return next;
                      });
                      setActive(MANIFEST_TAB);
                    }}
                  >
                    Видалити файл
                  </button>
                </div>
                <CodeEditor
                  value={current.data}
                  language={languageOfPath(active)}
                  label={`Код ${active}`}
                  minHeight="28rem"
                  onChange={(data) => setFiles((f) => ({ ...f, [active]: { encoding: "utf-8", data } }))}
                />
              </>
            )
          ) : null}
        </div>
      </div>
      <Section title={`Зміни відносно ${version} (${changed.length})`}>
        {patch ? (
          <UnifiedDiff diff={patch} label="Локальні зміни" />
        ) : (
          <p className="muted">Змін у файлах немає.</p>
        )}
      </Section>
      <Section title="Опублікувати нову версію">
        <div className="grid-2">
          <Field label="Нова версія">
            <input value={newVersion} onChange={(e) => setNewVersion(e.target.value)} />
          </Field>
          <Field label="Опис змін">
            <input value={summary} onChange={(e) => setSummary(e.target.value)} maxLength={4000} />
          </Field>
        </div>
        {manifestCheck.parseError || manifestCheck.issues.length ? (
          <p className="error-inline">Маніфест не відповідає схемі — виправте на вкладці {MANIFEST_TAB}.</p>
        ) : null}
        <ErrorBox error={publish.error} title="Версію не опубліковано" />
        <button
          type="button"
          className="btn btn-primary"
          disabled={
            publish.isPending || !manifestCheck.ok || !manifestCheck.value || !SEMVER_PATTERN.test(newVersion)
          }
          onClick={() => publish.mutate()}
        >
          Опублікувати як нову версію
        </button>
      </Section>
    </Page>
  );
}
