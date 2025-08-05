'use client'

import React, { useState, useEffect, useRef } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Map, Layers, Eye, EyeOff, ZoomIn, ZoomOut, MapPin, Loader } from 'lucide-react'
import { visualizationService } from '@/services/ortotool'
import { LayerConfig, FileMetadata, GeoJSONData, UploadedFileInfo } from '@/types'
import { LoadingOverlay, MapLoadingState } from '@/components/LoadingSpinner'

// Dynamic import to avoid SSR issues with Leaflet
import dynamic from 'next/dynamic'

const MapContainer = dynamic(
  () => import('react-leaflet').then((mod) => mod.MapContainer),
  { 
    ssr: false,
    loading: () => <MapLoadingState />
  }
)

const TileLayer = dynamic(
  () => import('react-leaflet').then((mod) => mod.TileLayer),
  { ssr: false }
)

const GeoJSON = dynamic(
  () => import('react-leaflet').then((mod) => mod.GeoJSON),
  { ssr: false }
)

interface MapViewerProps {
  uploadedFiles: UploadedFileInfo[]
}

export default function MapViewer({ uploadedFiles }: MapViewerProps) {
  const [layers, setLayers] = useState<LayerConfig[]>([])
  const [loading, setLoading] = useState(false)
  const [loadingMessage, setLoadingMessage] = useState('')
  const [loadingProgress, setLoadingProgress] = useState(0)
  const [error, setError] = useState<string | null>(null)
  const [mapCenter, setMapCenter] = useState<[number, number]>([-14.235, -53.323]) // Centro do Brasil
  const [mapZoom, setMapZoom] = useState(4)
  const [selectedFiles, setSelectedFiles] = useState<string[]>([])
  const [mapReady, setMapReady] = useState(false)
  const mapRef = useRef<any>(null)

  const loadFileData = async (filePath: string) => {
    setLoading(true)
    setError(null)
    setLoadingProgress(0)
    setLoadingMessage('Carregando metadados...')

    try {
      // Simular progresso para feedback visual
      setLoadingProgress(20)
      
      // Get file metadata
      setLoadingMessage('Extraindo metadados do arquivo...')
      const metadata: FileMetadata = await visualizationService.getFileMetadata(filePath)
      setLoadingProgress(50)
      
      let layerData = null
      
      if (metadata.type === 'vector') {
        setLoadingMessage('Convertendo dados vetoriais...')
        // Get vector preview data
        const geoJsonData: GeoJSONData = await visualizationService.getFilePreview(filePath)
        layerData = geoJsonData
        setLoadingProgress(80)
      } else {
        setLoadingMessage('Processando dados raster...')
        setLoadingProgress(80)
      }
      
      setLoadingMessage('Configurando camada...')
      // Create layer configuration
      const layerConfig: LayerConfig = {
        id: `layer_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
        name: filePath.split('/').pop() || filePath,
        type: metadata.type,
        visible: true,
        opacity: metadata.type === 'raster' ? 0.8 : 0.7,
        filePath,
        metadata,
        data: layerData
      }

      setLayers(prev => [...prev, layerConfig])
      setLoadingProgress(100)

      // Zoom to layer bounds if available
      if (metadata.bounds && mapRef.current) {
        setLoadingMessage('Ajustando visualização...')
        const bounds = [
          [metadata.bounds[1], metadata.bounds[0]], // [lat, lng]
          [metadata.bounds[3], metadata.bounds[2]]
        ]
        setTimeout(() => {
          if (mapRef.current) {
            mapRef.current.fitBounds(bounds, { padding: [20, 20] })
          }
        }, 500)
      }

    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erro ao carregar arquivo')
    } finally {
      setTimeout(() => {
        setLoading(false)
        setLoadingMessage('')
        setLoadingProgress(0)
      }, 500)
    }
  }

  const toggleLayerVisibility = (layerId: string) => {
    setLayers(prev => prev.map(layer => 
      layer.id === layerId 
        ? { ...layer, visible: !layer.visible }
        : layer
    ))
  }

  const removeLayer = (layerId: string) => {
    setLayers(prev => prev.filter(layer => layer.id !== layerId))
  }

  const handleFileSelect = (filePath: string) => {
    if (selectedFiles.includes(filePath)) {
      setSelectedFiles(prev => prev.filter(f => f !== filePath))
    } else {
      setSelectedFiles(prev => [...prev, filePath])
    }
  }

  const addSelectedFilesToMap = async () => {
    const filesToLoad = selectedFiles.filter(
      filePath => !layers.find(layer => layer.filePath === filePath)
    )
    
    for (let i = 0; i < filesToLoad.length; i++) {
      const filePath = filesToLoad[i]
      setLoadingMessage(`Carregando arquivo ${i + 1} de ${filesToLoad.length}...`)
      await loadFileData(filePath)
    }
    setSelectedFiles([])
  }

  const zoomToLayers = () => {
    if (layers.length === 0 || !mapRef.current) return

    const allBounds = layers
      .filter(layer => layer.metadata?.bounds)
      .map(layer => layer.metadata!.bounds)

    if (allBounds.length === 0) return

    // Calculate combined bounds
    const minLng = Math.min(...allBounds.map(b => b[0]))
    const minLat = Math.min(...allBounds.map(b => b[1]))
    const maxLng = Math.max(...allBounds.map(b => b[2]))
    const maxLat = Math.max(...allBounds.map(b => b[3]))

    const bounds = [
      [minLat, minLng],
      [maxLat, maxLng]
    ]

    mapRef.current.fitBounds(bounds, { padding: [20, 20] })
  }

  const getGeometryStyle = (feature: any) => {
    const geomType = feature.geometry?.type
    
    switch (geomType) {
      case 'Point':
      case 'MultiPoint':
        return {
          radius: 5,
          fillColor: '#3b82f6',
          color: '#1d4ed8',
          weight: 2,
          opacity: 1,
          fillOpacity: 0.7
        }
      case 'LineString':
      case 'MultiLineString':
        return {
          color: '#059669',
          weight: 3,
          opacity: 0.8
        }
      case 'Polygon':
      case 'MultiPolygon':
        return {
          fillColor: '#f59e0b',
          fillOpacity: 0.3,
          color: '#d97706',
          weight: 2,
          opacity: 0.8
        }
      default:
        return {
          color: '#6b7280',
          weight: 2,
          opacity: 0.8
        }
    }
  }

  // Fix para ícones do Leaflet
  useEffect(() => {
    if (typeof window !== 'undefined') {
      const L = require('leaflet')
      
      // Fix para ícones padrão do Leaflet
      delete (L.Icon.Default.prototype as any)._getIconUrl
      L.Icon.Default.mergeOptions({
        iconRetinaUrl: '/leaflet/marker-icon-2x.png',
        iconUrl: '/leaflet/marker-icon.png',
        shadowUrl: '/leaflet/marker-shadow.png',
      })
    }
  }, [])

  return (
    <div className="grid gap-6 lg:grid-cols-3">
      {/* File Selection Panel */}
      <Card className="lg:col-span-1">
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Layers className="w-5 h-5" />
            <span>Camadas</span>
            {loading && <Loader className="w-4 h-4 animate-spin text-blue-500" />}
          </CardTitle>
        </CardHeader>
        <CardContent>
          {/* Available Files */}
          <div className="space-y-4">
            <div>
              <h4 className="font-medium mb-2">Arquivos Disponíveis</h4>
              <div className="space-y-2 max-h-40 overflow-y-auto">
                {uploadedFiles
                  .filter(file => file.type === 'raster' || file.type === 'vector')
                  .map(file => (
                    <div key={file.path} className="flex items-center space-x-2">
                      <input
                        type="checkbox"
                        checked={selectedFiles.includes(file.path)}
                        onChange={() => handleFileSelect(file.path)}
                        className="rounded"
                        disabled={loading}
                      />
                      <span className="text-sm truncate" title={file.name}>
                        {file.name}
                      </span>
                      <span className="text-xs text-gray-500 capitalize">
                        {file.type}
                      </span>
                    </div>
                  ))}
              </div>
              {selectedFiles.length > 0 && (
                <Button 
                  onClick={addSelectedFilesToMap}
                  className="w-full mt-2"
                  disabled={loading}
                >
                  {loading ? (
                    <>
                      <Loader className="w-4 h-4 mr-2 animate-spin" />
                      Carregando...
                    </>
                  ) : (
                    `Adicionar ${selectedFiles.length} arquivo(s)`
                  )}
                </Button>
              )}
            </div>

            {/* Active Layers */}
            <div>
              <h4 className="font-medium mb-2">Camadas Ativas</h4>
              <div className="space-y-2">
                {layers.map(layer => (
                  <div key={layer.id} className="flex items-center justify-between p-2 bg-gray-50 rounded">
                    <div className="flex items-center space-x-2">
                      <button
                        onClick={() => toggleLayerVisibility(layer.id)}
                        className="text-gray-600 hover:text-gray-800"
                        disabled={loading}
                      >
                        {layer.visible ? <Eye className="w-4 h-4" /> : <EyeOff className="w-4 h-4" />}
                      </button>
                      <span className="text-sm truncate" title={layer.name}>
                        {layer.name}
                      </span>
                    </div>
                    <button
                      onClick={() => removeLayer(layer.id)}
                      className="text-red-500 hover:text-red-700 text-xs"
                      disabled={loading}
                    >
                      ×
                    </button>
                  </div>
                ))}
              </div>
            </div>

            {/* Map Controls */}
            <div className="space-y-2">
              <Button 
                onClick={zoomToLayers} 
                variant="outline" 
                size="sm" 
                className="w-full"
                disabled={layers.length === 0 || loading}
              >
                <ZoomIn className="w-4 h-4 mr-2" />
                Zoom para Camadas
              </Button>
            </div>
          </div>

          {error && (
            <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded">
              <p className="text-sm text-red-700">{error}</p>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Map */}
      <Card className="lg:col-span-2">
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Map className="w-5 h-5" />
            <span>Visualização</span>
            {loading && (
              <div className="flex items-center space-x-2 text-blue-500">
                <Loader className="w-4 h-4 animate-spin" />
                <span className="text-sm">{loadingMessage}</span>
              </div>
            )}
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="h-[600px] rounded-lg overflow-hidden border relative">
            {/* Loading Overlay */}
            {loading && (
              <LoadingOverlay 
                message={loadingMessage} 
                progress={loadingProgress} 
              />
            )}
            
            <MapContainer
              center={mapCenter}
              zoom={mapZoom}
              style={{ height: '100%', width: '100%' }}
              ref={mapRef}
              whenReady={() => setMapReady(true)}
              className="z-10"
            >
              {/* Base map */}
              <TileLayer
                attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
                url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                maxZoom={19}
              />

              {/* Vector layers */}
              {layers
                .filter(layer => layer.type === 'vector' && layer.visible && layer.data)
                .map(layer => (
                  <GeoJSON
                    key={`${layer.id}-${layer.visible}`}
                    data={layer.data}
                    style={getGeometryStyle}
                    onEachFeature={(feature, layer) => {
                      // Add popup with feature properties
                      if (feature.properties) {
                        const content = Object.entries(feature.properties)
                          .map(([key, value]) => `<strong>${key}:</strong> ${value}`)
                          .join('<br>')
                        layer.bindPopup(content)
                      }
                    }}
                  />
                ))}
            </MapContainer>

            {/* Empty State */}
            {layers.length === 0 && !loading && (
              <div className="absolute inset-0 flex items-center justify-center bg-gray-50 bg-opacity-90 z-20">
                <div className="text-center">
                  <MapPin className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                  <p className="text-gray-600">Selecione arquivos para visualizar</p>
                  <p className="text-sm text-gray-500 mt-1">
                    Escolha arquivos GeoTIFF ou vetoriais para adicionar ao mapa
                  </p>
                </div>
              </div>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
