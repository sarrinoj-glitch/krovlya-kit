---
name: feedback-no-local-server
description: "HARD RULE — never start a local dev/build server on the user's Mac; it exhausts RAM and crashes/reboots the machine. Build and run on Vercel instead."
metadata: 
  node_type: memory
  type: feedback
---

**NEVER run a local server or local production build on the user's machine.** No `npm run dev`, `next dev`, `next build`, `next start`, `python -m http.server`, `vite`, etc. on their Mac.

**Why:** The user has only ~8GB RAM and a heavy background load (VS Code + ~30 Chrome tabs + MCP servers). Local Next/Turbopack builds spike CPU and RAM → swap thrash → the Mac freezes and **hard-shuts-down / requires reboot**. The user explicitly demanded I stop doing this.

**How to apply:**
- Iterate by editing code, then `git push` + `vercel --prod --yes` (or `vercel --yes` for preview). Vercel builds in the cloud; the user's machine only uploads (light).
- Verify with `curl` against the deployed URL, not localhost.
- A quick `npm run build` JUST to type-check is also risky — prefer `npx tsc --noEmit` if a local check is truly needed, but default to letting Vercel's build catch errors. When in doubt, don't run anything heavy locally.
- Project live at https://scroll-scrub-nine.vercel.app, repo `sarrinoj-glitch/forst-architecture`. See «project-architectural-scroll» (заметка не вошла в репозиторий).
- Lightweight local commands (git, ffmpeg/avifenc with `nice -n 10 -j 2`, ls, curl) are fine; long-running servers and full builds are NOT.
