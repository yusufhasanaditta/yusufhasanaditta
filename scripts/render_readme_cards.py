"""Renders the animated SVG cards for the GitHub profile README.

Reads data/contributions.json (refreshed from the GitHub GraphQL API when GITHUB_TOKEN is set) and writes cards/*.svg.
GitHub shows an SVG through <img>: no scripts and no network, but its own <style> (CSS keyframes) and SMIL run, so every
font is embedded as a base64 WOFF subset. Cards play once, top to bottom (hero, graph, activity, tiles, repos).
STATIC=1 renders every card at its final frame, to check the layout before pushing.
"""
import base64, datetime as dt, json, os, urllib.request
from collections import Counter, OrderedDict
from xml.sax.saxutils import escape

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATIC = os.environ.get("STATIC") == "1"
LOGIN = os.environ.get("PROFILE_LOGIN", "yusufhasanaditta")
NAME_FIRST, NAME_LAST = "Yusuf Hasan", "Aditta"
TAGLINE = "student founder · building EWUdiots for East West University"
FEATURED = ["EWUdiots", "language-hub", "porichoy", "Portfolio"]
FALLBACK_DESC = {"Portfolio": "My portfolio: projects, design work and how to reach me."}

PAPER, INK, MUTED, LINE = "#F4F1EA", "#141414", "#6B6760", "#DED8CC"
BLUE, RED, YELLOW = "#2B59FF", "#EF4638", "#F2B705"

QUERY = """query($login:String!){user(login:$login){login createdAt contributionsCollection{totalCommitContributions
contributionCalendar{totalContributions weeks{contributionDays{date contributionCount}}}}
repositories(privacy:PUBLIC, first:30, orderBy:{field:PUSHED_AT,direction:DESC}){totalCount nodes{name description
stargazerCount primaryLanguage{name color} pushedAt homepageUrl url}}}}"""


