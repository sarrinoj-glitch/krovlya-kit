#!/usr/bin/env python3
"""Вариант страницы с тёмным первым экраном-слайдшоу (как на основном домене Липецк Кровли).

    python3 make_site.py companies/<slug>.json      # сначала обычная сборка
    python3 tools/make_v4.py companies/<slug>.json  # → sites/<slug>/v4.html

Первый экран берётся из skeleton/v4.html, остальные блоки — из уже собранного sites/<slug>/index.html.
Тексты первого экрана задаются в JSON компании, в разделе "v4": slides, hotcards, plate, brand_sub, cta2, bg_alt.
slides — имена фото из assets/<slug>/ (без расширения). Если раздела slides нет, ставятся четыре фото-заглушки из assets/slides."""
import re, json, shutil, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
c = json.loads(Path(sys.argv[1]).resolve().read_text(encoding='utf-8'))
v = c.get('v4', {})
SITE = ROOT / 'sites' / c['slug']
s = (ROOT / 'skeleton' / 'v4.html').read_text(encoding='utf-8'); k = (SITE / 'index.html').read_text(encoding='utf-8')
tel, tel_txt, wa = '+' + c['phone'], c['phone_text'], 'https://wa.me/' + c['phone']

def sub_once(pattern, repl, text):
    new, n = re.subn(pattern, lambda m: repl, text, count=1, flags=re.S)
    assert n == 1, 'в шаблоне не найден блок: ' + pattern[:60]
    return new
def grab(pattern, text):
    m = re.search(pattern, text, re.S); assert m, pattern[:60]; return m.group(0)

CHECK = '<span class="hp-plate-check"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"><path d="M20 6 9 17l-5-5"/></svg></span>'
WA_PATH = re.search(r'aria-label="Написать в WhatsApp">\s*<svg viewBox="0 0 24 24" fill="currentColor"><path d="([^"]+)"', s).group(1)
ICONS = ['<path d="M3 11.5 12 4l9 7.5"/><path d="M5 10v9h14v-9"/>', '<rect x="3" y="5" width="18" height="14" rx="2"/><path d="M3 10h18M9 5v14"/>',
         '<path d="M4 21V7l3-3 3 3v14M10 21V7l3-3 3 3v14M16 21V7l3-3 2 2v15"/>', '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>']
slides = [f'assets/{c["slug"]}/{n}' for n in v['slides']] if v.get('slides') else [f'assets/slides/slide-0{i}' for i in range(1, 5)]

s = sub_once(r'<title>.*?</title>', f"<title>{c['title']}</title>", s)
s = sub_once(r'<meta name="description" content="[^"]*">', f'<meta name="description" content="{c["description"]}">', s)
s = sub_once(r"    \.hp-s1 \{ background-image: url\('assets/van/hero-1\.jpg'\); \}.*?\n    \}\n", ''.join(f"    .hp-s{i + 1} {{ background-image: url('{p}.jpg'); }}\n" for i, p in enumerate(slides)) +
             "    @supports (background-image: image-set(url('x.webp') type('image/webp'))) {\n" + ''.join(f"      .hp-s{i + 1} {{ background-image: image-set(url('{p}.webp') type('image/webp'), url('{p}.jpg') type('image/jpeg')); }}\n" for i, p in enumerate(slides)) + "    }\n", s)
s = sub_once(r'<div class="loader-logo">.*?</div>', f'<div class="loader-logo">{c["brand"]}<span>.</span></div>', s)
s = sub_once(r'<nav id="navbar">.*?</nav>', grab(r'<nav id="navbar">.*?</nav>', k), s)
hot = '\n'.join(f'''    <div class="hp-hotcard hp-c{i + 1}">
      <span class="hp-hotcard-ic"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round">{ICONS[i]}</svg></span>
      <span class="hp-hotcard-tx"><span class="hp-hotcard-title">{t}</span><span class="hp-hotcard-sub">{sub}</span></span>
    </div>''' for i, (t, sub) in enumerate(v['hotcards'][:4]))
