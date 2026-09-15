#!/usr/bin/env python3
"""Concordância entre verificadores automáticos de acessibilidade.

Entrada: raw/<pagina>.<ferramenta>.json (axe, lighthouse, ibm, htmlcs), pages.json, ibm_rulesets.json,
node_modules/html_codesniffer/Standards/WCAG2AA/ruleset.js.
Saída: results/metrics.json, results/*.csv, results/fig_*.png.

Unidade de análise: par (página, critério de sucesso WCAG 2.1 nível A ou AA) marcado como FALHA por uma
ferramenta. Só entram resultados que a própria ferramenta classifica como falha determinada
(axe: violations; Lighthouse: auditoria binária com score 0; IBM: level violation; HTML_CodeSniffer: type
error). O que a ferramenta pede revisão humana (axe incomplete, IBM potentialviolation, HTMLCS warning e
notice, Lighthouse manual) é contado à parte e nunca entra na concordância.
"""
import csv, json, os, re, sys, itertools, collections
import numpy as np

RAW = 'raw'; OUT = 'results'; os.makedirs(OUT, exist_ok=True)
PAGES = json.load(open('pages.json'))
TOOLS = ['axe', 'lighthouse', 'ibm', 'htmlcs']
TOOL_LABEL = {'axe': 'axe-core', 'lighthouse': 'Lighthouse', 'ibm': 'IBM Equal Access', 'htmlcs': 'HTML_CodeSniffer'}

# ---------- universo de critérios: WCAG 2.1 A e AA, a partir do ruleset WCAG_2_1 do IBM (50 checkpoints)
rulesets = json.load(open('ibm_rulesets.json'))
wcag21 = next(r for r in rulesets if r['id'] == 'WCAG_2_1')
SC_LEVEL = {}
for cp in wcag21['checkpoints']:
    if cp['wcagLevel'] in ('A', 'AA'):
        SC_LEVEL[cp['num']] = cp['wcagLevel']
SCS = sorted(SC_LEVEL, key=lambda s: tuple(int(x) for x in s.split('.')))
assert len(SCS) == 50, len(SCS)
IBM_RULE_TO_SC = collections.defaultdict(set)
for cp in wcag21['checkpoints']:
    if cp['num'] in SC_LEVEL:
        for r in cp['rules']:
            IBM_RULE_TO_SC[r['id']].add(cp['num'])

def axe_tag_to_sc(tag):
    m = re.fullmatch(r'wcag(\d)(\d)(\d{1,2})', tag)
    if not m: return None
    return f'{m.group(1)}.{m.group(2)}.{int(m.group(3))}'

def htmlcs_code_to_sc(code):
    m = re.search(r'Principle\d\.Guideline\d_\d\.(\d)_(\d)_(\d{1,2})', code)
    return f'{m.group(1)}.{m.group(2)}.{int(m.group(3))}' if m else None

# ---------- catálogo (cobertura potencial) por ferramenta
def axe_catalog(rules):
    cat = collections.defaultdict(set)
    for r in rules:
        if 'deprecated' in r['tags']: continue
        for t in r['tags']:
            sc = axe_tag_to_sc(t)
            if sc in SC_LEVEL: cat[sc].add(r['ruleId'])
    return cat

def htmlcs_catalog():
    src = open('node_modules/html_codesniffer/Standards/WCAG2AA/ruleset.js').read()
    cat = collections.defaultdict(set)
    for m in re.finditer(r"'(Principle\d\.Guideline\d_\d\.(\d)_(\d)_(\d{1,2})[A-Za-z_]*)'", src):
        sc = f'{m.group(2)}.{m.group(3)}.{int(m.group(4))}'
        if sc in SC_LEVEL: cat[sc].add(m.group(1))
    return cat

# ---------- leitura por página
flag = {t: collections.defaultdict(set) for t in TOOLS}          # tool -> page -> set(SC)
instances = {t: collections.defaultdict(int) for t in TOOLS}       # tool -> page -> n instâncias de falha
review = {t: collections.defaultdict(int) for t in TOOLS}          # tool -> page -> n itens "revisar"
rules_hit = {t: collections.defaultdict(lambda: collections.defaultdict(int)) for t in TOOLS}  # tool -> page -> rule -> n
pair_rules = {t: collections.defaultdict(lambda: collections.defaultdict(int)) for t in TOOLS}  # tool -> (page,sc) -> rule -> n
unmapped = collections.defaultdict(collections.Counter)
outside = collections.defaultdict(collections.Counter)             # falhas fora do universo A/AA 2.1 (ex.: 2.2, AAA)
versions = {}
axe_rules_ref = None
missing = []

