"""Build a CMA report page from its data.json.

Usage (from the repo root):  python3 _builder/build.py <slug>
Reads <slug>/data.json, writes <slug>/index.html using _builder/template.html.

data.json keys:
  report:   slug, title, prepared, preparedFor, agent{name,team,brokerage,email},
            market{medianNear,countNear,radiusNear,medianDom,...},
            appreciation{rate (decimal/yr), asOf (YYYY-MM-DD), source}
  subject:  one listing (status "Active", role "Subject")
  sold:     sold comps; role is "Anchor comp" | "Supporting" | "Upper bound" | "Ceiling" | "Floor"
            (value range and most-likely value come from Anchor + Supporting, time-adjusted)
  actives:  competing listings; status "Active" | "Under contract"
  method:   list of strings for the About page
Each listing: mls, status, role, why, vs, address, zip, units, type, listPrice, originalPrice,
  soldPrice, soldDate, listDate, dom, beds, baths, year, exterior, basement, parking, heating, lot,
  taxes, taxYear, remarks, lat, lon, images[] (Repliers paths like "mred/IMG-...jpg"),
  unitRows[] {unit, beds, baths, sqft, rent, lease, pays}, optional extraUnitNote, taxNote, showing.
"""
import json, os, sys
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
slug = sys.argv[1]
data = json.load(open(os.path.join(root, slug, "data.json")))
tpl = open(os.path.join(root, "_builder", "template.html")).read()
html = tpl.replace("/*DATA*/", json.dumps(data, ensure_ascii=False).replace("</", "<\\/")).replace("__TITLE__", data["report"]["title"])
open(os.path.join(root, slug, "index.html"), "w").write(html)
print("built", slug)
