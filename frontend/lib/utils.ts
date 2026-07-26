import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

type Plain = Record<string, unknown>;

export function snakeToCamelKey(k: string): string {
  return k.replace(/_([a-z0-9])/g, (_, c) => (c as string).toUpperCase());
}

export function camelToSnakeKey(k: string): string {
  return k.replace(/([A-Z0-9])/g, (_, c: string) => `_${c.toLowerCase()}`);
}

export function snakeToCamel<T>(value: unknown): T {
  if (Array.isArray(value)) return value.map((v) => snakeToCamel(v)) as T;
  if (value && typeof value === "object" && value.constructor === Object) {
    const out: Plain = {};
    for (const [k, v] of Object.entries(value as Plain)) {
      out[snakeToCamelKey(k)] = snakeToCamel(v);
    }
    return out as T;
  }
  return value as T;
}

export function camelToSnake(value: unknown): unknown {
  if (Array.isArray(value)) return value.map(camelToSnake);
  if (value && typeof value === "object" && value.constructor === Object) {
    const out: Plain = {};
    for (const [k, v] of Object.entries(value as Plain)) {
      out[camelToSnakeKey(k)] = camelToSnake(v);
    }
    return out;
  }
  return value;
}