for pid in PAGES:
    for t in TOOLS:
        f = os.path.join(RAW, f'{pid}.{t}.json')
        if not os.path.exists(f):
            missing.append((pid, t)); continue
        d = json.load(open(f))
        if t == 'axe':
            versions['axe'] = d['version']; axe_rules_ref = axe_rules_ref or d['rules']
            for v in d['violations']:
                scs = {axe_tag_to_sc(x) for x in v['tags']} - {None}
                n = len(v['nodes']); rules_hit[t][pid][v['id']] += n
                inside = {s for s in scs if s in SC_LEVEL}
                for s in inside: flag[t][pid].add(s); pair_rules[t][(pid, s)][v['id']] += n
                for s in scs - inside: outside[t][s] += n
                if not scs: unmapped[t][v['id']] += n
                instances[t][pid] += n
            review[t][pid] = sum(len(v['nodes']) for v in d['incomplete'])
        elif t == 'lighthouse':
            versions['lighthouse'] = d['version']
            axe_map = {r['ruleId']: r['tags'] for r in (axe_rules_ref or [])}
            for aid, a in d['audits'].items():
                if a['scoreDisplayMode'] == 'binary' and a['score'] == 0:
                    n = a['items'] or 1; rules_hit[t][pid][aid] += n; instances[t][pid] += n
                    tags = axe_map.get(aid)
                    if tags is None: unmapped[t][aid] += n; continue
                    scs = {axe_tag_to_sc(x) for x in tags} - {None}
                    inside = {s for s in scs if s in SC_LEVEL}
                    for s in inside: flag[t][pid].add(s); pair_rules[t][(pid, s)][aid] += n
                    for s in scs - inside: outside[t][s] += n
                    if not scs: unmapped[t][aid] += n
                elif a['scoreDisplayMode'] == 'manual':
                    review[t][pid] += 1
        elif t == 'ibm':
            versions['ibm'] = d['version']; versions['ibm_archive'] = d.get('ruleArchive')
            for r in d['results']:
                if r['level'] == 'violation':
                    rules_hit[t][pid][r['ruleId']] += 1; instances[t][pid] += 1
                    scs = IBM_RULE_TO_SC.get(r['ruleId'])
                    if not scs: unmapped[t][r['ruleId']] += 1; continue
                    for s in scs: flag[t][pid].add(s); pair_rules[t][(pid, s)][r['ruleId']] += 1
                elif r['level'] == 'potentialviolation':
                    review[t][pid] += 1
        elif t == 'htmlcs':
            versions['htmlcs'] = d['version']; versions['pa11y'] = d['pa11y']
            for i in d['issues']:
                if i['type'] == 'error':
                    rules_hit[t][pid][i['code']] += 1; instances[t][pid] += 1
                    sc = htmlcs_code_to_sc(i['code'])
                    if sc is None: unmapped[t][i['code']] += 1
                    elif sc in SC_LEVEL: flag[t][pid].add(sc); pair_rules[t][(pid, sc)][i['code']] += 1
                    else: outside[t][sc] += 1
                else:
                    review[t][pid] += 1

pages_ok = [p for p in PAGES if all(os.path.exists(os.path.join(RAW, f'{p}.{t}.json')) for t in TOOLS)]
if missing: print('FALTANDO:', missing, file=sys.stderr)

# ---------- matriz página x SC x ferramenta (só páginas completas)
cells = [(p, s) for p in pages_ok for s in SCS]
M = {t: np.array([1 if s in flag[t][p] else 0 for (p, s) in cells]) for t in TOOLS}

def jaccard(a, b):
    inter = int(((a == 1) & (b == 1)).sum()); uni = int(((a == 1) | (b == 1)).sum())
    return (inter / uni if uni else None), inter, uni

def cohen_kappa(a, b):
    n = len(a); po = float((a == b).mean())
    pa1 = float(a.mean()); pb1 = float(b.mean())
    pe = pa1 * pb1 + (1 - pa1) * (1 - pb1)
    return (po - pe) / (1 - pe) if pe < 1 else None, po

def fleiss_kappa(mats):
    X = np.stack(mats, axis=1)  # N x raters
    N, k = X.shape
    n1 = X.sum(axis=1); n0 = k - n1
    P_i = (n1 * (n1 - 1) + n0 * (n0 - 1)) / (k * (k - 1))
    P_bar = P_i.mean()
    p1 = n1.sum() / (N * k); p0 = 1 - p1
    P_e = p1 ** 2 + p0 ** 2
    return float((P_bar - P_e) / (1 - P_e)) if P_e < 1 else None

