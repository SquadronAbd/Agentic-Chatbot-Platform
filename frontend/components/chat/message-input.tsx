"use client";

import * as React from "react";
import { SendHorizontal } from "lucide-react";
import { Button } from "@/components/ui/button";
import { GlassCard } from "@/components/ui/glass-card";

export function MessageInput({ onSend }: { onSend: (text: string) => void }) {
  const [value, setValue] = React.useState("");

  function submit(e: React.FormEvent) {
    e.preventDefault();
    if (!value.trim()) return;
    onSend(value.trim());
    setValue("");
  }

  return (
    <form onSubmit={submit}>
      <GlassCard className="flex items-end gap-3 p-3">
        <textarea
          value={value}
          onChange={(e) => setValue(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter" && !e.shiftKey) {
              e.preventDefault();
              submit(e);
            }
          }}
          placeholder="Ask the agent anything about your knowledge base..."
          rows={1}
          className="max-h-32 flex-1 resize-none bg-transparent px-2 py-2 text-sm font-body outline-none placeholder:text-secondary"
        />
        <Button type="submit" aria-label="Send message" className="h-10 w-10 p-0">
          <SendHorizontal className="h-4 w-4" />
        </Button>
      </GlassCard>
    </form>
  );
}
