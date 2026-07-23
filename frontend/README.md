# AetherChat — Frontend

A Next.js 14 (App Router) frontend for the Agentic Chatbot Platform, implementing the routes and components from spec section 9, styled as **glassmorphism with a day/night toggle** — frosted panels floating over a slowly drifting "aurora" of blurred color, with fonts, palette, and glow intensity all swapping when you flip the switch.

## Design system

| Axis | Day (`light`) | Night (`dark`) |
|---|---|---|
| Background | `#EEF2FF → #F4F7FF` soft gradient | `#0A0B16 → #12142B` deep gradient |
| Glass panel | `rgba(255,255,255,.55)`, warm highlight sweep | `rgba(18,18,34,.45)`, cooler, glowing edges |
| Accent | Iris `#6C5CE7` + Aqua `#22D3EE` | Iris `#8C7CFF` + Aqua `#38E1FF` (glowing) |
| Display font | `Space Grotesk` (both themes — holds identity) |
| Body font | `Plus Jakarta Sans` (warm, humanist) | `Sora` (sharper, geometric) — **swaps on toggle** |
| Data/mono | `IBM Plex Mono` (timestamps, token counts, badges — both themes) |

The signature element is the **aurora field** (`components/layout/aurora-field.tsx`): three blurred, slowly-drifting gradient blobs behind every screen. Glassmorphism only reads as *glass* if there's something colorful blurred behind the panel — the aurora is that color source, and its palette/motion changes per theme.

## Routes (spec 9.1)

| Route | Access | Notes |
|---|---|---|
| `/login`, `/register` | Public | Centered glass card over full-bleed aurora |
| `/` | Authenticated | Chat interface |
| `/conversations` | Authenticated | Conversation list |
| `/documents` | Agent+ | Knowledge base manager, gated by `RoleGuard` |
| `/analytics` | Manager+ | Gated by `RoleGuard` |
| `/admin` | Admin only | Gated by `RoleGuard` |
| `/settings` | Authenticated | Profile & API keys |

## Key components (spec 9.2)

- `components/chat/chat-window.tsx` — message history, lightweight markdown (bold/inline code)
- `components/chat/streaming-message.tsx` — simulates the SSE token-by-token reveal `useChat` (Vercel AI SDK) will drive once `/chat/stream` is live
- `components/documents/document-uploader.tsx` — drag-and-drop with a progress bar, standing in for polling `GET /documents` while status is `processing`
- `components/auth/role-guard.tsx` — client-side RBAC gate mirroring the backend's permission matrix (spec 5.1) for immediate UI feedback; **the API Gateway remains the real source of truth**, this is UX only
- `components/analytics/analytics-dashboard.tsx` — Recharts line + bar charts
- `components/admin/user-table.tsx` — paginated table with an inline role-change `<select>`

## Running it

```bash
npm install
npm run dev   # http://localhost:3000
```

This is a **standalone frontend with mock data** (`lib/mock-data.ts`) — the backend (FastAPI, LangGraph agent service, Postgres) from spec sections 2–8 doesn't exist yet. Every page renders real, interactive UI against realistic sample data so the design and RBAC gating can be reviewed before the backend is wired up. Swap in real fetching (React Query is already a dependency) once `/api/v1/*` endpoints exist.

## Known items to revisit before shipping

- **Next.js security advisories**: `npm audit` currently reports one unpatched high-severity advisory range that only has a fix at Next.js **16.x**. Since the spec pins Next.js 14, this project stays on the latest patched `14.2.x` (`14.2.35`) rather than jumping two major versions unreviewed. Re-run `npm audit` before production deployment and decide then whether to upgrade to 15/16.
- **Auth is not wired up.** Login/register forms submit nowhere yet — they're ready for `POST /auth/login` / `POST /auth/register` (spec 8.1) once available.
- **`RoleGuard` is client-side only.** It's for UI polish (hiding/disabling nav, showing a 403 card) — actual authorization must stay enforced server-side per the RBAC matrix.
- Verified with `npm run build`: all 9 routes compile and prerender successfully.