pairwise = {}
for a, b in itertools.combinations(TOOLS, 2):
    j, inter, uni = jaccard(M[a], M[b]); k, po = cohen_kappa(M[a], M[b])
    pairwise[f'{a}|{b}'] = {'jaccard': j, 'intersecao': inter, 'uniao': uni, 'kappa_cohen': k, 'concordancia_observada': po,
                            'so_a': int(((M[a] == 1) & (M[b] == 0)).sum()), 'so_b': int(((M[a] == 0) & (M[b] == 1)).sum())}

union = np.zeros(len(cells), dtype=int)
for t in TOOLS: union |= M[t]
count_tools = sum(M[t] for t in TOOLS)
ENGINES = ['axe', 'ibm', 'htmlcs']
count_engines = sum(M[t] for t in ENGINES)

exclusive = {t: int(((M[t] == 1) & (count_tools == 1)).sum()) for t in TOOLS}
flagged_pairs = {t: int(M[t].sum()) for t in TOOLS}
distinct_sc = {t: sorted({s for p in pages_ok for s in flag[t][p]}, key=lambda s: tuple(int(x) for x in s.split('.'))) for t in TOOLS}

# por SC: quantas páginas cada ferramenta marcou
per_sc = []
for s in SCS:
    row = {'sc': s, 'nivel': SC_LEVEL[s]}
    for t in TOOLS: row[t] = sum(1 for p in pages_ok if s in flag[t][p])
    row['uniao'] = sum(1 for p in pages_ok if any(s in flag[t][p] for t in TOOLS))
    row['todas4'] = sum(1 for p in pages_ok if all(s in flag[t][p] for t in TOOLS))
    row['3engines'] = sum(1 for p in pages_ok if all(s in flag[t][p] for t in ENGINES))
    per_sc.append(row)

# por página
per_page = []
for p in pages_ok:
    row = {'pagina': p, 'sistema': PAGES[p]['system'], 'url': PAGES[p]['url']}
    for t in TOOLS:
        row[f'{t}_instancias'] = instances[t][p]; row[f'{t}_sc'] = len(flag[t][p]); row[f'{t}_revisar'] = review[t][p]
    row['sc_uniao'] = len(set().union(*[flag[t][p] for t in TOOLS]))
    row['sc_todas4'] = len(set.intersection(*[flag[t][p] for t in TOOLS])) if all(flag[t][p] for t in TOOLS) else 0
    row['sc_3engines'] = len(set.intersection(*[flag[t][p] for t in ENGINES])) if all(flag[t][p] for t in ENGINES) else 0
    per_page.append(row)

# por sistema
per_system = {}
for sysname in ('bold', 'dsgov'):
    ps = [p for p in pages_ok if PAGES[p]['system'] == sysname]
    per_system[sysname] = {'paginas': len(ps)}
    for t in TOOLS:
        per_system[sysname][f'{t}_instancias'] = sum(instances[t][p] for p in ps)
        per_system[sysname][f'{t}_pares'] = sum(len(flag[t][p]) for p in ps)
    per_system[sysname]['pares_uniao'] = sum(len(set().union(*[flag[t][p] for t in TOOLS])) for p in ps)

# cobertura potencial (catálogo)
cat_axe = axe_catalog(axe_rules_ref or []); cat_htmlcs = htmlcs_catalog()
cat_ibm = {s for s, lvl in SC_LEVEL.items() if any(s in v for v in IBM_RULE_TO_SC.values())}
lh_ids = set()
for pid in pages_ok:
    d = json.load(open(os.path.join(RAW, f'{pid}.lighthouse.json')))
    lh_ids |= {a['id'] for a in d['audits'].values() if a['scoreDisplayMode'] in ('binary', 'notApplicable')}
cat_lh = set()
for aid in lh_ids:
    for r in (axe_rules_ref or []):
        if r['ruleId'] == aid:
            cat_lh |= {axe_tag_to_sc(x) for x in r['tags']} - {None}
coverage = {'axe': sorted(cat_axe), 'lighthouse': sorted(s for s in cat_lh if s in SC_LEVEL), 'ibm': sorted(cat_ibm), 'htmlcs': sorted(cat_htmlcs)}
coverage_n = {t: len(v) for t, v in coverage.items()}
sc_no_tool = [s for s in SCS if not any(s in coverage[t] for t in TOOLS)]

# distribuição de concordância nos pares da união
dist = collections.Counter(int(c) for c in count_tools[union == 1])
dist_engines = collections.Counter(int(c) for c in count_engines[union == 1])

