#!/usr/bin/env python3
# Gera os SVGs estáticos do README (estilo NINJA) a partir dos dados do currículo do Kauã.
# Uso: python gerar_assets.py   (edite os dados abaixo e rode de novo para atualizar os assets)
import os, random, math
from ninja_stats import (ptext, window, header, txt, dash, tw, svg, MONO, BG, RED, DRED,
                         NINJA_GRID, NINJA_COLORS)

OUT = os.environ.get("OUT_DIR", "assets")
os.makedirs(OUT, exist_ok=True)
PINK = "#ff5c7a"


def save(name, content):
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write(content)
    print("ok", name)


# ------------------------------------------------------------------ utilitários de pixel-art
def grid(rows, x, y, u, cmap, extra=""):
    """Desenha uma grade de caracteres como retângulos agrupados por cor."""
    byc = {}
    for j, row in enumerate(rows):
        i = 0
        while i < len(row):
            ch = row[i]
            if ch not in cmap:
                i += 1
                continue
            k = i
            while k < len(row) and row[k] == ch:
                k += 1
            byc.setdefault(cmap[ch], []).append(f"M{x+i*u:g} {y+j*u:g}h{(k-i)*u:g}v{u:g}h-{(k-i)*u:g}z")
            i = k
    return "".join(f'<path fill="{c}"{extra} d="{"".join(p)}"/>' for c, p in byc.items())


def ninja(x, y, u, cls=""):
    g = grid(NINJA_GRID, 0, 0, u, NINJA_COLORS)
    c = f' class="{cls}"' if cls else ""
    return f'<g{c} transform="translate({x:g},{y:g})">{g}</g>'


ICONS = {
    "shuriken": ([
        ".....#.....", ".....#.....", "....###....", "....###....", "##.#####.##", "####.#.####",
        "##.#####.##", "....###....", "....###....", ".....#.....", ".....#.....",
    ], {"#": "#fff"}),
    "chip": ([
        "..#.#.#.#..", ".#########.", "###.....###", ".#.#####.#.", "###.#.#.###", ".#.#####.#.",
        "###.#.#.###", ".#.#####.#.", "###.....###", ".#########.", "..#.#.#.#..",
    ], {"#": "#fff"}),
    "scroll": ([
        ".#########.", "#.........#", "#.#######.#", "#.........#", "#.#######.#", "#.........#",
        "#.#####...#", "#.........#", ".#########.", "...........", "...........",
    ], {"#": "#fff"}),
    "kunai": ([
        "........##.", ".......###.", "......###..", ".....###...", "....###....", "...###.....",
        ".#.##......", "..##.......", ".####......", "#...#......", "...........",
    ], {"#": "#fff"}),
    "lock": ([
        "...#####...", "..#.....#..", "..#.....#..", "..#.....#..", ".#########.", ".#########.",
        ".####.####.", ".####.####.", ".#########.", ".#########.", "...........",
    ], {"#": "#fff"}),
    "check": ([
        "..........#", ".........##", "........##.", "#......##..", "##....##...", ".##..##....",
        "..####.....", "...##......",
    ], {"#": "#fff"}),
    "pagoda": ([
        "....#.#....", "...#####...", "..#######..", "....###....", "..#######..", ".#########.",
        "....###....", ".#########.", "###########", "...#.#.#...", "...#####...",
    ], {"#": "#fff"}),
    # --- inventário
    "python": (["..."], {"#": "#fff"}),
    "pandas": ([
        "RRRRRRRRRRR", "RRRRRRRRRRR", "###########", "#...#...#.#", "#...#...#.#", "###########",
        "#...#...#.#", "#...#...#.#", "###########", "...........", "...........",
    ], {"#": "#fff", "R": RED}),
    "sql": ([
        "..#######..", ".#########.", ".#.......#.", ".#########.", ".#.......#.", "..#######..",
        ".#.......#.", ".#########.", ".#.......#.", ".#########.", "..#######..",
    ], {"#": "#fff"}),
    "bi": ([
        "...........", "........##.", "........##.", "...##...##.", "...##...##.", "...##...##.",
        ".#.##.#.##.", ".#.##.#.##.", ".#.##.#.##.", ".#.##.#.##.", "###########",
    ], {"#": "#fff"}),
    "excel": ([
        "###########", "#.........#", "#.#.....#.#", "#..#...#..#", "#...#.#...#", "#....#....#",
        "#...#.#...#", "#..#...#..#", "#.#.....#.#", "#.........#", "###########",
    ], {"#": "#fff"}),
    "git": ([
        ".#.......#.", ".#.......#.", ".#.....##..", ".#...##....", ".#.##......", ".##........",
        ".#.........", ".#.........", ".#.........", ".#.........", ".#.........",
    ], {"#": "#fff"}),
    "github": ([
        "#.........#", "##.......##", "###########", "###########", "##.##.##.##", "###########",
        "###########", ".#########.", "..#######..", "...........", "...........",
    ], {"#": "#fff"}),
    "cloud": ([
        "...........", "....###....", "..#######..", ".#########.", "###########", "###########",
        "###########", ".#########.", "....#.#....", "...#...#...", "...........",
    ], {"#": "#fff"}),
    "ml": ([
        "##.......##", "#.#.....#.#", "#..#...#..#", "#...#.#...#", "#....#....#", "#.........#",
        "#.#######.#", "#.#.....#.#", "#.#.....#.#", "#.#######.#", "...........",
    ], {"#": "#fff"}),
}


