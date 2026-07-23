import Link from "next/link";
import { AuthCard } from "@/components/layout/auth-card";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";

export default function RegisterPage() {
  return (
    <AuthCard
      title="Create your account"
      subtitle="Start building with AetherChat"
      footer={
        <>
          Already have an account?{" "}
          <Link href="/login" className="font-medium text-iris-dim underline-offset-4 hover:underline dark:text-iris-light">
            Sign in
          </Link>
        </>
      }
    >
      <form className="space-y-4">
        <div>
          <label className="mb-1.5 block text-xs font-mono text-secondary">Full name</label>
          <Input placeholder="Jane Doe" required />
        </div>
        <div>
          <label className="mb-1.5 block text-xs font-mono text-secondary">Email</label>
          <Input type="email" placeholder="you@company.com" required />
        </div>
        <div>
          <label className="mb-1.5 block text-xs font-mono text-secondary">Password</label>
          <Input type="password" placeholder="••••••••" required />
        </div>
        <Button type="submit" className="w-full">
          Create account
        </Button>
      </form>
    </AuthCard>
  );
}
