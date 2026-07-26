"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { motion } from "framer-motion";
import { Compass, Home, ArrowLeft } from "lucide-react";
import { GlassCard } from "@/components/ui/glass-card";
import { Button } from "@/components/ui/button";
import { AuroraField } from "@/components/layout/aurora-field";

export default function NotFoundPage() {
  const router = useRouter();
  return (
    <div className="relative min-h-screen w-full overflow-hidden">
      <div className="absolute inset-0"><AuroraField /></div>
      <div className="relative z-10 flex min-h-screen items-center justify-center px-5 py-10">
        <motion.div
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4 }}
          className="w-full max-w-lg"
        >
          <GlassCard className="p-10 text-center shadow-glass">
            <div className="mx-auto mb-6 grid h-20 w-20 place-items-center rounded-3xl bg-gradient-to-br from-aqua/25 to-iris/20 shadow-glow-iris">
              <Compass className="h-10 w-10 text-aqua" />
            </div>
            <p className="mb-2 font-display text-6xl font-black tracking-tight bg-gradient-to-br from-aqua via-iris-light to-iris bg-clip-text text-transparent">
              404
            </p>
            <h1 className="font-display text-2xl font-bold">This page drifted into the nebula</h1>
            <p className="mx-auto mt-3 max-w-sm text-sm text-secondary">
              The page you're looking for doesn't exist or has been moved. Let's get you back on course.
            </p>
            <div className="mt-8 flex flex-col justify-center gap-3 sm:flex-row">
              <Button variant="glass" onClick={() => router.back()}>
                <ArrowLeft className="h-4 w-4" />
                Go back
              </Button>
              <Link href="/">
                <Button variant="primary">
                  <Home className="h-4 w-4" />
                  Back to home
                </Button>
              </Link>
            </div>
          </GlassCard>
        </motion.div>
      </div>
    </div>
  );
}
