'use client'

import React from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { FileImage, FileType, Trash2, Eye, Info } from 'lucide-react'
import { UploadedFile } from '@/types'

interface FileManagerProps {
  files: UploadedFile[]
  onFilesChange: (files: UploadedFile[]) => void
}

export default function FileManager({ files, onFilesChange }: FileManagerProps) {
  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes'
    const k = 1024
    const sizes = ['Bytes', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
  }

  const handleDelete = (fileId: string) => {
    onFilesChange(files.filter(f => f.id !== fileId))
  }

  const getFileIcon = (type: 'raster' | 'vector') => {
    return type === 'raster' ? FileImage : FileType
  }

  const getFileTypeColor = (type: 'raster' | 'vector') => {
    return type === 'raster' ? 'text-green-600' : 'text-blue-600'
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center justify-between">
          <span>Arquivos Carregados</span>
          <span className="text-sm font-normal text-gray-500">
            {files.length} arquivo{files.length !== 1 ? 's' : ''}
          </span>
        </CardTitle>
        <CardDescription>
          Gerencie os arquivos que foram enviados para o sistema
        </CardDescription>
      </CardHeader>
      <CardContent>
        {files.length === 0 ? (
          <div className="text-center py-8">
            <FileImage className="w-12 h-12 text-gray-400 mx-auto mb-4" />
            <p className="text-gray-500 dark:text-gray-400">
              Nenhum arquivo carregado ainda
            </p>
            <p className="text-sm text-gray-400 dark:text-gray-500 mt-1">
              Use a área de upload ao lado para começar
            </p>
          </div>
        ) : (
          <div className="space-y-3">
            {files.map((file) => {
              const Icon = getFileIcon(file.type)
              return (
                <div
                  key={file.id}
                  className="flex items-center justify-between p-4 border rounded-lg hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors"
                >
                  <div className="flex items-center space-x-3 flex-1 min-w-0">
                    <Icon className={`w-5 h-5 flex-shrink-0 ${getFileTypeColor(file.type)}`} />
                    
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium text-gray-900 dark:text-gray-100 truncate">
                        {file.name}
                      </p>
                      <div className="flex items-center space-x-4 mt-1 text-xs text-gray-500 dark:text-gray-400">
                        <span>{formatFileSize(file.size)}</span>
                        <span className="capitalize">{file.type}</span>
                        <span>{file.uploadedAt.toLocaleDateString('pt-BR')}</span>
                      </div>
                    </div>
                  </div>

                  <div className="flex items-center space-x-2 flex-shrink-0">
                    <Button variant="ghost" size="sm">
                      <Eye className="w-4 h-4" />
                    </Button>
                    
                    <Button variant="ghost" size="sm">
                      <Info className="w-4 h-4" />
                    </Button>
                    
                    <Button 
                      variant="ghost" 
                      size="sm"
                      onClick={() => handleDelete(file.id)}
                      className="text-red-600 hover:text-red-700 hover:bg-red-50 dark:text-red-400 dark:hover:bg-red-950"
                    >
                      <Trash2 className="w-4 h-4" />
                    </Button>
                  </div>
                </div>
              )
            })}
          </div>
        )}

        {files.length > 0 && (
          <div className="mt-6 pt-4 border-t">
            <div className="flex items-center justify-between text-sm">
              <span className="text-gray-600 dark:text-gray-400">
                Total: {formatFileSize(files.reduce((sum, file) => sum + file.size, 0))}
              </span>
              <div className="flex space-x-2">
                <Button variant="outline" size="sm">
                  Selecionar Todos
                </Button>
                <Button variant="outline" size="sm" className="text-red-600">
                  Limpar Todos
                </Button>
              </div>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  )
}
