"""Build the CMA hub: one page listing every report in the repo.

Usage (from the repo root):  python3 _builder/hub.py [out.html]
Reads every <slug>/data.json, computes the same value range and most-likely value
the report template does (Anchor + Supporting comps, time-adjusted), and writes a
self-contained HTML page (default /home/claude/cma-hub.html). That page is published
as Kevin's "CMA Hub" Claude artifact; it is not served on reports.househackusa.com.
Optional data.json field report.neighborhood overrides the auto-detected area name.
"""
import json, os, re, sys, glob, html
from datetime import date, datetime

root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
out = sys.argv[1] if len(sys.argv) > 1 else "/home/claude/cma-hub.html"
BASE = "https://reports.househackusa.com/"


def d(s):
    return datetime.strptime(s, "%Y-%m-%d").date()


def area_of(m):
    if m.get("neighborhood"):
        return m["neighborhood"]
    app = m.get("appreciation", {})
    lab = app.get("label") or ""
    x = re.search(r"\bin ([A-Z][A-Za-z .'-]+)$", lab)
    if x:
        return x.group(1).strip()
    x = re.search(r"\(([A-Z][A-Za-z .'-]+)\)", app.get("source", ""))
    if x:
        return x.group(1).strip()
    x = re.search(r"\bin ([A-Z][A-Za-z .'-]+?)(,| down| up|$)", app.get("source", ""))
    return x.group(1).strip() if x else ""


rows = []
for f in sorted(glob.glob(os.path.join(root, "*", "data.json"))):
    slug = os.path.basename(os.path.dirname(f))
    if slug.startswith("_"):
        continue
    R = json.load(open(f))
    M, S, APP = R["report"], R["subject"], R["report"]["appreciation"]
    asof = d(APP["asOf"])

    def adj(c):
        months = max(0, (asof - d(c["soldDate"])).days / 30.4375)
        return c["soldPrice"] * (1 + APP["rate"] * months / 12)

    core = [c for c in R["sold"] if c.get("role") in ("Anchor comp", "Supporting") and c.get("soldPrice")]
    vals = [adj(c) for c in core]
    r5 = lambda v: round(v / 5000) * 5000
    mid = round(sum(vals) / len(vals)) if vals else None
    units = S.get("unitRows") or []
    rent = sum((u.get("rent") or 0) for u in units)
    rep = sum(1 for u in units if u.get("rent"))
    anchor = next((c for c in R["sold"] if c.get("role") == "Anchor comp"), None)
    rows.append({
        "slug": slug, "url": BASE + slug + "/", "title": M["title"], "address": S.get("address"),
        "zip": S.get("zip"), "area": area_of(M), "prepared": M.get("prepared"), "asOf": APP["asOf"],
        "preparedFor": M.get("preparedFor") or "", "mode": M.get("mode") or "buyer",
        "status": S.get("status"), "mls": S.get("mls"), "type": S.get("type"), "units": S.get("units"),
        "unitsLabel": S.get("unitsLabel"), "beds": S.get("beds"), "baths": S.get("baths"),
        "listPrice": S.get("listPrice"), "low": r5(min(vals)) if vals else None,
        "high": r5(max(vals)) if vals else None, "mid": mid, "rate": APP["rate"],
        "rent": rent, "rentFull": bool(units) and rep == len(units), "rentAny": rep > 0,
        "soldCount": len(R["sold"]), "activeCount": len(R.get("actives") or []),
        "anchor": anchor and {"address": anchor["address"], "sold": anchor["soldPrice"], "date": anchor["soldDate"]},
        "medianNear": (M.get("market") or {}).get("medianNear"),
    })

rows.sort(key=lambda r: r["asOf"], reverse=True)
tpl = open(os.path.join(root, "_builder", "hub_template.html")).read()
page = (tpl.replace("/*ROWS*/", json.dumps(rows, ensure_ascii=False).replace("</", "<\\/"))
           .replace("__UPDATED__", html.escape(date.today().strftime("%B %-d, %Y"))))
open(out, "w").write(page)
print("hub:", len(rows), "reports ->", out)
