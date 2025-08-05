#!/bin/bash

# Geo Processor - Development Script
# Este script configura o ambiente de desenvolvimento local

echo "🔧 Configurando ambiente de desenvolvimento..."

# Verificar Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 não encontrado. Por favor, instale Python 3.11 ou superior."
    exit 1
fi

# Criar ambiente virtual
if [ ! -d "venv" ]; then
    echo "🐍 Criando ambiente virtual Python..."
    python3 -m venv venv
fi

# Ativar ambiente virtual
echo "🔄 Ativando ambiente virtual..."
source venv/bin/activate

# Atualizar pip
echo "📦 Atualizando pip..."
pip install --upgrade pip

# Instalar dependências
echo "📥 Instalando dependências..."
pip install -r requirements.txt

# Criar arquivo .env se não existir
if [ ! -f .env ]; then
    echo "📝 Criando arquivo .env..."
    cp .env.example .env
fi

# Criar diretórios
echo "📁 Criando diretórios..."
mkdir -p uploads outputs logs

echo ""
echo "✅ Ambiente de desenvolvimento configurado!"
echo ""
echo "📋 Para desenvolver localmente:"
echo "   1. Ative o ambiente: source venv/bin/activate"
echo "   2. Inicie Redis: redis-server"
echo "   3. Inicie a API: python main.py"
echo "   4. Inicie worker: celery -A workers.tasks worker --loglevel=info"
echo ""
echo "📋 Para usar Docker:"
echo "   1. Execute: ./start.sh"
echo ""
echo "⚠️  Lembre-se de configurar o arquivo .env com suas credenciais!"
