#!/usr/bin/env python3
"""CRM кровельщиков для Google Таблиц: один файл .xlsx, который открывается в Google Sheets.
Листы: Сводка, Канбан, Лиды (рабочий), по листу на менеджера, Справка."""
import re, json, datetime
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.formatting.rule import FormulaRule
from openpyxl.utils import get_column_letter as L

from pathlib import Path
HERE = Path(__file__).resolve().parent
SRC = HERE.parent / 'queue' / 'index.html'      # лиды берутся из страницы-очереди
OUT = HERE / 'CRM кровельщики.xlsx'
LEADS = json.loads(re.search(r'const LEADS = (\[.*?\]);\n', open(SRC, encoding='utf-8').read(), re.S).group(1))

MANAGERS = ['Ильяс', 'Зураб', 'Тимурлан']
# этап: (фон, цвет текста, что значит)
STAGES = [
    ('Очередь',     'F1F3F4', '5F6368', 'Ещё не писали'),
    ('Отправлено',  'E2ECF6', '2C5A84', 'Написали первое сообщение, ждём ответа'),
    ('Не ответил',  'E3E6E8', '3C4043', 'Молчит. Лид остаётся в таблице: можно напомнить позже'),
    ('Ответил',     'E1EFE9', '0F5A45', 'Ответил, идёт переписка'),
    ('Доработать',  'FBEFD8', '8A5200', 'Интерес есть, надо дожать: показать сайт, снять возражение'),
    ('Перезвонить', 'FFE3C2', '8A4B00', 'Просил связаться позже. Обязательно поставь дату'),
    ('Созвон',      'CDEBDD', '0B4534', 'Созвон назначен. Обязательно поставь дату и время'),
    ('Клиент',      '0F5A45', 'FFFFFF', 'Договорились, работаем'),
    ('Отказ',       'F8E4E2', 'A3312B', 'Отказался'),
    ('Не писать',   'EDEDED', '8A8A8A', 'Попросил не писать или номер не тот'),
]
SN = [s[0] for s in STAGES]
BOARD = SN[1:9]            # колонки канбана
ACTIVE = ['Ответил', 'Доработать', 'Перезвонить', 'Созвон']
MAXR = 2000                # формулы смотрят до этой строки: новые лиды можно дописывать вниз
INK, MUTED, LINE, HEAD = '16211D', '5A6A63', 'D7DFDA', '16211D'

OPEN_GOOD = ['Искал в 2ГИС кровельные компании {w} и наткнулся на вас: отзывы хорошие, а сайта нет.',
             'Смотрел в 2ГИС, кто делает кровлю {w}. У «{n}» хорошие отзывы, но сайта в карточке я не нашёл.',
             'Нашёл вас в 2ГИС среди кровельных компаний {w}: оценки высокие, а сайта нет.']
OPEN_PLAIN = ['Искал в 2ГИС кровельные компании {w} и наткнулся на вас. Сайта в карточке не увидел.',
              'Смотрел в 2ГИС, кто делает кровлю {w}, и нашёл «{n}». Сайта в карточке нет.',
              'Нашёл вас в 2ГИС среди кровельных компаний {w}, а сайта в карточке не нашёл.']
OFFER_LATER = ['Могу за вечер собрать для «{n}» сайт и показать. Платить не нужно, пока не понравится. Собрать?',
               'Готов за вечер собрать сайт для «{n}» и показать вам. Денег вперёд не беру. Собрать?',
               'Могу собрать сайт под «{n}» за вечер и показать. Не понравится — ничего не должны. Сделать?']
SITE_OPEN = 'Смотрел в 2ГИС кровельные компании {w}, зашёл на ваш сайт с телефона: [ЧТО НЕ ТАК НА САЙТЕ].'
SITE_LATER = 'Могу за вечер собрать вариант под «{n}», где это исправлено, и показать. Собрать?'


