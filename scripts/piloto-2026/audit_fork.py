#!/usr/bin/env python3
"""Piloto: auditoria antes/depois do fork do codigo de exemplo Menu Push (DSGov).

Mesmo ambiente pinado da reauditoria (ver scripts/reaudit-2026/README.md):
Chrome for Testing headless shell 142.0.7444.175, viewport 1366x900, e as duas
baterias registradas nos exports originais (axe-core 4.11.0 com o ruleset das
sondas; axe-core 4.10.3 com o ruleset WCAG 2.1 AA das passadas DevTools).

Paths configuraveis por env var (mesmas do reaudit_harness.py):
- REAUDIT_CHROME, REAUDIT_AXE_DIR

Uso: python audit_fork.py <arquivo.html> <saida-prefixo>
Gera <saida-prefixo>.axe-4.11.0.json e <saida-prefixo>.axe-4.10.3.json
"""
import json, os, sys
from playwright.sync_api import sync_playwright

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_TOOLDIR = os.path.join(os.path.dirname(HERE), "reaudit-2026")
CHROME = os.environ.get("REAUDIT_CHROME",
                        os.path.join(DEFAULT_TOOLDIR, "chrome-headless-shell-mac-arm64", "chrome-headless-shell"))
AXE_DIR = os.environ.get("REAUDIT_AXE_DIR", DEFAULT_TOOLDIR)

RUNS = {
    "4.11.0": {"runOnly": {"type": "tag", "values": ["wcag2a", "wcag2aa", "wcag21aa"]},
                "resultTypes": ["violations", "incomplete"], "reporter": "v1"},
    "4.10.3": {"runOnly": {"type": "tag", "values": ["wcag2a", "wcag2aa", "wcag21a", "wcag21aa"]},
                "resultTypes": ["violations", "incomplete"], "reporter": "v1"},
}


def main():
    target = os.path.abspath(sys.argv[1])
    prefix = sys.argv[2]
    with sync_playwright() as pw:
        browser = pw.chromium.launch(executable_path=CHROME, headless=True)
        ctx = browser.new_context(viewport={"width": 1366, "height": 900})
        page = ctx.new_page()
        page.goto("file://" + target, wait_until="load", timeout=30000)
        page.wait_for_timeout(1000)
        for ver, opts in RUNS.items():
            axe_src = open(os.path.join(AXE_DIR, f"axe-{ver}", "axe.min.js")).read()
            page.evaluate(axe_src)
            res = page.evaluate("opts => axe.run(document, opts)", opts)
            out = f"{prefix}.axe-{ver}.json"
            json.dump(res, open(out, "w"), indent=1, ensure_ascii=False)
            counts = {v["id"]: len(v["nodes"]) for v in res.get("violations", [])}
            print(f"{os.path.basename(target)} [axe {ver}]: {sum(counts.values())} nos | {counts}")
        browser.close()


if __name__ == "__main__":
    main()