def load():
    path = os.path.join(ROOT, "data", "contributions.json")
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        req = urllib.request.Request("https://api.github.com/graphql", json.dumps({"query": QUERY, "variables": {"login": LOGIN}}).encode(),
                                     {"Authorization": f"bearer {token}", "Content-Type": "application/json"})
        data = json.load(urllib.request.urlopen(req, timeout=30))
        if "errors" in data: raise SystemExit(data["errors"])
        user = data["data"]["user"]
        json.dump({"data": {"viewer": user}}, open(path, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    return json.load(open(path, encoding="utf-8"))["data"]["viewer"]


def font(name, file):
    b64 = base64.b64encode(open(os.path.join(ROOT, "fonts", file), "rb").read()).decode()
    return f"@font-face{{font-family:'{name}';src:url(data:font/woff;base64,{b64}) format('woff')}}"


FONTS = {"serif": font("Instrument Serif", "InstrumentSerif-Regular.woff"), "serif-i": font("Instrument Serif Italic", "InstrumentSerif-Italic.woff"),
         "geist": font("Geist", "geist-400.woff"), "geist-b": font("Geist SemiBold", "geist-600.woff"), "mono": font("Geist Mono", "mono-400.woff")}
KEYFRAMES = """
@keyframes up{from{opacity:0;transform:translateY(14px)}to{opacity:1;transform:none}}
@keyframes fade{from{opacity:0}to{opacity:1}}
@keyframes pop{0%{opacity:0;transform:scale(.2)}70%{opacity:1;transform:scale(1.25)}100%{opacity:1;transform:scale(1)}}
@keyframes grow{from{transform:scaleY(0)}to{transform:scaleY(1)}}
@keyframes type{from{clip-path:inset(0 100% 0 0)}to{clip-path:inset(0 0 0 0)}}
@keyframes blink{50%{opacity:0}}
.a{opacity:0;animation:up .7s cubic-bezier(.2,.8,.2,1) forwards}
.f{opacity:0;animation:fade .6s ease-out forwards}
.p{opacity:0;transform-box:fill-box;transform-origin:center;animation:pop .45s cubic-bezier(.2,.8,.2,1) forwards}
.g{transform-box:fill-box;transform-origin:bottom;transform:scaleY(0);animation:grow .8s cubic-bezier(.2,.8,.2,1) forwards}
.t{clip-path:inset(0 100% 0 0);animation:type 2.2s steps(60,end) forwards}
.c{animation:blink 1s steps(1) infinite}
@media (prefers-reduced-motion:reduce){*{animation:none!important;opacity:1!important;transform:none!important;clip-path:none!important}}
"""
if STATIC:
    KEYFRAMES = "*{animation:none!important;opacity:1!important;clip-path:none!important}.g{transform:none!important}"


def svg(w, h, body, fonts=("geist",), extra_css=""):
    css = "".join(FONTS[f] for f in fonts) + KEYFRAMES + extra_css
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img">'
            f"<style>{css}</style>{body}</svg>")


def d(s): return f"animation-delay:{s:.2f}s"


def card_bg(w, h, r=18): return f'<rect x="1" y="1" width="{w - 2}" height="{h - 2}" rx="{r}" fill="{PAPER}" stroke="{LINE}" stroke-width="1.5"/>'


# ---------- hero: the name with a sweeping blue shine, a typed tagline, an ASCII hourglass printing row by row ----------
HOURGLASS = ["  _________  ", " |=========| ", "  \\:::::::/  ", "   \\:::::/   ", "    \\:::/    ", "     )o(     ",
             "    / . \\    ", "   / ... \\   ", "  /:::::::\\  ", " |=========| ", "  ‾‾‾‾‾‾‾‾‾  "]


def hero():
    W, H = 840, 300
    shine = "" if STATIC else '<animateTransform attributeName="gradientTransform" type="translate" from="-1 0" to="1.2 0" dur="2.4s" begin="0.4s" fill="freeze"/>'
    rows = "".join(f'<text x="640" y="{64 + i * 19}" class="f" style="{d(0.3 + i * 0.09)}" font-family="Geist Mono" font-size="17" fill="{INK if i not in (3, 4, 6, 7, 8) else BLUE}" xml:space="preserve">{escape(r.replace("‾", "-"))}</text>' for i, r in enumerate(HOURGLASS))
    body = f"""{card_bg(W, H)}
<defs><linearGradient id="sh" x1="0" x2="1" gradientUnits="objectBoundingBox"><stop offset="0" stop-color="{INK}"/><stop offset=".42" stop-color="{INK}"/>
<stop offset=".5" stop-color="{BLUE}"/><stop offset=".58" stop-color="{INK}"/><stop offset="1" stop-color="{INK}"/>{shine}</linearGradient></defs>
<text x="44" y="64" class="a" style="{d(0)}" font-family="Geist SemiBold" font-size="14" letter-spacing="3" fill="{MUTED}">HELLO, I'M</text>
<text x="40" y="142" class="a" style="{d(0.1)}" font-family="Instrument Serif" font-size="86" fill="{INK}">{NAME_FIRST}</text>
<text x="40" y="214" class="a" style="{d(0.25)}" font-family="Instrument Serif Italic" font-size="86" fill="url(#sh)">{NAME_LAST}<tspan fill="{BLUE}">.</tspan></text>
<g class="t" style="{d(0.9)}"><text x="44" y="262" font-family="Geist Mono" font-size="15" fill="{INK}">&gt; {escape(TAGLINE)}</text></g>
<rect x="{44 + (len(TAGLINE) + 2) * 9.0 + 2:.0f}" y="249" width="9" height="17" fill="{BLUE}" class="c"/>
{rows}"""
    return svg(W, H, body, ("serif", "serif-i", "geist-b", "mono"))


# ---------- three tiles with a counter that runs up (SMIL <set> frames, CSS can't change text) ----------
def tile(label, color, value, unit, lines, delay):
    W, H = 270, 210
    frames = 18
    nums = [round(value * (1 - (1 - (i + 1) / frames) ** 3)) for i in range(frames)]
    if STATIC:
        counter = f'<text x="24" y="132" font-family="Instrument Serif" font-size="64" fill="{INK}">{value}</text>'
    else:
        counter = "".join(
            f'<text x="24" y="132" font-family="Instrument Serif" font-size="64" fill="{INK}" opacity="0">{n}'
            f'<set attributeName="opacity" to="1" begin="{delay + 0.3 + i * 0.05:.2f}s" dur="{0.05 if i < frames - 1 else "indefinite"}" {"" if i < frames - 1 else ""}/></text>'
            for i, n in enumerate(nums))
    sub = "".join(f'<text x="24" y="{170 + i * 20}" font-family="Geist" font-size="14" fill="{MUTED}">{escape(l)}</text>' for i, l in enumerate(lines))
    body = f"""<g class="a" style="{d(delay)}">{card_bg(W, H)}
<rect x="24" y="26" width="10" height="10" rx="2" fill="{color}"/><text x="42" y="36" font-family="Geist SemiBold" font-size="13" letter-spacing="3" fill="{INK}">{label}</text>
{counter}<text x="{24 + len(str(value)) * 30 + 10}" y="132" font-family="Instrument Serif Italic" font-size="26" fill="{color}">{escape(unit)}</text>
{sub}</g>"""
    return svg(W, H, body, ("serif", "serif-i", "geist", "geist-b"))


# ---------- activity: a bar per month, the best month in blue ----------
def activity(days):
    W, H = 840, 270
    months = OrderedDict()
    for x in days:
        k = x["date"][:7]; months[k] = months.get(k, 0) + x["contributionCount"]
    months = list(months.items())[-12:]
    top = max(v for _, v in months) or 1
    best = max(months, key=lambda kv: kv[1])[0]
    # streaks and busiest weekday
    longest = cur = 0
    for x in days:
        cur = cur + 1 if x["contributionCount"] else 0; longest = max(longest, cur)
    active = sum(1 for x in days if x["contributionCount"])
    wd = Counter()
    for x in days: wd[dt.date.fromisoformat(x["date"]).strftime("%A")] += x["contributionCount"]
    busiest = wd.most_common(1)[0][0] if wd else "-"
    bw, gap, x0, base, hmax = 34, 14, 44, 214, 120
    bars = ""
    for i, (k, v) in enumerate(months):
        h = max(3, v / top * hmax); x = x0 + i * (bw + gap)
        lab = dt.date.fromisoformat(k + "-01").strftime("%b")
        bars += (f'<rect x="{x}" y="{base - h:.1f}" width="{bw}" height="{h:.1f}" rx="4" fill="{BLUE if k == best else INK}" class="g" style="{d(1.6 + i * 0.06)}"/>'
                 f'<text x="{x + bw / 2}" y="{base + 20}" text-anchor="middle" font-family="Geist" font-size="12" fill="{MUTED}">{lab}</text>')
        if k == best: bars += f'<text x="{x + bw / 2}" y="{base - h - 8:.1f}" text-anchor="middle" font-family="Geist SemiBold" font-size="13" fill="{BLUE}" class="f" style="{d(2.4)}">{v}</text>'
    stats = [("longest streak", f"{longest} days"), ("active days", f"{active}"), ("busiest day", busiest)]
    st = "".join(f'<g class="a" style="{d(1.9 + i * 0.12)}"><text x="640" y="{96 + i * 52}" font-family="Instrument Serif" font-size="30" fill="{INK}">{escape(v)}</text>'
                 f'<text x="640" y="{116 + i * 52}" font-family="Geist" font-size="13" fill="{MUTED}">{escape(k)}</text></g>' for i, (k, v) in enumerate(stats))
    body = f"""{card_bg(W, H)}<text x="44" y="50" font-family="Geist SemiBold" font-size="13" letter-spacing="3" fill="{INK}" class="f" style="{d(1.5)}">ACTIVITY · LAST 12 MONTHS</text>
<line x1="44" y1="{base}" x2="610" y2="{base}" stroke="{LINE}" stroke-width="1.5"/>{bars}<line x1="614" y1="70" x2="614" y2="236" stroke="{LINE}" stroke-width="1.5"/>{st}"""
    return svg(W, H, body, ("serif", "geist", "geist-b"))


# ---------- contribution graph: blue squares pop in, sweeping left to right ----------
def graph(weeks, total):
    W, H = 840, 178
    cell, gap = 12, 3
    weeks = weeks[-53:]
    x0 = (W - len(weeks) * (cell + gap)) / 2
    cols = [PAPER, "#CBD7FF", "#8DA6FF", "#5479FF", BLUE]
    sq = ""
    for wi, wk in enumerate(weeks):
        for di, day in enumerate(wk["contributionDays"]):
            n = day["contributionCount"]; lvl = 0 if n == 0 else 1 if n < 3 else 2 if n < 5 else 3 if n < 8 else 4
            fill = cols[lvl] if lvl else "#E9E4D9"
            cls = f' class="p" style="{d(1.0 + wi * 0.018 + di * 0.01)}"' if lvl else ""
            sq += f'<rect x="{x0 + wi * (cell + gap):.1f}" y="{54 + di * (cell + gap)}" width="{cell}" height="{cell}" rx="2.5" fill="{fill}"{cls}/>'
    body = f"""{card_bg(W, H)}<text x="44" y="38" font-family="Geist SemiBold" font-size="13" letter-spacing="3" fill="{INK}" class="f" style="{d(0.9)}">{total} CONTRIBUTIONS IN THE LAST YEAR</text>{sq}"""
    return svg(W, H, body, ("geist-b",))


# ---------- repo cards ----------
def wrap(text, n):
    out, line = [], ""
    for w in (text or "").split():
        if len(line) + len(w) + 1 > n: out.append(line); line = w
        else: line = (line + " " + w).strip()
    if line: out.append(line)
    return out[:2] if len(out) <= 2 else out[:2][:-1] + [out[1][: n - 1] + "…"]


def repo(r, i):
    W, H = 410, 160
    lang = r.get("primaryLanguage") or {}
    desc = "".join(f'<text x="24" y="{84 + k * 21}" font-family="Geist" font-size="14" fill="{MUTED}">{escape(l)}</text>' for k, l in enumerate(wrap(r.get("description") or FALLBACK_DESC.get(r["name"], ""), 50)))
    live = '<text x="386" y="136" text-anchor="end" font-family="Geist SemiBold" font-size="13" fill="%s">live ↗</text>' % BLUE if r.get("homepageUrl") else ""
    body = f"""<g class="a" style="{d(2.4 + i * 0.12)}">{card_bg(W, H)}
<text x="24" y="48" font-family="Instrument Serif" font-size="30" fill="{INK}">{escape(r["name"])}</text>{desc}
<circle cx="30" cy="131" r="5" fill="{lang.get("color") or MUTED}"/><text x="42" y="136" font-family="Geist" font-size="13" fill="{INK}">{escape(lang.get("name") or "")}</text>{live}</g>"""
    return svg(W, H, body, ("serif", "geist", "geist-b"))


def main():
    u = load()
    cal = u["contributionsCollection"]["contributionCalendar"]
    days = [x for w in cal["weeks"] for x in w["contributionDays"]]
    repos = {r["name"]: r for r in u["repositories"]["nodes"]}
    out = os.path.join(ROOT, "cards"); os.makedirs(out, exist_ok=True)
    def write(name, s): open(os.path.join(out, name), "w", encoding="utf-8").write(s)
    write("hero.svg", hero())
    write("graph.svg", graph(cal["weeks"], cal["totalContributions"]))
    write("activity.svg", activity(days))
    n_repos = u["repositories"].get("totalCount", len(repos))
    write("build.svg", tile("BUILD", BLUE, n_repos, "public repos", ["EWUdiots, Language Hub,", "Porichoy and more"], 2.0))
    live = sum(1 for r in repos.values() if r.get("homepageUrl")) + 1  # + ewudiots.vercel.app
    write("design.svg", tile("DESIGN", RED, live, "sites live", ["premium UI and motion,", "3D maps, launch films"], 2.1))
    write("ship.svg", tile("SHIP", YELLOW, cal["totalContributions"], "contributions", ["in the last year,", "web and Android"], 2.2))
    for i, name in enumerate(FEATURED):
        if name in repos: write(f"repo-{name}.svg", repo(repos[name], i))
    print("cards written to", out)


if __name__ == "__main__":
    main()
