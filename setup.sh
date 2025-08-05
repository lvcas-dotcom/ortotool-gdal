#!/bin/bash

# 🛰️ ORTOTOOL - Script de Inicialização Automática
# ================================================
# Este script automatiza a inicialização completa do ORTOTOOL
# Inicia tanto o backend (FastAPI) quanto o frontend (Next.js)

set -e  # Parar execução se houver erro

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

# Função para imprimir mensagens coloridas
print_status() {
    echo -e "${BLUE}[ORTOTOOL]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "${PURPLE}"
    echo "🛰️  =============================================="
    echo "    ORTOTOOL - Sistema de Processamento"
    echo "    de Ortomosaicos Georreferenciados"
    echo "=============================================="
    echo -e "${NC}"
}

# Função para verificar se um processo está rodando
check_process() {
    local port=$1
    if lsof -i:$port > /dev/null 2>&1; then
        return 0
    else
        return 1
    fi
}

# Função para parar processos existentes
stop_existing_processes() {
    print_status "Verificando processos existentes..."
    
    # Parar backend (porta 8000)
    if check_process 8000; then
        print_warning "Backend já está rodando na porta 8000. Parando..."
        pkill -f "uvicorn.*main:app" || true
        sleep 2
    fi
    
    # Parar frontend (portas 3000/3001)
    if check_process 3000; then
        print_warning "Frontend já está rodando na porta 3000. Parando..."
        pkill -f "next.*dev" || true
        sleep 2
    fi
    
    if check_process 3001; then
        print_warning "Frontend já está rodando na porta 3001. Parando..."
        pkill -f "next.*dev" || true
        sleep 2
    fi
}

# Função para verificar dependências do sistema
check_system_dependencies() {
    print_status "Verificando dependências do sistema..."
    
    # Verificar Python3
    if ! command -v python3 &> /dev/null; then
        print_error "Python3 não encontrado. Instale com: sudo apt install python3"
        exit 1
    fi
    
    # Verificar Node.js
    if ! command -v node &> /dev/null; then
        print_error "Node.js não encontrado. Instale com: sudo apt install nodejs npm"
        exit 1
    fi
    
    # Verificar GDAL
    if ! command -v gdal-config &> /dev/null; then
        print_error "GDAL não encontrado. Execute primeiro:"
        echo "  sudo apt update"
        echo "  sudo apt install gdal-bin libgdal-dev python3-gdal"
        exit 1
    fi
    
    print_success "Dependências do sistema verificadas"
}

# Função para configurar o backend
setup_backend() {
    print_status "Configurando backend..."
    
    cd ortotool-backend
    
    # Verificar se requirements estão instalados
    if ! python3 -c "import fastapi, uvicorn, rasterio" &> /dev/null; then
        print_status "Instalando dependências Python..."
        pip3 install fastapi==0.104.1 "uvicorn[standard]==0.24.0" celery==5.3.4 redis==5.0.1 \
                     sqlalchemy==2.0.23 rasterio==1.3.9 geopandas==0.14.1 shapely==2.0.2 \
                     pyproj==3.6.1 fiona==1.9.5 python-multipart==0.0.6 aiofiles==23.2.0 \
                     pydantic==2.5.0 pydantic-settings==2.1.0 GDAL==3.4.1 || {
            print_error "Falha ao instalar dependências Python"
            exit 1
        }
    fi
    
    # Criar diretórios necessários
    mkdir -p uploads outputs logs data storage
    
    print_success "Backend configurado"
    cd ..
}

# Função para configurar o frontend
setup_frontend() {
    print_status "Configurando frontend..."
    
    cd ortotool-frontend
    
    # Verificar se node_modules existe
    if [ ! -d "node_modules" ]; then
        print_status "Instalando dependências do frontend..."
        npm install || {
            print_error "Falha ao instalar dependências do frontend"
            exit 1
        }
    fi
    
    # Verificar se .env.local existe
    if [ ! -f ".env.local" ]; then
        print_status "Criando arquivo de configuração..."
        cat > .env.local << EOF
# Environment variables for ORTOTOOL Frontend
# API Configuration
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1

# Map Configuration (when implemented)
NEXT_PUBLIC_MAP_PROVIDER=openstreetmap
NEXT_PUBLIC_MAP_API_KEY=your-api-key-here

# Development
NODE_ENV=development
EOF
    fi
    
    print_success "Frontend configurado"
    cd ..
}

