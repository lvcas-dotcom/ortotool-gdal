#!/bin/bash

# 🛰️ ORTOTOOL - Script para Parar Serviços
# ==========================================
# Este script para todos os serviços do ORTOTOOL

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

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

print_status "Parando serviços do ORTOTOOL..."

# Parar backend
if [ -f "logs/backend.pid" ]; then
    BACKEND_PID=$(cat logs/backend.pid)
    if kill $BACKEND_PID 2>/dev/null; then
        print_success "Backend parado (PID: $BACKEND_PID)"
    else
        print_warning "Backend já estava parado"
    fi
    rm -f logs/backend.pid
else
    print_warning "PID do backend não encontrado"
fi

# Parar frontend
if [ -f "logs/frontend.pid" ]; then
    FRONTEND_PID=$(cat logs/frontend.pid)
    if kill $FRONTEND_PID 2>/dev/null; then
        print_success "Frontend parado (PID: $FRONTEND_PID)"
    else
        print_warning "Frontend já estava parado"
    fi
    rm -f logs/frontend.pid
else
    print_warning "PID do frontend não encontrado"
fi

# Força parar processos residuais
pkill -f "uvicorn.*main:app" 2>/dev/null || true
pkill -f "next.*dev" 2>/dev/null || true

print_success "Todos os serviços foram parados"
