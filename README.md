# Dataset: auditoria de acessibilidade Bold vs DSGov (WCAG nível AA)

Relatórios brutos e scripts de análise da auditoria de acessibilidade digital de dois design systems institucionais brasileiros: Bold (Laboratório Bridge, UFSC) e Padrão Digital de Governo (DSGov, gov.br). Auditoria realizada em novembro de 2025 sobre a documentação pública então vigente de cada sistema.

Este repositório dá lastro de reprodutibilidade ao trabalho de origem e aos artigos derivados. Número-âncora do estudo: 277 não conformidades únicas de nível AA (75 no Bold, 202 no DSGov), obtidas após deduplicação (regra + seletor CSS + contexto do componente) e filtro de escopo que remove ocorrências de nível AAA.

## Estrutura

| Caminho | Conteúdo |
|---|---|
| `data/axe/` | Exports brutos do Axe DevTools (axe-core 4.10.3, WCAG 2.1 AA ruleset com marcações 2.0/2.1/2.2): duas passagens de documentação (`teste-doc-*`) e duas de bateria guiada (`testes-especificos-*`), uma por sistema |
| `data/evidencias-componentes/` | Sondas por componente (alert, button, form, input, message, table): axe-core 4.11.0 headless (`*.axe.json`, `*.axe-scoped.json`) e medição direta de contraste com razões computadas por elemento (`*.contrast.json`, `*.contrast_targeted.json`) |
| `scripts/` | Scripts de processamento e geração de gráficos usados na análise (`process_data.py`, `generate_charts.py`, `analyze_axe_json.py`, `generate_chart.py`) |

## Dicionário de dados (`data/evidencias-componentes/`)

Cada componente sondado tem um conjunto de arquivos por sufixo:

- `*.axe.json`: passagem completa do axe-core (headless, axe-core 4.11.0) sobre a página de documentação do componente, no formato padrão do axe-core com os grupos de resultado (`passes`, `violations`, `incomplete`, `inapplicable`) e os metadados de engine e ambiente (viewport, user agent).
- `*.axe-scoped.json`: a mesma passagem do axe-core restrita ao componente por seletores CSS (`context.include`), guardando os metadados do alvo (`ds`, `comp`, `url`), os seletores usados e o resultado (`results`) daquele recorte.
- `*.contrast.json`: medição direta de contraste dos elementos da página, com a razão computada por elemento nos estados normal, hover e foco e um resumo de quantas razões ficam abaixo dos limiares (`below45`, `below30`).
- `*.contrast_targeted.json`: medição de contraste restrita a um conjunto específico de seletores, cada item com seletor, texto, cor de primeiro plano, fundo e razão computada.
- `axe-summaries.json`: índice consolidado com uma entrada por componente sondado, cada uma com os metadados (`ds`, `comp`, `url`), um bloco estrutural (`lang`, contagem de `h1`, landmarks, presença de skip link) e um resumo do axe por impacto e por categoria.

## Condições de coleta

- Coleta: setembro a novembro de 2025 (passagens principais em 08/11/2025).
- Viewport das passagens Axe DevTools: 1440x900. Sondas headless por componente: 1366x900.
- Objetos auditados: documentação pública do Bold (bold.bridge.ufsc.br) e do DSGov (gov.br/ds). Design systems são versionados; os sites podem ter mudado após a coleta.
- Os campos `screenshotURL` dos exports apontam para a API da Deque (axe.deque.com) e podem exigir autenticação ou ter expirado; são preservados por fidelidade ao export original.

## Como reproduzir

Requisitos: Python 3.9+ e as dependências listadas em `requirements.txt` (`matplotlib` e `numpy`).

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Com o ambiente ativo, a partir da raiz do repositório:

```bash
python3 scripts/process_data.py      # deduplicação por regra + seletor
python3 scripts/analyze_axe_json.py  # análise por componente, tabelas LaTeX no stdout
```

Os dois scripts leem os exports em `data/axe/` por caminho relativo ao repositório e rodam tanto da raiz quanto de dentro de `scripts/`. As contagens canônicas (277 = 75 Bold + 202 DSGov, recorte AA) vêm do relatório de auditoria depositado com o trabalho de origem; saídas intermediárias de script podem divergir em regras específicas.

## Notas de leitura (transparência)

- As contagens brutas dos exports excedem os totais consolidados: o pipeline do estudo deduplica por regra + seletor + contexto e remove o nível AAA (aproximadamente 200 ocorrências brutas no Bold e 700 no DSGov; 119 e 278 após deduplicação; 75 e 202 no recorte final AA).
- Saídas intermediárias de script podem divergir da contagem consolidada em regras específicas (exemplo conhecido: 18 ocorrências de color-contrast no Bold numa saída intermediária contra 21 na contagem consolidada). O artigo derivado declara essas divergências; a reconciliação consta do relatório de auditoria depositado com o trabalho de origem.
- O script `scripts/process_data.py` implementa a etapa de deduplicação por regra + seletor CSS; a atribuição por contexto de componente ocorre na análise por componente (`scripts/analyze_axe_json.py`) e o filtro de escopo AA está especificado e reconciliado no relatório de auditoria depositado com o trabalho de origem. Os scripts `generate_chart.py` e `generate_charts.py` são stubs ilustrativos de figura com valores inseridos à mão, não a análise de registro.

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

Trabalho derivado aprovado na lista oficial do Fórum BrasilGov Academy (BrasilGov Summit 2026, Florianópolis): 'Inclusão por Padrão: Auditoria Comparativa de Acessibilidade entre Implementações Bold e DSGov em Portais Públicos' (Thiago Kenji Corrêa Xikota, UFSC). O fórum não publica anais; não há DOI nem link estável para o trabalho derivado.

## Licença

- Dados (`data/`): Creative Commons Attribution 4.0 International (CC BY 4.0). Ver `LICENSE-CC-BY-4.0`.
- Scripts (`scripts/`): MIT. Ver `LICENSE-MIT`.
