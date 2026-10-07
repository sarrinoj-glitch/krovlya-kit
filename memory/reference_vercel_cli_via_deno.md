---
name: reference-vercel-cli-via-deno
description: "Homebrew Node is broken (libsimdjson), so `vercel` CLI fails — run the installed CLI through Deno with node-compat flags; works with the user's existing login"
metadata:
  type: reference
---

`vercel` (→ node) падает с dyld-ошибкой libsimdjson. Рабочий обход (проверено 01.10.2026, Vercel CLI 54.18.7, deno 2.7.12) — запустить установленный CLI через Deno из папки проекта:

```
DENO_COMPAT=1 deno run -A --unstable-bare-node-builtins --unstable-detect-cjs --unstable-sloppy-imports --node-modules-dir=manual /opt/homebrew/lib/node_modules/vercel/dist/index.js deploy --prod --yes
```

Логин берётся из `~/Library/Application Support/com.vercel.cli/auth.json`, команда по умолчанию — team из config.json (sarrinoj-glitchs-projects). Имя нового проекта = имя папки. MCP-коннектор Vercel в этой сессии не авторизован. Локальный dev-сервер всё равно не запускать — [[feedback-no-local-server]].


**Проверка после деплоя (05.10.2026):** из сети пользователя (РФ) часть IP Vercel не отвечает — TCP открывается, TLS виснет (ERR_TIMED_OUT в браузере, curl exit 28). На тот момент не работали `64.29.17.131` и `216.198.79.131`, работали `*.195` и `76.76.21.21`. DNS отдаёт разные пары, поэтому сайт то открывается, то нет — это не сломанный деплой. Проверять так: `curl -m 10 --resolve <host>:443:76.76.21.21 https://<host>`. Если страницу должны открывать люди из РФ без VPN — предупреждать об этом заранее.
