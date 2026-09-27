import type { Stage } from "../api/types";
import { buildDag } from "../lib/dag";

const W = 220;
const H = 58;
const GAP_X = 70;
const GAP_Y = 22;

/** Processing chain of a task: stages as boxes, `inputs[].from` as arrows labelled with `select` (ТЗ §2). */
export function DagView({ stages }: { stages: readonly Stage[] }) {
  const dag = buildDag(stages);
  const layers = Math.max(1, ...dag.nodes.map((n) => n.layer + 1));
  const rows = Math.max(1, ...dag.nodes.map((n) => n.order + 1));
  const width = layers * (W + GAP_X);
  const height = rows * (H + GAP_Y) + GAP_Y;
  const pos = new Map(
    dag.nodes.map((n) => [n.id, { x: n.layer * (W + GAP_X) + 10, y: n.order * (H + GAP_Y) + GAP_Y }]),
  );
  return (
    <div className="dag" data-testid="dag">
      <svg width={width} height={height} role="img" aria-label="Ланцюжок етапів">
        <defs>
          <marker
            id="arrow"
            viewBox="0 0 10 10"
            refX="10"
            refY="5"
            markerWidth="7"
            markerHeight="7"
            orient="auto"
          >
            <path d="M0,0 L10,5 L0,10 z" className="dag-arrow" />
          </marker>
        </defs>
        {dag.edges.map((e, i) => {
          const a = pos.get(e.from);
          const b = pos.get(e.to);
          if (!a || !b) return null;
          const x1 = a.x + W;
          const y1 = a.y + H / 2;
          const x2 = b.x;
          const y2 = b.y + H / 2;
          const mx = (x1 + x2) / 2;
          return (
            <g key={i} data-testid={`dag-edge-${e.from}-${e.to}`}>
              <path
                d={`M${x1},${y1} C${mx},${y1} ${mx},${y2} ${x2},${y2}`}
                className={e.conditional ? "dag-edge dag-edge-cond" : "dag-edge"}
                markerEnd="url(#arrow)"
              />
              {e.select !== "output" || e.conditional ? (
                <text x={mx} y={(y1 + y2) / 2 - 4} className="dag-edge-label" textAnchor="middle">
                  {e.select}
                  {e.conditional ? " (умова)" : ""}
                </text>
              ) : null}
            </g>
          );
        })}
        {dag.nodes.map((n) => {
          const p = pos.get(n.id);
          if (!p) return null;
          return (
            <g key={n.id} transform={`translate(${p.x},${p.y})`} data-testid={`dag-node-${n.id}`}>
              <rect
                width={W}
                height={H}
                rx={8}
                className={n.kind === "collect" ? "dag-node dag-node-collect" : "dag-node"}
              />
              <text x={10} y={22} className="dag-title">
                {n.id}
              </text>
              <text x={10} y={42} className="dag-label">
                {n.label.length > 32 ? `${n.label.slice(0, 31)}…` : n.label}
              </text>
            </g>
          );
        })}
      </svg>
      {dag.issues.length ? (
        <ul className="error-inline" aria-label="Проблеми ланцюжка">
          {dag.issues.map((issue) => (
            <li key={issue}>{issue}</li>
          ))}
        </ul>
      ) : null}
    </div>
  );
}