metrics = {
    'versoes': versions, 'paginas_completas': pages_ok, 'faltando': missing,
    'universo': {'criterios_A_AA_wcag21': len(SCS), 'celulas': len(cells)},
    'pares_marcados': flagged_pairs, 'criterios_distintos': {t: len(v) for t, v in distinct_sc.items()}, 'criterios_distintos_lista': distinct_sc,
    'instancias_total': {t: sum(instances[t].values()) for t in TOOLS}, 'revisar_total': {t: sum(review[t].values()) for t in TOOLS},
    'uniao_pares': int(union.sum()), 'todas4_pares': int((count_tools == 4).sum()), 'tres_engines_pares': int((count_engines == 3).sum()),
    'exclusivos': exclusive, 'distribuicao_n_ferramentas': dict(sorted(dist.items())), 'distribuicao_n_engines_entre_pares_da_uniao': dict(sorted(dist_engines.items())),
    'pairwise': pairwise, 'fleiss_kappa_4': fleiss_kappa([M[t] for t in TOOLS]), 'fleiss_kappa_3engines': fleiss_kappa([M[t] for t in ENGINES]),
    'por_sistema': per_system, 'cobertura_catalogo_n': coverage_n, 'cobertura_catalogo': coverage, 'criterios_sem_ferramenta': sc_no_tool,
    'fora_do_universo': {t: dict(c) for t, c in outside.items()}, 'nao_mapeados': {t: dict(c) for t, c in unmapped.items()},
    'regras_por_ferramenta': {t: dict(sorted(collections.Counter({r: sum(rules_hit[t][p][r] for p in pages_ok) for p in pages_ok for r in rules_hit[t][p]}).items(), key=lambda x: -x[1])) for t in TOOLS},
}
json.dump(metrics, open(os.path.join(OUT, 'metrics.json'), 'w'), indent=1, ensure_ascii=False)
with open(os.path.join(OUT, 'por_pagina.csv'), 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=list(per_page[0].keys())); w.writeheader(); w.writerows(per_page)
with open(os.path.join(OUT, 'por_criterio.csv'), 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=list(per_sc[0].keys())); w.writeheader(); w.writerows(per_sc)
with open(os.path.join(OUT, 'matriz_pagina_sc.csv'), 'w', newline='') as f:
    w = csv.writer(f); w.writerow(['pagina', 'sc'] + TOOLS + [f'{t}_regras' for t in TOOLS])
    for i, (p, s) in enumerate(cells):
        if union[i]: w.writerow([p, s] + [int(M[t][i]) for t in TOOLS] + ['; '.join(f'{r}={n}' for r, n in sorted(pair_rules[t][(p, s)].items())) for t in TOOLS])
# regras que geram pares exclusivos, por ferramenta
excl_rules = {t: collections.Counter() for t in TOOLS}
for i, (p, s) in enumerate(cells):
    if union[i] and count_tools[i] == 1:
        t = next(tt for tt in TOOLS if M[tt][i] == 1)
        for r in pair_rules[t][(p, s)]: excl_rules[t][f'{s}:{r}'] += 1
metrics['regras_dos_pares_exclusivos'] = {t: dict(c) for t, c in excl_rules.items()}
# critérios experimentais/desativados por padrão no axe (informativo)
metrics['axe_regras_experimentais'] = sorted(r['ruleId'] for r in (axe_rules_ref or []) if 'experimental' in r['tags'])
metrics['axe_regras_deprecated'] = sorted(r['ruleId'] for r in (axe_rules_ref or []) if 'deprecated' in r['tags'])
json.dump(metrics, open(os.path.join(OUT, 'metrics.json'), 'w'), indent=1, ensure_ascii=False)

# ---------- figuras
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 9})
# fig 1: pares (página, SC) por ferramenta e sistema
fig, ax = plt.subplots(figsize=(6.5, 3.2))
x = np.arange(len(TOOLS)); wdt = 0.38
b = [per_system['bold'][f'{t}_pares'] for t in TOOLS]; g = [per_system['dsgov'][f'{t}_pares'] for t in TOOLS]
ax.bar(x - wdt/2, b, wdt, label='Bold (%d páginas)' % per_system['bold']['paginas'], color='#2b6cb0')
ax.bar(x + wdt/2, g, wdt, label='DSGov (%d páginas)' % per_system['dsgov']['paginas'], color='#c53030')
for i in range(len(TOOLS)):
    ax.text(x[i] - wdt/2, b[i] + 0.3, str(b[i]), ha='center', fontsize=8); ax.text(x[i] + wdt/2, g[i] + 0.3, str(g[i]), ha='center', fontsize=8)
