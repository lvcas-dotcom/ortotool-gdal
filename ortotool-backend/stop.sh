#!/bin/bash

# 🛰️ ORTOTOOL - Script de Finalização
# ================================================

echo "🛰️ ENCERRANDO ORTOTOOL - Sistema de Processamento de Ortomosaicos"
echo "================================================================="

# Verificar se Docker está disponível
if ! command -v docker &> /dev/null; then
    echo "❌ Docker não encontrado. Instale o Docker primeiro."
    exit 1
fi

if ! command -v docker compose &> /dev/null; then
    echo "❌ Docker Compose não encontrado. Instale o Docker Compose primeiro."
    exit 1
fi

echo "🛑 Parando todos os containers..."
docker compose -f docker-compose-simple.yml down

echo "🧹 Removendo containers órfãos..."
docker compose -f docker-compose-simple.yml down --remove-orphans

echo "📊 Verificando containers restantes..."
docker ps --filter "name=ortotool" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

echo ""
echo "🎯 ORTOTOOL ENCERRADO COM SUCESSO!"
echo "================================="
echo ""
echo "💡 Para reiniciar o sistema:"
echo "   ./scripts/start.sh"
echo ""
echo "🔧 Para limpeza completa (remove volumes):"
echo "   docker compose -f docker-compose-simple.yml down -v"
echo ""