def message(lead, i):
    f = lambda t: t.replace('{n}', lead['n']).replace('{w}', lead['w'])
    if lead['s']:
        return 'Здравствуйте! ' + f(SITE_OPEN) + '\n\n' + f(SITE_LATER)
    v = i % 3
    return 'Здравствуйте! ' + f((OPEN_GOOD if lead['g'] else OPEN_PLAIN)[v]) + '\n\n' + f(OFFER_LATER[v])


def fill(hex_): return PatternFill('solid', start_color=hex_, end_color=hex_)
def font(size=10, bold=False, color=INK, italic=False): return Font(name='Arial', size=size, bold=bold, color=color, italic=italic)
thin = Side(style='thin', color=LINE)
BOX = Border(left=thin, right=thin, top=thin, bottom=thin)
CENTER = Alignment(horizontal='center', vertical='center', wrap_text=True)
LEFT = Alignment(horizontal='left', vertical='center', wrap_text=True)
TOP = Alignment(horizontal='left', vertical='top', wrap_text=True)


def head(ws, row, labels, col=1, height=30):
    for k, t in enumerate(labels):
        c = ws.cell(row, col + k, t)
        c.font = font(10, True, 'FFFFFF'); c.fill = fill(HEAD); c.alignment = CENTER; c.border = BOX
    ws.row_dimensions[row].height = height


def stage_rules(ws, rng, first):
    """Красит ячейки с названием этапа. first — левая верхняя ячейка диапазона (относительная ссылка)."""
    for name, bg, fg, _ in STAGES:
        ws.conditional_formatting.add(rng, FormulaRule(formula=[f'{first}="{name}"'], fill=fill(bg), font=Font(name='Arial', bold=True, color=fg)))


def due_rules(ws, rng, first):
    ws.conditional_formatting.add(rng, FormulaRule(formula=[f'{first}="просрочено"'], fill=fill('F8E4E2'), font=Font(name='Arial', bold=True, color='A3312B')))
    ws.conditional_formatting.add(rng, FormulaRule(formula=[f'OR({first}="сегодня",{first}="укажи дату",LEFT({first},6)="молчит")'], fill=fill('FBEFD8'), font=Font(name='Arial', bold=True, color='8A5200')))


wb = Workbook()
S = wb.active; S.title = 'Сводка'
T = wb.create_sheet('Сегодня')
K = wb.create_sheet('Канбан')
W = wb.create_sheet('Лиды')
P = {m: wb.create_sheet(m) for m in MANAGERS}
H = wb.create_sheet('Справка')
for ws in wb.worksheets:
    ws.sheet_view.showGridLines = False
W.sheet_view.showGridLines = True

# ═══════════════════ Справка (и списки для выпадающих меню)
H.column_dimensions['A'].width = 22; H.column_dimensions['B'].width = 78
H['A1'] = 'Как пользоваться'; H['A1'].font = font(16, True)
steps = [
    ('1. Вся работа — на листе «Лиды»', 'Одна строка — одна компания. Меняются только жёлтые колонки: Этап, Менеджер, Следующий контакт, Заметка, Написали. Остальное считается само.'),
    ('2. Написать новому', 'В строке лида нажми «Написать»: откроется WhatsApp с готовым текстом. Отправил — поставь Этап «Отправлено», себя в «Менеджер» и дату в «Написали» (Ctrl + ; ставит сегодняшнюю).'),
    ('3. Вести лида', 'Меняй «Этап» по ходу дела. Для «Перезвонить» и «Созвон» ставь дату и время в «Следующий контакт». В «Заметку» пиши, о чём договорились.'),
    ('4. Что делать сегодня', 'Открой лист со своим именем: сверху дела на сегодня, просроченные и те, кто молчит три дня. Ниже — все твои лиды по этапам.'),
    ('5. Общая картина', '«Сводка» — цифры по этапам и менеджерам, «Сегодня» — дела всей команды, «Канбан» — кто на каком этапе. Эти листы и листы менеджеров не редактируются: они собираются из «Лидов».'),
    ('Фильтр только для себя', 'Чтобы твой фильтр на «Лидах» не мешал остальным: Данные → Создать режим фильтрации.'),
    ('Новый лид', 'Допиши строку в конец «Лидов» и протяни вниз формулы из колонок «Срок», «Написать» и «Чат» (и скрытых J, U, V).'),
]
r = 3
for t, d in steps:
    H.cell(r, 1, t).font = font(10, True); H.cell(r, 2, d).font = font(10)
    H.cell(r, 1).alignment = TOP; H.cell(r, 2).alignment = TOP
    H.row_dimensions[r].height = 44
    r += 1
