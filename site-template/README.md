# Сайт по шаблону

`skeleton/index.html` — готовая страница-образец (сайт компании «Ван»). `make_site.py` подставляет в неё содержимое из JSON-файла компании и складывает готовый сайт в `sites/<slug>/`.

```bash
python3 make_site.py companies/van.json            # собрать
python3 make_site.py companies/van.json --check     # убедиться, что образец воспроизводится без изменений
python3 tools/prep_photos.py ~/Downloads/фото assets/<slug>   # подготовить фото
```

| Папка | Что в ней |
|---|---|
| `companies/` | по одному JSON на компанию; `van.json` — образец |
| `skeleton/` | страница-образец: разметка, стили, скрипты |
| `frames/`, `frames-sm/` | кадры анимации первого экрана для компьютера и телефона |
| `assets/fonts/` | шрифт заголовков |
| `assets/<slug>/` | фото компании, `.jpg` + `.webp` |
| `sites/` | собранные сайты, в git не попадают |

Порядок работы и правила — в [../PLAYBOOK.md](../PLAYBOOK.md), шаг 5.
