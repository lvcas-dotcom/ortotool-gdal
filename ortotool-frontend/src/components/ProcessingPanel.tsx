'use client'

import React, { useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Scissors, RotateCw, Crop, Layers, Play } from 'lucide-react'
import { UploadedFile, ProcessingJob } from '@/types'

interface ProcessingPanelProps {
  files: UploadedFile[]
  onJobCreate: (job: ProcessingJob) => void
}

const operations = [
  {
    id: 'clip',
    name: 'Recorte',
    description: 'Recortar raster usando um polígono',
    icon: Scissors,
    category: 'geometric',
    requirements: { raster: 1, vector: 1 }
  },
  {
    id: 'reproject',
    name: 'Reprojeção',
    description: 'Alterar sistema de coordenadas',
    icon: RotateCw,
    category: 'geometric',
    requirements: { raster: 1 }
  },
  {
    id: 'resample',
    name: 'Reamostragem',
    description: 'Alterar resolução espacial',
    icon: Crop,
    category: 'geometric',
    requirements: { raster: 1 }
  },
  {
    id: 'mosaic',
    name: 'Mosaico',
    description: 'Combinar múltiplos rasters',
    icon: Layers,
    category: 'analysis',
    requirements: { raster: 2 }
  }
]

export default function ProcessingPanel({ files, onJobCreate }: ProcessingPanelProps) {
  const [selectedOperation, setSelectedOperation] = useState<string | null>(null)
  const [selectedFiles, setSelectedFiles] = useState<string[]>([])

  const rasterFiles = files.filter(f => f.type === 'raster')
  const vectorFiles = files.filter(f => f.type === 'vector')

  const canExecuteOperation = (operation: any) => {
    const reqs = operation.requirements
    if (reqs.raster && rasterFiles.length < reqs.raster) return false
    if (reqs.vector && vectorFiles.length < reqs.vector) return false
    return true
  }

  const handleExecute = () => {
    if (!selectedOperation) return

    const job: ProcessingJob = {
      id: Date.now().toString(),
      type: selectedOperation as any,
      status: 'pending',
      progress: 0,
      input_files: selectedFiles,
      parameters: {},
      created_at: new Date().toISOString(),
    }

    onJobCreate(job)
    
    // Simular processamento
    setTimeout(() => {
      job.status = 'processing'
      job.progress = 50
    }, 1000)
    
    setTimeout(() => {
      job.status = 'completed'
      job.progress = 100
      job.output_file = `result_${job.id}.tif`
    }, 5000)
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Operações de Processamento</CardTitle>
        <CardDescription>
          Selecione uma operação para processar seus arquivos
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Lista de Operações */}
        <div className="space-y-2">
          <h4 className="text-sm font-medium text-gray-900 dark:text-gray-100">
            Operações Disponíveis
          </h4>
          <div className="grid gap-2">
            {operations.map((operation) => {
              const Icon = operation.icon
              const canExecute = canExecuteOperation(operation)
              
              return (
                <button
                  key={operation.id}
                  onClick={() => canExecute && setSelectedOperation(operation.id)}
                  disabled={!canExecute}
                  className={`w-full text-left p-3 rounded-lg border transition-colors ${
                    selectedOperation === operation.id
                      ? 'border-blue-500 bg-blue-50 dark:bg-blue-950'
                      : canExecute
                      ? 'border-gray-200 hover:border-gray-300 dark:border-gray-700'
                      : 'border-gray-200 opacity-50 cursor-not-allowed dark:border-gray-700'
                  }`}
                >
                  <div className="flex items-center space-x-3">
                    <Icon className={`w-5 h-5 ${
                      selectedOperation === operation.id ? 'text-blue-600' : 'text-gray-500'
                    }`} />
                    <div className="flex-1">
                      <p className="font-medium text-sm">{operation.name}</p>
                      <p className="text-xs text-gray-600 dark:text-gray-400">
                        {operation.description}
                      </p>
                    </div>
                  </div>
                </button>
              )
            })}
          </div>
        </div>

        {/* Seleção de Arquivos */}
        {selectedOperation && (
          <div className="space-y-3">
            <h4 className="text-sm font-medium text-gray-900 dark:text-gray-100">
              Selecionar Arquivos
            </h4>
            
            {rasterFiles.length > 0 && (
              <div>
                <p className="text-xs text-gray-600 dark:text-gray-400 mb-2">
                  Arquivos Raster ({rasterFiles.length})
                </p>
                <div className="space-y-1">
                  {rasterFiles.map((file) => (
                    <label key={file.id} className="flex items-center space-x-2 text-sm">
                      <input
                        type="checkbox"
                        checked={selectedFiles.includes(file.id)}
                        onChange={(e) => {
                          if (e.target.checked) {
                            setSelectedFiles([...selectedFiles, file.id])
                          } else {
                            setSelectedFiles(selectedFiles.filter(id => id !== file.id))
                          }
                        }}
                        className="rounded"
                      />
                      <span className="truncate">{file.name}</span>
                    </label>
                  ))}
                </div>
              </div>
            )}

            {vectorFiles.length > 0 && selectedOperation === 'clip' && (
              <div>
                <p className="text-xs text-gray-600 dark:text-gray-400 mb-2">
                  Arquivos Vetoriais ({vectorFiles.length})
                </p>
                <div className="space-y-1">
                  {vectorFiles.map((file) => (
                    <label key={file.id} className="flex items-center space-x-2 text-sm">
                      <input
                        type="checkbox"
                        checked={selectedFiles.includes(file.id)}
                        onChange={(e) => {
                          if (e.target.checked) {
                            setSelectedFiles([...selectedFiles, file.id])
                          } else {
                            setSelectedFiles(selectedFiles.filter(id => id !== file.id))
                          }
                        }}
                        className="rounded"
                      />
                      <span className="truncate">{file.name}</span>
                    </label>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {/* Parâmetros (placeholder) */}
        {selectedOperation && (
          <div className="space-y-3">
            <h4 className="text-sm font-medium text-gray-900 dark:text-gray-100">
              Parâmetros
            </h4>
            <div className="p-3 bg-gray-50 dark:bg-gray-800 rounded-lg">
              <p className="text-sm text-gray-600 dark:text-gray-400">
                Parâmetros específicos serão configurados aqui baseados na operação selecionada
              </p>
            </div>
          </div>
        )}

        {/* Botão de Execução */}
        <div className="pt-4 border-t">
          <Button
            onClick={handleExecute}
            disabled={!selectedOperation || selectedFiles.length === 0}
            className="w-full"
          >
            <Play className="w-4 h-4 mr-2" />
            Executar Processamento
          </Button>
        </div>

        {/* Status dos Arquivos */}
        <div className="text-xs text-gray-500 dark:text-gray-400 space-y-1">
          <p>📁 Raster: {rasterFiles.length} arquivo{rasterFiles.length !== 1 ? 's' : ''}</p>
          <p>📐 Vetor: {vectorFiles.length} arquivo{vectorFiles.length !== 1 ? 's' : ''}</p>
        </div>
      </CardContent>
    </Card>
  )
}
