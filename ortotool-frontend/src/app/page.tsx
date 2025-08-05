'use client'

import React, { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Upload, Map, Settings, Activity, Download } from 'lucide-react'

// Componentes principais (serão criados em seguida)
import UploadZone from '@/components/UploadZone'
import MapViewer from '@/components/MapViewer'
import ProcessingPanel from '@/components/ProcessingPanel'
import JobTracker from '@/components/JobTracker'
import FileManager from '@/components/FileManager'

import { UploadedFile, ProcessingJob } from '@/types'
import { systemService } from '@/services/ortotool'

export default function HomePage() {
  const [activeTab, setActiveTab] = useState<'upload' | 'map' | 'process' | 'jobs'>('upload')
  const [uploadedFiles, setUploadedFiles] = useState<UploadedFile[]>([])
  const [activeJobs, setActiveJobs] = useState<ProcessingJob[]>([])
  const [systemHealth, setSystemHealth] = useState<{ status: string; version: string } | null>(null)

  // Verificar saúde do sistema ao carregar
  useEffect(() => {
    const checkHealth = async () => {
      try {
        const response = await systemService.getHealth()
        setSystemHealth(response.data)
      } catch (error) {
        console.error('Erro ao verificar saúde do sistema:', error)
      }
    }

    checkHealth()
  }, [])

  const handleFileUpload = (file: UploadedFile) => {
    setUploadedFiles(prev => [...prev, file])
  }

  const handleJobCreate = (job: ProcessingJob) => {
    setActiveJobs(prev => [...prev, job])
  }

  const tabs = [
    { id: 'upload', label: 'Upload', icon: Upload },
    { id: 'map', label: 'Visualizar', icon: Map },
    { id: 'process', label: 'Processar', icon: Settings },
    { id: 'jobs', label: 'Trabalhos', icon: Activity },
  ] as const

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-gray-900 dark:to-gray-800">
      {/* Header */}
      <header className="border-b bg-white/80 backdrop-blur-sm dark:bg-gray-900/80">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2">
                <div className="w-8 h-8 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-lg flex items-center justify-center">
                  <span className="text-white font-bold text-sm">🛰️</span>
                </div>
                <div>
                  <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
                    ORTOTOOL
                  </h1>
                  <p className="text-sm text-gray-500 dark:text-gray-400">
                    Sistema de Processamento de Ortomosaicos
                  </p>
                </div>
              </div>
            </div>
            
            <div className="flex items-center space-x-4">
              {systemHealth && (
                <div className="flex items-center space-x-2 text-sm">
                  <div className={`w-2 h-2 rounded-full ${
                    systemHealth.status === 'healthy' ? 'bg-green-500' : 'bg-red-500'
                  }`} />
                  <span className="text-gray-600 dark:text-gray-300">
                    Sistema {systemHealth.status}
                  </span>
                </div>
              )}
              <Button variant="outline" size="sm">
                <Download className="w-4 h-4 mr-2" />
                Exportar
              </Button>
            </div>
          </div>
        </div>
      </header>

      {/* Navigation Tabs */}
      <nav className="border-b bg-white dark:bg-gray-900">
        <div className="container mx-auto px-4">
          <div className="flex space-x-8">
            {tabs.map((tab) => {
              const Icon = tab.icon
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`flex items-center space-x-2 py-4 px-2 border-b-2 font-medium text-sm transition-colors ${
                    activeTab === tab.id
                      ? 'border-blue-500 text-blue-600 dark:text-blue-400'
                      : 'border-transparent text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200'
                  }`}
                >
                  <Icon className="w-4 h-4" />
                  <span>{tab.label}</span>
                  {tab.id === 'jobs' && activeJobs.length > 0 && (
                    <span className="bg-blue-500 text-white text-xs rounded-full px-2 py-1 min-w-[20px] text-center">
                      {activeJobs.length}
                    </span>
                  )}
                </button>
              )
            })}
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-6">
        <div className="grid gap-6">
          {activeTab === 'upload' && (
            <div className="grid gap-6 lg:grid-cols-2">
              <UploadZone onFileUpload={handleFileUpload} />
              <FileManager files={uploadedFiles} onFilesChange={setUploadedFiles} />
            </div>
          )}

          {activeTab === 'map' && (
            <Card>
              <CardHeader>
                <CardTitle>Visualização de Dados</CardTitle>
                <CardDescription>
                  Visualize seus arquivos geoespaciais no mapa interativo
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="h-[600px] w-full">
                  <MapViewer files={uploadedFiles} />
                </div>
              </CardContent>
            </Card>
          )}

          {activeTab === 'process' && (
            <div className="grid gap-6 lg:grid-cols-3">
              <div className="lg:col-span-1">
                <ProcessingPanel 
                  files={uploadedFiles} 
                  onJobCreate={handleJobCreate}
                />
              </div>
              <div className="lg:col-span-2">
                <Card>
                  <CardHeader>
                    <CardTitle>Preview de Processamento</CardTitle>
                    <CardDescription>
                      Visualize os parâmetros e resultados esperados
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="h-[400px] bg-gray-50 dark:bg-gray-800 rounded-lg flex items-center justify-center">
                      <p className="text-gray-500 dark:text-gray-400">
                        Selecione uma operação para ver o preview
                      </p>
                    </div>
                  </CardContent>
                </Card>
              </div>
            </div>
          )}

          {activeTab === 'jobs' && (
            <JobTracker jobs={activeJobs} onJobsChange={setActiveJobs} />
          )}
        </div>
      </main>
    </div>
  )
}
