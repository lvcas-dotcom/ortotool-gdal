# 🛰️ ORTOTOOL - Sistema de Processamento de Ortomosaicos

## 📖 Visão Geral

O **ORTOTOOL** é um sistema robusto e **fácil de usar** para processamento de ortomosaicos georreferenciados. Desenvolvido para **simplificar** o trabalho com dados geoespaciais, oferecendo uma interface amigável e processamento profissional.

## ✨ Funcionalidades Principais

- **📤 Upload Inteligente**: Envio de ortomosaicos (GeoTIFF) e vetores (Shapefile, GeoJSON)
- **✂️ Recorte Preciso**: Corte por área de interesse com reprojeção automática
- **🗺️ Reprojeção Avançada**: Suporte a SIRGAS 2000, UTM, WGS84 e 30+ sistemas
- **📏 Reamostragem**: Alteração de resolução com múltiplos métodos
- **🧩 Mosaicos Robustos**: Combinação de múltiplos ortomosaicos
- **📊 Monitoramento**: Acompanhamento em tempo real do progresso
- **🌐 Interface Web**: Acesso via navegador, sem instalação complexa

## 🚀 Início Rápido (2 minutos)

### Pré-requisitos
- Docker e Docker Compose instalados
- Pelo menos 4GB de RAM disponível
- Portas 8000 e 5555 livres

### Instalação e Execução

```bash
# 1. Clone ou baixe o projeto
cd ortotool

# 2. Execute o script de inicialização
./start.sh
```

**Pronto!** O sistema estará disponível em:
- 🌐 **Interface Principal**: http://localhost:8000
- 📚 **Documentação**: http://localhost:8000/docs
- 🌺 **Monitor**: http://localhost:5555

## 📋 Guia de Uso Simples

### 1️⃣ Upload de Arquivos
```bash
# Upload de ortomosaico
curl -X POST "http://localhost:8000/api/v1/upload/raster" \
     -F "file=@meu_ortomosaico.tif"

# Upload de área de interesse (shapefile)
curl -X POST "http://localhost:8000/api/v1/upload/vector" \
     -F "file=@area_interesse.shp"
```

### 2️⃣ Processamento

#### Recorte por Área
```bash
curl -X POST "http://localhost:8000/api/v1/raster/clip" \
     -H "Content-Type: application/json" \
     -d '{
       "raster_file": "uploads/meu_ortomosaico.tif",
       "vector_file": "uploads/area_interesse.shp",
       "output_name": "orto_recortado"
     }'
```

#### Reprojeção
```bash
curl -X POST "http://localhost:8000/api/v1/raster/reproject" \
     -H "Content-Type: application/json" \
     -d '{
       "raster_file": "uploads/meu_ortomosaico.tif",
       "target_crs": "EPSG:31983",
       "output_name": "orto_sirgas2000"
     }'
```

#### Reamostragem
```bash
curl -X POST "http://localhost:8000/api/v1/raster/resample" \
     -H "Content-Type: application/json" \
     -d '{
       "raster_file": "uploads/meu_ortomosaico.tif",
       "target_resolution": 0.5,
       "resampling_method": "bilinear",
       "output_name": "orto_50cm"
     }'
```

### 3️⃣ Monitoramento
```bash
# Verificar status de um job
curl "http://localhost:8000/api/v1/jobs/{job_id}"

# Listar todos os jobs
curl "http://localhost:8000/api/v1/jobs/"
```

### 4️⃣ Download do Resultado
```bash
# Baixar resultado processado
curl "http://localhost:8000/api/v1/download/result/{job_id}" \
     -o resultado_final.tif
```

## 🎯 Casos de Uso Comuns

### Recorte de Ortomosaico por Propriedade
1. Upload do ortomosaico grande
2. Upload do shapefile da propriedade
3. Executar recorte
4. Baixar ortomosaico da propriedade

### Padronização de Sistema de Coordenadas
1. Upload de múltiplos ortomosaicos
2. Reprojetar todos para SIRGAS 2000 UTM
3. Baixar ortomosaicos padronizados

### Criação de Mosaico Regional
1. Upload de vários ortomosaicos adjacentes
2. Reprojetar para mesmo CRS (se necessário)
3. Criar mosaico unificado
4. Baixar mosaico final

## 🔧 Gerenciamento do Sistema

### Comandos Úteis
```bash
# Verificar status dos serviços
docker-compose -f docker-compose-simple.yml ps

# Ver logs em tempo real
docker-compose -f docker-compose-simple.yml logs -f

# Parar o sistema
docker-compose -f docker-compose-simple.yml down

# Reiniciar o sistema
./start.sh

# Limpar dados processados (cuidado!)
sudo rm -rf geo-processor/{uploads,outputs}/*
```

### Monitoramento de Performance
- **CPU/RAM**: Via htop ou docker stats
- **Jobs Celery**: http://localhost:5555
- **Status Sistema**: http://localhost:8000/health

## 📊 Formatos e Limites

### Formatos Suportados
- **Raster**: GeoTIFF (.tif, .tiff)
- **Vetor**: Shapefile (.shp), GeoJSON (.geojson, .json)

### Limites do Sistema
- **Tamanho máximo de arquivo**: 25GB
- **Jobs simultâneos**: 5
- **Timeout de processamento**: 2 horas
- **Sistemas de coordenadas**: 30+ CRS suportados

## 🏗️ Arquitetura Simplificada

```
🌐 Navegador/Cliente
       ↓ HTTP/REST
🐍 FastAPI (Python)
       ↓ Tasks
🔄 Celery + Redis
       ↓ Processing
🛰️ GDAL + Rasterio
       ↓ Results
📁 Armazenamento Local
```

## 🚨 Solução de Problemas

### Problema: Porta 8000 em uso
```bash
# Encontrar processo usando a porta
sudo lsof -i :8000

# Matar processo se necessário
sudo kill -9 <PID>
```

### Problema: Container não inicia
```bash
# Verificar logs
docker-compose -f docker-compose-simple.yml logs api

# Reconstruir containers
docker-compose -f docker-compose-simple.yml down
docker-compose -f docker-compose-simple.yml up --build
```

### Problema: Processamento lento
- Verificar RAM disponível (mínimo 4GB)
- Reduzir número de jobs simultâneos
- Verificar tamanho dos arquivos de entrada

## 📞 Suporte

### Recursos de Ajuda
- **Interface Web**: http://localhost:8000 (guia visual)
- **Documentação API**: http://localhost:8000/docs (interativa)
- **Status Sistema**: http://localhost:8000/health
- **Logs Detalhados**: `docker-compose logs -f`

### Contato
- 🏢 **Interno**: Equipe de TI da empresa
- 📧 **Email**: contate o administrador do sistema
- 🔧 **Versão**: 2.0.0

---

## 🎉 Benefícios do ORTOTOOL

✅ **Simples**: Interface web intuitiva  
✅ **Robusto**: Processamento profissional com GDAL  
✅ **Escalável**: Processamento assíncrono com Celery  
✅ **Monitorável**: Acompanhamento em tempo real  
✅ **Flexível**: Múltiplos formatos e operações  
✅ **Empresarial**: Pronto para uso profissional  

**Transforme seus ortomosaicos com facilidade e eficiência! 🛰️**
