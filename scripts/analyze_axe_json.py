import json
import re
from collections import defaultdict
import os

# Paths (repo-relative: scripts/ -> ../data/axe/)
BASE = os.path.join(os.path.dirname(__file__), '..', 'data', 'axe')
DSGOV_PATH = os.path.join(BASE, 'teste-doc-dsgov-axe.json')
BOLD_PATH = os.path.join(BASE, 'teste-doc-bold-axe.json')

def parse_dsgov_component(title):
    # Format: "State change detected - Padrão Digital de Governo - [Component]"
    # or "Full page scan - Padrão Digital de Governo - [Component]"
    match = re.search(r'Padrão Digital de Governo - (.+)$', title)
    if match:
        name = match.group(1).strip()
        # Remove date if present " - 11/8/2025"
        name = re.sub(r' - \d{1,2}/\d{1,2}/\d{4}$', '', name)
        return name
    return "Unknown"

def parse_bold_component(url):
    # Format: .../components/[name]
    if '/components/' in url:
        parts = url.split('/components/')[-1].split('/')
        return parts[0].capitalize() # e.g. "button" -> "Button"
    return "Unknown"

def analyze_json(path, system_name):
    with open(path, 'r') as f:
        data = json.load(f)
    

    issues = data.get('allIssues', [])
    import sys
    print(f"DEBUG: Found {len(issues)} issues in {system_name}", file=sys.stderr)

    


    comp_counts = defaultdict(int)
    raw_comp_counts = defaultdict(int)
    rule_counts = defaultdict(int)
    rule_details = {}
    seen_violations = set()



    for issue in issues:
        rule_id = issue.get('ruleId')
        impact = issue.get('impact')
        
        # SANITIZATION: Deduplicate based on Rule + Selector + Component Context
        # We need to construct a unique key for this specific instance
        # If the JSON structure allows, we use 'nodes' list. If flattening, we iterate nodes.
        

        # Handle both nested 'nodes' (standard Axe) and flat 'allIssues' (DevTools export)
        nodes_list = issue.get('nodes')
        
        # If 'nodes' exists and is a list, iterate it.
        # Otherwise, treat the 'issue' itself as the node (flat format).
        if nodes_list and isinstance(nodes_list, list):
            items_to_process = nodes_list
            is_nested = True
        else:
            items_to_process = [issue]
            is_nested = False

        for node in items_to_process:
            # Selector: 'target' in standard, 'selector' in flat
            selector_list = node.get('target') or node.get('selector', [])
            selector = selector_list[0] if selector_list else ''
            
            # Context: Might be on parent 'issue' or current 'node'
            # In flat format, they are the same object.
            page_title = node.get('testPageTitle') or issue.get('testPageTitle', '')
            url_str = node.get('testUrl') or issue.get('testUrl', '')
            
            if system_name == 'DSGov':
                comp_name = parse_dsgov_component(page_title)

            else:
                comp_name = parse_bold_component(url_str)
            
            raw_comp_counts[comp_name] += 1

            




            # raw_comp_counts[comp_name] += 1 # Moved up or handled
            pass


            

            # DEBUG
            import sys
            print(f"DEBUG: System={system_name}, ParsedComp={comp_name}", file=sys.stderr)





            # FILTER: Exclude 'best-practice' or non-WCAG matches if strictly following AA.
            # Thesis says: "strict par with WCAG 2.1 AA".
            # Axe tags usually: ['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa', 'best-practice']
            tags = issue.get('tags', [])
            is_wcag = any('wcag' in t for t in tags)
            if not is_wcag:
                continue
            
            # EXPLICIT EXCLUSION: Thesis specifically removes AAA rules to reach the 202 count.
            # 'color-contrast-enhanced' is AAA.
            if rule_id in ['color-contrast-enhanced']:
                continue

            # DEDUPLICATION: "Global elements counted once"
            # We use RuleID + Selector as key.
            unique_key = f"{rule_id}|{selector}"
            
            # Count only unique occurrences
            if unique_key not in seen_violations:
                seen_violations.add(unique_key)

                
                # Count by Rule
                rule_counts[rule_id] += 1
                if rule_id not in rule_details:
                     rule_details[rule_id] = {'description': issue.get('help'), 'impact': impact}

                # Count by Component (First Attribution)
                # This approximates the "Component responsible" if the scan order is logical
                # or statistically distributes "Menu" errors to the first page scanned.
                # Ideally, we'd distinguish "Shell" vs "Content", but without DOM analysis this is best effort.
                comp_counts[comp_name] += 1




    import sys
    print(f"\nDEBUG: Raw component distribution for {system_name}:", file=sys.stderr)
    for name, count in sorted(raw_comp_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"  {name}: {count}", file=sys.stderr)
    print("--------------------------------------------------\n", file=sys.stderr)

    return comp_counts, rule_counts, rule_details


dsgov_comps, dsgov_rules, rule_info = analyze_json(DSGOV_PATH, 'DSGov')
bold_comps, bold_rules, _ = analyze_json(BOLD_PATH, 'Bold')

# Update rule info with any missing from Bold
for r in bold_rules:
    if r not in rule_info:
        # We need to find the description for this rule in bold file, 
        # but for simplicity assume dsgov covers most. 
        # If strictly needed, I'd read it from bold too.
        rule_info[r] = {'description': r, 'impact': 'unknown'}

# --- TABLE A: Componentes ---
# Find intersection of components or just list all
all_comps = sorted(list(set(dsgov_comps.keys()) | set(bold_comps.keys())))

print("--- TABLE A LATEX CONTENT ---")
print("\\begin{tabular}{@{}llcc@{}}")
print("\\toprule")
print("\\textbf{Componente} & \textbf{DSGov (Manual)} & \textbf{Bold (Encapsulado)} & \textbf{Redução} \\\\ \\midrule")

# Specific components manual check to mapping names if they differ?
# Assuming names are relatively similar (e.g. Button vs Button).
# DSGov might be "Botão"? No, the JSON said "Button".

for comp in all_comps:
    # Filter for common components usually found in Design Systems
    # to avoid noise if the list is huge
    if dsgov_comps[comp] == 0 and bold_comps[comp] == 0:
        continue
        
    ds_count = dsgov_comps.get(comp, 0)
    bd_count = bold_comps.get(comp, 0)
    
    diff_pct = "-"
    if ds_count > 0:
        reduction = ((ds_count - bd_count) / ds_count) * 100
        diff_pct = f"{reduction:.0f}\\%"
    elif bd_count > 0:
        diff_pct = "+100\\%" # Increase
        
    # Highlighting significant ones
    row = f"{comp} & {ds_count} & {bd_count} & {diff_pct} \\\\"
    print(row)

print("\\bottomrule")
print("\\end{tabular}")
print("\n")

# --- TABLE B: Top Rules ---
# We will list Top 10 rules from DSGov and show their status in Bold

sorted_rules = sorted(dsgov_rules.items(), key=lambda x: x[1], reverse=True)[:10]

print("--- TABLE B LATEX CONTENT ---")
print("\\begin{tabular}{@{}lp{8cm}cc@{}}") # Check column width
print("\\toprule")
print("\\textbf{Regra (ID)} & \textbf{Descrição do Erro} & \textbf{DSGov} & \textbf{Bold} \\\\ \\midrule")

for rule_id, count in sorted_rules:
    desc = rule_info.get(rule_id, {}).get('description', rule_id)
    bd_count = bold_rules.get(rule_id, 0)
    print(f"\\texttt{{{rule_id}}} & {desc} & {count} & {bd_count} \\\\")

print("\\bottomrule")
print("\\end{tabular}")