plate = '\n'.join(f'            <li class="hp-plate-item">{CHECK}{t}</li>' for t in v['plate'][:3])
hero = f'''<section class="hp-hero" id="v3-hero" aria-label="Главный экран">
  <div class="hp-hero-bg" role="img" aria-label="{v.get("bg_alt", "Фото для примера")}">
{chr(10).join(f'    <div class="hp-hero-slide hp-s{i + 1}{" is-active" if i == 0 else ""}"></div>' for i in range(len(slides)))}
  </div>
  <div class="hp-hero-grade"></div>
  <div class="hp-hero-glow"></div>
  <div class="hp-foliage hp-foliage-tl"></div>
  <div class="hp-foliage hp-foliage-br"></div>
  <div class="hp-hero-vignette"></div>
  <div class="hp-hero-grain"></div>

  <header class="hp-header">
    <a class="hp-brand" href="#v3-hero" aria-label="{c["brand"]} — на главную">
      <span class="hp-brand-mark" aria-hidden="true">
        <svg viewBox="0 0 24 24" fill="none" stroke="#040a18" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 11.5 12 4l9 7.5"/><path d="M5 10v9h14v-9"/><path d="M9.5 19v-5h5v5"/></svg>
      </span>
      <span class="hp-brand-text">
        <span class="hp-brand-name">{c["brand"]}</span>
        <span class="hp-brand-sub">{v.get("brand_sub", "")}</span>
      </span>
    </a>
    <nav class="hp-nav" aria-label="Основная навигация">
{chr(10).join(f'      <a href="{h}">{t}</a>' for h, t in c["header_nav"])}
    </nav>
    <div class="hp-header-right">
      <a class="hp-contacts" href="tel:{tel}">
        <span class="hp-contacts-phone">{tel_txt}</span>
        <span class="hp-contacts-hours">{c["hours_short"]}</span>
      </a>
      <div class="hp-messengers">
        <a class="hp-msg-btn" href="{wa}" aria-label="Написать в WhatsApp">
          <svg viewBox="0 0 24 24" fill="currentColor"><path d="{WA_PATH}"/></svg>
        </a>
      </div>
      <a class="hp-btn-cta" href="#cta"><span>{c["cta_label"]}</span><svg viewBox="0 0 24 24" fill="none" stroke="#040a18" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" style="width:16px;height:16px"><path d="M5 12h14M13 6l6 6-6 6"/></svg></a>
      <button class="hp-burger" aria-label="Открыть меню">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M4 7h16M4 12h16M4 17h16"/></svg>
      </button>
    </div>
  </header>

  <div class="hp-hotspots" aria-hidden="true">
{hot}
  </div>

  <div class="hp-hero-inner">
    <div class="hp-hero-content">
      <span class="hp-eyebrow hp-reveal hp-r1">{c["hero"]["eyebrow"]}</span>
      <h1 class="hp-hero-title hp-reveal hp-r2">{c["hero"]["title_html"]}</h1>
      <div class="hp-hero-offer hp-reveal hp-r3">
        <div class="hp-hero-plate">
          <ul class="hp-plate-list">
{plate}
          </ul>
          <a class="hp-btn-primary" href="#cta">{c["cta_label"]}<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" style="width:18px;height:18px;margin-left:10px"><path d="M5 12h14M13 6l6 6-6 6"/></svg></a>
          <a class="hp-btn-play hp-btn-catalog" href="#services">
            <span class="hp-play-ic"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round"><path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"/><path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/></svg></span>
            <span>{v.get("cta2", "Посмотреть услуги")}</span>
          </a>
        </div>
      </div>
    </div>
  </div>

  <div class="hp-scroll-hint" aria-hidden="true">
    <span class="hp-scroll-mouse"></span>
    Листайте
  </div>
</section>'''
s = sub_once(r'<section class="hp-hero" id="v3-hero".*?</section>', hero, s)
s = sub_once(r'<!-- Баннер[^\n]*-->\s*<section class="v4-banner".*?</section>\s*', '', s)
s = sub_once(r'<section id="advantages".*?</section>\s*', '', s)
s = sub_once(r'<section id="gallery".*?</section>\s*', '', s)
has_why = '<section id="why"' in k
for pat in (r'<section id="services" class="section">.*?</section>', r'<section id="why" class="section">.*?</section>', r'<section id="process" class="v3-timeline">.*?</section>',
            r'<section id="faq" class="section section-tone-warm">.*?</section>', r'<section id="cta" class="final-cta">.*?</section>', r'<footer>.*?</footer>'):
    if 'id="why"' in pat and not has_why:
        s = sub_once(r'(<!-- Отзывы -->\s*)?' + pat + r'\s*', '', s); continue
    s = sub_once(pat, grab(pat, k), s)
