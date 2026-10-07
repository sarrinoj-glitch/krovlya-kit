#!/usr/bin/env python3
"""Собирает сайт кровельной компании из шаблона.

    python3 make_site.py companies/van.json            → sites/van/
    python3 make_site.py companies/van.json --check     → сравнить с образцом skeleton/index.html

Шаблон (skeleton/index.html) — готовая страница-образец. Скрипт меняет в ней только содержимое:
шапку, первый экран, услуги, отзывы, шаги, вопросы, финальный блок, подвал и номер WhatsApp.
Стили, анимация и скрипты остаются как есть. Все тексты и цифры берутся из JSON-файла компании:
в них должны быть только проверяемые факты (см. PLAYBOOK.md)."""
import json, re, shutil, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SKELETON = ROOT / 'skeleton' / 'index.html'

ARROW = '<svg class="btn-arrow" width="16" height="16" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="3" y1="8" x2="13" y2="8"/><polyline points="9 4 13 8 9 12"/></svg>'
WA_PATH = 'M17.5 14.4c-.3-.15-1.77-.87-2.04-.97-.27-.1-.47-.15-.67.15-.2.3-.77.97-.95 1.17-.17.2-.35.22-.65.07-.3-.15-1.26-.46-2.4-1.48-.89-.79-1.49-1.77-1.66-2.07-.17-.3-.02-.46.13-.61.13-.13.3-.35.45-.52.15-.17.2-.3.3-.5.1-.2.05-.37-.02-.52-.07-.15-.67-1.62-.92-2.22-.24-.58-.49-.5-.67-.51l-.57-.01c-.2 0-.52.07-.79.37-.27.3-1.04 1.02-1.04 2.48 0 1.46 1.07 2.88 1.22 3.08.15.2 2.1 3.2 5.08 4.49.71.31 1.26.49 1.69.63.71.22 1.36.19 1.87.12.57-.09 1.77-.72 2.02-1.42.25-.7.25-1.3.17-1.42-.07-.13-.27-.2-.57-.35zM12.05 21.5h-.01a9.4 9.4 0 0 1-4.8-1.32l-.34-.2-3.57.94.95-3.48-.22-.36a9.43 9.43 0 1 1 8 4.42zM12.05 2a11.4 11.4 0 0 0-9.86 17.13L1 23l3.96-1.04A11.4 11.4 0 1 0 12.05 2z'
TG_PATH = 'M21.94 4.6 18.9 19.2c-.23 1.02-.84 1.27-1.7.79l-4.7-3.46-2.27 2.18c-.25.25-.46.46-.94.46l.33-4.78L18.4 5.6c.38-.34-.08-.53-.59-.19L6.07 12.96l-4.66-1.46c-1.01-.32-1.03-1.01.21-1.5L20.64 3.1c.84-.32 1.58.2 1.3 1.5z'
FAQ_ICON = '<span class="faq-icon" aria-hidden="true"><svg width="14" height="14" viewBox="0 0 14 14" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"><line x1="7" y1="2" x2="7" y2="12"/><line x1="2" y1="7" x2="12" y2="7"/></svg></span>'
CHIP = '<span class="v3-trust-chip"><svg viewBox="0 0 24 24" fill="none" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">{ic}</svg>{t}</span>'
# иконки идут по порядку: первая плашка — первая иконка и т.д.
CHIP_ICONS = [
    '<path d="m12 2 9 5-9 5-9-5 9-5z"/><path d="m3 12 9 5 9-5"/><path d="m3 17 9 5 9-5"/>',
    '<rect x="3" y="5" width="18" height="14" rx="2"/><path d="M3 10h18M9 5v14"/>',
    '<path d="M1 3h15v13H1z"/><path d="M16 8h4l3 3v5h-7z"/><circle cx="5.5" cy="18.5" r="2.5"/><circle cx="18.5" cy="18.5" r="2.5"/>',
    '<path d="M3 17h13V9H9l-3 4H3z"/><circle cx="7" cy="18" r="2"/><circle cx="14" cy="18" r="2"/><path d="M16 12h5v5"/>',
]
STEP_ICONS = [
    '<path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72c.13.96.36 1.9.7 2.81a2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45c.91.34 1.85.57 2.81.7A2 2 0 0 1 22 16.92z"/>',
    '<path d="M3 7V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2v2"/><rect x="3" y="7" width="18" height="14" rx="2"/><line x1="7" y1="11" x2="17" y2="11"/>',
    '<rect x="4" y="4" width="16" height="16" rx="2"/><line x1="9" y1="9" x2="15" y2="9"/><line x1="9" y1="13" x2="15" y2="13"/><line x1="9" y1="17" x2="13" y2="17"/>',
    '<path d="M5 4h14a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2z"/><path d="M9 12l2 2 4-4"/>',
    '<path d="M3 9h18"/><path d="M5 9v10h14V9"/><path d="M9 19v-5h6v5"/>',
    '<circle cx="12" cy="12" r="10"/><path d="M9 12l2 2 4-4"/>',
]


