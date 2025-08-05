"""
🛰️ ORTOTOOL - Sistema Simplificado de Processamento de Ortomosaicos
==================================================================

Sistema robusto e fácil de usar para tratamento de ortos georreferenciados.
Desenvolvido para simplificar o trabalho com dados geoespaciais.

Funcionalidades:
- Upload de ortomosaicos e vetores
- Recorte, reprojeção, reamostragem e mosaico
- Interface web amigável
- Processamento assíncrono
- Monitoramento em tempo real

Autor: GitHub Copilot | Data: 2025
"""

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import logging
from pathlib import Path
from datetime import datetime

# Configuração de logging simplificada
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - ORTOTOOL - %(levelname)s - %(message)s'
)
logger = logging.getLogger("ORTOTOOL")

# Criar diretórios essenciais
for directory in ['uploads', 'outputs', 'logs']:
    Path(directory).mkdir(exist_ok=True)

# Aplicação FastAPI
app = FastAPI(
    title="🛰️ ORTOTOOL - Processador de Ortomosaicos",
    description="Sistema simplificado para tratamento de ortos georreferenciados",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS simplificado
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir rotas
from routers import upload, raster, jobs, download

app.include_router(upload.router, prefix="/api/v1", tags=["📤 Upload"])
app.include_router(raster.router, prefix="/api/v1", tags=["🛰️ Processamento"])
app.include_router(jobs.router, prefix="/api/v1", tags=["📊 Monitoramento"])
app.include_router(download.router, prefix="/api/v1", tags=["📥 Download"])

@app.get("/", response_class=HTMLResponse)
async def home():
    """Interface web principal do ORTOTOOL"""
    return """
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>🛰️ ORTOTOOL - Processador de Ortomosaicos</title>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body { 
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                color: white;
            }
            .container {
                max-width: 1200px;
                margin: 0 auto;
                padding: 20px;
            }
            .header {
                text-align: center;
                margin-bottom: 40px;
                background: rgba(255,255,255,0.1);
                padding: 30px;
                border-radius: 15px;
                backdrop-filter: blur(10px);
            }
            .header h1 { font-size: 3em; margin-bottom: 10px; }
            .header p { font-size: 1.2em; opacity: 0.9; }
            .grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                gap: 20px;
                margin-bottom: 40px;
            }
            .card {
                background: rgba(255,255,255,0.1);
                padding: 25px;
                border-radius: 15px;
                backdrop-filter: blur(10px);
                transition: transform 0.3s ease;
            }
            .card:hover { transform: translateY(-5px); }
            .card h3 { 
                font-size: 1.5em; 
                margin-bottom: 15px; 
                color: #4CAF50; 
            }
            .card p { line-height: 1.6; opacity: 0.9; }
            .status {
                background: rgba(76, 175, 80, 0.3);
                padding: 15px;
                border-radius: 10px;
                text-align: center;
                margin-bottom: 30px;
                border-left: 5px solid #4CAF50;
            }
            .buttons {
                display: flex;
                justify-content: center;
                gap: 20px;
                flex-wrap: wrap;
                margin: 30px 0;
            }
            .btn {
                background: #4CAF50;
                color: white;
                padding: 15px 30px;
                text-decoration: none;
                border-radius: 25px;
                font-weight: bold;
                transition: all 0.3s ease;
                display: inline-flex;
                align-items: center;
                gap: 10px;
            }
            .btn:hover {
                background: #45a049;
                transform: scale(1.05);
            }
            .quick-start {
                background: rgba(255,255,255,0.1);
                padding: 25px;
                border-radius: 15px;
                backdrop-filter: blur(10px);
            }
            .code {
                background: rgba(0,0,0,0.3);
                padding: 15px;
                border-radius: 8px;
                font-family: 'Courier New', monospace;
                margin: 10px 0;
                overflow-x: auto;
            }
            .footer {
                text-align: center;
                margin-top: 40px;
                opacity: 0.8;
                font-size: 0.9em;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🛰️ ORTOTOOL</h1>
                <p>Sistema Profissional de Processamento de Ortomosaicos</p>
            </div>

            <div class="status">
                ✅ Sistema Online e Operacional | Pronto para Processar Seus Ortos
            </div>

            <div class="grid">
                <div class="card">
                    <h3>📤 Upload Inteligente</h3>
                    <p>Envie ortomosaicos (GeoTIFF) e arquivos vetoriais (Shapefile, GeoJSON) com validação automática e detecção de formato.</p>
                </div>

                <div class="card">
                    <h3>✂️ Recorte Preciso</h3>
                    <p>Corte ortomosaicos usando áreas de interesse com reprojeção automática entre diferentes sistemas de coordenadas.</p>
                </div>

                <div class="card">
                    <h3>🗺️ Reprojeção Avançada</h3>
                    <p>Converta entre SIRGAS 2000, UTM, WGS84 e outros sistemas com suporte a mais de 30 CRS diferentes.</p>
                </div>

                <div class="card">
                    <h3>📏 Reamostragem</h3>
                    <p>Altere a resolução espacial com métodos bilinear, cúbico, vizinho mais próximo e média para qualidade otimizada.</p>
                </div>

                <div class="card">
                    <h3>🧩 Mosaicos Robustos</h3>
                    <p>Combine múltiplos ortomosaicos com diferentes métodos de mesclagem e ajuste automático de sobreposições.</p>
                </div>

                <div class="card">
                    <h3>📊 Monitoramento Real</h3>
                    <p>Acompanhe o progresso de todas as operações em tempo real com notificações e estimativas de tempo.</p>
                </div>
            </div>

            <div class="buttons">
                <a href="/docs" class="btn">📚 Documentação Completa</a>
                <a href="/api/v1/upload/files" class="btn">📁 Gerenciar Arquivos</a>
                <a href="/api/v1/jobs/worker/status" class="btn">📊 Status do Sistema</a>
                <a href="http://localhost:5555" class="btn">🌺 Monitor Flower</a>
            </div>

            <div class="quick-start">
                <h2>⚡ Início Rápido - Guia Prático</h2>
                
                <h3>1️⃣ Upload de Ortomosaico</h3>
                <div class="code">curl -X POST "http://localhost:8000/api/v1/upload/raster" -F "file=@meu_orto.tif"</div>
                
                <h3>2️⃣ Processar (Exemplo: Recorte)</h3>
                <div class="code">curl -X POST "http://localhost:8000/api/v1/raster/clip" \\<br>
&nbsp;&nbsp;-H "Content-Type: application/json" \\<br>
&nbsp;&nbsp;-d '{"raster_file": "uploads/meu_orto.tif", "vector_file": "uploads/area.shp"}'</div>
                
                <h3>3️⃣ Acompanhar Progresso</h3>
                <div class="code">curl "http://localhost:8000/api/v1/jobs/{job_id}"</div>
                
                <h3>4️⃣ Baixar Resultado</h3>
                <div class="code">curl "http://localhost:8000/api/v1/download/result/{job_id}" -o resultado_final.tif</div>
            </div>

            <div class="footer">
                <p>🏢 Desenvolvido para facilitar o trabalho com dados geoespaciais</p>
                <p>📧 Suporte técnico: contate a equipe de TI da sua empresa</p>
                <p>🔧 Versão 2.0.0 | Última atualização: 2025</p>
            </div>
        </div>
    </body>
    </html>
    """

@app.get("/health")
async def health_check():
    """Verificação de saúde do sistema"""
    try:
        from workers.tasks import get_worker_status
        worker_status = get_worker_status()
        workers_ok = len(worker_status.get('stats', {})) > 0
        
        dirs_ok = all(Path(d).exists() for d in ['uploads', 'outputs', 'logs'])
        
        status = "healthy" if dirs_ok and workers_ok else "degraded"
        
        return {
            "status": status,
            "timestamp": datetime.now(),
            "version": "2.0.0",
            "sistema": "ORTOTOOL",
            "workers_ativos": len(worker_status.get('stats', {})),
            "diretorios_ok": dirs_ok
        }
    except:
        return {
            "status": "unhealthy",
            "timestamp": datetime.now(),
            "error": "Problema na verificação do sistema"
        }

@app.get("/api/v1/info")
async def info_sistema():
    """Informações do sistema ORTOTOOL"""
    return {
        "nome": "ORTOTOOL - Processador de Ortomosaicos",
        "versao": "2.0.0",
        "descricao": "Sistema profissional para tratamento de ortos georreferenciados",
        "funcionalidades": [
            "Upload de GeoTIFF e vetores",
            "Recorte por área de interesse",
            "Reprojeção entre CRS (SIRGAS, UTM, WGS84)",
            "Reamostragem de resolução",
            "Criação de mosaicos",
            "Processamento assíncrono com monitoramento"
        ],
        "formatos_suportados": {
            "raster": [".tif", ".tiff", ".geotiff"],
            "vetor": [".shp", ".geojson", ".json"]
        },
        "limites": {
            "tamanho_maximo_arquivo": "25GB",
            "jobs_simultaneos": 5,
            "timeout_processamento": "2 horas"
        },
        "endpoints_principais": {
            "upload": "/api/v1/upload/",
            "processamento": "/api/v1/raster/",
            "monitoramento": "/api/v1/jobs/",
            "download": "/api/v1/download/",
            "documentacao": "/docs"
        }
    }

if __name__ == "__main__":
    import uvicorn
    
    logger.info("🚀 Iniciando ORTOTOOL v2.0...")
    logger.info("📍 Interface principal: http://localhost:8000")
    logger.info("📚 Documentação API: http://localhost:8000/docs")
    logger.info("🌺 Monitor Celery: http://localhost:5555")
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
        log_level="info"
    )