r += 1
H.cell(r, 1, 'Этапы').font = font(13, True); r += 1
STAGE_ROW0 = r
for name, bg, fg, what in STAGES:
    c = H.cell(r, 1, name); c.fill = fill(bg); c.font = font(10, True, fg); c.alignment = CENTER; c.border = BOX
    H.cell(r, 2, what).font = font(10); H.cell(r, 2).alignment = LEFT
    H.row_dimensions[r].height = 22
    r += 1
STAGE_RNG = f"'Справка'!$A${STAGE_ROW0}:$A${STAGE_ROW0 + len(STAGES) - 1}"
r += 1
H.cell(r, 1, 'Менеджеры').font = font(13, True); r += 1
MGR_ROW0 = r
for m in MANAGERS:
    H.cell(r, 1, m).font = font(10, True); H.cell(r, 1).border = BOX; H.cell(r, 1).alignment = CENTER
    r += 1
MGR_RNG = f"'Справка'!$A${MGR_ROW0}:$A${MGR_ROW0 + len(MANAGERS) - 1}"
H.cell(r + 1, 1, 'Не переименовывай этапы в списке выше: на них завязаны подсчёты и цвета.').font = font(9, False, MUTED, True)
H.merge_cells(start_row=r + 1, start_column=1, end_row=r + 1, end_column=2)

# ═══════════════════ Лиды
COLS = [  # (заголовок, ширина)
    ('№', 6), ('Компания', 34), ('Этап', 16), ('Менеджер', 15), ('Следующий контакт', 20), ('Срок', 16), ('Заметка', 48), ('Телефон', 16),
    ('Написали', 15), ('ранг', 5), ('Написать', 16), ('Чат', 16), ('Город', 20), ('Рейтинг', 11), ('Отзывов', 11), ('Сайт', 24), ('Пометки', 30),
    ('Пачка', 9), ('Регион', 24), ('Текст первого сообщения', 70), ('карточка', 10), ('дело', 6),
]
head(W, 1, [c[0] for c in COLS], height=34)
for k, (_, w) in enumerate(COLS):
    W.column_dimensions[L(k + 1)].width = w
EDIT = fill('FFFBE6')     # колонки, которые заполняет человек
seq = {}
ROWS = []
for lead in LEADS:
    i = seq.get(lead['b'], 0); seq[lead['b']] = i + 1
    ROWS.append((lead, i))
