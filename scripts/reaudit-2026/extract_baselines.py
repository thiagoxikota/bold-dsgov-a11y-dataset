#!/usr/bin/env python3
"""Extrai baselines (nov/2025) do dataset para comparacao com a reauditoria de 2026.

Saida: baselines.json com duas camadas:
- sondas: 8 paginas de componente, axe-core 4.11.0 headless, contagem de nos por regra
- devtools: passadas Axe DevTools 4.10.3 (doc completa), contagem de issues por pagina+regra,
  com variante AA (excluindo regras marcadas wcag2aaa, espelhando o filtro do pipeline)

Uso: python extract_baselines.py [saida.json]  (roda de qualquer cwd; acha o repo pelo proprio path)
"""
import json, glob, os, sys

DATASET = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

out = {"sondas": {}, "devtools": {}}

# Camada 1: sondas full-page (*.axe.json)
for f in sorted(glob.glob(os.path.join(DATASET, "data/evidencias-componentes/*.axe.json"))):
    d = json.load(open(f))
    if isinstance(d, list):
        d = d[0]
    pid = os.path.basename(f).replace(".axe.json", "")
    by_id = {v["id"]: len(v["nodes"]) for v in d.get("violations", [])}
    by_impact = {}
    for v in d.get("violations", []):
        for n in v["nodes"]:
            imp = n.get("impact") or v.get("impact") or "?"
            by_impact[imp] = by_impact.get(imp, 0) + 1
    out["sondas"][pid] = {
        "url": d["url"],
        "timestamp": d.get("timestamp"),
        "axe": d["testEngine"]["version"],
        "byId": by_id,
        "byImpact": by_impact,
        "total": sum(by_id.values()),
        "incomplete": {v["id"]: len(v["nodes"]) for v in d.get("incomplete", [])},
    }

# Camada 2: passadas DevTools (teste-doc-*)
for sysname, f in [("bold", "data/axe/teste-doc-bold-axe.json"),
                   ("dsgov", "data/axe/teste-doc-dsgov-axe.json")]:
    d = json.load(open(os.path.join(DATASET, f)))
    pages = {}
    for it in d["allIssues"]:
        url = it["testUrl"]
        rule = it["ruleId"]
        tags = it.get("tags") or []
        is_aaa = "wcag2aaa" in tags
        p = pages.setdefault(url, {"all": {}, "aa": {}})
        p["all"][rule] = p["all"].get(rule, 0) + 1
        if not is_aaa:
            p["aa"][rule] = p["aa"].get(rule, 0) + 1
    out["devtools"][sysname] = {
        "root_url": d["url"],
        "axe": d["axeVersion"],
        "dates": [d["testingStartDate"], d["testingEndDate"]],
        "issueSummary": d["issueSummary"],
        "total_all": len(d["allIssues"]),
        "total_aa": sum(sum(p["aa"].values()) for p in pages.values()),
        "pages": pages,
    }

dst = sys.argv[1] if len(sys.argv) > 1 else "baselines.json"
json.dump(out, open(dst, "w"), indent=1, ensure_ascii=False)
print(f"baselines -> {dst}")
for pid, s in out["sondas"].items():
    print(f"  sonda {pid}: {s['total']} nos | {s['byId']}")
for sysname, s in out["devtools"].items():
    print(f"  devtools {sysname}: {s['total_all']} issues ({s['total_aa']} nao-AAA) em {len(s['pages'])} paginas")
