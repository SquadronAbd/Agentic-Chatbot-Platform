import type { Metadata } from "next";
import { Space_Grotesk, Plus_Jakarta_Sans, Sora, IBM_Plex_Mono } from "next/font/google";
import { ThemeProvider } from "@/components/theme/theme-provider";
import { AppQueryProvider } from "@/providers/query-provider";
import { Toaster } from "sonner";
// TypeScript may complain about side-effect CSS imports in some setups.
// @ts-ignore
import "./globals.css";

const spaceGrotesk = Space_Grotesk({
  subsets: ["latin"],
  variable: "--space-grotesk",
  display: "swap",
});

const plusJakarta = Plus_Jakarta_Sans({
  subsets: ["latin"],
  variable: "--plus-jakarta",
  display: "swap",
});

const sora = Sora({
  subsets: ["latin"],
  variable: "--sora",
  display: "swap",
});

const plexMono = IBM_Plex_Mono({
  subsets: ["latin"],
  weight: ["400", "500"],
  variable: "--plex-mono",
  display: "swap",
});

export const metadata: Metadata = {
  title: "FinRAG",
  description: "FinRAG is a multi-agent AI platform for intelligent document and conversation experiences.",
};

const PUBLIC_PATHS = ["/login", "/register", "/403", "/404"];

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html
      lang="en"
      suppressHydrationWarning
      className={`${spaceGrotesk.variable} ${plusJakarta.variable} ${sora.variable} ${plexMono.variable}`}
    >
      <body className="font-body antialiased">
        <AppQueryProvider>
          <ThemeProvider>
            {children}
            <Toaster
              richColors
              closeButton
              position="top-right"
              toastOptions={{
                className: "glass glass-highlight glass-strong font-body",
              }}
              style={{
                backdropFilter: "blur(20px)",
              }}
            />
          </ThemeProvider>
        </AppQueryProvider>
      </body>
    </html>
  );
}