def sub_once(pattern, repl, text):
    new, n = re.subn(pattern, lambda m: repl, text, count=1, flags=re.S)
    assert n == 1, 'в шаблоне не найден блок: ' + pattern[:60]
    return new


def picture(base, alt, w, h, indent='          '):
    return (f'{indent}<picture>\n{indent}  <source srcset="{base}.webp" type="image/webp">\n'
            f'{indent}  <img src="{base}.jpg" alt="{alt}" loading="lazy" decoding="async" width="{w}" height="{h}">\n{indent}</picture>')


def build(c):
    s = SKELETON.read_text(encoding='utf-8')
    tel, tel_txt = '+' + c['phone'], c['phone_text']
    wa = 'https://wa.me/' + c['phone']
    tg = c.get('telegram') or ''
    links = lambda items: '\n'.join(f'    <a href="{h}">{t}</a>' for h, t in items)

    s = sub_once(r'<title>.*?</title>', f"<title>{c['title']}</title>", s)
    s = sub_once(r'<meta name="description" content="[^"]*">', f'<meta name="description" content="{c["description"]}">', s)
    s = sub_once(r'<div class="loader-logo">.*?</div>', f'<div class="loader-logo">{c["brand"]}<span>.</span></div>', s)
    s = sub_once(r'<nav id="navbar">.*?</nav>', f'''<nav id="navbar">
  <a href="#v3-hero" class="nav-logo">{c["brand"]}<span>.</span></a>
  <div class="nav-links">
{links(c["nav"])}
  </div>
  <div class="nav-right">
    <a href="tel:{tel}" class="nav-phone">{tel_txt}</a>
    <a href="#cta" class="nav-cta">{c["cta_label"]}</a>
  </div>
</nav>''', s)

    tg_btn = f'''
        <a class="hp-msg-btn" href="{tg}" aria-label="Написать в Telegram">
          <svg viewBox="0 0 24 24" fill="currentColor"><path d="{TG_PATH}"/></svg>
        </a>''' if tg else ''
    s = sub_once(r'<header class="hp-header">.*?</header>', f'''<header class="hp-header">
    <a class="hp-brand" href="#v3-hero" aria-label="{c["brand"]} — на главную">
      <span class="hp-brand-mark" aria-hidden="true">
        <svg viewBox="0 0 24 24" fill="none" stroke="#040a18" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 9h18"/><path d="M5 9v10h14V9"/><path d="M9 19v-5h6v5"/></svg>
      </span>
      <span class="hp-brand-text">
        <span class="hp-brand-name">{c["brand"]}</span>
        <span class="hp-brand-sub">{c["tagline"]}</span>
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
        </a>{tg_btn}
      </div>
      <a class="hp-btn-cta" href="#cta"><span>{c["cta_label"]}</span><svg viewBox="0 0 24 24" fill="none" stroke="#040a18" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" style="width:16px;height:16px"><path d="M5 12h14M13 6l6 6-6 6"/></svg></a>
      <button class="hp-burger" aria-label="Открыть меню">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M4 7h16M4 12h16M4 17h16"/></svg>
      </button>
    </div>
  </header>''', s)

    h = c['hero']
    chips = '\n          '.join(CHIP.format(ic=CHIP_ICONS[i % 4], t=t) for i, t in enumerate(h['chips']))
    s = sub_once(r'<div class="hp-hero-content">.*?</div>\s*</div>\s*(?=<!-- ПРАВО: scroll-видео)', f'''<div class="hp-hero-content">
      <span class="hp-eyebrow hp-reveal hp-r1">{h["eyebrow"]}</span>
      <h1 class="hp-hero-title hp-reveal hp-r2">{h["title_html"]}</h1>
      <p class="hp-hero-subtitle hp-reveal hp-r3">{h["subtitle_html"]}</p>
      <div class="v3-hero-cta hp-reveal hp-r4">
        <a class="hp-btn-primary" href="#cta">{c["cta_label"]}<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" style="width:18px;height:18px;margin-left:10px"><path d="M5 12h14M13 6l6 6-6 6"/></svg></a>
        <a class="hp-btn-play hp-btn-catalog" href="#services">
          <span class="hp-play-ic"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round"><path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"/><path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/></svg></span>
          <span>{h["cta2"]}</span>
        </a>
      </div>
      <div class="v3-trust hp-reveal hp-r4" aria-label="{h["chips_aria"]}">
        <span class="v3-trust-label">{h["chips_label"]}</span>
        <div class="v3-trust-list">
          {chips}
        </div>
      </div>
    </div>
  </div>

  ''', s)

    def card(k, show, hide):
        p = f' data-prefix="{k["prefix"]}"' if k.get('prefix') else ''
        return f'''      <div class="annotation-card" data-show="{show}" data-hide="{hide}">
        <div class="card-number">{k["label"]}</div>
        <h3 class="card-title">{k["title"]}</h3>
        <p class="card-desc">{k["desc"]}</p>
        <div class="card-stat">
          <span class="card-stat-number" data-count="{k["count"]}"{p} data-suffix="{k["suffix"]}">0</span>
          <span class="card-stat-label">{k["stat_label"]}</span>
        </div>
      </div>'''
    zones = [('0', '0.26'), ('0.28', '0.50'), ('0.52', '0.74'), ('0.76', '0.98')]
    assert len(c['cards']) == 4, 'под анимацией ровно четыре подписи'
    cards = '\n\n'.join(card(k, *zones[i]) for i, k in enumerate(c['cards']))
    s = sub_once(r'<div class="v3-cards">.*?</div>\s*</div>\s*(?=<div class="hp-scroll-hint")', f'''<div class="v3-cards">
{cards}
    </div>
  </div>

  ''', s)

    sv = c['services']
    assert len(sv['items']) == 4 and len(sv['tabs']) == 5, 'в сетке услуг четыре карточки и пять вкладок (первая — «все»)'

    def service(i, it):
        d = f' data-delay="{i * 100}"' if i else ''
        return f'''      <article class="service-card v3-reveal-up" data-tab-idx="{i}"{d}>
        <div class="service-num">{it["num"]}</div>
        <h3 class="service-title">{it["title"]}</h3>
        <p class="service-desc">{it["desc"]}</p>
        <div class="service-meta">
          <span class="service-tag">{it["tag"]}</span>
          <a href="#cta" class="service-cta">{it["cta"]} →</a>
        </div>
      </article>'''
    tabs = '\n'.join(f'        <button class="v3-tab{" is-active" if i == 0 else ""}" data-tab="{"all" if i == 0 else i - 1}" role="tab">{t}</button>' for i, t in enumerate(sv['tabs']))
    ph = sv['photo']
    s = sub_once(r'<section id="services" class="section">.*?</section>', f'''<section id="services" class="section">
  <div class="section-inner">
    <div class="section-head">
      <div>
        <span class="section-eyebrow">{sv["eyebrow"]}</span>
        <h2 class="section-title">{sv["title_html"]}</h2>
        <p class="section-lede">{sv["lede"]}</p>
      </div>
      <div class="section-head-right">
        <div class="section-visual van-photo">
{picture(ph["file"], ph["alt"], ph["w"], ph["h"])}
        </div>
        <a href="#cta" class="btn btn-secondary section-cta">
          {c["cta_label"]}
          {ARROW}
        </a>
      </div>
    </div>

    <div class="v3-tabs-wrap v3-reveal-up">
      <div class="v3-tabs" role="tablist" data-v3-tabs>
{tabs}
      </div>
    </div>
    <div class="services-grid v3-bento" data-bento>
      <span class="v3-bento-beam v3-beam-h1"></span>
      <span class="v3-bento-beam v3-beam-h1 v3-beam-spark"></span>
{(chr(10) + chr(10)).join(service(i, it) for i, it in enumerate(sv["items"]))}
    </div>
  </div>
</section>''', s)

    rv = c['reviews']
    assert len(rv['themes']) == 3, 'в блоке отзывов три темы'

    def theme(t):
        return f'''      <div class="why-item">
        <div class="why-num">{t["label"]}</div>
        <h3 class="why-title">{t["title"]}</h3>
        <p class="why-desc">{t["desc"]}</p>
        <div class="why-photo">
{picture(t["photo"], t["alt"], t["w"], t["h"])}
        </div>
      </div>'''
    q = rv['quote']
    quote = f'<div class="v3-testi"><div class="v3-testi-stars">★★★★★</div><div class="v3-testi-text">{q["text"]}</div><div class="v3-testi-meta"><div class="v3-testi-ava">{q["initials"]}</div><div><div class="v3-testi-name">{q["name"]}</div><div class="v3-testi-sub">{q["sub"]}</div></div></div></div>'
    rlinks = '\n      '.join(f'<a class="v3-testi" href="{l["href"]}" target="_blank" rel="noopener"><div class="v3-testi-stars">★★★★★</div><div class="v3-testi-text"><strong>{l["title"]}</strong>{l["sub"]}</div><div class="v3-testi-meta"><div><div class="v3-testi-name">{l["cta"]} ↗</div></div></div></a>' for l in rv['links'])
    s = sub_once(r'<section id="why" class="section">.*?</section>', f'''<section id="why" class="section">
  <div class="section-inner">
    <div class="section-head">
      <div>
        <span class="section-eyebrow">{rv["eyebrow"]}</span>
        <h2 class="section-title">{rv["title_html"]}</h2>
        <p class="section-lede">{rv["lede"]}</p>
      </div>
    </div>

    <div class="why-grid">
{chr(10).join(theme(t) for t in rv["themes"])}
    </div>

    <div class="van-reviews">
      {quote}
      {rlinks}
    </div>

    <div class="why-foot">
      <div class="why-foot-text">
        {rv["foot_html"]}
      </div>
      <a href="#cta" class="btn btn-primary why-foot-cta">
        {c["cta_label"]}
        {ARROW}
      </a>
    </div>
  </div>
</section>''', s)

    pr = c['process']
    assert len(pr['steps']) == 6, 'в блоке «как проходит работа» шесть шагов'
    steps = '\n'.join(f'''      <div class="v3-tl-step">
        <div class="v3-tl-dot"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round">{STEP_ICONS[i]}</svg></div>
        <div class="v3-tl-num">{i + 1:02d}</div><div class="v3-tl-title">{t}</div><div class="v3-tl-sub">{d}</div>
      </div>''' for i, (t, d) in enumerate(pr['steps']))
    s = sub_once(r'<section id="process" class="v3-timeline">.*?</section>', f'''<section id="process" class="v3-timeline">
  <div class="v3-tl-card v3-reveal-up">
  <div class="v3-timeline-head">
    <span class="section-eyebrow">{pr["eyebrow"]}</span>
    <h2>{pr["title_html"]}</h2>
  </div>
  <div class="v3-tl-track v3-reveal-up" data-delay="200">
    <div class="v3-tl-rail" aria-hidden="true"></div>
    <div class="v3-tl-steps">
{steps}
    </div>
  </div>
  </div><!-- /.v3-tl-card -->
</section>''', s)

    fq = c['faq']
    items = '\n'.join(f'''      <details class="faq-item"{' open' if i == 0 else ''}>
        <summary class="faq-summary">
          {it["q"]}
          {FAQ_ICON}
        </summary>
        <div class="faq-body">
          {it["a"]}
        </div>
      </details>''' for i, it in enumerate(fq['items']))
    s = sub_once(r'<section id="faq" class="section section-tone-warm">.*?</section>', f'''<section id="faq" class="section section-tone-warm">
  <div class="section-inner">
    <div class="section-head">
      <div>
        <span class="section-eyebrow">{fq["eyebrow"]}</span>
        <h2 class="section-title">{fq["title_html"]}</h2>
        <p class="section-lede">{fq["lede"]}</p>
      </div>
    </div>

    <div class="faq-list">
{items}
    </div>
  </div>
</section>''', s)

    ct = c['cta']; k = ct['calc']
    opts = '\n'.join(f'        <button type="button" class="v3-calc-opt" data-calc-mat="{o["id"]}" data-min="{o["min"]}" data-max="{o["max"]}" data-label="{o["wa_label"]}">{o["title"]}<small>{o["small"]}</small></button>' for o in k['options'])
    s = sub_once(r'<section id="cta" class="final-cta">.*?</section>', f'''<section id="cta" class="final-cta">
  <div class="v3-aurora" aria-hidden="true"></div>
  <div class="final-cta-card">
    <div class="final-cta-text">
      <span class="final-eyebrow">{ct["eyebrow"]}</span>
      <h2 class="final-title">{ct["title_html"]}</h2>
      <p class="final-lede">{ct["lede"]}</p>

      <div class="final-actions">
        <a href="tel:{tel}" class="btn final-btn final-btn-primary v3-magnetic">Позвонить {tel_txt}</a>
        <a href="{wa}" target="_blank" rel="noopener" class="btn final-btn final-btn-ghost">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor"><path d="{WA_PATH}"/></svg>
          Написать в&nbsp;WhatsApp
        </a>
        <div class="final-meta">
          <div>
            <div class="final-meta-item-label"><span class="v3-map-marker">Адрес</span></div>
            <div class="final-meta-item-value">{ct["address_html"]}</div>
          </div>
          <div>
            <div class="final-meta-item-label">График</div>
            <div class="final-meta-item-value">{ct["hours_html"]}</div>
          </div>
        </div>
      </div>
    </div>

    <!-- Правая колонка: калькулятор-вилка + плашка с графиком -->
    <div class="v3-cta-right">
    <div class="v3-calc-inline" data-calc-inline>
      <div class="v3-calc-inline-head">
        <span class="v3-calc-inline-eyebrow">Калькулятор · 30 секунд</span>
        <h3 class="v3-calc-inline-title">{k["title"]}</h3>
      </div>
      <div class="v3-calc-progress" aria-hidden="true">
        <span class="is-active"></span><span></span><span></span>
      </div>

      <div class="v3-calc-step" data-step="1">
        <h4>Шаг 1 из 3 · Площадь кровли</h4>
        <p>{k["area_hint"]}</p>
        <input type="number" inputmode="numeric" min="10" max="50000" placeholder="{k["area_placeholder"]}" class="v3-calc-input" data-calc-area aria-label="Площадь кровли в квадратных метрах">
        <div class="v3-calc-actions"><button type="button" class="v3-calc-btn v3-calc-btn--next" data-calc-next>Далее →</button></div>
      </div>

      <div class="v3-calc-step" data-step="2" style="display:none">
        <h4>Шаг 2 из 3 · Тип кровли</h4>
        <p>{k["type_hint"]}</p>
{opts}
        <div class="v3-calc-actions"><button type="button" class="v3-calc-btn v3-calc-btn--back" data-calc-back>← Назад</button><button type="button" class="v3-calc-btn v3-calc-btn--next" data-calc-next disabled>Посчитать →</button></div>
      </div>

      <div class="v3-calc-step" data-step="3" style="display:none">
        <div class="v3-calc-result">
          <span class="v3-calc-inline-eyebrow">Ориентировочная стоимость</span>
          <div class="v3-calc-result-price" data-calc-total>— ₽</div>
          <p class="v3-calc-result-note">{k["result_note"]}</p>
        </div>
        <div class="v3-calc-actions">
          <a class="v3-calc-btn v3-calc-btn--submit" data-calc-wa href="{wa}" target="_blank" rel="noopener" style="text-align:center;text-decoration:none;display:block;line-height:1.2;flex:1">Отправить заявку в&nbsp;WhatsApp</a>
        </div>
        <div class="v3-calc-actions"><button type="button" class="v3-calc-btn v3-calc-btn--back" data-calc-back style="flex:1">Изменить</button><a class="v3-calc-btn v3-calc-btn--back" href="tel:{tel}" style="flex:1;text-align:center;text-decoration:none;line-height:1.2">Позвонить</a></div>
        <canvas class="v3-calc-confetti" data-calc-confetti></canvas>
      </div>
    </div>
    <div class="v3-live"><span class="v3-live-dot" aria-hidden="true"></span>{ct["live"]}</div>
    </div><!-- /.v3-cta-right -->
  </div>
</section>''', s)

    p2 = f'\n    <a href="tel:+{c["phone2"]}">{c["phone2_text"]}</a>' if c.get('phone2') else ''
    s = sub_once(r'<footer>.*?</footer>', f'''<footer>
  <div class="footer-brand">{c["brand"]}<span>.</span></div>
  <div class="footer-meta">
    <span class="footer-addr">{c["footer_address"]}</span>
    <a href="tel:{tel}">{tel_txt}</a>{p2}
    <a href="{wa}" target="_blank" rel="noopener">WhatsApp</a>
    <span>&copy; {c["year"]} {c["legal"]}</span>
  </div>
</footer>''', s)
    s = sub_once(r"const WA_NUMBER = '\d+';", f"const WA_NUMBER = '{c['phone']}';", s)
    return s


