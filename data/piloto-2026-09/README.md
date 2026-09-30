# Reprodução de 30/09/2026 do piloto do Menu Push (DSGov)

Reexecução de `scripts/piloto-2026/audit_fork.py` sobre os mesmos arquivos `before/menu-push.html` e `after/menu-push.html` de `data/piloto-2026-07/`, no mesmo ambiente pinado (Chrome for Testing headless shell 142.0.7444.175, viewport 1366x900, axe-core 4.11.0 e 4.10.3 dos tarballs oficiais do npm), em 30/09/2026.

| Arquivo | axe-core 4.11.0 | axe-core 4.10.3 |
|---|---|---|
| before/menu-push.html | 22 nós (aria-required-parent 21, aria-required-children 1) | 22 nós (idêntico) |
| after/menu-push.html | 0 | 0 |

Resultado idêntico ao piloto de 30/07/2026. Exports completos nos quatro JSON desta pasta; hashes em `SHA256SUMS`.

```bash
cd scripts/piloto-2026
../reaudit-2026/.venv/bin/python audit_fork.py ../../data/piloto-2026-07/before/menu-push.html ../../data/piloto-2026-09/before
../reaudit-2026/.venv/bin/python audit_fork.py ../../data/piloto-2026-07/after/menu-push.html ../../data/piloto-2026-09/after
```
