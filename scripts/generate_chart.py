import matplotlib.pyplot as plt
import numpy as np

# Data (approximate based on JSON summaries I saw)
# DSGov: Critical 202, Serious 527, Moderate 4, Minor 12
# Bold: Critical 4, Serious 67, Moderate 9, Minor 0
# (These numbers are from the head of the files I viewed earlier)

categories = ['Crítico', 'Sério', 'Moderado', 'Menor']
dsgov_values = [202, 527, 4, 12]
bold_values = [4, 67, 9, 0]

x = np.arange(len(categories))
width = 0.35

fig, ax = plt.subplots(figsize=(8, 5))
rects1 = ax.bar(x - width/2, dsgov_values, width, label='DSGov (Manual)', color='#b03030')
rects2 = ax.bar(x + width/2, bold_values, width, label='Bold (Encapsulado)', color='#2d5f8b')

ax.set_ylabel('Quantidade de Violações')
ax.set_title('Distribuição de Violações por Severidade (Axe-core)')
ax.set_xticks(x)
ax.set_xticklabels(categories)
ax.legend()

ax.bar_label(rects1, padding=3)
ax.bar_label(rects2, padding=3)

fig.tight_layout()

plt.savefig('/Users/thiagoxikota/Documents/academic/Writing/Papers/Acessibilidade_Design_Systems_Publicos/figures/severity_dist.png')
print("Chart saved.")
