# Память проекта

Заметки, которые Claude накопил за время работы над кровельным направлением. Это не инструкция, а контекст:
что уже решено, что проверено на практике и какие правила задал владелец. Новому менеджеру стоит прочитать
`project_*` и `feedback_*`; `reference_*` пригодятся, когда дойдёт до конкретного инструмента.

Сюда перенесено только то, что относится к рассылке, сайтам и продажам. Личные заметки владельца, другие клиенты
и проекты под соглашением о неразглашении в публичный репозиторий не вошли.

Пути вида `~/Desktop/MyTests/...` и `~/Downloads/...` — с компьютера владельца. У себя ориентируйся на папки этого репозитория.

- [Project: CRM кровельщиков](project_roofing_crm.md) — Google Таблица на троих (Ильяс, Зураб, Тимурлан) + страница-очередь; как собирается и что импортируется из xlsx
- [Project: сайт «Ван»](project_van_krovlya.md) — копия Липецк Кровли v3 под кровельщика из Краснодара в MyTests/van-krovlya, live sarrinoj-glitch.github.io/van-krovlya; к репо/Vercel оригинала не подключать
- [Project: AI clinic SaaS GTM](project_ai_clinic_saas.md) — Kai/Mike-model recurring AI-админ+ассистент для РФ клиник/натяжных; продаём заявки, не сайты
- [Reference: parser-2gis](reference_parser_2gis.md) — working CLI command with anti-bot tweaks (no-headless, no-disable-images, JSON output)
- [Reference: HTML→PDF](reference_html_to_pdf.md) — headless Chrome + the print-CSS rules that stop layouts breaking; verify with pdftoppm
- [Reference: Vercel CLI via Deno](reference_vercel_cli_via_deno.md) — node broken → run installed vercel CLI under deno with compat flags; deploy works
- [Feedback: no invented numbers](feedback_no_invented_numbers.md) — every figure in client materials = fact / user norm / labeled assumption; user asks «откуда это?»
- [Feedback: communication style](feedback_communication_style.md) — terse, decisive, structured A/B/C/D choices; no long lectures
- [Feedback: design vs conversion](feedback_design_vs_conversion.md) — premium effects don't replace sales mechanics; layer conversion on top
- [Feedback: case copy style](feedback_case_copy_style.md) — кейсы и тексты для клиентов: подробно, человеческим языком, с «почему», фактура из хранилищ Obsidian
- [Feedback: NO local server](feedback_no_local_server.md) — HARD RULE: never run dev/build server locally (8GB Mac crashes); build on Vercel
- [User role](user_role.md) — developer/founder selling website services to Moscow clinics via cold call
