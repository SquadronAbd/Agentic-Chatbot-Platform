import * as React from "react";
import { cn } from "@/lib/utils";
import type { ManagedUser, Role } from "@/lib/types";
import { MoreHorizontal, Pencil, Trash2 } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Avatar } from "@/components/ui/avatar";
import { Button } from "@/components/ui/button";
import { Spinner } from "@/components/ui/spinner";

export interface Column<T> {
  key: keyof T | string;
  header: string;
  cell?: (row: T) => React.ReactNode;
  className?: string;
}

interface DataTableProps<T> {
  columns: Column<T>[];
  data: T[];
  keyField: keyof T | string;
  rowActions?: (row: T) => React.ReactNode;
  className?: string;
  isLoading?: boolean;
  emptyState?: React.ReactNode;
}

function UsersTableRowActions({
  row,
  onEdit,
  onDelete,
  isDeleting,
}: {
  row: ManagedUser;
  onEdit?: (row: ManagedUser) => void;
  onDelete?: (row: ManagedUser) => void;
  isDeleting?: boolean;
}) {
  const [open, setOpen] = React.useState(false);
  const ref = React.useRef<HTMLDivElement>(null);

  React.useEffect(() => {
    function handleClick(e: MouseEvent) {
      if (ref.current && !ref.current.contains(e.target as Node)) setOpen(false);
    }
    document.addEventListener("mousedown", handleClick);
    return () => document.removeEventListener("mousedown", handleClick);
  }, []);

  return (
    <div className="relative" ref={ref}>
      <Button variant="ghost" size="icon" onClick={() => setOpen((v) => !v)}>
        <MoreHorizontal className="h-4 w-4" />
      </Button>
      {open && (
        <div className="absolute right-0 top-full z-20 mt-1 w-40 overflow-hidden rounded-xl glass shadow-glass-lg">
          {onEdit && (
            <button
              onClick={() => {
                setOpen(false);
                onEdit(row);
              }}
              className="flex w-full items-center gap-2 px-3 py-2 text-left text-sm hover:bg-white/10"
            >
              <Pencil className="h-3.5 w-3.5" />
              Edit
            </button>
          )}
          {onDelete && (
            <button
              onClick={() => {
                setOpen(false);
                onDelete(row);
              }}
              disabled={isDeleting}
              className="flex w-full items-center gap-2 px-3 py-2 text-left text-sm text-rose-400 hover:bg-white/10 disabled:opacity-50"
            >
              {isDeleting ? <Spinner className="h-3.5 w-3.5" /> : <Trash2 className="h-3.5 w-3.5" />}
              Delete
            </button>
          )}
        </div>
      )}
    </div>
  );
}

export const userColumns: Column<ManagedUser>[] = [
  {
    key: "user",
    header: "User",
    cell: (row) => (
      <div className="flex items-center gap-3">
        <Avatar name={row.name} size="sm" />
        <div className="min-w-0">
          <p className="truncate font-medium">{row.name}</p>
          <p className="truncate text-xs text-secondary">{row.email}</p>
        </div>
      </div>
    ),
  },
  {
    key: "role",
    header: "Role",
    cell: (row) => (
      <RoleBadgeSelect role={row.role} />
    ),
  },
  {
    key: "lastActive",
    header: "Last active",
    cell: (row) => <span className="text-sm text-secondary">{row.lastActive}</span>,
  },
];

function RoleBadgeSelect({
  role,
  onChange,
  readOnly,
}: {
  role: Role;
  onChange?: (r: Role) => void;
  readOnly?: boolean;
}) {
  const tone = role === "admin" ? "iris" : role === "manager" ? "aqua" : role === "agent" ? "default" : "outline";
  if (readOnly || !onChange) {
    return (
      <Badge tone={tone as Parameters<typeof Badge>[0]["tone"]}>
        {role}
      </Badge>
    );
  }
  return (
    <select
      value={role}
      onChange={(e) => onChange(e.target.value as Role)}
      className="glass cursor-pointer rounded-lg px-2 py-1 text-xs font-medium outline-none focus:shadow-glow-iris"
    >
      <option value="viewer">Viewer</option>
      <option value="agent">Agent</option>
      <option value="manager">Manager</option>
      <option value="admin">Admin</option>
    </select>
  );
}

export function DataTable<T extends object>({
  columns,
  data,
  keyField,
  rowActions,
  className,
  isLoading,
  emptyState,
}: DataTableProps<T>) {
  const getKey = (row: T): string => {
    const v = row[keyField as keyof T];
    return typeof v === "string" || typeof v === "number" ? String(v) : JSON.stringify(row);
  };

  if (isLoading) {
    return (
      <div className={cn("glass glass-highlight overflow-hidden rounded-glass shadow-glass", className)}>
        <div className="animate-pulse">
          <div className="grid gap-4 border-b border-white/10 p-4" style={{ gridTemplateColumns: `repeat(${columns.length + (rowActions ? 1 : 0)}, minmax(0,1fr))` }}>
            {columns.map((_, i) => (
              <div key={i} className="h-4 w-3/4 rounded-md bg-white/10" />
            ))}
            {rowActions && <div className="h-4 w-8 rounded-md bg-white/10 justify-self-end" />}
          </div>
          {Array.from({ length: 5 }).map((_, ri) => (
            <div key={ri} className="grid gap-4 border-b border-white/10 p-4" style={{ gridTemplateColumns: `repeat(${columns.length + (rowActions ? 1 : 0)}, minmax(0,1fr))` }}>
              {columns.map((_, ci) => (
                <div key={ci} className="h-4 w-5/6 rounded-md bg-white/10" />
              ))}
              {rowActions && <div className="h-8 w-8 rounded-md bg-white/10 justify-self-end" />}
            </div>
          ))}
        </div>
      </div>
    );
  }

  if (!data.length) {
    return emptyState ?? <div className="text-sm text-secondary">No data</div>;
  }

  return (
    <div className={cn("glass glass-highlight overflow-hidden rounded-glass shadow-glass", className)}>
      <div className="overflow-x-auto">
        <table className="w-full text-left text-sm">
          <thead className="border-b border-white/10 bg-white/5">
            <tr>
              {columns.map((col) => (
                <th key={String(col.key)} className={cn("px-4 py-3 font-semibold", col.className)}>
                  {col.header}
                </th>
              ))}
              {rowActions && <th className="w-16 px-4 py-3" />}
            </tr>
          </thead>
          <tbody>
            {data.map((row) => (
              <tr key={getKey(row)} className="border-b border-white/5 last:border-0 transition-colors hover:bg-white/5">
                {columns.map((col) => {
                  const value = col.cell ? col.cell(row) : (row[col.key as keyof T] as unknown as React.ReactNode);
                  return (
                    <td key={String(col.key)} className={cn("px-4 py-3 align-middle", col.className)}>
                      {value}
                    </td>
                  );
                })}
                {rowActions && (
                  <td className="px-4 py-3 text-right align-middle">
                    {rowActions(row)}
                  </td>
                )}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export { UsersTableRowActions, RoleBadgeSelect };
