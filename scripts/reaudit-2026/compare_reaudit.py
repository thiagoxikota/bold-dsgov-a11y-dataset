#!/usr/bin/env python3
"""Compara a reauditoria de 2026 com os baselines de nov/2025 e gera diffs.json.

Tres tabelas:
1. sonda: 8 paginas instrumentadas, axe 4.11.0, mesmo ruleset das sondas originais
2. devtools_auto: passadas DevTools (nao-AAA, automatizadas) vs run principal 4.10.3
3. supplement: regras best-practice/WCAG 2.2 do baseline vs passada suplementar

Uso: python compare_reaudit.py <baselines.json> <reaudit_dir> <out.json>
(<reaudit_dir> e o diretorio data/reaudit-YYYY-MM, com manifest.json no topo e raw/ dentro)
"""
import json, os, sys, glob

BEST_PRACTICE_OR_22 = {"region", "landmark-one-main", "aria-allowed-role",
                       "landmark-unique", "target-size", "heading-order",
                       "landmark-no-duplicate-banner", "landmark-no-duplicate-contentinfo"}


def norm(u):
    return u.rstrip("/")


def main():
    baselines = json.load(open(sys.argv[1]))
    outdir = sys.argv[2]
    manifest = json.load(open(os.path.join(outdir, "manifest.json")))
    rawdir = os.path.join(outdir, "raw") if os.path.isdir(os.path.join(outdir, "raw")) else outdir

    diffs = {"sonda": {}, "devtools_auto": {}, "supplement": {}, "totals": {}}

    # 1. Camada sonda
    sonda_equal = True
    for pid, base in baselines["sondas"].items():
        page = manifest["pages"].get(pid, {})
        new = (page.get("layers") or {}).get("sonda", {}).get("byId", {})
        rules = sorted(set(base["byId"]) | set(new))
        entry = {r: {"nov2025": base["byId"].get(r, 0), "reaudit": new.get(r, 0)} for r in rules}
        changed = {r: v for r, v in entry.items() if v["nov2025"] != v["reaudit"]}
        diffs["sonda"][pid] = {"url": base["url"], "rules": entry, "changed": changed}
        if changed:
            sonda_equal = False

    # 2. Camada DevTools (nao-AAA, automatizada) vs run principal
    for sysname, dt in baselines["devtools"].items():
        for url, pdata in dt["pages"].items():
            nurl = norm(url)
            new = {}
            for pid, page in manifest["pages"].items():
                if norm(page["url"]) == nurl:
                    new = (page.get("layers") or {}).get("devtools", {}).get("byId", {})
            base_auto = {r: c for r, c in pdata["aa"].items()}
            rules = sorted(set(base_auto) | set(new))
            entry = {}
            for r in rules:
                b, n = base_auto.get(r, 0), new.get(r, 0)
                cls = "match" if b == n else (
                    "config_excluded" if r in BEST_PRACTICE_OR_22 else "diff")
                entry[r] = {"nov2025": b, "reaudit": n, "class": cls}
            diffs["devtools_auto"].setdefault(sysname, {})[url] = entry

    # 3. Passada suplementar: as regras excluidas por config seguem presentes?
    for f in sorted(glob.glob(os.path.join(rawdir, "*.supp.axe-4.10.3.json"))):
        pid = os.path.basename(f).split(".")[0]
        d = json.load(open(f))
        counts = {v["id"]: len(v["nodes"]) for v in d.get("violations", [])
                  if v["id"] in BEST_PRACTICE_OR_22}
        diffs["supplement"][pid] = counts

    diffs["totals"] = {
        "sonda_paginas": len(diffs["sonda"]),
        "sonda_sem_diff": sonda_equal,
        "sonda_nov2025_nos": sum(b["total"] for b in baselines["sondas"].values()),
        "sonda_reaudit_nos": sum(
            (manifest["pages"].get(pid, {}).get("layers") or {}).get("sonda", {}).get("total", 0)
            for pid in baselines["sondas"]),
    }

    json.dump(diffs, open(sys.argv[3], "w"), indent=1, ensure_ascii=False)
    print("sonda: paginas =", diffs["totals"]["sonda_paginas"],
          "| nov2025 =", diffs["totals"]["sonda_nov2025_nos"], "nos",
          "| reaudit =", diffs["totals"]["sonda_reaudit_nos"], "nos",
          "| identico =", diffs["totals"]["sonda_sem_diff"])
    for pid, p in diffs["sonda"].items():
        if p["changed"]:
            print("  DIFF", pid, p["changed"])
    print("devtools_auto: diffs nao explicados por config:")
    for sysname, pages in diffs["devtools_auto"].items():
        for url, entry in pages.items():
            for r, v in entry.items():
                if v["class"] == "diff":
                    print(f"  {sysname} {url} {r}: {v['nov2025']} -> {v['reaudit']}")


if __name__ == "__main__":
    main()
