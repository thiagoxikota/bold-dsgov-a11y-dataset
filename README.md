# Dataset: auditoria de acessibilidade Bold vs DSGov (WCAG nível AA)

Relatórios brutos e scripts de análise da auditoria de acessibilidade digital de dois design systems institucionais brasileiros: Bold (Laboratório Bridge, UFSC) e Padrão Digital de Governo (DSGov, gov.br). Auditoria realizada em novembro de 2025 sobre a documentação pública então vigente de cada sistema.

Este repositório dá lastro de reprodutibilidade ao trabalho de origem e aos artigos derivados. Número-âncora do estudo: 277 não conformidades únicas de nível AA (75 no Bold, 202 no DSGov), obtidas após deduplicação (regra + seletor CSS + contexto do componente) e filtro de escopo que remove ocorrências de nível AAA.

## Estrutura

| Caminho | Conteúdo |
|---|---|
| `data/axe/` | Exports brutos do Axe DevTools (axe-core 4.10.3, WCAG 2.1 AA ruleset com marcações 2.0/2.1/2.2): duas passagens de documentação (`teste-doc-*`) e duas de bateria guiada (`testes-especificos-*`), uma por sistema |
| `data/evidencias-componentes/` | Sondas por componente (alert, button, form, input, message, table): axe-core 4.11.0 headless (`*.axe.json`, `*.axe-scoped.json`) e medição direta de contraste com razões computadas por elemento (`*.contrast.json`, `*.contrast_targeted.json`) |
| `scripts/` | Scripts de processamento e geração de gráficos usados na análise (`process_data.py`, `generate_charts.py`, `analyze_axe_json.py`, `generate_chart.py`) |

## Condições de coleta

- Coleta: setembro a novembro de 2025 (passagens principais em 08/11/2025).
- Viewport das passagens Axe DevTools: 1440x900. Sondas headless por componente: 1366x900.
- Objetos auditados: documentação pública do Bold (bold.bridge.ufsc.br) e do DSGov (gov.br/ds). Design systems são versionados; os sites podem ter mudado após a coleta.
- Os campos `screenshotURL` dos exports apontam para a API da Deque (axe.deque.com) e podem exigir autenticação ou ter expirado; são preservados por fidelidade ao export original.

## Notas de leitura (transparência)

- As contagens brutas dos exports excedem os totais consolidados: o pipeline do estudo deduplica por regra + seletor + contexto e remove o nível AAA (aproximadamente 200 ocorrências brutas no Bold e 700 no DSGov; 119 e 278 após deduplicação; 75 e 202 no recorte final AA).
- Saídas intermediárias de script podem divergir da contagem consolidada em regras específicas (exemplo conhecido: 18 ocorrências de color-contrast no Bold numa saída intermediária contra 21 na contagem consolidada). O artigo derivado declara essas divergências; a reconciliação consta do relatório de auditoria depositado com o trabalho de origem.

## Trabalho de origem e citação

Trabalho de origem (fonte-mãe do dataset):

XIKOTA, Thiago Kenji Corrêa. Acessibilidade digital em design systems públicos: uma auditoria de conformidade do Bold e DSGov. Trabalho de Conclusão de Curso (Bacharelado em Ciências da Computação), INE/CTC, Universidade Federal de Santa Catarina, Florianópolis, 2025. Repositório institucional UFSC: handle 123456789/270866. Zenodo: DOI 10.5281/zenodo.17740734.

BibTeX:

```bibtex
@misc{xikota2025dsaudit,
  author = {Xikota, Thiago Kenji Corr{\^e}a},
  title  = {Acessibilidade digital em design systems p{\'u}blicos: uma auditoria de conformidade do Bold e DSGov},
  year   = {2025},
  note   = {Trabalho de Conclus{\~a}o de Curso (Bacharelado em Ci{\^e}ncias da Computa{\c c}{\~a}o), INE/CTC/UFSC},
  doi    = {10.5281/zenodo.17740734},
  url    = {https://repositorio.ufsc.br/handle/123456789/270866}
}
```

Ver também `CITATION.cff`.

## Licença

- Dados (`data/`): Creative Commons Attribution 4.0 International (CC BY 4.0). Ver `LICENSE-CC-BY-4.0`.
- Scripts (`scripts/`): MIT. Ver `LICENSE-MIT`.
