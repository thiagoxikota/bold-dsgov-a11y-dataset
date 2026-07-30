#!/usr/bin/env python3
"""Reauditoria 2026 dos dois design systems (Bold e DSGov) com ambiente pinado.

Ambiente que espelha a coleta de nov/2025 (ver README.md deste diretorio para o setup):
- Browser: Chrome for Testing headless shell 142.0.7444.175 (baseline: HeadlessChrome/142)
- Viewport: 1366x900 (baseline das sondas)
- axe-core 4.11.0 (camada sondas) e 4.10.3 (camada DevTools, aproximacao headless)
- Ruleset sondas: runOnly tags [wcag2a, wcag2aa, wcag21aa], resultTypes [violations, incomplete]
- Ruleset devtools-aprox: tags [wcag2a, wcag2aa, wcag21a, wcag21aa]

Paths configuraveis por env var:
- REAUDIT_CHROME: binario do chrome-headless-shell (default: ./chrome-headless-shell-mac-arm64/chrome-headless-shell)
- REAUDIT_AXE_DIR: diretorio contendo axe-4.11.0/axe.min.js e axe-4.10.3/axe.min.js (default: .)

Uso: python reaudit_harness.py <outdir> [--only page_id]
"""
import json, os, sys, time
from playwright.sync_api import sync_playwright

HERE = os.path.dirname(os.path.abspath(__file__))
CHROME = os.environ.get("REAUDIT_CHROME",
                        os.path.join(HERE, "chrome-headless-shell-mac-arm64", "chrome-headless-shell"))
AXE_DIR = os.environ.get("REAUDIT_AXE_DIR", HERE)
AXE = {
    "4.11.0": open(os.path.join(AXE_DIR, "axe-4.11.0", "axe.min.js")).read(),
    "4.10.3": open(os.path.join(AXE_DIR, "axe-4.10.3", "axe.min.js")).read(),
}

# Paginas de registro: uniao das sondas (8), das passadas DevTools (12) e dos testes especificos.
PAGES = [
    ("bold_home",        "https://bold.bridge.ufsc.br/pt/",                              "bold",  ["devtools"]),
    ("bold_alert",       "https://bold.bridge.ufsc.br/pt/components/alert/",             "bold",  ["sonda", "devtools"]),
    ("bold_button",      "https://bold.bridge.ufsc.br/pt/components/button/",            "bold",  ["sonda", "devtools"]),
    ("bold_checkbox",    "https://bold.bridge.ufsc.br/pt/components/checkbox/",          "bold",  ["devtools"]),
    ("bold_form",        "https://bold.bridge.ufsc.br/pt/components/form/",              "bold",  ["sonda", "devtools"]),
    ("bold_table",       "https://bold.bridge.ufsc.br/pt/components/table/",             "bold",  ["sonda"]),
    ("bold_a11y",        "https://bold.bridge.ufsc.br/pt/design-guidelines/accessibility", "bold", ["devtools"]),
    ("bold_getting_started", "https://bold.bridge.ufsc.br/pt/getting-started/",          "bold",  ["devtools"]),
    ("dsgov_home",       "https://www.gov.br/ds/home",                                   "dsgov", ["devtools"]),
    ("dsgov_a11y",       "https://www.gov.br/ds/acessibilidade",                         "dsgov", ["devtools"]),
    ("dsgov_button",     "https://www.gov.br/ds/components/button?tab=desenvolvedor",    "dsgov", ["sonda", "devtools"]),
    ("dsgov_input",      "https://www.gov.br/ds/components/input?tab=desenvolvedor",     "dsgov", ["sonda", "devtools"]),
    ("dsgov_menu",       "https://www.gov.br/ds/components/menu?tab=desenvolvedor",      "dsgov", ["sonda", "devtools"]),
    ("dsgov_message",    "https://www.gov.br/ds/components/message?tab=desenvolvedor",   "dsgov", ["sonda", "devtools"]),
    ("dsgov_table",      "https://www.gov.br/ds/components/table?tab=desenvolvedor",     "dsgov", ["sonda"]),
]

RUNS = {
    "sonda":    {"axe": "4.11.0", "opts": {"runOnly": {"type": "tag", "values": ["wcag2a", "wcag2aa", "wcag21aa"]},
                                            "resultTypes": ["violations", "incomplete"], "reporter": "v1"}},
    "devtools": {"axe": "4.10.3", "opts": {"runOnly": {"type": "tag", "values": ["wcag2a", "wcag2aa", "wcag21a", "wcag21aa"]},
                                            "resultTypes": ["violations", "incomplete"], "reporter": "v1"}},
}


def audit_page(pw, page_id, url, layers, outdir):
    browser = pw.chromium.launch(executable_path=CHROME, headless=True)
    ctx = browser.new_context(viewport={"width": 1366, "height": 900})
    page = ctx.new_page()
    results = {}
    try:
        page.goto(url, wait_until="load", timeout=60000)
        try:
            page.wait_for_load_state("networkidle", timeout=15000)
        except Exception:
            pass  # paginas com polling nunca ficam idle; segue com o settle fixo
        page.wait_for_timeout(3000)
        for layer in layers:
            run = RUNS[layer]
            page.evaluate(AXE[run["axe"]])
            res = page.evaluate("opts => axe.run(document, opts)", run["opts"])
            fname = f"{page_id}.{layer}.axe-{run['axe']}.json"
            json.dump(res, open(os.path.join(outdir, fname), "w"), indent=1, ensure_ascii=False)
            counts = {v["id"]: len(v["nodes"]) for v in res.get("violations", [])}
            results[layer] = {"file": fname, "byId": counts, "total": sum(counts.values()),
                              "ua": res.get("testEnvironment", {}).get("userAgent", "")}
    finally:
        browser.close()
    return results


def main():
    outdir = sys.argv[1]
    only = sys.argv[sys.argv.index("--only") + 1] if "--only" in sys.argv else None
    os.makedirs(outdir, exist_ok=True)
    manifest = {"started": time.strftime("%Y-%m-%dT%H:%M:%S%z"), "chrome": "142.0.7444.175 (headless shell)",
                "viewport": "1366x900", "pages": {}}
    with sync_playwright() as pw:
        for page_id, url, system, layers in PAGES:
            if only and page_id != only:
                continue
            print(f"[{page_id}] {url}", flush=True)
            try:
                r = audit_page(pw, page_id, url, layers, outdir)
                for layer, info in r.items():
                    print(f"   {layer} (axe {RUNS[layer]['axe']}): {info['total']} nos | {info['byId']}", flush=True)
                manifest["pages"][page_id] = {"url": url, "system": system, "ok": True, "layers": r}
            except Exception as e:
                print(f"   ERRO: {e}", flush=True)
                manifest["pages"][page_id] = {"url": url, "system": system, "ok": False, "error": str(e)}
    manifest["finished"] = time.strftime("%Y-%m-%dT%H:%M:%S%z")
    json.dump(manifest, open(os.path.join(outdir, "manifest.json"), "w"), indent=1, ensure_ascii=False)
    print("manifest ->", os.path.join(outdir, "manifest.json"))


if __name__ == "__main__":
    main()
