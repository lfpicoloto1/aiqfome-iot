#!/bin/bash
# Atualiza o projeto no Pi sem merge manual (usa versão do GitHub).
set -e
cd "$(dirname "$0")/.."
echo ">>> Pasta: $(pwd)"

if git rev-parse --git-dir >/dev/null 2>&1; then
    echo ">>> Abortando merge pendente (se houver)..."
    git merge --abort 2>/dev/null || true

    echo ">>> Baixando do GitHub..."
    git fetch origin

    echo ">>> Aplicando versão remota (descarta mudanças locais)..."
    git reset --hard origin/main

    echo ">>> OK. Versão atual:"
    git log -1 --oneline
else
    echo "ERRO: não é um repositório git."
    exit 1
fi

if [ -d .venv ]; then
    echo ">>> Atualizando dependências..."
    .venv/bin/pip install -q -r requirements.txt
fi

echo ""
echo "Pronto! Teste com:"
echo "  source .venv/bin/activate"
echo "  python3 -m src.main --backend fbdev --fbdev /dev/fb1"
