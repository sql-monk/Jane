import type { Stage } from "../api/types";

export type JsonValue = null | boolean | number | string | JsonValue[] | { [key: string]: JsonValue };
export type JsonType = "null" | "boolean" | "number" | "string" | "array" | "object";
export function jsonType(value: JsonValue): JsonType {
  return value === null ? "null" : Array.isArray(value) ? "array" : (typeof value as JsonType);
}
export function emptyValue(type: JsonType): JsonValue {
  return { null: null, boolean: false, number: 0, string: "", array: [], object: {} }[type];
}
export function renameField(value: Record<string, JsonValue>, from: string, to: string) {
  if (!to || (to !== from && Object.hasOwn(value, to))) throw new Error("Назва порожня або вже існує");
  return Object.fromEntries(Object.entries(value).map(([key, item]) => [key === from ? to : key, item]));
}
export function moveItem(value: JsonValue[], index: number, delta: number) {
  const result = [...value];
  const target = index + delta;
  if (target < 0 || target >= value.length) return result;
  [result[index], result[target]] = [result[target]!, result[index]!];
  return result;
}
export function renameStage(stages: Stage[], from: string, to: string): Stage[] {
  if (
    !/^[a-z0-9](?:[a-z0-9._-]{0,98}[a-z0-9])?$/.test(to) ||
    stages.some((s) => s.stage_id === to && to !== from)
  )
    throw new Error("Некоректний або зайнятий stage_id");
  return stages.map((stage) => ({
    ...stage,
    stage_id: stage.stage_id === from ? to : stage.stage_id,
    ...(stage.inputs
      ? { inputs: stage.inputs.map((input) => (input.from === from ? { ...input, from: to } : input)) }
      : {}),
  }));
}
export function removeStage(stages: Stage[], id: string): Stage[] {
  return stages
    .filter((stage) => stage.stage_id !== id)
    .map((stage) => ({
      ...stage,
      ...(stage.inputs ? { inputs: stage.inputs.filter((input) => input.from !== id) } : {}),
    }));
}