def icon(name, cx, cy, u, fill=None, dim=False):
    rows, cmap = ICONS[name]
    if fill:
        cmap = {k: fill for k in cmap}
    h = len(rows)
    w = max(len(r) for r in rows)
    return grid(rows, cx - w * u / 2, cy - h * u / 2, u, cmap, ' opacity=".45"' if dim else "")


def paths_text(s, x, y, px, fill="#fff", anchor="start"):
    return ptext(s, x, y, px, fill, anchor)


# ================================================================== BANNER
def banner():
    W, H = 800, 300
    rnd = random.Random(7)
    css = (
        "@keyframes bl{50%{opacity:0}}.blink{animation:bl 1s steps(1) infinite}"
        "@keyframes tw{50%{opacity:.15}}.tw{animation:tw 2.4s steps(2) infinite}"
        "@keyframes pulse{50%{opacity:.55}}.pulse{animation:pulse 3s steps(3) infinite}"
        "@keyframes bob{50%{transform:translateY(-3px)}}.bob{animation:bob 1.6s steps(2) infinite}"
        "@keyframes orbit{to{transform:rotate(360deg)}}.orbit{animation:orbit 3.6s linear infinite}"
        "@keyframes spin{to{transform:rotate(-360deg)}}.spin{animation:spin .9s steps(8) infinite}"
        "@keyframes fall{0%{transform:translate(0,0);opacity:0}10%{opacity:.9}90%{opacity:.9}100%{transform:translate(-90px,290px);opacity:0}}"
        ".fall{animation:fall 7s linear infinite}"
        "@keyframes bf{0%,4%{opacity:0;transform:translateY(8px)}10%,60%{opacity:1;transform:translateY(0)}70%,100%{opacity:0;transform:translateY(-6px)}}"
        ".bf{animation:bf 5s steps(5) infinite}"
        "@keyframes fill{0%{transform:scaleX(.05)}70%,100%{transform:scaleX(1)}}"
        ".fill{transform-origin:0 0;animation:fill 6s steps(24) infinite}"
        "@keyframes slash{0%,86%{opacity:0;transform:scaleX(0)}90%{opacity:1;transform:scaleX(1)}100%{opacity:0;transform:scaleX(1)}}"
        ".slash{transform-origin:0 0;animation:slash 6s linear infinite}"
    )
    b = []
    # moldura
    b.append(f'<rect x="1.5" y="1.5" width="{W-3}" height="{H-3}" fill="{BG}" stroke="#fff" stroke-width="3"/>')
    b.append(f'<rect x="7" y="7" width="{W-14}" height="{H-14}" fill="none" stroke="{DRED}" stroke-width="1.5"/>')
    # estrelas
    for i in range(34):
        x, y = rnd.randrange(16, W - 16), rnd.randrange(16, 200)
        if 330 < x < 630 and y > 30:
            continue
        s = rnd.choice([2, 2, 3])
        b.append(f'<rect class="tw" style="animation-delay:-{rnd.random()*2.4:.1f}s" x="{x}" y="{y}" width="{s}" height="{s}" fill="#fff" opacity=".8"/>')
    # pétalas de sakura caindo
    for i in range(9):
        x = rnd.randrange(250, 790)
        d = rnd.random() * 7
        b.append(f'<g transform="translate({x},12)"><rect class="fall" style="animation-delay:-{d:.1f}s;animation-duration:{6+rnd.random()*4:.1f}s" width="4" height="4" fill="{PINK}"/></g>')
    CX = 480
    # lua + halo
    cy, r = 100, 46
    b.append(f'<g class="pulse">' + "".join(
        f'<rect x="{CX-math.sqrt(max(0,(r+14)**2-dy*dy)):.0f}" y="{cy+dy-2}" width="{2*math.sqrt(max(0,(r+14)**2-dy*dy)):.0f}" height="4" fill="#3a0c18"/>'
        for dy in range(-(r + 14), r + 15, 4)) + '</g>')
    for dy in range(-r, r + 1, 4):
        hw = math.sqrt(max(0, r * r - dy * dy))
        b.append(f'<rect x="{CX-hw:.0f}" y="{cy+dy-2}" width="{2*hw:.0f}" height="4" fill="#ece6e8"/>')
    for (dx, dy, w, h) in [(-22, -18, 12, 8), (14, -26, 8, 6), (6, 8, 16, 10), (-30, 14, 8, 6), (24, 24, 8, 6)]:
        b.append(f'<rect x="{CX+dx}" y="{cy+dy}" width="{w}" height="{h}" fill="#d3c9cd"/>')
    # torii
    T = "#c4122f"; TD = "#7d0c1f"
    b.append(f'<rect x="{CX-66}" y="86" width="132" height="8" fill="{T}"/>')
    b.append(f'<rect x="{CX-72}" y="80" width="12" height="6" fill="{T}"/><rect x="{CX+60}" y="80" width="12" height="6" fill="{T}"/>')
    b.append(f'<rect x="{CX-58}" y="94" width="116" height="5" fill="{TD}"/>')
    b.append(f'<rect x="{CX-50}" y="108" width="100" height="7" fill="{T}"/>')
    b.append(f'<rect x="{CX-40}" y="99" width="10" height="44" fill="{T}"/><rect x="{CX+30}" y="99" width="10" height="44" fill="{T}"/>')
    b.append(f'<rect x="{CX-44}" y="141" width="18" height="6" fill="{TD}"/><rect x="{CX+26}" y="141" width="18" height="6" fill="{TD}"/>')
    b.append(f'<rect x="{CX-6}" y="99" width="12" height="9" fill="{TD}"/>')
    # título
    b.append(ptext("PLAYER 1 · RANK GENIN", CX, 20, 2, "#8a8a99", "middle"))
    title = "KAUÃ KENZO MATSUO"
    b.append(ptext(title, CX + 3, 169, 3, "#5c1020", "middle"))
    b.append(ptext(title, CX, 166, 3, "#fff", "middle"))
    b.append(f'<g transform="translate({CX-152},178) rotate(-6)"><rect class="slash" width="304" height="3" fill="#fff"/></g>')
    b.append(ptext("ENGENHARIA DA COMPUTAÇÃO", CX, 200, 2, "#cfcfd8", "middle"))
    b.append(ptext("PYTHON · IA · AUTOMAÇÃO", CX, 224, 2, PINK, "middle"))
    # barra de chakra
    bx, bw = 330, 300
    b.append(txt(290, 253, "CHAKRA", "#aaa", 13, "end").replace('text-anchor="end"', 'text-anchor="end"'))
    b.append(f'<rect x="{bx-1}" y="241" width="{bw+2}" height="14" fill="{BG}" stroke="#555" stroke-width="1.5"/>')
    b.append(f'<g transform="translate({bx},243)"><rect class="fill" width="{bw}" height="10" fill="{RED}"/></g>')
    b.append(txt(bx + bw + 14, 253, "PYTHON + IA", "#aaa", 13, "start"))
    b.append(f'<g class="blink">{ptext("PRESSIONE START", CX, 272, 2, "#fff", "middle")}</g>')
    # ninja
    b.append(f'<rect x="28" y="248" width="200" height="6" fill="#2a1018"/><rect x="28" y="248" width="200" height="2" fill="{DRED}"/>')
    b.append(f'<g class="bf">{txt(128, 138, "BUFF! PYTHON +10", PINK, 13, "middle")}</g>')
    b.append('<g transform="translate(128,206)">'
             f'<g class="orbit"><g transform="translate(62,0)"><g class="spin">{icon("shuriken", 0, 0, 2, PINK)}</g></g></g>'
             f'<g class="orbit" style="animation-delay:-1.8s;animation-duration:5s"><g transform="translate(-72,0)"><g class="spin">{icon("shuriken", 0, 0, 1.5, "#aaa")}</g></g></g></g>')
    b.append(f'<g class="bob">{ninja(128-30, 158, 5)}</g>')
    return svg(W, H, "".join(b), css).replace("<svg ", '<svg role="img" ', 1).replace(
        "<style>", "<title>Banner ninja: Kauã Kenzo Matsuo, estudante de Engenharia da Computação focado em Python e IA</title><style>", 1)


