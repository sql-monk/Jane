/** Renders a unified diff (from registry diffPackage or computed locally) with added/removed line colouring. */
export function UnifiedDiff({ diff, label }: { diff: string; label: string }) {
  const lines = diff.replace(/\n$/, "").split("\n");
  return (
    <pre className="diff" aria-label={label}>
      {lines.map((line, i) => {
        const cls =
          line.startsWith("+++") || line.startsWith("---")
            ? "diff-file"
            : line.startsWith("@@")
              ? "diff-hunk"
              : line.startsWith("+")
                ? "diff-add"
                : line.startsWith("-")
                  ? "diff-del"
                  : "diff-ctx";
        return (
          <span key={i} className={cls}>
            {line}
            {"\n"}
          </span>
        );
      })}
    </pre>
  );
}
