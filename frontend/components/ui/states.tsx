import * as React from "react";
import { Inbox, AlertCircle, RefreshCw } from "lucide-react";
import { GlassCard } from "@/components/ui/glass-card";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

export function EmptyState({
  title,
  description,
  icon: Icon = Inbox,
  action,
  onAction,
  className,
}: {
  title: string;
  description?: string;
  icon?: React.ComponentType<{ className?: string }>;
  action?: string;
  onAction?: () => void;
  className?: string;
}) {
  return (
    <GlassCard
      className={cn(
        "flex flex-col items-center justify-center gap-4 px-8 py-16 text-center",
        className
      )}
    >
      <div className="grid h-16 w-16 place-items-center rounded-2xl bg-gradient-to-br from-iris/20 to-aqua/20">
        <Icon className="h-8 w-8 text-iris" />
      </div>
      <div className="space-y-1.5">
        <h3 className="font-display text-lg font-semibold">{title}</h3>
        {description && <p className="max-w-sm text-sm text-secondary">{description}</p>}
      </div>
      {action && onAction && (
        <Button variant="primary" onClick={onAction}>
          {action}
        </Button>
      )}
    </GlassCard>
  );
}

export function ErrorState({
  title = "Something went wrong",
  description,
  onRetry,
  className,
}: {
  title?: string;
  description?: string;
  onRetry?: () => void;
  className?: string;
}) {
  return (
    <GlassCard
      className={cn(
        "flex flex-col items-center justify-center gap-4 px-8 py-16 text-center",
        className
      )}
    >
      <div className="grid h-16 w-16 place-items-center rounded-2xl bg-rose-500/15">
        <AlertCircle className="h-8 w-8 text-rose-400" />
      </div>
      <div className="space-y-1.5">
        <h3 className="font-display text-lg font-semibold">{title}</h3>
        {description && <p className="max-w-sm text-sm text-secondary">{description}</p>}
      </div>
      {onRetry && (
        <Button variant="glass" onClick={onRetry}>
          <RefreshCw className="h-4 w-4" />
          Retry
        </Button>
      )}
    </GlassCard>
  );
}