# ================================================================== SOBRE MIM
def sobre():
    lines = [
        "Oi! Eu sou o Kauã, moro em Suzano (SP) e estudo Engenharia da Computação",
        "na UNICID. Sou estagiário de TI na Mais Capital, onde dou suporte N1/N2 e",
        'uso <tspan fill="#ff5c7a">Python</tspan> para automatizar rotinas. Criei o AUTOMATSUO, um RPA para ERP',
        "industrial (Baan / Infor LN) que reduziu cerca de 40% do tempo operacional.",
        'Hoje meu foco é <tspan fill="#ff5c7a">Python</tspan>, <tspan fill="#ff5c7a">dados</tspan> e <tspan fill="#ff5c7a">inteligência artificial</tspan>.',
    ]
    H = 30 + 56 + len(lines) * 24 + 34
    b = header("SOBRE MIM") + window(0, 30, 800, H - 30)
    b += ptext("KAUÃ:", 28, 52, 2, PINK)
    for i, l in enumerate(lines):
        b += txt(28, 98 + i * 24, l, "#ddd", 15)
    ay = H - 34
    b += f'<g class="blink"><path fill="{RED}" d="M762 {ay}h14v3h-3v3h-3v3h-2v-3h-3v-3h-3zM768 {ay+9}h2v2h-2z"/></g>'
    return svg(800, H, b, "@keyframes bl{50%{opacity:0}}.blink{animation:bl 1s steps(1) infinite}").replace(
        "<style>", "<title>Sobre mim</title><style>", 1)


