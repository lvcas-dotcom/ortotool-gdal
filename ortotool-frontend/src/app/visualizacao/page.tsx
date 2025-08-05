'use client'

import React, { useState, useEffect } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { ArrowLeft, RefreshCw, Info } from 'lucide-react'
import Link from 'next/link'
import MapViewer from '@/components/MapViewer'
import MetadataViewer from '@/components/MetadataViewer'
import { visualizationService } from '@/services/ortotool'
import { UploadedFileInfo } from '@/types'

export default function VisualizacaoPage() {
  const [uploadedFiles, setUploadedFiles] = useState<UploadedFileInfo[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [selectedFile, setSelectedFile] = useState<UploadedFileInfo | null>(null)
  const [showMetadata, setShowMetadata] = useState(false)

  const loadUploadedFiles = async () => {
    setLoading(true)
    setError(null)
    
    try {
      const files = await visualizationService.listUploadedFiles()
      setUploadedFiles(files)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erro ao carregar arquivos')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadUploadedFiles()
  }, [])

  const geospatialFiles = uploadedFiles.filter(file => 
    file.type === 'raster' || file.type === 'vector'
  )

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      <div className="container mx-auto p-6">
        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center space-x-4">
            <Link href="/">
              <Button variant="outline" size="sm">
                <ArrowLeft className="w-4 h-4 mr-2" />
                Voltar
              </Button>
            </Link>
            <div>
              <h1 className="text-3xl font-bold text-gray-900 dark:text-gray-100">
                Visualização de Dados
              </h1>
              <p className="text-gray-600 dark:text-gray-400">
                Visualize e analise seus dados geoespaciais
              </p>
            </div>
          </div>
          
          <Button 
            onClick={loadUploadedFiles}
            variant="outline"
            disabled={loading}
          >
            <RefreshCw className={`w-4 h-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
            Atualizar
          </Button>
        </div>

        {/* Error Message */}
        {error && (
          <Card className="mb-6 border-red-200 bg-red-50">
            <CardContent className="p-4">
              <div className="flex items-center space-x-2">
                <div className="w-4 h-4 bg-red-500 rounded-full"></div>
                <p className="text-red-700">{error}</p>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Info Panel */}
        <Card className="mb-6">
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Info className="w-5 h-5" />
              <span>Informações dos Arquivos</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="text-center p-4 bg-blue-50 rounded-lg">
                <div className="text-2xl font-bold text-blue-600">
                  {uploadedFiles.length}
                </div>
                <div className="text-sm text-blue-800">Total de Arquivos</div>
              </div>
              
              <div className="text-center p-4 bg-green-50 rounded-lg">
                <div className="text-2xl font-bold text-green-600">
                  {uploadedFiles.filter(f => f.type === 'raster').length}
                </div>
                <div className="text-sm text-green-800">Arquivos Raster</div>
              </div>
              
              <div className="text-center p-4 bg-purple-50 rounded-lg">
                <div className="text-2xl font-bold text-purple-600">
                  {uploadedFiles.filter(f => f.type === 'vector').length}
                </div>
                <div className="text-sm text-purple-800">Arquivos Vetoriais</div>
              </div>
            </div>

            {geospatialFiles.length === 0 && !loading && (
              <div className="text-center py-8">
                <p className="text-gray-600 dark:text-gray-400">
                  Nenhum arquivo geoespacial encontrado. 
                  <Link href="/" className="text-blue-600 hover:underline ml-1">
                    Faça upload de arquivos GeoTIFF ou vetoriais
                  </Link>
                  .
                </p>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Map Viewer */}
        {geospatialFiles.length > 0 && (
          <div className="grid gap-6 lg:grid-cols-4">
            <div className="lg:col-span-3">
              <MapViewer uploadedFiles={geospatialFiles} />
            </div>
            
            {/* Metadata Panel */}
            <div className="lg:col-span-1">
              <Card className="mb-4">
                <CardHeader>
                  <CardTitle className="text-sm">Arquivos Disponíveis</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2 max-h-60 overflow-y-auto">
                    {geospatialFiles.map(file => (
                      <div 
                        key={file.path} 
                        className={`p-2 rounded cursor-pointer border transition-colors ${
                          selectedFile?.path === file.path 
                            ? 'border-blue-500 bg-blue-50' 
                            : 'border-gray-200 hover:border-gray-300'
                        }`}
                        onClick={() => setSelectedFile(file)}
                      >
                        <div className="text-sm font-medium truncate" title={file.name}>
                          {file.name}
                        </div>
                        <div className="text-xs text-gray-500 flex justify-between">
                          <span className="capitalize">{file.type}</span>
                          <span>{(file.size / (1024 * 1024)).toFixed(1)} MB</span>
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
              
              <MetadataViewer 
                selectedFile={selectedFile} 
                onClose={() => setSelectedFile(null)} 
              />
            </div>
          </div>
        )}

        {/* Loading State */}
        {loading && (
          <Card>
            <CardContent className="p-8">
              <div className="text-center">
                <div className="animate-spin w-8 h-8 border-4 border-blue-500 border-t-transparent rounded-full mx-auto mb-4"></div>
                <p className="text-gray-600 dark:text-gray-400">
                  Carregando arquivos...
                </p>
              </div>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  )
}