for n, (lead, i) in enumerate(ROWS):
    r = n + 2
    notes = [('без сайта' if not lead['s'] else 'есть сайт: сначала впиши в текст, что на нём не так')]
    if not lead['c']: notes.append('WhatsApp не подтверждён')
    if lead['t']: notes.append('похоже на магазин')
    stage, nxt, note, sent = 'Очередь', None, None, None
    if lead['p'] == '79180999091':   # перенесено со скриншота страницы от 06.10.2026
        stage, nxt, note, sent = 'Созвон', datetime.datetime(2026, 10, 6, 17, 0), 'сделал сайт + надо подготовить презу', datetime.date(2026, 10, 6)
    vals = [n + 1, lead['n'], stage, None, nxt,
            f'=IF(OR(C{r}="",C{r}="Очередь",C{r}="Клиент",C{r}="Отказ",C{r}="Не писать"),"",IF(E{r}="",IF(AND(C{r}="Отправлено",I{r}<>"",TODAY()-INT(I{r})>=3),"молчит "&(TODAY()-INT(I{r}))&" дн.",IF(OR(C{r}="Перезвонить",C{r}="Созвон"),"укажи дату","")),IF(INT(E{r})<TODAY(),"просрочено",IF(INT(E{r})=TODAY(),"сегодня",IF(INT(E{r})=TODAY()+1,"завтра",TEXT(E{r},"dd.mm"))))))',
            note, lead['p'], sent,
            f'=IFERROR(MATCH(C{r},{STAGE_RNG},0),99)',
            f'=HYPERLINK("https://wa.me/"&H{r}&"?text="&ENCODEURL(T{r}),"✉ Написать")',
            f'=HYPERLINK("https://wa.me/"&H{r},"Открыть чат")',
            lead['city'] or lead['reg'], float(lead['r']) if lead['k'] and lead['r'] else None, lead['k'] or None, lead['s'] or None, ', '.join(notes),
            lead['b'], lead['reg'], message(lead, i),
            f'=B{r}&IF(D{r}<>""," · "&D{r},"")&IF(F{r}<>"",CHAR(10)&F{r},"")',
            f'=IF(OR(F{r}="просрочено",F{r}="сегодня",F{r}="укажи дату",LEFT(F{r},6)="молчит"),1,0)']
    for k, v in enumerate(vals):
        c = W.cell(r, k + 1, v)
        c.font = font(10); c.alignment = Alignment(vertical='center', wrap_text=(k in (6,)))
    W.cell(r, 2).font = font(10, True)
    for k in (3, 4, 5, 7, 9):
        W.cell(r, k).fill = EDIT
    W.cell(r, 3).alignment = CENTER; W.cell(r, 4).alignment = CENTER; W.cell(r, 6).alignment = CENTER
    W.cell(r, 5).number_format = 'dd.mm.yyyy hh:mm'; W.cell(r, 9).number_format = 'dd.mm.yyyy'
    W.cell(r, 8).number_format = '@'
    for k in (11, 12):
        W.cell(r, k).font = font(10, True, '0F5A45'); W.cell(r, k).alignment = CENTER
    W.cell(r, 20).alignment = Alignment(vertical='center', wrap_text=False)
    W.row_dimensions[r].height = 24
LAST = len(ROWS) + 1
W.freeze_panes = 'C2'
W.auto_filter.ref = f'A1:V{LAST}'
for col in ('J', 'U', 'V'):
    W.column_dimensions[col].hidden = True
dv = DataValidation(type='list', formula1='"' + ','.join(SN) + '"', allow_blank=False, showErrorMessage=True, errorTitle='Этап', error='Выбери этап из списка')
dvm = DataValidation(type='list', formula1='"' + ','.join(MANAGERS) + '"', allow_blank=True, showErrorMessage=True, errorTitle='Менеджер', error='Выбери менеджера из списка')
W.add_data_validation(dv); W.add_data_validation(dvm)
dv.add(f'C2:C{MAXR}'); dvm.add(f'D2:D{MAXR}')
stage_rules(W, f'C2:C{MAXR}', 'C2')
due_rules(W, f'F2:F{MAXR}', 'F2')
for k, m in enumerate(MANAGERS):
    W.conditional_formatting.add(f'D2:D{MAXR}', FormulaRule(formula=[f'D2="{m}"'], font=Font(name='Arial', bold=True, color=['2C5A84', '8A5200', '0F5A45'][k])))
W.conditional_formatting.add(f'A2:B{MAXR}', FormulaRule(formula=['OR($C2="Не писать",$C2="Отказ")'], font=Font(name='Arial', color='9AA0A6', strike=True)))

