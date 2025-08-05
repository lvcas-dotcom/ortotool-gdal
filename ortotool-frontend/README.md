# 🛰️ ORTOTOOL Frontend

Interface web moderna para o sistema de processamento de ortomosaicos georreferenciados.

## 🚀 Tecnologias

- **Next.js 14** - Framework React com App Router
- **TypeScript** - Tipagem estática
- **Tailwind CSS** - Estilização utilitária
- **Lucide React** - Ícones modernos
- **Axios** - Cliente HTTP
- **React Dropzone** - Upload de arquivos

## 📁 Estrutura do Projeto

```
ortotool-frontend/
├── src/
│   ├── app/                    # App Router do Next.js
│   │   ├── layout.tsx         # Layout principal
│   │   └── page.tsx           # Página inicial
│   ├── components/            # Componentes React
│   │   ├── ui/               # Componentes UI base
│   │   ├── UploadZone.tsx    # Área de upload
│   │   ├── MapViewer.tsx     # Visualizador de mapas
│   │   ├── ProcessingPanel.tsx # Painel de operações
│   │   ├── JobTracker.tsx    # Rastreamento de jobs
│   │   └── FileManager.tsx   # Gerenciador de arquivos
│   ├── services/             # Serviços e APIs
│   │   ├── api.ts           # Configuração base da API
│   │   └── ortotool.ts      # Serviços específicos
│   ├── types/               # Definições de tipos
│   │   └── index.ts        # Tipos globais
│   ├── lib/                # Utilitários
│   │   └── utils.ts        # Funções auxiliares
│   └── globals.css         # Estilos globais
├── package.json
├── tailwind.config.js
├── next.config.js
└── README.md
```

## 🔧 Instalação e Execução

### 1. Instalar dependências
\`\`\`bash
npm install
\`\`\`

### 2. Configurar variáveis de ambiente
Crie um arquivo \`.env.local\`:
\`\`\`env
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
\`\`\`

### 3. Executar em desenvolvimento
\`\`\`bash
npm run dev
\`\`\`

### 4. Acessar a aplicação
Abra [http://localhost:3000](http://localhost:3000) no navegador.

## 🎯 Funcionalidades

### ✅ Implementadas
- **Upload de Arquivos**: Drag & drop para GeoTIFF e Shapefiles
- **Gerenciamento**: Lista e organização de arquivos
- **Processamento**: Interface para operações geoespaciais
- **Monitoramento**: Rastreamento de jobs em tempo real
- **UI Responsiva**: Design adaptável para desktop e mobile

### 🚧 Em Desenvolvimento
- **Visualização de Mapas**: Integração com Leaflet/OpenLayers
- **Parâmetros Avançados**: Configuração detalhada das operações
- **Download de Resultados**: Sistema de exportação
- **Autenticação**: Login e controle de acesso

## 🔌 Integração com Backend

O frontend comunica com o backend através de:
- **API REST**: Endpoints padronizados
- **WebSockets**: Atualizações em tempo real (futuro)
- **File Upload**: Multipart form data
- **Job Tracking**: Polling de status

### Endpoints Utilizados
\`\`\`
POST /api/v1/upload/raster     # Upload de raster
POST /api/v1/upload/vector     # Upload de vetor
POST /api/v1/raster/clip       # Recorte
POST /api/v1/raster/reproject  # Reprojeção
POST /api/v1/raster/resample   # Reamostragem
POST /api/v1/raster/mosaic     # Mosaico
GET  /api/v1/jobs/{id}         # Status do job
GET  /api/v1/download/{id}     # Download resultado
\`\`\`

## 🎨 Design System

### Cores
- **Primary**: Blue (processamento geoespacial)
- **Success**: Green (operações concluídas)
- **Warning**: Yellow (jobs pendentes)
- **Error**: Red (falhas)

### Componentes
- **Cards**: Containers para seções
- **Buttons**: Ações primárias e secundárias
- **Progress**: Barras de progresso para jobs
- **Icons**: Lucide React para consistência

## 📱 Responsividade

- **Desktop**: Layout em grid com múltiplas colunas
- **Tablet**: Adaptação para telas médias
- **Mobile**: Stack vertical com navegação por tabs

## 🧪 Desenvolvimento

### Scripts Disponíveis
\`\`\`bash
npm run dev        # Desenvolvimento
npm run build      # Build de produção
npm run start      # Executar build
npm run lint       # Linting
npm run type-check # Verificação de tipos
\`\`\`

### Padrões de Código
- **TypeScript**: Tipagem obrigatória
- **ESLint**: Linting configurado
- **Prettier**: Formatação automática
- **Conventional Commits**: Padronização de commits

## 🚀 Deploy

### Desenvolvimento
O frontend roda na porta **3000** por padrão.

### Produção
Para deploy em produção:
\`\`\`bash
npm run build
npm start
\`\`\`

### Docker (Futuro)
\`\`\`dockerfile
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
RUN npm run build
EXPOSE 3000
CMD ["npm", "start"]
\`\`\`

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature
3. Commit suas mudanças
4. Push para a branch
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT.

---

**ORTOTOOL Frontend** - Interface moderna para processamento geoespacial 🛰️
