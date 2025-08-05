'use client'

import React, { useState, useEffect } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Info, Globe, Layers, Database, Clock, FileText, Loader } from 'lucide-react'
import { visualizationService } from '@/services/ortotool'
import { FileMetadata, UploadedFileInfo } from '@/types'
import LoadingSpinner from '@/components/LoadingSpinner'

interface MetadataViewerProps {
  selectedFile: UploadedFileInfo | null
  onClose: () => void
}

export default function MetadataViewer({ selectedFile, onClose }: MetadataViewerProps) {
  const [metadata, setMetadata] = useState<FileMetadata | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (selectedFile) {
      loadMetadata()
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [selectedFile])

  const loadMetadata = async () => {
    if (!selectedFile) return

    setLoading(true)
    setError(null)

    try {
      const data = await visualizationService.getFileMetadata(selectedFile.path)
      setMetadata(data)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erro ao carregar metadados')
    } finally {
      setLoading(false)
    }
  }

  if (!selectedFile) {
    return (
      <Card className="h-full">
        <CardContent className="p-8">
          <div className="text-center text-gray-500">
            <Info className="w-12 h-12 mx-auto mb-4 text-gray-400" />
            <p>Selecione um arquivo para ver os metadados</p>
          </div>
        </CardContent>
      </Card>
    )
  }

  const formatFileSize = (bytes: number): string => {
    const units = ['B', 'KB', 'MB', 'GB', 'TB']
    let size = bytes
    let unitIndex = 0

    while (size >= 1024 && unitIndex < units.length - 1) {
      size /= 1024
      unitIndex++
    }

    return `${size.toFixed(1)} ${units[unitIndex]}`
  }

  const formatDate = (timestamp: number): string => {
    return new Date(timestamp).toLocaleString('pt-BR')
  }

  const formatBounds = (bounds: number[]): string => {
    return `[${bounds.map(b => b.toFixed(6)).join(', ')}]`
  }

  return (
    <Card className="h-full">
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle className="flex items-center space-x-2">
            <FileText className="w-5 h-5" />
            <span>Metadados</span>
          </CardTitle>
          <Button variant="outline" size="sm" onClick={onClose}>
            ×
          </Button>
        </div>
      </CardHeader>
      
      <CardContent className="space-y-6">
        {/* File Information */}
        <div>
          <h3 className="font-medium mb-3 flex items-center">
            <Database className="w-4 h-4 mr-2" />
            Informações do Arquivo
          </h3>
          <div className="space-y-2 text-sm">
            <div className="flex justify-between">
              <span className="text-gray-600">Nome:</span>
              <span className="font-mono text-right flex-1 ml-2">{selectedFile.name}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Tamanho:</span>
              <span className="font-mono">{formatFileSize(selectedFile.size)}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Tipo:</span>
              <span className="font-mono capitalize">{selectedFile.type}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Extensão:</span>
              <span className="font-mono">.{selectedFile.extension}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Modificado:</span>
              <span className="font-mono text-right flex-1 ml-2">{formatDate(selectedFile.modified)}</span>
            </div>
          </div>
        </div>

        {/* Loading State */}
        {loading && (
          <div className="py-6">
            <LoadingSpinner 
              size="md" 
              message="Carregando metadados..." 
            />
          </div>
        )}

        {/* Error State */}
        {error && (
          <div className="p-3 bg-red-50 border border-red-200 rounded text-sm text-red-700">
            {error}
          </div>
        )}

        {/* Metadata */}
        {metadata && (
          <>
            {/* Spatial Information */}
            <div>
              <h3 className="font-medium mb-3 flex items-center">
                <Globe className="w-4 h-4 mr-2" />
                Informações Espaciais
              </h3>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-600">CRS:</span>
                  <span className="font-mono text-right flex-1 ml-2">{metadata.crs || 'N/A'}</span>
                </div>
                {metadata.bounds && (
                  <div>
                    <span className="text-gray-600">Limites:</span>
                    <div className="font-mono text-xs mt-1 p-2 bg-gray-50 rounded">
                      {formatBounds(metadata.bounds)}
                    </div>
                  </div>
                )}
              </div>
            </div>

            {/* Raster-specific metadata */}
            {metadata.type === 'raster' && metadata.bands && (
              <div>
                <h3 className="font-medium mb-3 flex items-center">
                  <Layers className="w-4 h-4 mr-2" />
                  Informações Raster
                </h3>
                <div className="space-y-2 text-sm">
                  {metadata.width && metadata.height && (
                    <div className="flex justify-between">
                      <span className="text-gray-600">Dimensões:</span>
                      <span className="font-mono">{metadata.width} × {metadata.height}</span>
                    </div>
                  )}
                  <div className="flex justify-between">
                    <span className="text-gray-600">Bandas:</span>
                    <span className="font-mono">{metadata.count || metadata.bands.length}</span>
                  </div>
                  {metadata.resolution && (
                    <div className="flex justify-between">
                      <span className="text-gray-600">Resolução:</span>
                      <span className="font-mono">{metadata.resolution[0].toFixed(2)} × {metadata.resolution[1].toFixed(2)}</span>
                    </div>
                  )}
                </div>

                {/* Band Information */}
                {metadata.bands && metadata.bands.length > 0 && (
                  <div className="mt-4">
                    <h4 className="font-medium mb-2 text-sm">Detalhes das Bandas:</h4>
                    <div className="space-y-2">
                      {metadata.bands.map((band, index) => (
                        <div key={index} className="p-2 bg-gray-50 rounded text-xs">
                          <div className="flex justify-between mb-1">
                            <span className="font-medium">Banda {band.index}</span>
                            <span>{band.dtype}</span>
                          </div>
                          {band.nodata !== null && (
                            <div className="text-gray-600 mb-1">
                              No Data: {band.nodata}
                            </div>
                          )}
                          {band.min !== undefined && band.max !== undefined && (
                            <div className="text-gray-600">
                              Min: {band.min.toFixed(2)} | Max: {band.max.toFixed(2)}
                            </div>
                          )}
                          {band.mean !== undefined && band.std !== undefined && (
                            <div className="text-gray-600">
                              Média: {band.mean.toFixed(2)} | Desvio: {band.std.toFixed(2)}
                            </div>
                          )}
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}

            {/* Vector-specific metadata */}
            {metadata.type === 'vector' && (
              <div>
                <h3 className="font-medium mb-3 flex items-center">
                  <Layers className="w-4 h-4 mr-2" />
                  Informações Vetoriais
                </h3>
                <div className="space-y-2 text-sm">
                  {metadata.feature_count !== undefined && (
                    <div className="flex justify-between">
                      <span className="text-gray-600">Feições:</span>
                      <span className="font-mono">{metadata.feature_count.toLocaleString()}</span>
                    </div>
                  )}
                  {metadata.geometry_type && (
                    <div className="flex justify-between">
                      <span className="text-gray-600">Geometria:</span>
                      <span className="font-mono">{metadata.geometry_type}</span>
                    </div>
                  )}
                  {metadata.columns && metadata.columns.length > 0 && (
                    <div>
                      <span className="text-gray-600">Colunas ({metadata.columns.length}):</span>
                      <div className="mt-2 space-y-1">
                        {metadata.columns.map((column, index) => (
                          <div key={index} className="flex justify-between text-xs p-1 bg-gray-50 rounded">
                            <span className="font-mono">{column}</span>
                            {metadata.column_types?.[column] && (
                              <span className="text-gray-500">{metadata.column_types[column]}</span>
                            )}
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              </div>
            )}
          </>
        )}

        {/* Reload Button */}
        {selectedFile && (
          <Button 
            onClick={loadMetadata}
            variant="outline" 
            size="sm" 
            className="w-full"
            disabled={loading}
          >
            {loading ? (
              <>
                <Loader className="w-4 h-4 mr-2 animate-spin" />
                Carregando...
              </>
            ) : (
              <>
                <Clock className="w-4 h-4 mr-2" />
                Recarregar Metadados
              </>
            )}
          </Button>
        )}
      </CardContent>
    </Card>
  )
}