RC = f"'Лиды'!$C$2:$C${MAXR}"; RD = f"'Лиды'!$D$2:$D${MAXR}"; RF = f"'Лиды'!$F$2:$F${MAXR}"
RV = f"'Лиды'!$V$2:$V${MAXR}"; RU = f"'Лиды'!$U$2:$U${MAXR}"; RB = f"'Лиды'!$B$2:$B${MAXR}"; BLOCK = f"'Лиды'!$B$2:$J${MAXR}"
LIST_HEAD = ['Компания', 'Этап', 'Менеджер', 'Следующий контакт', 'Срок', 'Заметка', 'Телефон', 'Написали', 'ранг', 'Чат']
LIST_W = [34, 16, 15, 20, 16, 48, 16, 15, 5, 16]


def tiles(ws, row, items, cols=None):
    """Плитки: подпись сверху, крупная цифра снизу."""
    for k, (label, formula, color) in enumerate(items):
        k = (cols[k] - 1) if cols else k
        a = ws.cell(row, k + 1, label); a.font = font(9, False, MUTED); a.alignment = CENTER; a.fill = fill('F2F5F3')
        b = ws.cell(row + 1, k + 1, formula); b.font = font(22, True, color); b.alignment = CENTER; b.fill = fill('F2F5F3')
    ws.row_dimensions[row].height = 30; ws.row_dimensions[row + 1].height = 40


def list_block(ws, row, formula, rows):
    """Список лидов, который собирается формулой из «Лидов»; справа ссылка на чат."""
    head(ws, row, LIST_HEAD)
    ws.cell(row + 1, 1, formula)
    for r in range(row + 1, row + 1 + rows):
        ws.cell(r, 10, f'=IF(G{r}="","",HYPERLINK("https://wa.me/"&G{r},"Открыть чат"))').font = font(10, True, '0F5A45')
        ws.cell(r, 10).alignment = CENTER
        for k in range(1, 10):
            ws.cell(r, k).font = font(10, k == 1); ws.cell(r, k).alignment = Alignment(vertical='center', wrap_text=(k == 6), horizontal='center' if k in (2, 3, 5) else None)
        ws.cell(r, 4).number_format = 'dd.mm.yyyy hh:mm'; ws.cell(r, 8).number_format = 'dd.mm.yyyy'; ws.cell(r, 7).number_format = '@'
    stage_rules(ws, f'B{row + 1}:B{row + rows}', f'B{row + 1}')
    due_rules(ws, f'E{row + 1}:E{row + rows}', f'E{row + 1}')


def any_of(rng, names): return '+'.join(f'COUNTIF({rng},"{n}")' for n in names)


# ═══════════════════ Сводка
for k in range(8):
    S.column_dimensions[L(k + 1)].width = 19
