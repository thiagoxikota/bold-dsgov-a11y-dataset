#!/usr/bin/env python3
"""Passada suplementar: mesmas paginas, axe 4.10.3, com best-practice e WCAG 2.2 habilitados.

Cobre as regras que a passada principal exclui por config (region, landmark-one-main,
aria-allowed-role, landmark-unique, target-size), para fechar o diff contra as passadas
DevTools de nov/2025, que usam o mapeamento proprietario da Deque (a extensao reporta
essas regras dentro do escopo WCAG dela; o axe-core open source as marca best-practice
ou wcag22aa).

Paths configuraveis por env var (mesmas do reaudit_harness.py).
Uso: python reaudit_supplement.py <outdir>
"""
import json, os, sys
from playwright.sync_api import sync_playwright

HERE = os.path.dirname(os.path.abspath(__file__))
CHROME = os.environ.get("REAUDIT_CHROME",
                        os.path.join(HERE, "chrome-headless-shell-mac-arm64", "chrome-headless-shell"))
AXE_DIR = os.environ.get("REAUDIT_AXE_DIR", HERE)
AXE_SRC = open(os.path.join(AXE_DIR, "axe-4.10.3", "axe.min.js")).read()

PAGES = [
    ("bold_home",     "https://bold.bridge.ufsc.br/pt/"),
    ("bold_form",     "https://bold.bridge.ufsc.br/pt/components/form/"),
    ("bold_getting_started", "https://bold.bridge.ufsc.br/pt/getting-started/"),
    ("dsgov_home",    "https://www.gov.br/ds/home"),
    ("dsgov_a11y",    "https://www.gov.br/ds/acessibilidade"),
    ("dsgov_button",  "https://www.gov.br/ds/components/button?tab=desenvolvedor"),
    ("dsgov_input",   "https://www.gov.br/ds/components/input?tab=desenvolvedor"),
    ("dsgov_menu",    "https://www.gov.br/ds/components/menu?tab=desenvolvedor"),
    ("dsgov_message", "https://www.gov.br/ds/components/message?tab=desenvolvedor"),
]

OPTS = {"runOnly": {"type": "tag",
                    "values": ["wcag2a", "wcag2aa", "wcag21a", "wcag21aa",
                                "wcag22a", "wcag22aa", "best-practice"]},
        "resultTypes": ["violations", "incomplete"], "reporter": "v1"}


def main():
    outdir = sys.argv[1]
    os.makedirs(outdir, exist_ok=True)
    with sync_playwright() as pw:
        for page_id, url in PAGES:
            print(f"[{page_id}] {url}", flush=True)
            browser = pw.chromium.launch(executable_path=CHROME, headless=True)
            ctx = browser.new_context(viewport={"width": 1366, "height": 900})
            page = ctx.new_page()
            try:
                page.goto(url, wait_until="load", timeout=60000)
                try:
                    page.wait_for_load_state("networkidle", timeout=15000)
                except Exception:
                    pass
                page.wait_for_timeout(3000)
                page.evaluate(AXE_SRC)
                res = page.evaluate("opts => axe.run(document, opts)", OPTS)
                json.dump(res, open(os.path.join(outdir, f"{page_id}.supp.axe-4.10.3.json"), "w"),
                          indent=1, ensure_ascii=False)
                counts = {v["id"]: len(v["nodes"]) for v in res.get("violations", [])}
                print(f"   {sum(counts.values())} nos | {counts}", flush=True)
            except Exception as e:
                print(f"   ERRO: {e}", flush=True)
            finally:
                browser.close()


if __name__ == "__main__":
    main()
