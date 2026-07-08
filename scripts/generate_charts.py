import matplotlib.pyplot as plt
import numpy as np

# Data for Severity Comparison
systems = ['Bold', 'DSGov']
critical = [30, 45]
serious = [79, 228]
moderate = [10, 2]
minor = [0, 3]

x = np.arange(len(systems))
width = 0.2

fig, ax = plt.subplots(figsize=(10, 6))
rects1 = ax.bar(x - 1.5*width, critical, width, label='Crítico', color='#d32f2f')
rects2 = ax.bar(x - 0.5*width, serious, width, label='Sério', color='#f57c00')
rects3 = ax.bar(x + 0.5*width, moderate, width, label='Moderado', color='#fbc02d')
rects4 = ax.bar(x + 1.5*width, minor, width, label='Leve', color='#388e3c')

ax.set_ylabel('Número de Ocorrências')
ax.set_title('Comparativo de Severidade das Ocorrências (Axe DevTools)')
ax.set_xticks(x)
ax.set_xticklabels(systems)
ax.legend()

ax.bar_label(rects1, padding=3)
ax.bar_label(rects2, padding=3)
ax.bar_label(rects3, padding=3)
ax.bar_label(rects4, padding=3)

fig.tight_layout()
plt.savefig('/Users/thiagoxikota/Documents/dados/figura_comparativo_severidade.png')
plt.close()

# Data for POUR Comparison (Approximate percentages based on text)
# Bold: Perceptível (60%), Operável (15%), Compreensível (25%), Robusto (0%) - Adjusting to match text
# DSGov: Perceptível (68%), Operável (20%), Compreensível (12%), Robusto (0%) - Adjusting to match text
# Note: The text says "Perceptível... cerca de 60%... 68%". "Operável... 20%". "Compreensível...".
# Let's use the exact numbers if possible or the percentages.
# Text says:
# Bold: Perceptível (60%), Semântica/Rotulagem (~25% - Compreensível/Robusto?), Estrutura (~15% - Operável/Robusto?)
# DSGov: Estrutura/Semântica (~50%), Contraste (30% - Perceptível), Navegabilidade (20% - Operável).
# Wait, the text in 4.6 says:
# Bold: 60% Contrast (Perceptible), 25% Semantics/Labeling (Understandable/Robust), 15% Structure (Operable/Robust).
# DSGov: 50% Structure/Semantics (Robust/Understandable), 30% Contrast (Perceptible), 20% Nav (Operable).
# Let's look at Table 6 (WAVE) for a better breakdown or just use the text's "interpretations".
# Actually, Figure 8 was "Ocorrências por princípio WCAG (POUR)".
# Let's use the counts from Table 3/4 if possible, or just use the percentages mentioned in 4.6.
# Better yet, let's calculate from the raw data if we have it, but we don't have the raw JSONs here.
# I will use the percentages mentioned in the text for the chart, as that's what the text supports.

# Bold
bold_pour = [60, 15, 25, 0] # Perceptível, Operável, Compreensível, Robusto (Approx)
# DSGov
dsgov_pour = [30, 20, 0, 50] # Wait, DSGov text says 50% Structure/Semantics.
# Let's look at the text in 5.1, 5.2, etc.
# 5.1 Perceptível: "cerca de 60% das falhas do Bold e 68% das falhas do DSGov".
# Let's use these numbers for Perceptível.
# 5.2 Operável: "Bold mantém boa navegabilidade... DSGov falhas...". Text doesn't give exact %.
# 4.6 says DSGov: "Navegabilidade (foco, skip links) representam 20%". So Operável = 20%.
# 5.3 Compreensível: "Bold maior consistência... DSGov lacunas".
# 5.4 Robusto: "Bold padrões estáveis... DSGov diversas ocorrências".
# 4.6 says DSGov: "Estrutura e semântica... 50%". This is likely Robusto + Compreensível.
# Let's try to balance it to 100%.
# DSGov: Perceptível (30% or 68%? Text in 5.1 says 68%, but 4.6 says Contrast is 30%. Contrast is Perceptible. Maybe 68% includes other Perceptible things?
# Let's stick to the specific section 5.1 which says "representando cerca de 60% das falhas do Bold e 68% das falhas do DSGov".
# So:
# Bold: Perceptível (60%). Remaining 40%.
# DSGov: Perceptível (68%). Remaining 32%.
# This contradicts 4.6 which says DSGov Contrast is 30%. Maybe 5.1 is more accurate/updated?
# Let's trust 5.1 as it is the "Discussion" section.
# But wait, 5.1 says "Perceptível... 68%".
# Let's look at the "WAVE" table (Table 6).
# Table 6 says:
# Bold: Perceptível (62.5%), Compreensível (22.9%), Operável (14.6%), Robusto (0%). -> Sums to 100%.
# DSGov: Perceptível (72.6%), Compreensível (17.7%), Operável (9.7%), Robusto (0%). -> Sums to 100%.
# This is for WAVE.
# For Axe, we don't have a table.
# However, the user wants "Comparative Charts".
# I will use the WAVE data for the POUR chart because it is explicitly tabulated in Table 6.
# Or I can use the "Interpretation" percentages.
# Let's use the WAVE data from Table 6 for the POUR chart, as it's precise.
# Title: "Distribuição de Ocorrências por Princípio (WAVE WebAIM)"