S['A1'] = 'Воронка кровельщиков'; S['A1'].font = font(18, True)
S['A2'] = '=\"Положение дел на \"&TEXT(TODAY(),\"dd.mm.yyyy\")&\". Лист собирается сам из «Лидов».\"'; S['A2'].font = font(10, False, MUTED)
tiles(S, 4, [
    ('в очереди', f'=COUNTIF({RC},"Очередь")', MUTED),
    ('написали', f'=COUNTA({RB})-COUNTIF({RC},"Очередь")-COUNTIF({RC},"Не писать")', '2C5A84'),
    ('в работе', '=' + any_of(RC, ACTIVE), '0F5A45'),
    ('дел на сегодня', f'=COUNTIF({RF},"сегодня")+COUNTIF({RF},"укажи дату")', '8A5200'),
    ('просрочено', f'=COUNTIF({RF},"просрочено")', 'A3312B'),
    ('молчат 3+ дня', f'=COUNTIF({RF},"молчит*")', '8A5200'),
    ('созвонов назначено', f'=COUNTIF({RC},"Созвон")', '0F5A45'),
    ('клиентов', f'=COUNTIF({RC},"Клиент")', '0F5A45'),
])
S['A7'] = 'Этапы и менеджеры'; S['A7'].font = font(13, True)
head(S, 8, ['Этап', 'Всего'] + MANAGERS + ['Без менеджера', 'Доля'], height=26)
r0 = 9
for k, name in enumerate(BOARD):
    r = r0 + k
    bg, fg = STAGES[SN.index(name)][1:3]
    c = S.cell(r, 1, name); c.fill = fill(bg); c.font = font(10, True, fg); c.alignment = CENTER; c.border = BOX
    S.cell(r, 2, f'=COUNTIF({RC},"{name}")').font = font(11, True)
    for j, m in enumerate(MANAGERS):
        S.cell(r, 3 + j, f'=COUNTIFS({RC},"{name}",{RD},"{m}")')
    S.cell(r, 6, f'=B{r}-SUM(C{r}:E{r})')
    S.cell(r, 7, f'=REPT("█",IF(MAX($B${r0}:$B${r0 + 7})=0,0,ROUND(B{r}/MAX($B${r0}:$B${r0 + 7})*24,0)))').font = font(10, False, fg if fg != 'FFFFFF' else bg)
    for j in range(2, 7):
        S.cell(r, j).alignment = CENTER; S.cell(r, j).border = BOX
        if j > 2: S.cell(r, j).font = font(10)
    S.cell(r, 7).alignment = Alignment(horizontal='left', vertical='center')
    S.row_dimensions[r].height = 22
rt = r0 + 8
S.cell(rt, 1, 'Всего в воронке').font = font(10, True)
for j in range(2, 7):
    S.cell(rt, j, f'=SUM({L(j)}{r0}:{L(j)}{r0 + 7})').font = font(10, True); S.cell(rt, j).alignment = CENTER
rc = rt + 2
S.cell(rc, 1, 'Конверсия').font = font(13, True)
conv = [('Написали', '=B5', None),
        ('Ответили', '=' + any_of(RC, ACTIVE + ['Клиент', 'Отказ']), None),
        ('Созвон или клиент', '=' + any_of(RC, ['Созвон', 'Клиент']), None),
        ('Клиенты', f'=COUNTIF({RC},"Клиент")', None)]
head(S, rc + 1, ['Шаг', 'Лидов', 'От написанных'], height=24)
for k, (label, f, _) in enumerate(conv):
    r = rc + 2 + k
    S.cell(r, 1, label).font = font(10, True); S.cell(r, 2, f).font = font(11, True); S.cell(r, 2).alignment = CENTER
    c = S.cell(r, 3, f'=IF($B${rc + 2}=0,"—",B{r}/$B${rc + 2})'); c.number_format = '0%'; c.alignment = CENTER; c.font = font(10)
    for j in (1, 2, 3): S.cell(r, j).border = BOX
S.cell(rc + 7, 1, 'Что сделать сейчас — на листе «Сегодня». Кто на каком этапе — на листе «Канбан».').font = font(10, False, MUTED)
S.freeze_panes = 'A4'

# ═══════════════════ Сегодня
for k, w in enumerate(LIST_W):
    T.column_dimensions[L(k + 1)].width = w
T.column_dimensions['I'].hidden = True
T['A1'] = 'Сегодня'; T['A1'].font = font(18, True)
T['A2'] = 'Все дела команды: на сегодня, просроченные, без даты и те, кто молчит три дня. Сверху самые старые. Править — на листе «Лиды».'; T['A2'].font = font(10, False, MUTED)
list_block(T, 4, f'=IFERROR(SORT(FILTER({BLOCK},{RV}=1),4,TRUE),"Дел нет")', 200)
T.freeze_panes = 'A5'