def main():
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    if not args:
        sys.exit(__doc__)
    cfg_path = Path(args[0]).resolve()
    c = json.loads(cfg_path.read_text(encoding='utf-8'))
    html = build(c)
    if '--check' in sys.argv:
        same = html == SKELETON.read_text(encoding='utf-8')
        print('совпадает с образцом' if same else 'ОТЛИЧАЕТСЯ от образца')
        sys.exit(0 if same else 1)
    out = ROOT / 'sites' / c['slug']
    out.mkdir(parents=True, exist_ok=True)
    (out / 'index.html').write_text(html, encoding='utf-8')
    (out / '.nojekyll').write_text('')
    for d in ('frames', 'frames-sm', 'assets/fonts', 'assets/' + c['slug']):
        src = ROOT / d
        if not src.exists():
            print('нет папки', d, '— положи туда фото компании'); continue
        shutil.copytree(src, out / d, dirs_exist_ok=True, ignore=shutil.ignore_patterns('src', '.DS_Store'))
    left = sorted(set(re.findall(r'assets/[\w/.-]+\.(?:jpg|webp)', html)))
    missing = [p for p in left if not (out / p).exists()]
    print('готово:', out / 'index.html')
    if missing:
        print('не найдены файлы фото:', ', '.join(missing))


if __name__ == '__main__':
    main()
