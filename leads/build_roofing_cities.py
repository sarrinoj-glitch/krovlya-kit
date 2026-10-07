import csv
import json
import re
import sys
from datetime import datetime
import os

HERE = os.path.dirname(os.path.abspath(__file__))   # сырые выгрузки парсера кладутся в leads/raw/

SRCS = [HERE + "/raw/roofing_cities_raw.json"]
# numbers already collected earlier: Krasnodar list and the Moscow call list
KNOWN_FILES = [HERE + "/roofing_krasnodar_150.csv"]
# Krasnodar itself plus settlements of its agglomeration
AGGLO = ("Краснодар", "Яблоновский", "Динская", "Новая Адыгея", "Энем", "Козет", "Тахтамукай",
         "Елизаветинская", "Северный", "Южный", "Знаменский", "Новотитаровская", "Афипский", "Старая Адыгея")
ROOF = re.compile(r"кров|крыш", re.I)
TRADE = re.compile(r"магазин|торгов|гипермаркет|база|материал|завод|производств|склад|оптов", re.I)
SKIP_REGIONS = ("Москва", "Московская область")  # Sochi is new: the Krasnodar list is deduped by phone
MAX_BRANCHES = 5
DST = HERE + "/roofing_cities_500.csv"
LIMIT = 500

SOCIAL = ("vk.com", "ok.ru", "t.me", "instagram.com", "wa.me", "youtube.com", "2gis.", "avito.ru", "taplink", "dzen.ru")


def digits(s):
    d = re.sub(r"\D", "", s or "")
    if len(d) == 11 and d[0] == "8":
        d = "7" + d[1:]
    return d


def is_mobile(d):
    return len(d) == 11 and d.startswith("79")


def contacts(rec, kind):
    out = []
    for g in rec.get("contact_groups") or []:
        for c in g.get("contacts") or []:
            if c.get("type") == kind:
                out.append(c)
    return out


def wa_number(c):
    for key in ("value", "url", "text"):
        m = re.search(r"(?:wa\.me/|phone=)\+?(\d{11})", c.get(key) or "")
        if m:
            return digits(m.group(1))
    return digits(c.get("value") or c.get("text"))


def site_of(rec):
    for c in contacts(rec, "website"):
        url = (c.get("text") or c.get("value") or c.get("url") or "").strip()
        if url and not any(s in url.lower() for s in SOCIAL):
            return url
    return ""


def address(rec):
    a = rec.get("address") or {}
    parts = []
    for comp in a.get("components") or []:
        street, num = comp.get("street"), comp.get("number")
        if street:
            parts.append(f"{street}, {num}" if num else street)
    return "; ".join(parts) or rec.get("address_name") or ""


def age(rec):
    created = (rec.get("dates") or {}).get("created_at")
    if not created:
        return ""
    try:
        y = datetime.fromisoformat(created.replace("Z", "+00:00")).year
        return datetime.now().year - y
    except ValueError:
        return ""


def city_of(rec):
    for a in rec.get("adm_div") or []:
        if a.get("type") in ("city", "settlement"):
            return (a.get("name") or "").replace("\xa0", " ")
    return ""


def region_of(rec):
    return next((a.get("name") for a in rec.get("adm_div") or [] if a.get("type") == "region"), "")


def relevant(rec):
    if any(r.get("name") == "Кровельные работы" for r in rec.get("rubrics") or []):
        return True
    return bool(ROOF.search(rec.get("name") or ""))


data, ids = [], set()
for src in SRCS:
    try:
        with open(src, encoding="utf-8-sig") as f:
            for rec in json.load(f):
                rid = (rec.get("id") or "").split("_")[0]
                if rid not in ids:
                    ids.add(rid)
                    data.append(rec)
    except FileNotFoundError:
        print("нет файла", src)
skipped = {"не кровля": 0, "сеть": 0, "уже собранный регион": 0, "номер уже был": 0, "нет мобильного": 0}
known = set()
for kf in KNOWN_FILES:
    try:
        with open(kf, encoding="utf-8-sig") as f:
            for row in csv.DictReader(f):
                for col in ("WhatsApp", "Мобильный", "Телефон", "Все телефоны"):
                    for part in re.split(r"\s*/\s*", row.get(col) or ""):
                        d = digits(part)
                        if len(d) == 11:
                            known.add(d)
    except FileNotFoundError:
        print("нет файла", kf)

