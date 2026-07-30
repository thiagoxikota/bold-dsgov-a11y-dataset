# Reauditoria 2026: harness

Scripts que reexecutam a auditoria axe sobre a versao ao vivo dos dois sistemas e comparam com a coleta de set-nov/2025. Resultados da rodada de 30/07/2026 em `data/reaudit-2026-07/` (relatorio no README de la).

## Setup (uma vez)

O harness pina browser e axe-core nas versoes registradas nos exports originais. Nada disso vai para o git; baixa local, dentro deste diretorio:

```bash
cd scripts/reaudit-2026

# 1. Venv com playwright (a versao do playwright nao importa; o browser vem de fora)
python3 -m venv .venv && .venv/bin/pip install playwright==1.61.0

# 2. Chrome for Testing headless shell 142 (mesma major registrada nas sondas de nov/2025)
curl -sL -o chrome.zip "https://storage.googleapis.com/chrome-for-testing-public/142.0.7444.175/mac-arm64/chrome-headless-shell-mac-arm64.zip"
unzip -q chrome.zip && rm chrome.zip

# 3. axe-core nas duas versoes da coleta original (tarballs oficiais do npm)
for v in 4.11.0 4.10.3; do
  curl -sL "https://registry.npmjs.org/axe-core/-/axe-core-$v.tgz" -o axe.tgz
  mkdir -p "axe-$v" && tar -xzf axe.tgz -C "axe-$v" --strip-components=1 && rm axe.tgz
done
```

Em outra plataforma, troque `mac-arm64` pelo target correspondente e aponte `REAUDIT_CHROME` para o binario.

## Rodada

```bash
# baselines a partir dos exports de nov/2025 (deterministico)
python3 extract_baselines.py ../../data/reaudit-2026-07/baselines.json

# passada principal: 15 paginas, camadas sonda (axe 4.11.0) e devtools-aprox (axe 4.10.3)
.venv/bin/python reaudit_harness.py ../../data/reaudit-2026-07/raw
mv ../../data/reaudit-2026-07/raw/manifest.json ../../data/reaudit-2026-07/manifest.json

# passada suplementar: regras best-practice e WCAG 2.2 (fecham o diff contra o mapeamento da Deque)
.venv/bin/python reaudit_supplement.py ../../data/reaudit-2026-07/raw

# comparacao
python3 compare_reaudit.py ../../data/reaudit-2026-07/baselines.json ../../data/reaudit-2026-07 ../../data/reaudit-2026-07/diffs.json
```

## Limites conhecidos

- `axe.run` via `page.evaluate` roda so no frame principal. A extensao Axe DevTools injeta em iframes; os exemplos em iframe do Bold (button-name, image-alt no form e no getting-started) ficam fora do alcance do harness. O diff classifica, nao esconde.
- A camada devtools-aprox e aproximacao: extensao (Chrome desktop 129.0, declarado no TCC) versus headless (Chrome 142). Comparacao de presenca/contagem por regra, nao de igualdade de export.
- Lighthouse e WAVE ficam fora do escopo desta reauditoria; o harness cobre a camada axe.
