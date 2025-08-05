#!/bin/bash

# 🛰️ ORTOTOOL - Script de Parada
# ===============================

echo "🛑 PARANDO ORTOTOOL..."
echo "====================="

# Verificar se docker está disponível
if ! command -v docker &> /dev/null; then
    echo "❌ Docker não encontrado."
    exit 1
fi

# Verificar se docker compose está disponível
if ! command -v docker compose &> /dev/null; then
    echo "❌ Docker Compose não encontrado."
    exit 1
fi

# Verificar se o arquivo existe
if [ ! -f "docker-compose-simple.yml" ]; then
    echo "❌ Arquivo docker-compose-simple.yml não encontrado!"
    exit 1
fi

# Parar todos os containers
echo "🔄 Parando containers..."
docker compose -f docker-compose-simple.yml down

# Remover containers órfãos
echo "🧹 Removendo containers órfãos..."
docker compose -f docker-compose-simple.yml down --remove-orphans

# Verificar se foram parados
if [ $? -eq 0 ]; then
    echo ""
    echo "✅ ORTOTOOL PARADO COM SUCESSO!"
    echo "==============================="
    echo ""
    echo "💡 COMANDOS ÚTEIS:"
    echo "   � Reiniciar:           ./start.sh"
    echo "   🧹 Limpar dados:        docker compose -f docker-compose-simple.yml down -v"
    echo "   👀 Ver containers:      docker ps -a"
    echo "   🔍 Ver logs salvos:     docker compose -f docker-compose-simple.yml logs"
    echo ""
else
    echo "❌ Erro ao parar os containers."
    echo "   Tente executar manualmente:"
    echo "   docker compose -f docker-compose-simple.yml down"
fi
