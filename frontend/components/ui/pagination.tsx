import * as React from "react";
import { ChevronLeft, ChevronsLeft, ChevronsRight, ChevronRight } from "lucide-react";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

export interface PaginationProps {
  page: number;
  totalPages: number;
  onPageChange: (page: number) => void;
  className?: string;
  totalItems?: number;
  itemsPerPage?: number;
}

export function Pagination({
  page,
  totalPages,
  onPageChange,
  className,
  totalItems,
  itemsPerPage,
}: PaginationProps) {
  const pages = React.useMemo(() => {
    const result: Array<number | "ellipsis"> = [];
    const maxVisible = 5;
    let start = Math.max(1, page - Math.floor(maxVisible / 2));
    let end = Math.min(totalPages, start + maxVisible - 1);
    start = Math.max(1, end - maxVisible + 1);

    if (start > 1) {
      result.push(1);
      if (start > 2) result.push("ellipsis");
    }
    for (let i = start; i <= end; i++) {
      result.push(i);
    }
    if (end < totalPages) {
      if (end < totalPages - 1) result.push("ellipsis");
      result.push(totalPages);
    }
    return result;
  }, [page, totalPages]);

  const startItem = totalItems && itemsPerPage ? (page - 1) * itemsPerPage + 1 : null;
  const endItem = totalItems && itemsPerPage ? Math.min(page * itemsPerPage, totalItems) : null;

  return (
    <div className={cn("flex flex-col items-center gap-3 sm:flex-row sm:justify-between", className)}>
      <div className="text-xs text-secondary">
        {totalItems !== undefined && startItem && endItem
          ? `Showing ${startItem}–${endItem} of ${totalItems} items`
          : `Page ${page} of ${totalPages}`}
      </div>
      <div className="flex items-center gap-1">
        <Button
          variant="ghost"
          size="sm"
          onClick={() => onPageChange(1)}
          disabled={page === 1}
          className="h-8 w-8 p-0"
        >
          <ChevronsLeft className="h-4 w-4" />
        </Button>
        <Button
          variant="ghost"
          size="sm"
          onClick={() => onPageChange(page - 1)}
          disabled={page === 1}
          className="h-8 w-8 p-0"
        >
          <ChevronLeft className="h-4 w-4" />
        </Button>
        {pages.map((p, i) =>
          p === "ellipsis" ? (
            <span key={`e-${i}`} className="px-2 text-secondary">
              …
            </span>
          ) : (
            <Button
              key={p}
              variant={p === page ? "primary" : "ghost"}
              size="sm"
              onClick={() => onPageChange(p)}
              className="h-8 w-8 p-0"
            >
              {p}
            </Button>
          )
        )}
        <Button
          variant="ghost"
          size="sm"
          onClick={() => onPageChange(page + 1)}
          disabled={page === totalPages || totalPages === 0}
          className="h-8 w-8 p-0"
        >
          <ChevronRight className="h-4 w-4" />
        </Button>
        <Button
          variant="ghost"
          size="sm"
          onClick={() => onPageChange(totalPages)}
          disabled={page === totalPages || totalPages === 0}
          className="h-8 w-8 p-0"
        >
          <ChevronsRight className="h-4 w-4" />
        </Button>
      </div>
    </div>
  );
}