# ================================================================== FICHA
def ficha():
    H = 250
    b = header("FICHA DO NINJA") + window(0, 30, 800, H - 30)
    cols = [28, 375]
    rows = [
        (("CLASSE", "Ninja de Automação · Python e IA"), ("ESPECIALIDADE", "RPA · Dados · Machine Learning")),
        (("CLÃ", "Engenharia da Computação · UNICID"), ("MISSÃO PRINCIPAL", "Dados, IA e Sistemas")),
    ]
    for r, pair in enumerate(rows):
        y = 64 + r * 62
        for c, (lab, val) in enumerate(pair):
            b += ptext(lab, cols[c], y, 2, "#7a7a88") + txt(cols[c], y + 36, val, "#fff", 15)
    b += ptext("RANK GENIN · ESTAGIÁRIO DE TI", 28, 190, 2, "#fff")
    b += ptext("FORMATURA 2030", 772, 190, 2, "#7a7a88", "end")
    b += f'<rect x="28" y="212" width="744" height="14" fill="#1a1a22" stroke="#33333d" stroke-width="1.5"/>'
    b += f'<rect x="28" y="212" width="260" height="14" fill="{RED}"/><rect x="28" y="212" width="260" height="4" fill="{PINK}"/>'
    return svg(800, H, b).replace("<style>", "<title>Ficha do ninja</title><style>", 1)


