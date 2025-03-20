#!/bin/bash
# Script de instalação do UCAN

set -e

# Diretório do script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

echo "===== Instalando UCAN ====="
echo "Diretório do projeto: $PROJECT_DIR"

# Verificar se o Poetry está instalado
if ! command -v poetry &> /dev/null; then
    echo "Poetry não encontrado. Instalando..."
    curl -sSL https://install.python-poetry.org | python3 -
fi

# Entrar no diretório do projeto
cd "$PROJECT_DIR"

# Instalar as dependências
echo "Instalando dependências..."
poetry install

# Criar diretório de cache e conversas
echo "Criando diretórios de dados..."
mkdir -p ~/.ucan/cache
mkdir -p ~/.ucan/conversations
mkdir -p ~/.ucan/logs

# Criar arquivo .env se não existir
if [ ! -f "$PROJECT_DIR/.env" ]; then
    echo "Criando arquivo .env..."
    cp "$PROJECT_DIR/.env.example" "$PROJECT_DIR/.env"
    echo "Por favor, edite o arquivo .env com suas configurações."
fi

# Criar ícones do aplicativo se não existirem
ICONS_DIR="$PROJECT_DIR/ucan/resources/icons"
if [ ! -d "$ICONS_DIR" ]; then
    echo "Criando diretório de ícones..."
    mkdir -p "$ICONS_DIR"
    # Aqui você pode adicionar comandos para baixar ícones padrão
fi

echo "===== Instalação completa! ====="
echo "Para executar o aplicativo, use: poetry run ucan" 