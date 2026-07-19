import type { ServerEvent } from "./events";

export function parseServerEvent(raw: string): ServerEvent {
  const value: unknown = JSON.parse(raw);
  if (!value || typeof value !== "object" || !("type" in value) || typeof value.type !== "string") {
    throw new Error("Invalid server event");
  }
  return value as ServerEvent;
}