rows, seen = [], set()
for rec in data:
    if not relevant(rec):
        skipped["не кровля"] += 1
        continue
    if region_of(rec) in SKIP_REGIONS:
        skipped["уже собранный регион"] += 1
        continue
    if ((rec.get("org") or {}).get("branch_count") or 1) > MAX_BRANCHES:
        skipped["сеть"] += 1
        continue
    name_ex = rec.get("name_ex") or {}
    name = name_ex.get("primary") or rec.get("name") or ""
    phones = [(c.get("text") or c.get("value") or "").strip() for c in contacts(rec, "phone")]
    phone_digits = [digits(p) for p in phones]
    wa = next((n for n in (wa_number(c) for c in contacts(rec, "whatsapp")) if len(n) == 11), "")
    mobile = next((d for d in phone_digits if is_mobile(d)), "")
    key = wa or mobile
    if not key:
        skipped["нет мобильного"] += 1
        continue
    if key in known or any(d in known for d in phone_digits):
        skipped["номер уже был"] += 1
        continue
    if key in seen:
        continue
    seen.add(key)
    tg = next(((c.get("value") or c.get("url") or c.get("text") or "") for c in contacts(rec, "telegram")), "")
    site = site_of(rec)
    reviews = rec.get("reviews") or {}
    count = reviews.get("general_review_count") or 0
    rating = reviews.get("general_rating") or ""
    prio = "A" if not site else ("B" if count < 30 else "C")
    target = wa or mobile
    rows.append({
        "Приоритет": prio,
        "Сайт?": "🟢 нет" if not site else "есть",
        "Регион": region_of(rec),
        "Город": city_of(rec),
        "Тип": "торговля?" if TRADE.search(rec.get("name") or "") else "подрядчик",
        "Название": name,
        "Юр. лицо": name_ex.get("legal_name") or "",
        "WhatsApp": f"+{wa}" if wa else "",
        "Мобильный": f"+{mobile}" if mobile else "",
        "Ссылка wa.me": f"https://wa.me/{target}" if target else "",
        "Все телефоны": " / ".join(p for p in phones if p),
        "Сайт": site,
        "Telegram": tg,
        "Адрес": address(rec),
        "Рейтинг": rating,
        "Отзывов": count,
        "Возраст(лет)": age(rec),
        "Рубрики": ", ".join(r.get("name", "") for r in rec.get("rubrics") or []),
        "_wa": bool(wa), "_mob": bool(mobile),
        "_local": True,
        "_trade": bool(TRADE.search(rec.get("name") or "")),
    })

# Krasnodar agglomeration first, then the rest of the region; inside: reachable in WhatsApp, no-site first
def order(r):
    return (r["_trade"], r["Приоритет"], not r["_wa"], -r["Отзывов"])


rows.sort(key=order)
final = rows[:LIMIT]
final.sort(key=lambda r: (r["_trade"], r["Приоритет"], not r["_wa"], r["Регион"], -r["Отзывов"]))

cols = [c for c in final[0] if not c.startswith("_")]
with open(DST, "w", encoding="utf-8-sig", newline="") as f:
    w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
    w.writeheader()
    w.writerows(final)


def stat(rs, label):
    print(f"{label}: всего {len(rs)} | "
          f"WhatsApp указан {sum(r['_wa'] for r in rs)} | "
          f"только мобильный {sum((not r['_wa']) and r['_mob'] for r in rs)} | "
          f"только городской {sum(not (r['_wa'] or r['_mob']) for r in rs)} | "
          f"торговля? {sum(r['_trade'] for r in rs)} | A {sum(r['Приоритет']=='A' for r in rs)} B {sum(r['Приоритет']=='B' for r in rs)} C {sum(r['Приоритет']=='C' for r in rs)}")


print(f"сырых уникальных записей: {len(data)} | отсеяно: {skipped}")
stat(rows, "после дедупа")
stat(final, "в файле")
import collections
print(collections.Counter(r["Регион"] for r in final).most_common())
print(collections.Counter(r["Город"] for r in final).most_common(12))
print(DST)
