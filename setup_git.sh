#!/usr/bin/env bash
# setup_git.sh — inicializa o repositório e instala o hook de pre-commit com ruff
# Execute UMA VEZ na raiz do projeto: bash setup_git.sh

set -e

echo "▶ Inicializando repositório git..."
git init

echo "▶ Instalando hook de pre-commit (ruff)..."

mkdir -p .git/hooks

cat > .git/hooks/pre-commit << 'HOOK'
#!/usr/bin/env bash
# Hook de pre-commit: bloqueia o commit se ruff encontrar erros.
# Para pular em emergência (não recomendado): git commit --no-verify

set -e

echo "🔍 Rodando ruff check..."
if ! ruff check .; then
    echo ""
    echo "❌ ruff encontrou erros. Commit bloqueado."
    echo "   Corrija com: ruff check . --fix && ruff format ."
    echo "   Depois: git add . && git commit -m '...'"
    exit 1
fi

echo "✅ ruff check passou — commit autorizado."
HOOK

chmod +x .git/hooks/pre-commit

echo "▶ Verificando .gitignore..."
if ! grep -q "^\.env$" .gitignore 2>/dev/null; then
    echo "⚠️  .gitignore não encontrado ou sem entrada '.env'. Verifique antes de prosseguir."
    exit 1
fi

echo "▶ Primeiro commit..."
git add .
git status

echo ""
echo "──────────────────────────────────────────────"
echo "Revise os arquivos acima. .env NÃO deve aparecer."
echo "Se estiver tudo certo, execute:"
echo "  git commit -m 'chore: estrutura inicial do projeto'"
echo "──────────────────────────────────────────────"