# ================================================================== MAPA
def mapa():
    H = 232
    css = ("@keyframes bob{50%{transform:translateY(-4px)}}.bob{animation:bob 1.2s steps(2) infinite}"
           "@keyframes bl{50%{opacity:0}}.blink{animation:bl 1s steps(1) infinite}")
    b = header("CAMINHO DO NINJA")
    xs = [80, 240, 400, 560, 720]
    cy = 120
    # linhas
    for i in range(4):
        x1, x2 = xs[i] + 34, xs[i + 1] - 34
        done = i < 2
        col = "#666" if done else "#2f2f3a"
        b += f'<line x1="{x1}" y1="{cy}" x2="{x2}" y2="{cy}" stroke="{col}" stroke-width="5" stroke-dasharray="12 8"/>'
    labels = [("GUARDA", "MIRIM"), ("JOVEM APRENDIZ", "KOMATSU"), ("MAIS CAPITAL", "ESTÁGIO DE TI"), ("ANALISTA", "DE DADOS"), ("CHEFÃO:", "ENGENHEIRO DE IA")]
    for i, x in enumerate(xs):
        if i < 2:   # concluído
            b += f'<rect x="{x-22}" y="{cy-22}" width="44" height="44" fill="#fff"/>'
            b += grid(ICONS["check"][0], x - 11 * 2.2 / 2 - 0, cy - 8 * 2.2 / 2 + 1, 2.2, {"#": BG})
            col = "#fff"
        elif i == 2:
            b += f'<rect x="{x-29}" y="{cy-29}" width="58" height="58" fill="{BG}" stroke="{RED}" stroke-width="4"/>'
            b += f'<rect x="{x-35}" y="{cy-35}" width="70" height="70" fill="none" stroke="{DRED}" stroke-width="2" class="blink"/>'
            b += ptext("3", x, cy - 10, 4, "#fff", "middle")
            col = "#fff"
        else:
            b += f'<rect x="{x-22}" y="{cy-22}" width="44" height="44" fill="none" stroke="#4a4a58" stroke-width="3" stroke-dasharray="6 5"/>'
            b += icon("lock" if i == 3 else "pagoda", x, cy, 2.6, "#4a4a58")
            col = "#5d5d6c"
        b += txt(x, 188, labels[i][0], col, 14, "middle") + txt(x, 208, labels[i][1], col, 14, "middle")
    b += f'<g class="bob">{ninja(xs[2]-16, 24, 3.4)}</g>'
    return svg(800, H, b, css).replace("<style>", "<title>Caminho do ninja</title><style>", 1)