# Função para iniciar o backend
start_backend() {
    print_status "Iniciando backend..."
    
    cd ortotool-backend
    
    # Iniciar backend em background
    PYTHONPATH=$(pwd) nohup python3 -m uvicorn main:app --reload --host 0.0.0.0 --port 8000 \
        > ../logs/backend.log 2>&1 &
    
    BACKEND_PID=$!
    echo $BACKEND_PID > ../logs/backend.pid
    
    cd ..
    
    # Aguardar backend inicializar
    print_status "Aguardando backend inicializar..."
    for i in {1..30}; do
        if check_process 8000; then
            print_success "Backend iniciado com sucesso (PID: $BACKEND_PID)"
            return 0
        fi
        sleep 1
    done
    
    print_error "Timeout ao iniciar backend"
    return 1
}

# Função para iniciar o frontend
start_frontend() {
    print_status "Iniciando frontend..."
    
    cd ortotool-frontend
    
    # Iniciar frontend em background
    nohup npm run dev > ../logs/frontend.log 2>&1 &
    FRONTEND_PID=$!
    echo $FRONTEND_PID > ../logs/frontend.pid
    
    cd ..
    
    # Aguardar frontend inicializar
    print_status "Aguardando frontend inicializar..."
    for i in {1..60}; do
        if check_process 3000 || check_process 3001; then
            if check_process 3000; then
                FRONTEND_PORT=3000
            else
                FRONTEND_PORT=3001
            fi
            print_success "Frontend iniciado com sucesso (PID: $FRONTEND_PID, Porta: $FRONTEND_PORT)"
            return 0
        fi
        sleep 1
    done
    
    print_error "Timeout ao iniciar frontend"
    return 1
}

# Função para mostrar status final
show_status() {
    print_header
    print_success "🎉 ORTOTOOL iniciado com sucesso!"
    echo
    print_status "📊 Status dos Serviços:"
    
    if check_process 8000; then
        echo -e "  ${GREEN}✅ Backend:${NC}  http://localhost:8000"
        echo -e "     ${BLUE}📚 API Docs:${NC} http://localhost:8000/docs"
    else
        echo -e "  ${RED}❌ Backend:${NC}  Falha ao iniciar"
    fi
    
    if check_process 3000; then
        echo -e "  ${GREEN}✅ Frontend:${NC} http://localhost:3000"
    elif check_process 3001; then
        echo -e "  ${GREEN}✅ Frontend:${NC} http://localhost:3001"
    else
        echo -e "  ${RED}❌ Frontend:${NC} Falha ao iniciar"
    fi
    
    echo
    print_status "📁 Logs disponíveis em:"
    echo "  • Backend:  logs/backend.log"
    echo "  • Frontend: logs/frontend.log"
    echo
    print_status "🛑 Para parar os serviços:"
    echo "  • Backend:  kill \$(cat logs/backend.pid)"
    echo "  • Frontend: kill \$(cat logs/frontend.pid)"
    echo "  • Ambos:    ./stop_services.sh"
    echo
    print_success "🚀 Aplicação pronta para uso!"
}

# Função principal
main() {
    # Verificar se está no diretório correto
    if [ ! -d "ortotool-backend" ] || [ ! -d "ortotool-frontend" ]; then
        print_error "Execute este script na raiz do projeto ORTOTOOL"
        print_error "Estrutura esperada:"
        echo "  ortotool/"
        echo "  ├── ortotool-backend/"
        echo "  ├── ortotool-frontend/"
        echo "  └── setup.sh"
        exit 1
    fi
    
    print_header
    
    # Criar diretório de logs
    mkdir -p logs
    
    # Parar processos existentes
    stop_existing_processes
    
    # Verificar dependências
    check_system_dependencies
    
    # Configurar serviços
    setup_backend
    setup_frontend
    
    # Iniciar serviços
    if start_backend && start_frontend; then
        show_status
    else
        print_error "Falha ao iniciar alguns serviços. Verifique os logs."
        exit 1
    fi
}

# Tratar sinais para limpeza
cleanup() {
    print_warning "Interrompido pelo usuário"
    if [ -f "logs/backend.pid" ]; then
        kill $(cat logs/backend.pid) 2>/dev/null || true
    fi
    if [ -f "logs/frontend.pid" ]; then
        kill $(cat logs/frontend.pid) 2>/dev/null || true
    fi
    exit 1
}

trap cleanup SIGINT SIGTERM

# Executar função principal
main "$@"