# ═══════════════════ Канбан
K['A1'] = 'Канбан'; K['A1'].font = font(18, True)
K['A2'] = 'Кто на каком этапе. В карточке: компания · менеджер, ниже срок. Этап меняется на листе «Лиды».'; K['A2'].font = font(10, False, MUTED)
for k, name in enumerate(BOARD):
    col = k + 1
    bg, fg = STAGES[SN.index(name)][1:3]
    K.column_dimensions[L(col)].width = 27
    c = K.cell(4, col, f'="{name} · "&COUNTIF({RC},"{name}")'); c.fill = fill(bg); c.font = font(11, True, fg); c.alignment = CENTER; c.border = BOX
    K.cell(5, col, f'=IFERROR(FILTER({RU},{RC}="{name}"),"—")')
    for r in range(5, 305):
        K.cell(r, col).alignment = TOP; K.cell(r, col).font = font(10)
K.row_dimensions[4].height = 30
K.conditional_formatting.add('A5:H304', FormulaRule(formula=['AND(A5<>"",A5<>"—")'], fill=fill('F2F5F3'), border=BOX))
K.conditional_formatting.add('A5:H304', FormulaRule(formula=['ISNUMBER(SEARCH("просрочено",A5))'], font=Font(name='Arial', color='A3312B', bold=True)))
K.freeze_panes = 'A5'

# ═══════════════════ листы менеджеров
for m, ws in P.items():
    for k, w in enumerate(LIST_W):
        ws.column_dimensions[L(k + 1)].width = w
    ws.column_dimensions['I'].hidden = True; ws.column_dimensions['C'].hidden = True
    ws['A1'] = m; ws['A1'].font = font(18, True, ['2C5A84', '8A5200', '0F5A45'][MANAGERS.index(m)])
    ws['A2'] = 'Твои дела и твои лиды. Лист собирается сам: править нужно на листе «Лиды».'; ws['A2'].font = font(10, False, MUTED)
    mine = lambda names: '+'.join(f'COUNTIFS({RC},"{n}",{RD},$A$1)' for n in names)
    tiles(ws, 4, [
        ('в работе', '=' + mine(ACTIVE), '0F5A45'),
        ('ждём ответа', '=' + mine(['Отправлено']), '2C5A84'),
        ('дел на сегодня', f'=COUNTIFS({RF},"сегодня",{RD},$A$1)+COUNTIFS({RF},"укажи дату",{RD},$A$1)', '8A5200'),
        ('просрочено', f'=COUNTIFS({RF},"просрочено",{RD},$A$1)', 'A3312B'),
        ('молчат 3+ дня', f'=COUNTIFS({RF},"молчит*",{RD},$A$1)', '8A5200'),
        ('клиентов', '=' + mine(['Клиент']), '0F5A45'),
    ], cols=[1, 2, 4, 5, 7, 8, 10])
    for r_ in (4, 5):
        ws.cell(r_, 6).fill = fill('F2F5F3')
    ws['A7'] = 'Что сделать сейчас'; ws['A7'].font = font(13, True)
    list_block(ws, 8, f'=IFERROR(ARRAY_CONSTRAIN(SORT(FILTER({BLOCK},({RD}=$A$1)*({RV}=1)),4,TRUE),25,9),"Дел нет")', 25)
    ws['A35'] = 'Все мои лиды по этапам'; ws['A35'].font = font(13, True)
    list_block(ws, 36, f'=IFERROR(SORT(FILTER({BLOCK},({RD}=$A$1)*({RC}<>"Очередь")),9,TRUE),"Пока никого: поставь себя в колонке «Менеджер» на листе «Лиды»")', 300)
    ws.freeze_panes = 'A4'

for ws, color in ((S, '16211D'), (T, 'A3312B'), (K, '16211D'), (W, 'F2B600'), (H, '9AA0A6')):
    ws.sheet_properties.tabColor = color
for m, c in zip(MANAGERS, ['2C5A84', '8A5200', '0F5A45']):
    P[m].sheet_properties.tabColor = c
wb.save(OUT)
print('saved', OUT, 'rows', len(ROWS), 'with site', sum(1 for l, _ in ROWS if l['s']))
