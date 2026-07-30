# Reauditoria de 30/07/2026: diffs frente a coleta de set-nov/2025

Reexecucao do protocolo de auditoria sobre a versao ao vivo da documentacao do Bold (bold.bridge.ufsc.br) e do DSGov (gov.br/ds) em 30/07/2026, com ambiente pinado nas versoes registradas nos exports originais. Objetivo: registrar o que mudou (ou nao) nos dois sistemas desde a coleta do estudo, antes de qualquer uso publico novo dos numeros. Harness e instrucoes de reproducao em `scripts/reaudit-2026/`.

## Ambiente

| Item | Coleta nov/2025 | Reauditoria jul/2026 |
|---|---|---|
| Browser (sondas) | HeadlessChrome/142 (registrado nos JSONs) | Chrome for Testing headless shell 142.0.7444.175 |
| Browser (passadas DevTools) | Chrome desktop 129.0 (declarado no TCC) | nao reproduzivel; aproximado em headless 142 |
| axe-core (sondas) | 4.11.0 | 4.11.0 (tarball oficial npm) |
| axe-core (DevTools) | 4.10.3 (extensao 4.117.0) | 4.10.3 (tarball oficial npm) |
| Viewport | 1366x900 | 1366x900 |
| Ruleset sondas | runOnly [wcag2a, wcag2aa, wcag21aa] | identico |

15 paginas auditadas: a uniao das 8 paginas instrumentadas pelas sondas, das 12 paginas das passadas DevTools e da pagina getting-started dos testes especificos.

## Resultado 1: camada sondas (reproducao exata do ambiente)

Zero diferenca. As 8 paginas instrumentadas somavam 451 nos em violacao em nov/2025 e somam 451 nos em 30/07/2026, com as mesmas regras e as mesmas contagens, pagina por pagina:

| Pagina | nov/2025 | jul/2026 | Regras (identicas nas duas datas) |
|---|---|---|---|
| bold_alert | 4 | 4 | color-contrast 4 |
| bold_button | 5 | 5 | color-contrast 5 |
| bold_form | 10 | 10 | color-contrast 10 |
| bold_table | 24 | 24 | button-name 19, color-contrast 5 |
| dsgov_button | 94 | 94 | aria-required-parent 37, listitem 37, color-contrast 15, outras 5 |
| dsgov_input | 105 | 105 | aria-required-parent 37, listitem 37, color-contrast 26, outras 5 |
| dsgov_message | 107 | 107 | aria-required-parent 37, listitem 37, color-contrast 28, outras 5 |
| dsgov_table | 102 | 102 | aria-required-parent 37, listitem 37, color-contrast 23, outras 5 |

A pagina do menu do DSGov, que nao tinha sonda em nov/2025, entra agora como registro novo: 159 nos (color-contrast 80, aria-required-parent 37, listitem 37, outras 5).

## Resultado 2: camada DevTools (aproximacao headless)

Todo diff apontado pelo comparador se resolve em uma de quatro classes, verificadas uma a uma em `diffs.json`:

1. **Config de ruleset.** region, landmark-one-main, aria-allowed-role, landmark-unique (best-practice no axe-core open source) e target-size (wcag22aa) ficam fora da passada principal por construcao. A passada suplementar, com essas tags habilitadas, confirma que continuam presentes onde estavam: region 8 e landmark-one-main 1 na home do Bold; aria-allowed-role 2 e landmark-unique 1 nas paginas do DSGov; target-size 2 no input.
2. **Iframe.** button-name 2, image-alt 2 e scrollable-region-focusable 1 no form do Bold (e button-name/image-alt no getting-started) vivem em iframes de exemplo, que a extensao DevTools escaneia e o harness headless nao. As sondas de nov/2025, tambem headless, ja nao os viam. Sem evidencia de mudanca no site.
3. **Divergencia cross-tool ja documentada.** color-contrast no input (23 na extensao, 26 na sonda) e no message (27 na extensao, 28 na sonda) em nov/2025. A reauditoria bate exatamente com as sondas (26 e 28). A divergencia entre ferramentas e pre-existente e esta declarada no README raiz do dataset.
4. **Mudanca real no sistema.** Duas, ambas no DSGov:
   - **gov.br/ds/acessibilidade** nao exibe mais, no estado de carga, as 74 ocorrencias do shell do menu de componentes (aria-required-parent 37 + listitem 37) nem 1 das 2 aria-required-children. A pagina hoje tem o mesmo perfil de violacoes da home (aria-allowed-attr 1, aria-required-children 1, link-in-text-block 2). As mesmas falhas de shell persistem nas 5 paginas de componentes auditadas, com os mesmos seletores.
   - **gov.br/ds/components/menu** perdeu 1 ocorrencia de target-size (WCAG 2.2) presente em nov/2025.

## Conclusao

Nenhum numero-ancora do estudo muda. Os totais consolidados (75 Bold, 202 DSGov, 277 no recorte AA) descrevem a coleta de set-nov/2025 e continuam reproduziveis onde a reproducao exata e possivel: a camada de sondas retornou identidade total, no por no. Os padroes centrais seguem observaveis ao vivo em 30/07/2026: as falhas de estrutura ARIA exclusivas do DSGov (aria-required-parent, listitem) continuam nas paginas de componentes; o contraste segue dominante nos dois sistemas; as duas unicas mudancas reais detectadas reduzem ocorrencias em paginas nao instrumentadas e nao alteram os seletores que sustentam a contagem deduplicada.

Escopo: esta reauditoria cobre a camada axe. Lighthouse, WAVE, inspecao heuristica e checklist eMAG nao foram reexecutados.

## Arquivos

- `manifest.json`: indice da rodada (paginas, camadas, contagens, ambiente)
- `baselines.json`: baselines de nov/2025 derivados dos exports originais (deterministico)
- `diffs.json`: comparacao por pagina e por regra, com classe de cada diff
- `raw/`: exports axe completos da rodada (24 da passada principal, 9 da suplementar)
