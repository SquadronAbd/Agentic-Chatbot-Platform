import Link from "next/link";
import { AuthCard } from "@/components/layout/auth-card";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";

export default function LoginPage() {
  return (
    <AuthCard
      title="Welcome back"
      subtitle="Sign in to AetherChat"
      footer={
        <>
          New here?{" "}
          <Link href="/register" className="font-medium text-iris-dim underline-offset-4 hover:underline dark:text-iris-light">
            Create an account
          </Link>
        </>
      }
    >
      <form className="space-y-4">
        <div>
          <label className="mb-1.5 block text-xs font-mono text-secondary">Email</label>
          <Input type="email" placeholder="you@company.com" required />
        </div>
        <div>
          <label className="mb-1.5 block text-xs font-mono text-secondary">Password</label>
          <Input type="password" placeholder="••••••••" required />
        </div>
        <Button type="submit" className="w-full">
          Sign in
        </Button>
      </form>
    </AuthCard>
  );
}
