# Reauditoria 2026-08: rodada de confirmacao (01/08/2026)

Reexecucao integral do protocolo sobre a versao ao vivo do Bold e do DSGov em
01/08/2026, com o mesmo ambiente pinado da rodada de 30/07/2026 (Chrome for
Testing headless shell 142.0.7444.175, axe-core 4.11.0 e 4.10.3 dos tarballs
oficiais do npm, viewport 1366x900, rulesets identicos) e as mesmas baselines
deterministicas extraidas dos exports de set-nov/2025.

## Resultado

1. **Camada de sondas: identidade total, de novo.** As 8 paginas instrumentadas
   somam 451 nos em violacao, os mesmos 451 de nov/2025 e de 30/07/2026, regra
   por regra, pagina por pagina (`diffs.json`, secao `sonda`).
2. **Camada devtools-aproximada: classificacao identica a da rodada de julho.**
   Nenhum diff novo frente a `data/reaudit-2026-07/diffs.json`; as mesmas
   classes de artefato de ferramenta e as mesmas duas mudancas reais do DSGov
   ja triadas em julho (shell de /ds/acessibilidade e target-size do menu).
3. **Nenhum numero-ancora do estudo mudou.** Os totais consolidados
   (75/202/277 AA) permanecem sustentados pelos seletores das paginas de
   componentes, presentes ao vivo nesta rodada.

## Arquivos

- `raw/`: exports integrais das passadas (sonda 4.11.0, devtools-aprox 4.10.3,
  suplementar) sobre as 15 paginas.
- `baselines.json`: baselines de nov/2025 (deterministicas, mesmas de julho).
- `diffs.json`: comparacao completa contra nov/2025.
- `manifest.json`: ambiente, versoes e paginas da rodada.

Harness: `scripts/reaudit-2026/` (mesmos scripts da rodada de julho, sem
alteracao).
