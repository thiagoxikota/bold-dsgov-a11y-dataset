# Concordância entre verificadores automáticos (coleta de 14/09/2026)

Quatro verificadores executados sobre as mesmas 15 páginas de documentação do Bold e do DSGov (as mesmas de `reaudit-2026-08/`), no mesmo dia e ambiente. Base do artigo "Quatro verificadores, uma página: concordância entre ferramentas automáticas de acessibilidade na documentação do Bold e do Padrão Digital de Governo" (Xikota; Wazlawick, 2026, em preparação).

| Ferramenta | Versão | Motor | Falha determinada | Revisão humana |
|---|---|---|---|---|
| axe-core | 4.11.0 | próprio | `violations` | `incomplete` |
| Lighthouse | 12.8.2 (axe-core 4.11.0 embutido) | axe-core | auditoria binária com `score` 0 | auditorias `manual` |
| IBM Equal Access (accessibility-checker) | 4.0.34, arquivo de regras "latest" em 14/09/2026, política WCAG_2_1 | próprio | `violation` | `potentialviolation` |
| HTML_CodeSniffer via pa11y | 2.5.1 / 8.0.0, padrão WCAG2AA | próprio | `error` | `warning`, `notice` |

Ambiente: Chrome for Testing 148 headless (puppeteer 24.43.1), 1366x900, `networkidle2` + 2,5 s; coleta entre 19:11 e 19:29 UTC (16h11 a 16h29 BRT). Log em `collect.log`.

- `raw/<pagina>.<ferramenta>.json`: 60 arquivos (15 páginas x 4 ferramentas). O `.axe.json` inclui `rules` (catálogo com etiquetas WCAG, usado também para mapear as auditorias do Lighthouse).
- `results/metrics.json`: pares (página, critério A/AA da WCAG 2.1) por ferramenta, união, exclusivos, Jaccard e kappa de Cohen par a par, kappa de Fleiss, cobertura de catálogo, regras por par.
- `results/por_pagina.csv`, `results/por_criterio.csv`, `results/matriz_pagina_sc.csv` (pares da união com as regras que os produziram, por ferramenta) e as quatro figuras.

Reprodução: `cd scripts/concordancia-2026 && npm install && node collect.mjs` (grava em `raw/`), depois `python3 analyze.py` (numpy e matplotlib; lê `raw/`, `pages.json`, `ibm_rulesets.json` e `node_modules/html_codesniffer/Standards/WCAG2AA/ruleset.js`). Os números canônicos do artigo vêm de `results/metrics.json` desta pasta.

Resumo: união de 75 pares; 12 marcados pelas quatro ferramentas, 37 por uma só; kappa de Fleiss 0,52 (quatro) e 0,41 (três motores independentes); axe-core e Lighthouse com kappa 0,90 entre si; instâncias de 324 (IBM) a 4.014 (HTML_CodeSniffer).