ax.set_xticks(x); ax.set_xticklabels([TOOL_LABEL[t] for t in TOOLS]); ax.set_ylabel('pares (página, critério) com falha'); ax.legend(frameon=False)
ax.spines[['top', 'right']].set_visible(False); fig.tight_layout(); fig.savefig(os.path.join(OUT, 'fig1_pares_por_ferramenta.png'), dpi=200); plt.close(fig)
# fig 2: matriz de concordância par a par (Jaccard)
fig, ax = plt.subplots(figsize=(4.6, 4))
J = np.ones((len(TOOLS), len(TOOLS)))
for i, a in enumerate(TOOLS):
    for j, bb in enumerate(TOOLS):
        if i != j:
            key = f'{a}|{bb}' if f'{a}|{bb}' in pairwise else f'{bb}|{a}'; J[i, j] = pairwise[key]['jaccard'] or 0
im = ax.imshow(J, cmap='Blues', vmin=0, vmax=1)
for i in range(len(TOOLS)):
    for j in range(len(TOOLS)):
        ax.text(j, i, f'{J[i, j]:.2f}', ha='center', va='center', color='white' if J[i, j] > 0.6 else 'black')
ax.set_xticks(range(len(TOOLS))); ax.set_yticks(range(len(TOOLS)))
ax.set_xticklabels([TOOL_LABEL[t] for t in TOOLS], rotation=30, ha='right'); ax.set_yticklabels([TOOL_LABEL[t] for t in TOOLS])
ax.set_title('Índice de Jaccard sobre pares (página, critério)', fontsize=9); fig.colorbar(im, ax=ax, fraction=0.046)
fig.tight_layout(); fig.savefig(os.path.join(OUT, 'fig2_jaccard.png'), dpi=200); plt.close(fig)
# fig 3: quantas ferramentas marcam cada par da união
fig, ax = plt.subplots(figsize=(5, 3))
ks = sorted(dist); vals = [dist[k] for k in ks]
ax.bar([str(k) for k in ks], vals, color='#4a5568')
for i, v in enumerate(vals): ax.text(i, v + 0.3, str(v), ha='center', fontsize=8)
ax.set_xlabel('número de ferramentas que marcam o mesmo par (página, critério)'); ax.set_ylabel('pares')
ax.spines[['top', 'right']].set_visible(False); fig.tight_layout(); fig.savefig(os.path.join(OUT, 'fig3_distribuicao_concordancia.png'), dpi=200); plt.close(fig)
# fig 4: heatmap critério x ferramenta (páginas marcadas), só critérios com alguma marcação
rows = [r for r in per_sc if r['uniao'] > 0]
fig, ax = plt.subplots(figsize=(5.2, 0.32 * len(rows) + 1.2))
H = np.array([[r[t] for t in TOOLS] for r in rows])
im = ax.imshow(H, cmap='Reds', vmin=0, vmax=max(1, H.max()))
for i in range(H.shape[0]):
    for j in range(H.shape[1]): ax.text(j, i, str(H[i, j]), ha='center', va='center', fontsize=8, color='white' if H[i, j] > H.max()*0.6 else 'black')
ax.set_xticks(range(len(TOOLS))); ax.set_xticklabels([TOOL_LABEL[t] for t in TOOLS], rotation=30, ha='right')
ax.set_yticks(range(len(rows))); ax.set_yticklabels([f"{r['sc']} ({r['nivel']})" for r in rows])
ax.set_title('Páginas com falha por critério e ferramenta (de %d)' % len(pages_ok), fontsize=9)
fig.tight_layout(); fig.savefig(os.path.join(OUT, 'fig4_criterio_ferramenta.png'), dpi=200); plt.close(fig)

print(json.dumps({k: metrics[k] for k in ['versoes', 'pares_marcados', 'criterios_distintos', 'instancias_total', 'revisar_total', 'uniao_pares', 'todas4_pares', 'tres_engines_pares', 'exclusivos', 'distribuicao_n_ferramentas', 'fleiss_kappa_4', 'fleiss_kappa_3engines', 'cobertura_catalogo_n', 'criterios_sem_ferramenta', 'nao_mapeados', 'fora_do_universo']}, indent=1, ensure_ascii=False))
print('pairwise:'); [print(' ', k, {kk: (round(vv, 3) if isinstance(vv, float) else vv) for kk, vv in v.items()}) for k, v in pairwise.items()]
print('páginas completas:', len(pages_ok), '| faltando:', len(missing))