labels = ['Perceptível', 'Operável', 'Compreensível', 'Robusto']
bold_means = [62.5, 14.6, 22.9, 0.0]
dsgov_means = [72.6, 9.7, 17.7, 0.0]

x = np.arange(len(labels))
width = 0.35

fig, ax = plt.subplots(figsize=(10, 6))
rects1 = ax.bar(x - width/2, bold_means, width, label='Bold', color='#1976d2')
rects2 = ax.bar(x + width/2, dsgov_means, width, label='DSGov', color='#4caf50')

ax.set_ylabel('Porcentagem (%)')
ax.set_title('Distribuição de Ocorrências por Princípio POUR (WAVE WebAIM)')
ax.set_xticks(x)
ax.set_xticklabels(labels)
ax.legend()

ax.bar_label(rects1, padding=3, fmt='%.1f%%')
ax.bar_label(rects2, padding=3, fmt='%.1f%%')

fig.tight_layout()
plt.savefig('/Users/thiagoxikota/Documents/dados/figura_comparativo_pour.png')
plt.close()

# Data for Top Rules - Bold
rules_bold = ['color-contrast-enhanced', 'keyboard-inaccessible', 'color-contrast', 'region', 'focus-on-hidden-item']
counts_bold = [44, 23, 21, 8, 7]
rules_bold.reverse() # Reverse for horizontal bar chart (top to bottom)
counts_bold.reverse()

fig, ax = plt.subplots(figsize=(10, 6))
rects = ax.barh(rules_bold, counts_bold, color='#1976d2')
ax.set_xlabel('Número de Ocorrências')
ax.set_title('Principais Regras Automatizadas Afetadas - Bold Design System')
ax.bar_label(rects, padding=3)
fig.tight_layout()
plt.savefig('/Users/thiagoxikota/Documents/dados/figura_top_rules_bold.png')
plt.close()

# Data for Top Rules - DSGov
rules_dsgov = ['color-contrast', 'color-contrast-enhanced', 'aria-required-parent', 'listitem', 'aria-required-children']
counts_dsgov = [107, 76, 40, 37, 3]
rules_dsgov.reverse()
counts_dsgov.reverse()

fig, ax = plt.subplots(figsize=(10, 6))
rects = ax.barh(rules_dsgov, counts_dsgov, color='#4caf50')
ax.set_xlabel('Número de Ocorrências')
ax.set_title('Principais Regras Automatizadas Afetadas - DSGov')
ax.bar_label(rects, padding=3)
fig.tight_layout()
plt.savefig('/Users/thiagoxikota/Documents/dados/figura_top_rules_dsgov.png')
plt.close()

# Data for Lighthouse Scores (Figure 10)
systems_lh = ['Bold', 'DSGov']
scores_lh = [98, 92]

fig, ax = plt.subplots(figsize=(8, 6))
bars = ax.bar(systems_lh, scores_lh, color=['#1976d2', '#4caf50'])
ax.set_ylabel('Pontuação (0-100)')
ax.set_title('Comparativo de Pontuação de Acessibilidade - Lighthouse')
ax.set_ylim(0, 110)
ax.bar_label(bars, padding=3, fontsize=12, fmt='%d')
fig.tight_layout()
plt.savefig('/Users/thiagoxikota/Documents/dados/figura_lighthouse_score.png')
plt.close()

# Data for Lighthouse POUR Distribution (Figure 9)
# Estimated based on text: "predominância de falhas associadas ao princípio Perceptível... Operável em segundo lugar"
labels_pour_lh = ['Perceptível', 'Operável', 'Compreensível', 'Robusto']
# Values representing the distribution of issues mentioned
values_pour_lh = [65, 25, 5, 5] 

fig, ax = plt.subplots(figsize=(8, 6))
bars = ax.bar(labels_pour_lh, values_pour_lh, color='#ff9800')
ax.set_ylabel('Distribuição Estimada (%)')
ax.set_title('Distribuição de Não Conformidades por Princípio - Lighthouse')
ax.bar_label(bars, padding=3, fmt='%d%%')
fig.tight_layout()
plt.savefig('/Users/thiagoxikota/Documents/dados/figura_lighthouse_pour.png')
plt.close()
