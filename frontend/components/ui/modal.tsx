"use client";

import * as React from "react";
import { X } from "lucide-react";
import { AnimatePresence, motion } from "framer-motion";
import { cn } from "@/lib/utils";
import { GlassCard } from "@/components/ui/glass-card";
import { Button } from "@/components/ui/button";

interface ModalProps {
  open: boolean;
  onClose: () => void;
  title?: string;
  description?: string;
  children: React.ReactNode;
  className?: string;
  showCloseButton?: boolean;
  footer?: React.ReactNode;
}

export function Modal({
  open,
  onClose,
  title,
  description,
  children,
  className,
  showCloseButton = true,
  footer,
}: ModalProps) {
  React.useEffect(() => {
    if (!open) return;
    function handleKey(e: KeyboardEvent) {
      if (e.key === "Escape") onClose();
    }
    document.addEventListener("keydown", handleKey);
    document.body.style.overflow = "hidden";
    return () => {
      document.removeEventListener("keydown", handleKey);
      document.body.style.overflow = "";
    };
  }, [open, onClose]);

  return (
    <AnimatePresence>
      {open && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.18 }}
            className="absolute inset-0 bg-black/50 backdrop-blur-sm"
            onClick={onClose}
          />
          <motion.div
            initial={{ opacity: 0, scale: 0.95, y: 8 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.95, y: 8 }}
            transition={{ duration: 0.2, ease: [0.22, 1, 0.36, 1] }}
            className={cn("relative z-10 w-full max-w-lg", className)}
          >
            <GlassCard strong className="flex max-h-[85vh] flex-col overflow-hidden shadow-glass-lg">
              {(title || showCloseButton) && (
                <div className="flex items-start justify-between gap-4 border-b border-white/10 px-6 py-4">
                  <div>
                    {title && <h2 className="font-display text-lg font-semibold">{title}</h2>}
                    {description && <p className="mt-1 text-sm text-secondary">{description}</p>}
                  </div>
                  {showCloseButton && (
                    <Button variant="ghost" size="icon" onClick={onClose} aria-label="Close">
                      <X className="h-4 w-4" />
                    </Button>
                  )}
                </div>
              )}
              <div className="flex-1 overflow-y-auto px-6 py-4">{children}</div>
              {footer && (
                <div className="border-t border-white/10 px-6 py-4">{footer}</div>
              )}
            </GlassCard>
          </motion.div>
        </div>
      )}
    </AnimatePresence>
  );
}

interface ConfirmDialogProps {
  open: boolean;
  onClose: () => void;
  onConfirm: () => void;
  title?: string;
  description?: string;
  confirmLabel?: string;
  cancelLabel?: string;
  confirmVariant?: "primary" | "danger";
  isLoading?: boolean;
}

export function ConfirmDialog({
  open,
  onClose,
  onConfirm,
  title = "Are you sure?",
  description,
  confirmLabel = "Confirm",
  cancelLabel = "Cancel",
  confirmVariant = "primary",
  isLoading,
}: ConfirmDialogProps) {
  return (
    <Modal
      open={open}
      onClose={onClose}
      title={title}
      showCloseButton={false}
      footer={
        <div className="flex justify-end gap-2">
          <Button variant="glass" size="sm" onClick={onClose} disabled={isLoading}>
            {cancelLabel}
          </Button>
          <Button variant={confirmVariant} size="sm" onClick={onConfirm} disabled={isLoading}>
            {confirmLabel}
          </Button>
        </div>
      }
    >
      {description && <p className="text-sm text-secondary">{description}</p>}
    </Modal>
  );
}
