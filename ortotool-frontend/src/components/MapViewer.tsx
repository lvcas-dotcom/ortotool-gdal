'use client'

import React from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'

interface MapViewerProps {
  files: any[]
}

export default function MapViewer({ files }: MapViewerProps) {
  return (
    <div className="w-full h-full bg-gray-100 dark:bg-gray-800 rounded-lg flex items-center justify-center">
      <div className="text-center">
        <div className="w-16 h-16 bg-gray-300 dark:bg-gray-600 rounded-lg mx-auto mb-4 flex items-center justify-center">
          <span className="text-2xl">🗺️</span>
        </div>
        <h3 className="text-lg font-medium text-gray-900 dark:text-gray-100 mb-2">
          Visualizador de Mapas
        </h3>
        <p className="text-sm text-gray-600 dark:text-gray-400">
          Em desenvolvimento - Integração com Leaflet/OpenLayers
        </p>
        {files.length > 0 && (
          <p className="text-xs text-gray-500 dark:text-gray-500 mt-2">
            {files.length} arquivo{files.length !== 1 ? 's' : ''} carregado{files.length !== 1 ? 's' : ''}
          </p>
        )}
      </div>
    </div>
  )
}
