#!/bin/bash

# 🛰️ ORTOTOOL - Script de Inicialização Simplificada
# =====================================================

echo "🛰️ INICIANDO ORTOTOOL - Sistema de Processamento de Ortomosaicos"
echo "================================================================="

# Verificar se Docker está instalado
if ! command -v docker &> /dev/null; then
    echo "❌ Docker não encontrado. Por favor, instale o Docker primeiro."
    echo "   Visite: https://docs.docker.com/get-docker/"
    exit 1
fi

# Verificar se Docker Compose está disponível (plugin ou standalone)
if ! docker compose version &> /dev/null && ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose não encontrado. Por favor, instale o Docker Compose."
    echo "   Visite: https://docs.docker.com/compose/install/"
    exit 1
fi

echo "✅ Docker e Docker Compose encontrados"

# Ir para o diretório do projeto
cd /home/lucas-ti/Documentos/ortotool/geo-processor

# Verificar se o arquivo docker-compose existe
if [ ! -f "docker-compose-simple.yml" ]; then
    echo "❌ Arquivo docker-compose-simple.yml não encontrado!"
    echo "   Certifique-se de que está no diretório correto do projeto."
    exit 1
fi

echo "✅ Arquivo de configuração encontrado"

# Criar diretórios necessários
echo "📁 Criando diretórios necessários..."
mkdir -p {uploads,outputs,logs}
mkdir -p data/{postgres,minio}

# Definir comando do compose (plugin ou standalone)
COMPOSE_CMD="docker compose"
if ! docker compose version &> /dev/null; then
    COMPOSE_CMD="docker-compose"
fi

# Parar containers existentes (se houver)
echo "🛑 Parando containers existentes..."
$COMPOSE_CMD -f docker-compose-simple.yml down

# Construir e iniciar os serviços
echo "🔨 Construindo e iniciando os serviços..."
$COMPOSE_CMD -f docker-compose-simple.yml up --build -d

# Aguardar inicialização
echo "⏳ Aguardando inicialização dos serviços..."
sleep 30

# Verificar status dos containers
echo "📊 Verificando status dos serviços..."
$COMPOSE_CMD -f docker-compose-simple.yml ps

echo ""
echo "🎉 ORTOTOOL INICIADO COM SUCESSO!"
echo "================================="
echo ""
echo "🌐 Interface Principal: http://localhost:8000"
echo "📚 Documentação API:    http://localhost:8000/docs"
echo "🌺 Monitor Celery:      http://localhost:5555"
echo "📊 Status do Sistema:   http://localhost:8000/health"
echo ""
echo "💡 COMO USAR:"
echo "   1. Acesse http://localhost:8000 para ver a interface"
echo "   2. Use a documentação em /docs para entender as APIs"
echo "   3. Faça upload de seus ortomosaicos e processe!"
echo ""
echo "🔧 COMANDOS ÚTEIS:"
echo "   • Ver logs:     $COMPOSE_CMD -f docker-compose-simple.yml logs -f"
echo "   • Parar tudo:   $COMPOSE_CMD -f docker-compose-simple.yml down"
echo "   • Reiniciar:    ./scripts/start.sh"
echo ""
echo "📞 SUPORTE:"
echo "   Se encontrar problemas, verifique os logs dos containers"
echo "   e certifique-se de que as portas 8000 e 5555 estão livres."
echo ""
