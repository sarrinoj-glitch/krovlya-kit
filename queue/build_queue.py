#!/usr/bin/env python3
"""Вшивает списки лидов в страницу-очередь (index.html).

    python3 build_queue.py ../leads/roofing_krasnodar_150.csv ../leads/roofing_cities_500.csv

Первый файл становится «Пачкой 1», второй — «Пачкой 2». Формат CSV — как у скриптов из leads/.
В очередь попадают только лиды с мобильным номером: на городской в WhatsApp не написать."""
import csv, json, re, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PAGE = HERE / 'index.html'
LOC = json.loads((HERE / 'locative.json').read_text(encoding='utf-8'))   # «Краснодар» → «в Краснодаре»
# пригороды первой пачки: по ним работает фильтр «Только Краснодар и пригороды»
LOCAL = {'Краснодар', 'аул Козет', 'пгт Яблоновский', 'пос. Березовый', 'пос. Индустриальный', 'пос. Пригородный', 'пос. Южный',
         'ст-ца Динская', 'ст-ца Елизаветинская', 'ст-ца Новотитаровская'}


def digits(v):
    return re.sub(r'\D', '', v or '')


def leads(path, batch, seen):
    out = []
    for r in csv.DictReader(open(path, encoding='utf-8-sig')):
        p = digits(r.get('WhatsApp')) or digits(r.get('Мобильный'))
        if not (len(p) == 11 and p.startswith('79')) or p in seen:
            continue
        seen.add(p)
        reg = r.get('Регион') or 'Краснодарский край'
        city = r.get('Город', '') or reg          # в карточке нет города — подставляем регион
        k = int(r['Отзывов']) if (r.get('Отзывов') or '').isdigit() else 0
        rating = r.get('Рейтинг', '') or ''
        out.append({'b': batch, 'n': r['Название'], 'city': city, 'reg': reg,
                    'w': LOC.get(city) or ('в городе ' + city if city else 'в вашем городе'), 'p': p,
                    'c': bool(digits(r.get('WhatsApp'))), 's': r.get('Сайт', '') or '', 'r': rating, 'k': k,
                    'g': bool(rating) and float(rating) >= 4.5 and k >= 3, 't': r.get('Тип') == 'торговля?',
                    'l': batch == 1 and city in LOCAL})
    return out


def main():
    files = [a for a in sys.argv[1:] if not a.startswith('--')]
    if not 1 <= len(files) <= 2:
        sys.exit(__doc__)
    seen, all_leads = set(), []
    for i, f in enumerate(files):
        all_leads += leads(f, i + 1, seen)
    html = PAGE.read_text(encoding='utf-8')
    new, n = re.subn(r'const LEADS = \[.*?\];\n', lambda m: 'const LEADS = ' + json.dumps(all_leads, ensure_ascii=False, separators=(',', ':')) + ';\n', html, count=1, flags=re.S)
    assert n == 1, 'в index.html не найдена строка const LEADS'
    if '--check' in sys.argv:
        print('совпадает' if new == html else 'отличается'); return
    PAGE.write_text(new, encoding='utf-8')
    print('в очереди', len(all_leads), 'лидов:', ', '.join(f'пачка {b} — {sum(1 for l in all_leads if l["b"] == b)}' for b in (1, 2)))


if __name__ == '__main__':
    main()
