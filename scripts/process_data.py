import json
import os

def load_json(filepath):
    try:
        with open(filepath, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading {filepath}: {e}")
        return {}

def process_files():
    files = {
        'Bold': ['teste-doc-bold-axe.json', 'testes-especificos-bold-axe.json'],
        'DSGov': ['teste-doc-dsgov-axe.json', 'testes-especificos-dsgov-axe.json']
    }
    
    # Store processed data
    # Structure: system -> list of dicts
    processed_data = {
        'Bold': [],
        'DSGov': []
    }
    
    # Track unique violations to avoid duplicates
    # Set of (ruleId, selector_str)
    unique_tracker = {
        'Bold': set(),
        'DSGov': set()
    }

    for system, file_list in files.items():
        for filename in file_list:
            if not os.path.exists(filename):
                print(f"File not found: {filename}")
                continue
            
            content = load_json(filename)
            
            # Determine where the issues are
            issues = []
            if 'allIssues' in content:
                issues = content['allIssues']
            elif 'violations' in content:
                # If using raw Axe output, violations is the key
                # But we need to flatten it
                for v in content['violations']:
                    for node in v.get('nodes', []):
                        issues.append({
                            'ruleId': v.get('id'),
                            'description': v.get('description'),
                            'help': v.get('help'),
                            'helpUrl': v.get('helpUrl'),
                            'impact': v.get('impact'),
                            'selector': node.get('target'), # target is list of selectors
                            'source': node.get('html')
                        })
            
            for issue in issues:
                rule_id = issue.get('ruleId') or issue.get('id')
                description = issue.get('description') or issue.get('help')
                impact = issue.get('impact')
                help_url = issue.get('helpUrl')
                
                # Normalize selector
                selectors = issue.get('selector') or issue.get('target') or []
                if isinstance(selectors, list) and len(selectors) > 0:
                    # Use the first selector as the primary key
                    primary_selector = selectors[0]
                elif isinstance(selectors, str):
                    primary_selector = selectors
                else:
                    primary_selector = "Unknown"
                
                # Deduplicate
                key = (rule_id, primary_selector)
                if key not in unique_tracker[system]:
                    unique_tracker[system].add(key)
                    processed_data[system].append({
                        'ruleId': rule_id,
                        'description': description,
                        'impact': impact,
                        'helpUrl': help_url,
                        'selector': primary_selector
                    })

    return processed_data

def generate_markdown(data, scores):
    md = "# Relatório Unificado de Acessibilidade\n\n"
    
    # 1. Visão Geral Comparativa
    md += "## 1. Visão Geral Comparativa\n\n"
    md += "| Métrica | Bold | DSGov |\n"
    md += "|---|---|---|\n"
    md += f"| Pontuação de Acessibilidade (Lighthouse) | {scores.get('Bold', 'N/A')} | {scores.get('DSGov', 'N/A')} |\n"
    md += f"| Total de Violações Únicas (Axe) | {len(data['Bold'])} | {len(data['DSGov'])} |\n"
    
    # Top Categories
    md += "| Principais Categorias de Erro | "
    for system in ['Bold', 'DSGov']:
        cats = {}
        for issue in data[system]:
            # Infer category from ruleId or description keywords if needed
            # Axe rule IDs often have prefixes like 'aria-', 'color-', 'html-'
            # We'll use the prefix before the first hyphen
            rid = issue['ruleId']
            cat = rid.split('-')[0] if '-' in rid else rid
            cats[cat] = cats.get(cat, 0) + 1
        
        # Sort by count
        top_cats = sorted(cats.items(), key=lambda x: x[1], reverse=True)[:3]
        cat_str = ", ".join([f"{k} ({v})" for k, v in top_cats])
        md += f"{cat_str} | "
    md += "\n\n"
    
    # 2. Detalhamento Técnico
    for system in ['Bold', 'DSGov']:
        md += f"## 2. Detalhamento Técnico: {system}\n\n"
        md += "### Tabela de Violações\n\n"
        md += "| Regra (ID) | Descrição | Impacto | Qtd. Ocorrências | Elementos (Amostra de Seletores) | Link Evidência |\n"
        md += "|---|---|---|---|---|---|\n"
        
        # Group by ruleId
        grouped = {}
        for issue in data[system]:
            rid = issue['ruleId']
            if rid not in grouped:
                grouped[rid] = {
                    'description': issue['description'],
                    'impact': issue['impact'],
                    'helpUrl': issue['helpUrl'],
                    'selectors': []
                }
            grouped[rid]['selectors'].append(issue['selector'])
            
        # Sort by impact (Critical > Serious > Moderate > Minor)
        impact_order = {'critical': 0, 'serious': 1, 'moderate': 2, 'minor': 3, None: 4}
        sorted_rules = sorted(grouped.items(), key=lambda x: impact_order.get(x[1]['impact'], 4))
        
        for rid, info in sorted_rules:
            count = len(info['selectors'])
            # Take up to 2 samples, truncate if too long
            samples = info['selectors'][:2]
            sample_str = ", ".join([f"`{s}`" for s in samples])
            if count > 2:
                sample_str += ", ..."
            
            # Escape pipes in description
            desc = info['description'].replace('|', '\|') if info['description'] else "N/A"
            
            md += f"| {rid} | {desc} | {info['impact']} | {count} | {sample_str} | [Link]({info['helpUrl']}) |\n"
        
        md += "\n"

    # Calculate Severity Counts
    print("\n--- Severity Counts ---")
    for system in ['Bold', 'DSGov']:
        severity_counts = {'critical': 0, 'serious': 0, 'moderate': 0, 'minor': 0}
        for issue in data[system]:
            impact = issue.get('impact')
            if impact in severity_counts:
                severity_counts[impact] += 1
        print(f"{system}: {severity_counts}")
    print("-----------------------\n")

    return md

if __name__ == "__main__":
    scores = {'Bold': '98', 'DSGov': '92'}
    data = process_files()
    report = generate_markdown(data, scores)
    
    with open('relatorio_acessibilidade.md', 'w') as f:
        f.write(report)
    print("Report generated: relatorio_acessibilidade.md")