s = re.sub(r'<style>\s*/\* отзывы: три статичные карточки вместо бегущей ленты \*/.*?</style>\s*', '', s, count=1, flags=re.S)
s = sub_once(r'</style>\s*\n\s*<!-- Первый экран', '''/* кнопка-бургер в шаблоне ничего не открывает — скрываем */
.hp-burger { display: none !important; }
/* блоки, перенесённые из основной версии сайта */
.section-visual.van-photo { border-radius: 14px; overflow: hidden; box-shadow: var(--shadow-card); }
.section-visual.van-photo picture { display: block; width: 100%; height: 100%; }
.section-visual.van-photo img { object-fit: cover; }
.van-reviews { margin-top: 56px; display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 18px; }
.van-reviews .v3-testi { width: auto; }
.van-reviews a.v3-testi { text-decoration: none; }
.van-reviews .v3-testi-text strong { display: block; color: #fff; font-family: 'Space Grotesk', sans-serif; font-size: 1.5rem; line-height: 1.2; margin-bottom: 6px; }
@media (max-width: 860px) { .van-reviews { grid-template-columns: 1fr; } }
@media (max-width: 1024px) {
  .why-item:not(:first-child):not(:last-child) .why-photo { margin-left: 0; margin-right: 0; }
  .why-photo { margin-top: 20px; }
}
</style>

<!-- Первый экран''', s)
s = sub_once(r"const WA_NUMBER = '\d+';", f"const WA_NUMBER = '{c['phone']}';", s)
s = sub_once(r"      root\.querySelector\('\[data-calc-total\]'\)\.innerHTML = 'от ' \+ fmt\(data\.area \* data\.min\) \+ '<br>до ' \+ fmt\(data\.area \* data\.max\) \+ ' ₽';",
             "      root.querySelector('[data-calc-total]').innerHTML = data.max ? 'от ' + fmt(data.area * data.min) + '<br>до ' + fmt(data.area * data.max) + ' ₽' : (root.dataset.noPrice || 'Посчитаем<br>после осмотра');", s)
s = sub_once(r"      const text = 'Здравствуйте! Хочу рассчитать кровлю\. Площадь: ' \+ data\.area \+ ' м²\. Тип: ' \+ data\.label \+ '\.';",
             "      const text = (root.dataset.waIntro || 'Здравствуйте! Хочу рассчитать кровлю.') + ' Площадь: ' + data.area + ' м². ' + (root.dataset.waType || 'Тип') + ': ' + data.label + '.';", s)
if 'name="robots"' not in s:
    s = s.replace('<meta name="viewport" content="width=device-width, initial-scale=1.0">', '<meta name="viewport" content="width=device-width, initial-scale=1.0">\n  <meta name="robots" content="noindex, nofollow">', 1)
if c.get('demo_note'):
    s = s.replace('<body>', '<body>\n<div style="background:#111B30;color:#fff;font:600 13px/1.4 Manrope,system-ui,sans-serif;text-align:center;padding:9px 16px;position:relative;z-index:50">' + c['demo_note'] + '</div>', 1)
(SITE / 'v4.html').write_text(s, encoding='utf-8')
if not v.get('slides'):
    shutil.copytree(ROOT / 'assets' / 'slides', SITE / 'assets' / 'slides', dirs_exist_ok=True)
visible = re.sub(r'<style\b.*?</style>|<script\b.*?</script>|<!--.*?-->', ' ', s[s.index('<body'):], flags=re.S)
left = sorted(set(re.findall(r'Ван\b|9180999091|assets/van/[\w.-]+|#advantages|#gallery', visible)))
print('готово:', SITE / 'v4.html', '| остатки образца:', left or 'нет')
