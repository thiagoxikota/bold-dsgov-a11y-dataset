# Reauditoria 2026-11: rodada de confirmação (25/11/2026)

Reexecução integral do protocolo sobre a versão ao vivo do Bold e do DSGov em 25/11/2026, com o mesmo ambiente pinado das rodadas de 30/07 e 01/08/2026 (Chrome for Testing headless shell 142.0.7444.175, axe-core 4.11.0 e 4.10.3 dos tarballs oficiais do npm, viewport 1366x900, rulesets idênticos) e as mesmas baselines determinísticas de set-nov/2025.

## Resultado

1. **Camada de sondas: identidade total pela terceira vez.** As 8 páginas instrumentadas somam 451 nós em violação, os mesmos 451 de nov/2025, 30/07/2026 e 01/08/2026, regra por regra, página por página (`diffs.json`, seção `sonda`).
2. **Camada devtools-aproximada: nenhum diff novo.** Os diffs restantes caem nas mesmas classes triadas em `data/reaudit-2026-07/README.md`: exemplos em iframe do Bold fora do alcance do harness, divergência de color-contrast entre ferramentas já documentada e a mudança real no shell de gov.br/ds/acessibilidade, já registrada em julho.
3. **Nenhum número-âncora do estudo mudou** (75/202/277 no recorte AA).
4. **Correção do menu ainda não publicada.** O merge request 221 do govbr-ds-core ("fix(menu): remove roles aria inadequados") entrou em `main` em 14/10/2026 (UTC). Em 25/11/2026, a release mais recente no GitLab e no npm (`@govbr-ds/core`) continua sendo a v4.0.0-next.11, de 06/05/2026, e a documentação ao vivo segue com as 37 ocorrências de aria-required-parent e as 37 de listitem por página de componente.

## Arquivos

- `raw/`: exports integrais das passadas (sonda 4.11.0, devtools-aprox 4.10.3, suplementar) sobre as 15 páginas.
- `baselines.json`, `diffs.json`, `manifest.json`: mesmos formatos das rodadas anteriores.

Harness: `scripts/reaudit-2026/` (instruções de reprodução no README de lá).
