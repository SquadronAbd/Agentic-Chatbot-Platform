"use client";

import * as React from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { toast } from "sonner";
import { AuthCard } from "@/components/layout/auth-card";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Spinner } from "@/components/ui/spinner";
import { registerSchema, type RegisterValues } from "@/lib/schemas";
import { useAuthStore } from "@/store/auth-store";

export default function RegisterPage() {
  const router = useRouter();
  const regFn = useAuthStore((s) => s.register);
  const isLoading = useAuthStore((s) => s.isLoading);
  const error = useAuthStore((s) => s.error);
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated);
  const clearError = useAuthStore((s) => s.clearError);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<RegisterValues>({
    resolver: zodResolver(registerSchema),
    defaultValues: { name: "", email: "", password: "", confirmPassword: "" },
  });

  React.useEffect(() => {
    if (isAuthenticated) router.replace("/");
  }, [isAuthenticated, router]);

  React.useEffect(() => {
    if (error) {
      toast.error(error);
      clearError();
    }
  }, [error, clearError]);

  async function onSubmit(values: RegisterValues) {
    try {
      await regFn({ name: values.name, email: values.email, password: values.password });
      toast.success("Account created! Welcome.");
      router.replace("/");
    } catch {
      // handled via store effect
    }
  }

  return (
    <AuthCard
      title="Create your account"
      subtitle="Start chatting with FinRAG"
      footer={
        <>
          Already have an account?{" "}
          <Link
            href="/login"
            className="font-medium text-iris-dim underline-offset-4 hover:underline dark:text-iris-light"
          >
            Sign in
          </Link>
        </>
      }
    >
      <form className="space-y-3.5" onSubmit={handleSubmit(onSubmit)} noValidate>
        <div>
          <label className="mb-1.5 block text-xs font-mono text-secondary">Full name</label>
          <Input placeholder="Jane Doe" autoComplete="name" disabled={isLoading} {...register("name")} />
          {errors.name && <p className="mt-1 text-xs text-rose-400">{errors.name.message}</p>}
        </div>
        <div>
          <label className="mb-1.5 block text-xs font-mono text-secondary">Email</label>
          <Input
            type="email"
            placeholder="you@company.com"
            autoComplete="email"
            disabled={isLoading}
            {...register("email")}
          />
          {errors.email && <p className="mt-1 text-xs text-rose-400">{errors.email.message}</p>}
        </div>
        <div>
          <label className="mb-1.5 block text-xs font-mono text-secondary">Password</label>
          <Input
            type="password"
            placeholder="At least 8 characters"
            autoComplete="new-password"
            disabled={isLoading}
            {...register("password")}
          />
          {errors.password && (
            <p className="mt-1 text-xs text-rose-400">{errors.password.message}</p>
          )}
        </div>
        <div>
          <label className="mb-1.5 block text-xs font-mono text-secondary">Confirm password</label>
          <Input
            type="password"
            placeholder="Re-enter password"
            autoComplete="new-password"
            disabled={isLoading}
            {...register("confirmPassword")}
          />
          {errors.confirmPassword && (
            <p className="mt-1 text-xs text-rose-400">{errors.confirmPassword.message}</p>
          )}
        </div>
        <Button type="submit" className="w-full" disabled={isLoading}>
          {isLoading ? (
            <>
              <Spinner size="sm" />
              Creating account…
            </>
          ) : (
            "Create account"
          )}
        </Button>
      </form>
    </AuthCard>
  );
}
