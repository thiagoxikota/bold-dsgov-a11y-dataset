# Piloto de 30/07/2026: correcao experimental em fork do exemplo Menu Push (DSGov)

Prova de conceito da camada de correcao do protocolo, executada sobre um FORK do codigo de exemplo da documentacao oficial. A correcao e experimental, aplicada a um fork local, e NAO foi incorporada pelo mantenedor do DSGov. Nada aqui altera o DSGov em producao.

## O que foi forkado

O codigo de exemplo da variante "Menu Principal Empurrando (Push)" da aba desenvolvedor de gov.br/ds/components/menu, copiado verbatim em 30/07/2026. E o codigo que um desenvolvedor copia e cola ao implementar o menu; e tambem a mesma variante (`br-menu push`) que o proprio portal de documentacao instancia no shell, onde a auditoria de nov/2025 registrou as falhas de estrutura ARIA exclusivas do DSGov (aria-required-parent, listitem).

O fork envolve o exemplo num esqueleto minimo (html lang + head + main), identico no antes e no depois: o diff entre os dois arquivos e exclusivamente a correcao (`correcao.diff`, 27 atributos removidos, nenhuma outra mudanca).

## O defeito

O exemplo mistura dois modelos semanticos incompatíveis: roles de arvore ARIA (`role="tree"` no nav, `role="treeitem"` em 26 links) sobre uma estrutura nativa de lista (ul/li). As WAI-ARIA Authoring Practices exigem que treeitem viva dentro de tree/group; os ul/li quebram essa cadeia. Resultado da auditoria no fork ANTES da correcao: 22 nos em violacao (aria-required-parent 21, criticas; aria-required-children 1, critica).

## A correcao especificada pelo protocolo

O quadro de recomendacoes do trabalho de origem (dimensao Robusto) especifica: restricao de uso de ARIA apenas quando HTML semantico nao for suficiente. Um menu de navegacao com ul/li ja tem semantica nativa de lista; os roles de arvore sao desnecessarios e, incompletos, quebram a arvore de acessibilidade. Correcao aplicada: remover `role="tree"` (1 ocorrencia) e `role="treeitem"` (26 ocorrencias). Nenhuma outra mudanca.

## Resultado (mesma auditoria, mesmo ambiente pinado)

| Bateria | Antes | Depois |
|---|---|---|
| axe-core 4.11.0, ruleset das sondas | 22 nos (aria-required-parent 21, aria-required-children 1) | 0 |
| axe-core 4.10.3, ruleset WCAG 2.1 AA das passadas DevTools | 22 nos (identico) | 0 |

Ambiente: Chrome for Testing headless shell 142.0.7444.175, viewport 1366x900, axe-core dos tarballs oficiais do npm; o mesmo da reauditoria de 30/07/2026 (`data/reaudit-2026-07/`). Script: `scripts/piloto-2026/audit_fork.py`.

## Leitura honesta dos limites

- A correcao vale para o FORK do exemplo. O DSGov em producao, o shell do portal e o codigo distribuido do componente permanecem como estao; nenhum PR foi enviado ao mantenedor.
- No fork, as regras sinalizadas foram aria-required-parent e aria-required-children. A regra listitem, registrada no shell do portal em nov/2025, nao fere no fork isolado (o contexto de ancestrais do shell difere do exemplo puro). O piloto prova a eliminacao da falha de estrutura ARIA sinalizada no proprio fork, nao de todas as falhas do shell.
- O fork nao carrega o CSS do design system: a camada visual (contraste) esta fora do escopo deste piloto, que isola a camada de marcacao, onde vive o defeito de estrutura ARIA.
- Remover os roles resolve a estrutura invalida. Implementar um padrao completo de tree view interativa (aria-expanded nos itens, navegacao por setas, conforme APG) e uma alternativa mais cara que o mantenedor pode preferir; o protocolo especifica o caminho minimo seguro.

## Arquivos

- `before/menu-push.html` e `after/menu-push.html`: fork antes e depois da correcao
- `correcao.diff`: diff unificado (a correcao inteira, auditavel linha a linha)
- `before.axe-*.json` e `after.axe-*.json`: exports completos das quatro auditorias
- `SHA256SUMS`: hashes de integridade dos seis artefatos
