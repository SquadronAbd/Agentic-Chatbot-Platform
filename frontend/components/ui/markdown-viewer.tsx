import * as React from "react";
import { motion, AnimatePresence } from "framer-motion";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import rehypeRaw from "rehype-raw";
import { Prism as SyntaxHighlighter } from "react-syntax-highlighter";
import { oneDark, oneLight } from "react-syntax-highlighter/dist/esm/styles/prism";
import { Check, Copy } from "lucide-react";
import { cn } from "@/lib/utils";
import { useUIStore } from "@/store/ui-store";

function CodeBlock({
  inline,
  className,
  children,
}: { inline?: boolean; className?: string; children?: React.ReactNode }) {
  const match = /language-(\w+)/.exec(className || "");
  const code = String(children ?? "").replace(/\n$/, "");
  const [copied, setCopied] = React.useState(false);
  const theme = useUIStore((s) => s.theme);

  if (!inline && match) {
    const SH = SyntaxHighlighter as any;
    return (
      <div className="my-4 overflow-hidden rounded-xl border border-white/10">
        <div className="flex items-center justify-between border-b border-white/10 bg-black/20 px-4 py-2 text-xs text-secondary">
          <span className="font-mono">{match[1]}</span>
          <button
            type="button"
            onClick={() => {
              void navigator.clipboard.writeText(code);
              setCopied(true);
              window.setTimeout(() => setCopied(false), 2000);
            }}
            className="inline-flex items-center gap-1 hover:text-[var(--text-primary)]"
          >
            {copied ? <Check className="h-3.5 w-3.5 text-emerald-400" /> : <Copy className="h-3.5 w-3.5" />}
            {copied ? "Copied" : "Copy"}
          </button>
        </div>
        <SH
          language={match[1]}
          PreTag="div"
          style={(theme === "dark" ? oneDark : oneLight) as any}
          customStyle={{ margin: 0, borderRadius: 0, fontSize: 13 }}
          codeTagProps={{ style: { fontFamily: "var(--font-mono)" } }}
        >
          {code}
        </SH>
      </div>
    );
  }

  return (
    <code
      className={cn(
        "rounded-md bg-white/15 px-1.5 py-0.5 font-mono text-[13px]",
        className
      )}
    >
      {children}
    </code>
  );
}

export function MarkdownViewer({
  content,
  className,
  animate,
}: {
  content: string;
  className?: string;
  animate?: boolean;
}) {
  const Wrapper = animate ? motion.div : React.Fragment;
  const wrapperProps = animate
    ? {
        initial: { opacity: 0, y: 4 },
        animate: { opacity: 1, y: 0 },
        transition: { duration: 0.25 },
      }
    : {};

  return (
    <Wrapper {...(wrapperProps as object)}>
      <article className={cn("prose prose-sm max-w-none text-[var(--text-primary)] prose-strong:font-semibold prose-a:text-iris prose-headings:font-display dark:prose-invert", className)}>
        <ReactMarkdown
          remarkPlugins={[remarkGfm]}
          rehypePlugins={[rehypeRaw]}
          components={{
            code: CodeBlock as unknown as React.ComponentType<React.ComponentPropsWithoutRef<"code"> & { inline?: boolean }>,
            p: ({ children }) => <p className="mb-3 leading-relaxed last:mb-0">{children}</p>,
            ul: ({ children }) => <ul className="mb-3 ml-5 list-disc space-y-1">{children}</ul>,
            ol: ({ children }) => <ol className="mb-3 ml-5 list-decimal space-y-1">{children}</ol>,
            li: ({ children }) => <li className="leading-relaxed">{children}</li>,
            blockquote: ({ children }) => (
              <blockquote className="mb-3 border-l-2 border-iris/60 pl-4 italic text-secondary">
                {children}
              </blockquote>
            ),
            table: ({ children }) => (
              <div className="my-4 overflow-x-auto rounded-xl border border-white/10">
                <table className="w-full text-sm">{children}</table>
              </div>
            ),
            th: ({ children }) => (
              <th className="border-b border-white/10 bg-white/5 px-4 py-2 text-left font-semibold">{children}</th>
            ),
            td: ({ children }) => (
              <td className="border-b border-white/5 px-4 py-2">{children}</td>
            ),
            h1: ({ children }) => <h1 className="mb-4 mt-6 font-display text-2xl font-bold">{children}</h1>,
            h2: ({ children }) => <h2 className="mb-3 mt-5 font-display text-xl font-bold">{children}</h2>,
            h3: ({ children }) => <h3 className="mb-2 mt-4 font-display text-lg font-semibold">{children}</h3>,
            hr: () => <hr className="my-5 border-white/10" />,
            a: ({ href, children }) => (
              <a
                href={href}
                target="_blank"
                rel="noopener noreferrer"
                className="text-iris underline-offset-2 hover:underline"
              >
                {children}
              </a>
            ),
          }}
        >
          {content}
        </ReactMarkdown>
      </article>
    </Wrapper>
  );
}

export { AnimatePresence };
