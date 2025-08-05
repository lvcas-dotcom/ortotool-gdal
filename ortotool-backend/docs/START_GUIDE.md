# 🚀 GUIA DE INÍCIO RÁPIDO - ORTOTOOL

## ⚡ Instalação e Execução (2 minutos)

### 1. Verificar Pré-requisitos
```bash
# Verificar se Docker está instalado
docker --version

# Verificar se Docker Compose está instalado  
docker-compose --version
```

Se não estiverem instalados:
- **Docker**: https://docs.docker.com/get-docker/
- **Docker Compose**: https://docs.docker.com/compose/install/

### 2. Iniciar o Sistema
```bash
# Executar no diretório do projeto
./start.sh
```

### 3. Acessar o Sistema
- 🌐 **Interface**: http://localhost:8000
- 📚 **Documentação**: http://localhost:8000/docs

## 📤 Primeiro Uso - Upload e Processamento

### Via Interface Web (Recomendado)
1. Acesse http://localhost:8000
2. Clique em "📚 Documentação Completa"
3. Use a seção "📤 Upload" para enviar arquivos
4. Use "🛰️ Processamento" para processar

### Via Linha de Comando
```bash
# 1. Upload de ortomosaico
curl -X POST "http://localhost:8000/api/v1/upload/raster" \
     -F "file=@meu_orto.tif"

# 2. Upload de área (shapefile) 
curl -X POST "http://localhost:8000/api/v1/upload/vector" \
     -F "file=@area.shp"

# 3. Recortar ortomosaico
curl -X POST "http://localhost:8000/api/v1/raster/clip" \
     -H "Content-Type: application/json" \
     -d '{
       "raster_file": "uploads/meu_orto.tif",
       "vector_file": "uploads/area.shp"
     }'

# 4. Acompanhar progresso (use o job_id retornado)
curl "http://localhost:8000/api/v1/jobs/SEU_JOB_ID"

# 5. Baixar resultado quando pronto
curl "http://localhost:8000/api/v1/download/result/SEU_JOB_ID" \
     -o resultado.tif
```

## 🛠️ Comandos Essenciais

```bash
# Iniciar sistema
./start.sh

# Parar sistema  
./stop.sh

# Ver logs
docker-compose -f docker-compose-simple.yml logs -f

# Status dos containers
docker-compose -f docker-compose-simple.yml ps

# Verificar saúde do sistema
curl http://localhost:8000/health
```

## 🆘 Problemas Comuns

### Porta 8000 em uso
```bash
sudo lsof -i :8000
sudo kill -9 <PID>
```

### Container não inicia
```bash
docker-compose -f docker-compose-simple.yml down
docker-compose -f docker-compose-simple.yml up --build
```

### Sem espaço em disco
```bash
# Limpar arquivos processados
sudo rm -rf geo-processor/{uploads,outputs}/*

# Limpar containers e imagens não usadas
docker system prune -a
```

## 📞 Ajuda Rápida

- **Interface Visual**: http://localhost:8000
- **API Interativa**: http://localhost:8000/docs  
- **Monitor Celery**: http://localhost:5555
- **Status Sistema**: http://localhost:8000/health

**Pronto para processar ortomosaicos! 🛰️✨**