# ================================================================== ATRIBUTOS
def atributos():
    attrs = [  # (nome, nível 0-5, destaque)
        ("PYTHON", 4, True),
        ("IA E MACHINE LEARNING", 3, True),
        ("AUTOMAÇÃO / RPA", 4, False),
        ("DADOS E ETL (PANDAS)", 4, False),
        ("SQL (MYSQL)", 3, False),
        ("POWER BI E EXCEL", 3, False),
        ("SUPORTE TÉCNICO N1/N2", 3, False),
        ("GIT E GITHUB", 3, False),
    ]
    rowh = 34
    H = 30 + 24 + len(attrs) * rowh + 40
    b = header("ATRIBUTOS") + window(0, 30, 800, H - 30)
    x0, seg, gap = 330, 84, 6
    for i, (name, lv, hi) in enumerate(attrs):
        y = 62 + i * rowh
        b += txt(28, y + 14, name, PINK if hi else "#fff", 16)
        for s in range(5):
            on = s < lv
            col = (RED if hi else "#fff") if on else "#1d1d26"
            b += f'<rect x="{x0 + s*(seg+gap)}" y="{y}" width="{seg}" height="16" fill="{col}"/>'
            if on:
                b += f'<rect x="{x0 + s*(seg+gap)}" y="{y}" width="{seg}" height="4" fill="{PINK if hi else "#ddd"}" opacity=".55"/>'
        if hi:
            b += icon("shuriken", 300, y + 8, 1.4, PINK)
    b += f'<rect x="28" y="{H-34}" width="10" height="10" fill="{RED}"/>'
    b += txt(46, H - 25, "afinidade principal  ·  nível de 0 a 5", "#7a7a88", 13)
    return svg(800, H, b).replace("<style>", "<title>Atributos: Python, IA e Machine Learning, Automação RPA, Dados, SQL, Power BI, Suporte, Git</title><style>", 1)


# ================================================================== CONQUISTAS
def conquistas():
    cards = [
        ("shuriken", ("Automatsuo", "-40% de tempo"), False),
        ("chip", ("Azure AI", "AI-900"), False),
        ("scroll", ("Rastreio", "RECOF"), False),
        ("kunai", ("Guarda Mirim", "400 horas"), False),
        ("lock", ("ML Aplicada", "à Indústria"), True),
    ]
    W, gap = 150, 12.5
    H = 170
    b = header("CONQUISTAS")
    for i, (ic, (l1, l2), locked) in enumerate(cards):
        x = i * (W + gap)
        if locked:
            b += f'<rect x="{x+1.5:g}" y="31.5" width="{W-3}" height="136" fill="{BG}" stroke="#4a4a58" stroke-width="3" stroke-dasharray="7 5"/>'
            col = "#5d5d6c"
        else:
            b += f'<rect x="{x+1.5:g}" y="31.5" width="{W-3}" height="136" fill="{BG}" stroke="#fff" stroke-width="3"/>'
            b += f'<rect x="{x+1.5+3:g}" y="31.5" width="{W-9}" height="4" fill="{RED}"/>'
            col = "#fff"
        b += icon(ic, x + W / 2, 78, 4, "#4a4a58" if locked else (PINK if i == 0 else "#fff"))
        b += txt(x + W / 2, 124, l1, "#5d5d6c" if locked else "#fff", 14, "middle") + txt(x + W / 2, 144, l2, "#5d5d6c" if locked else "#aaa", 14, "middle")
    return svg(800, H, b).replace("<style>", "<title>Conquistas: Automatsuo, AI-900, RECOF, Guarda Mirim; bloqueada: ML Aplicada à Indústria</title><style>", 1)


