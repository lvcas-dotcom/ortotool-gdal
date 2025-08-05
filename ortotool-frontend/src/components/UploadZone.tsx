'use client'

import React, { useCallback, useState } from 'react'
import { useDropzone } from 'react-dropzone'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Upload, FileImage, FileType, AlertCircle } from 'lucide-react'
import { uploadService } from '@/services/ortotool'
import { UploadedFile } from '@/types'

interface UploadZoneProps {
  onFileUpload: (file: UploadedFile) => void
}

export default function UploadZone({ onFileUpload }: UploadZoneProps) {
  const [uploading, setUploading] = useState(false)
  const [uploadProgress, setUploadProgress] = useState(0)
  const [error, setError] = useState<string | null>(null)

  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    for (const file of acceptedFiles) {
      setUploading(true)
      setError(null)
      setUploadProgress(0)

      try {
        const isRaster = file.name.toLowerCase().match(/\.(tif|tiff|geotiff|jpg|jpeg|png)$/i)
        const isVector = file.name.toLowerCase().match(/\.(shp|geojson|gpkg|kml|kmz)$/i)

        if (!isRaster && !isVector) {
          throw new Error('Formato de arquivo não suportado')
        }

        let response
        if (isRaster) {
          response = await uploadService.uploadRaster(file)
        } else {
          response = await uploadService.uploadVector(file)
        }

        // Response agora vem diretamente do backend
        const uploadedFile: UploadedFile = {
          id: Date.now().toString(),
          name: file.name,
          size: file.size,
          type: isRaster ? 'raster' : 'vector',
          path: response.filename,
          uploadedAt: new Date(),
          info: undefined, // TODO: Implementar info do raster
        }

        onFileUpload(uploadedFile)
        setUploadProgress(100)
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Erro desconhecido')
      } finally {
        setUploading(false)
        setTimeout(() => setUploadProgress(0), 2000)
      }
    }
  }, [onFileUpload])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'image/tiff': ['.tif', '.tiff'],
      'image/jpeg': ['.jpg', '.jpeg'],
      'image/png': ['.png'],
      'application/json': ['.geojson'],
      'application/zip': ['.shp'],
      'application/gpx+xml': ['.gpx'],
      'application/kml+xml': ['.kml'],
      'application/vnd.google-earth.kmz': ['.kmz'],
    },
    multiple: true,
    maxSize: 25 * 1024 * 1024 * 1024, // 25GB
  })

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center space-x-2">
          <Upload className="w-5 h-5" />
          <span>Upload de Arquivos</span>
        </CardTitle>
        <CardDescription>
          Faça upload de ortomosaicos (GeoTIFF) ou arquivos vetoriais (Shapefile, GeoJSON)
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div
          {...getRootProps()}
          className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors ${
            isDragActive
              ? 'border-blue-500 bg-blue-50 dark:bg-blue-950'
              : 'border-gray-300 hover:border-gray-400 dark:border-gray-600'
          } ${uploading ? 'pointer-events-none opacity-50' : ''}`}
        >
          <input {...getInputProps()} />
          
          <div className="flex flex-col items-center space-y-4">
            {uploading ? (
              <>
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500" />
                <p className="text-sm text-gray-600 dark:text-gray-400">
                  Fazendo upload... {uploadProgress}%
                </p>
                {uploadProgress > 0 && (
                  <div className="w-full bg-gray-200 rounded-full h-2 dark:bg-gray-700">
                    <div
                      className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                      style={{ width: `${uploadProgress}%` }}
                    />
                  </div>
                )}
              </>
            ) : (
              <>
                <div className="flex space-x-2">
                  <FileImage className="w-8 h-8 text-gray-400" />
                  <FileType className="w-8 h-8 text-gray-400" />
                </div>
                
                {isDragActive ? (
                  <p className="text-lg font-medium text-blue-600">
                    Solte os arquivos aqui...
                  </p>
                ) : (
                  <div className="space-y-2">
                    <p className="text-lg font-medium text-gray-900 dark:text-gray-100">
                      Arraste arquivos aqui ou clique para selecionar
                    </p>
                    <p className="text-sm text-gray-600 dark:text-gray-400">
                      Suporte: GeoTIFF, TIFF, Shapefile, GeoJSON, KML
                    </p>
                    <p className="text-xs text-gray-500 dark:text-gray-500">
                      Tamanho máximo: 25GB por arquivo
                    </p>
                  </div>
                )}
                
                <Button variant="outline" className="mt-4">
                  Selecionar Arquivos
                </Button>
              </>
            )}
          </div>
        </div>

        {error && (
          <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg dark:bg-red-950 dark:border-red-800">
            <div className="flex items-center space-x-2">
              <AlertCircle className="w-4 h-4 text-red-500" />
              <p className="text-sm text-red-700 dark:text-red-300">{error}</p>
            </div>
          </div>
        )}

        <div className="mt-6 grid grid-cols-2 gap-4 text-sm">
          <div className="space-y-2">
            <h4 className="font-medium text-gray-900 dark:text-gray-100">
              Arquivos Raster
            </h4>
            <ul className="text-gray-600 dark:text-gray-400 space-y-1">
              <li>• GeoTIFF (.tif, .tiff)</li>
              <li>• JPEG (.jpg, .jpeg)</li>
              <li>• PNG (.png)</li>
            </ul>
          </div>
          <div className="space-y-2">
            <h4 className="font-medium text-gray-900 dark:text-gray-100">
              Arquivos Vetoriais
            </h4>
            <ul className="text-gray-600 dark:text-gray-400 space-y-1">
              <li>• Shapefile (.shp + auxiliares)</li>
              <li>• GeoJSON (.geojson)</li>
              <li>• KML/KMZ (.kml, .kmz)</li>
            </ul>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}
