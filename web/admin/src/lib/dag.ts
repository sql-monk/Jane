// Stage graph of a task (TaskConfig.stages[].inputs[].from) for the chain view and early checks.
import type { Stage } from "../api/types";

export interface DagNode {
  id: string;
  kind: Stage["kind"];
  title: string;
  label: string;
  layer: number;
  order: number;
}

export interface DagEdge {
  from: string;
  to: string;
  select: string;
  conditional: boolean;
}

export interface Dag {
  nodes: DagNode[];
  edges: DagEdge[];
  /** Human-readable structural problems (the orchestrator validation is authoritative). */
  issues: string[];
}

export function stageLabel(stage: Stage): string {
  if (stage.kind === "collect") return `collector: ${stage.collector?.collector ?? "?"}`;
  const handler = stage.handler;
  return handler ? `${handler.package_id}@${handler.version}` : "handler: ?";
}

export function buildDag(stages: readonly Stage[]): Dag {
  const issues: string[] = [];
  const byId = new Map<string, Stage>();
  for (const stage of stages) {
    if (byId.has(stage.stage_id)) issues.push(`етап «${stage.stage_id}» оголошено двічі`);
    byId.set(stage.stage_id, stage);
  }
  const edges: DagEdge[] = [];
  for (const stage of stages) {
    for (const input of stage.inputs ?? []) {
      if (!byId.has(input.from)) {
        issues.push(`етап «${stage.stage_id}» читає з невідомого етапу «${input.from}»`);
        continue;
      }
      edges.push({
        from: input.from,
        to: stage.stage_id,
        select: input.select ?? "output",
        conditional: input.when !== undefined,
      });
    }
  }
  // Longest-path layering (Kahn); stages left over are in a cycle.
  const incoming = new Map<string, number>();
  for (const id of byId.keys()) incoming.set(id, 0);
  for (const edge of edges) incoming.set(edge.to, (incoming.get(edge.to) ?? 0) + 1);
  const layer = new Map<string, number>();
  const queue = [...byId.keys()].filter((id) => incoming.get(id) === 0);
  for (const id of queue) layer.set(id, 0);
  while (queue.length) {
    const id = queue.shift() as string;
    for (const edge of edges.filter((e) => e.from === id)) {
      layer.set(edge.to, Math.max(layer.get(edge.to) ?? 0, (layer.get(id) ?? 0) + 1));
      const left = (incoming.get(edge.to) ?? 0) - 1;
      incoming.set(edge.to, left);
      if (left === 0) queue.push(edge.to);
    }
  }
  const cyclic = [...byId.keys()].filter((id) => !layer.has(id));
  if (cyclic.length) issues.push(`цикл між етапами: ${cyclic.join(", ")}`);
  const collectStages = stages.filter((s) => s.kind === "collect");
  if (collectStages.length === 0 && stages.length > 0) issues.push("немає етапу збору (kind=collect)");
  for (const stage of stages) {
    if (stage.kind === "handler" && (stage.inputs ?? []).length === 0) {
      issues.push(`етап-обробник «${stage.stage_id}» не має входів`);
    }
  }
  const perLayer = new Map<number, number>();
  const nodes: DagNode[] = stages.map((stage) => {
    const l = layer.get(stage.stage_id) ?? 0;
    const order = perLayer.get(l) ?? 0;
    perLayer.set(l, order + 1);
    return {
      id: stage.stage_id,
      kind: stage.kind,
      title: stage.title ?? stage.stage_id,
      label: stageLabel(stage),
      layer: l,
      order,
    };
  });
  return { nodes, edges, issues };
}