# ================================================================== INVENTÁRIO
def inventario():
    items = [("python", "Python"), ("pandas", "Pandas"), ("sql", "SQL"), ("bi", "Power BI"), ("excel", "Excel"),
             ("git", "Git"), ("github", "GitHub"), ("cloud", "Azure AI"), ("ml", "ML")]
    H = 176
    b = header("INVENTÁRIO") + window(0, 30, 800, H - 30)
    n, w, gap = len(items), 76, 10
    x0 = (800 - (n * w + (n - 1) * gap)) / 2
    for i, (ic, label) in enumerate(items):
        x = x0 + i * (w + gap)
        locked = i == n - 1
        if locked:
            b += f'<rect x="{x:g}" y="48" width="{w}" height="{w}" fill="#0c0c12" stroke="#2f2f3a" stroke-width="2.5"/>'
            b += ptext("?", x + w / 2, 68, 4, "#3d3d4a", "middle")
            b += txt(x + w / 2, 148, label, "#3d3d4a", 13, "middle")
        else:
            hi = i == 0
            b += f'<rect x="{x:g}" y="48" width="{w}" height="{w}" fill="#0c0c12" stroke="{RED if hi else "#fff"}" stroke-width="2.5"/>'
            if ic == "python":
                b += ptext("PY", x + w / 2, 70, 4, PINK, "middle")
            else:
                b += icon(ic, x + w / 2, 86, 3.4, None)
            b += txt(x + w / 2, 148, label, PINK if hi else "#aaa", 13, "middle")
    return svg(800, H, b).replace("<style>", "<title>Inventário: Python, Pandas, SQL, Power BI, Excel, Git, GitHub, Azure AI; ML em breve</title><style>", 1)


# ================================================================== MISSÕES
def missoes():
    quests = [
        ("!", "AUTOMATSUO — RPA em Python para ERP industrial", "AUTORAL", "act"),
        ("!", "Mais Capital — suporte N1/N2 e automação de rotinas", "ESTÁGIO", "act"),
        ("!", "Machine Learning Aplicada à Indústria — SENAI", "EM CURSO", "act"),
        ("v", "Komatsu — ERP Baan, KPIs em Excel e RECOF", "CONCLUÍDA", "done"),
        ("v", "Criar meu README ninja", "CONCLUÍDA", "done"),
    ]
    rowh = 44
    H = 30 + 20 + len(quests) * rowh + 22
    b = header("DIÁRIO DE MISSÕES") + window(0, 30, 800, H - 30)
    for i, (ic, text, tag, st) in enumerate(quests):
        y = 52 + i * rowh
        cyy = y + 22
        if st == "act":
            b += ptext("!", 36, cyy - 9, 2, PINK)
            b += txt(58, cyy + 5, text, "#fff", 16)
            tw_ = tw(tag, 2) + 18
            b += f'<rect x="{772-tw_:g}" y="{cyy-12}" width="{tw_:g}" height="24" fill="{BG}" stroke="#fff" stroke-width="2"/>'
            b += ptext(tag, 772 - tw_ / 2, cyy - 6, 2, "#fff", "middle")
        else:
            b += grid(ICONS["check"][0], 28, cyy - 8, 2.2, {"#": "#5d5d6c"})
            b += txt(58, cyy + 5, text, "#5d5d6c", 16).replace("<text ", '<text text-decoration="line-through" ', 1)
            tw_ = tw(tag, 2) + 18
            b += f'<rect x="{772-tw_:g}" y="{cyy-12}" width="{tw_:g}" height="24" fill="{BG}" stroke="#3d3d4a" stroke-width="2"/>'
            b += ptext(tag, 772 - tw_ / 2, cyy - 6, 2, "#5d5d6c", "middle")
        if i < len(quests) - 1:
            b += dash(28, 772, y + rowh - 1)
    return svg(800, H, b).replace("<style>", "<title>Diário de missões: Automatsuo, Mais Capital, ML Aplicada; Komatsu e README concluídos</title><style>", 1)


# ================================================================== CONTINUE
def continuar():
    css = "@keyframes bl{50%{opacity:0}}.blink{animation:bl 1s steps(1) infinite}"
    css += "@keyframes spin{to{transform:rotate(360deg)}}.spin{animation:spin 1.2s steps(8) infinite}"
    for n in range(10):  # n9 aparece primeiro, n0 por último
        a, z = (9 - n) * 10, (10 - n) * 10
        css += (f"@keyframes n{n}{{0%,{a}%{{opacity:{0 if a else 1}}}"
                + (f"{a+.01}%,{z}%{{opacity:1}}{z+.01}%,100%{{opacity:0}}" if a else f"{z}%{{opacity:1}}{z+.01}%,100%{{opacity:0}}") + "}"
                + f".n{n}{{animation:n{n} 10s steps(1,end) infinite}}")
    b = ptext("CONTINUE?", 400, 18, 6, "#fff", "middle")
    for sx in (150, 650):
        b += f'<g transform="translate({sx},40)"><g class="spin">{icon("shuriken", 0, 0, 3, RED)}</g></g>'
    for n in range(10):
        b += f'<g class="n{n}">{ptext(str(n), 400, 70, 5, PINK, "middle")}</g>'
    b += txt(400, 128, "insira uma oportunidade de estágio e aceite a missão", "#aaa", 15, "middle")
    return svg(800, 144, b, css).replace("<style>", "<title>Continue? Insira uma oportunidade de estágio</title><style>", 1)


# ================================================================== RODAPÉ
def rodape():
    css = ("@keyframes bl{50%{opacity:0}}.blink{animation:bl 1s steps(1) infinite}"
           "@keyframes bob{50%{transform:translateY(-2px)}}.bob{animation:bob 1.4s steps(2) infinite}"
           "@keyframes fly{0%{transform:translateX(0);opacity:0}6%{opacity:1}60%{opacity:1}70%,100%{transform:translateX(640px);opacity:0}}"
           ".fly{animation:fly 6s linear infinite}"
           "@keyframes spin{to{transform:rotate(360deg)}}.spin{animation:spin .6s steps(6) infinite}")
    b = '<rect x="0" y="70" width="800" height="30" fill="#1b1b24"/><rect x="0" y="70" width="800" height="5" fill="#3a1520"/>'
    for x, y in ((50, 82), (230, 88), (420, 82), (610, 88), (760, 82)):
        b += f'<rect x="{x}" y="{y}" width="14" height="5" fill="#2e2e3a"/>'
    b += f'<g class="bob">{ninja(60, 10, 3.4)}</g>'
    b += '<g transform="translate(130,56)"><g class="fly"><g class="spin">' + icon("shuriken", 0, 0, 1.2, PINK) + '</g></g></g>'
    b += ptext("OBRIGADO POR VISITAR", 400, 20, 3, "#fff", "middle")
    b += grid(ICONS["check"][0], 336, 52, 2, {"#": "#5d5d6c"})
    b += f'<g class="blink">{ptext("MISSÃO CUMPRIDA · JOGO SALVO", 372, 52, 1.6, "#7a7a88")}</g>'
    return svg(800, 100, b, css).replace("<style>", "<title>Obrigado por visitar — jogo salvo</title><style>", 1)


# ================================================================== BOTÕES
def botao(nome, texto):
    w = int(tw(texto, 2) + 58)
    b = f'<rect x="1.5" y="1.5" width="{w-3}" height="37" fill="{BG}" stroke="#fff" stroke-width="3"/>'
    b += f'<path fill="{RED}" d="M14 12h4v16h-4zM18 15h4v10h-4zM22 18h4v4h-4z"/>'
    b += ptext(texto, 36, 13, 2, "#fff")
    s = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} 40" width="{w}" height="40" shape-rendering="crispEdges" role="img"><title>{texto}</title><rect width="{w}" height="40" fill="{BG}"/>{b}</svg>'
    save(nome, s)


if __name__ == "__main__":
    save("banner.svg", banner())
    save("sobre-mim.svg", sobre())
    save("ficha.svg", ficha())
    save("mapa.svg", mapa())
    save("atributos.svg", atributos())
    save("conquistas.svg", conquistas())
    save("inventario.svg", inventario())
    save("missoes.svg", missoes())
    save("continue.svg", continuar())
    save("rodape.svg", rodape())
    botao("btn-linkedin.svg", "LINKEDIN")
    botao("btn-email.svg", "E-MAIL")
    botao("btn-github.svg", "GITHUB")
    botao("btn-sp.svg", "SUZANO · SP")
