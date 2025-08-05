'use client'

import React, { useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { CheckCircle, XCircle, Clock, Loader2, Download, Trash2 } from 'lucide-react'
import { ProcessingJob } from '@/types'

interface JobTrackerProps {
  jobs: ProcessingJob[]
  onJobsChange: (jobs: ProcessingJob[]) => void
}

export default function JobTracker({ jobs, onJobsChange }: JobTrackerProps) {
  const getStatusIcon = (status: ProcessingJob['status']) => {
    switch (status) {
      case 'pending':
        return <Clock className="w-4 h-4 text-yellow-500" />
      case 'processing':
        return <Loader2 className="w-4 h-4 text-blue-500 animate-spin" />
      case 'completed':
        return <CheckCircle className="w-4 h-4 text-green-500" />
      case 'failed':
        return <XCircle className="w-4 h-4 text-red-500" />
    }
  }

  const getStatusColor = (status: ProcessingJob['status']) => {
    switch (status) {
      case 'pending':
        return 'text-yellow-700 bg-yellow-50 border-yellow-200 dark:text-yellow-300 dark:bg-yellow-950 dark:border-yellow-800'
      case 'processing':
        return 'text-blue-700 bg-blue-50 border-blue-200 dark:text-blue-300 dark:bg-blue-950 dark:border-blue-800'
      case 'completed':
        return 'text-green-700 bg-green-50 border-green-200 dark:text-green-300 dark:bg-green-950 dark:border-green-800'
      case 'failed':
        return 'text-red-700 bg-red-50 border-red-200 dark:text-red-300 dark:bg-red-950 dark:border-red-800'
    }
  }

  const getOperationName = (type: ProcessingJob['type']) => {
    const names = {
      clip: 'Recorte',
      reproject: 'Reprojeção',
      resample: 'Reamostragem',
      mosaic: 'Mosaico'
    }
    return names[type] || type
  }

  const handleDelete = (jobId: string) => {
    onJobsChange(jobs.filter(j => j.id !== jobId))
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString('pt-BR')
  }

  const pendingJobs = jobs.filter(j => j.status === 'pending')
  const processingJobs = jobs.filter(j => j.status === 'processing')
  const completedJobs = jobs.filter(j => j.status === 'completed')
  const failedJobs = jobs.filter(j => j.status === 'failed')

  return (
    <div className="space-y-6">
      {/* Estatísticas */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center space-x-2">
              <Clock className="w-4 h-4 text-yellow-500" />
              <div>
                <p className="text-2xl font-bold">{pendingJobs.length}</p>
                <p className="text-xs text-gray-600 dark:text-gray-400">Pendentes</p>
              </div>
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center space-x-2">
              <Loader2 className="w-4 h-4 text-blue-500" />
              <div>
                <p className="text-2xl font-bold">{processingJobs.length}</p>
                <p className="text-xs text-gray-600 dark:text-gray-400">Processando</p>
              </div>
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center space-x-2">
              <CheckCircle className="w-4 h-4 text-green-500" />
              <div>
                <p className="text-2xl font-bold">{completedJobs.length}</p>
                <p className="text-xs text-gray-600 dark:text-gray-400">Concluídos</p>
              </div>
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center space-x-2">
              <XCircle className="w-4 h-4 text-red-500" />
              <div>
                <p className="text-2xl font-bold">{failedJobs.length}</p>
                <p className="text-xs text-gray-600 dark:text-gray-400">Falhas</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Lista de Jobs */}
      <Card>
        <CardHeader>
          <CardTitle>Histórico de Processamentos</CardTitle>
          <CardDescription>
            Acompanhe o status dos seus processamentos em tempo real
          </CardDescription>
        </CardHeader>
        <CardContent>
          {jobs.length === 0 ? (
            <div className="text-center py-8">
              <Clock className="w-12 h-12 text-gray-400 mx-auto mb-4" />
              <p className="text-gray-500 dark:text-gray-400">
                Nenhum processamento iniciado
              </p>
              <p className="text-sm text-gray-400 dark:text-gray-500 mt-1">
                Execute uma operação na aba "Processar" para ver o progresso aqui
              </p>
            </div>
          ) : (
            <div className="space-y-3">
              {jobs.map((job) => (
                <div
                  key={job.id}
                  className="flex items-center justify-between p-4 border rounded-lg hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors"
                >
                  <div className="flex items-center space-x-4 flex-1">
                    {getStatusIcon(job.status)}
                    
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center space-x-2">
                        <p className="text-sm font-medium text-gray-900 dark:text-gray-100">
                          {getOperationName(job.type)}
                        </p>
                        <span className={`px-2 py-1 text-xs rounded-full border ${getStatusColor(job.status)}`}>
                          {job.status}
                        </span>
                      </div>
                      
                      <p className="text-xs text-gray-600 dark:text-gray-400 mt-1">
                        Criado em: {formatDate(job.created_at)}
                      </p>
                      
                      {job.status === 'processing' && (
                        <div className="mt-2">
                          <div className="flex items-center justify-between text-xs text-gray-600 dark:text-gray-400 mb-1">
                            <span>Progresso</span>
                            <span>{job.progress}%</span>
                          </div>
                          <div className="w-full bg-gray-200 rounded-full h-2 dark:bg-gray-700">
                            <div
                              className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                              style={{ width: `${job.progress}%` }}
                            />
                          </div>
                        </div>
                      )}
                      
                      {job.error && (
                        <p className="text-xs text-red-600 dark:text-red-400 mt-1">
                          Erro: {job.error}
                        </p>
                      )}
                    </div>
                  </div>

                  <div className="flex items-center space-x-2 flex-shrink-0">
                    {job.status === 'completed' && job.output_file && (
                      <Button variant="ghost" size="sm" className="text-green-600">
                        <Download className="w-4 h-4" />
                      </Button>
                    )}
                    
                    {job.status !== 'processing' && (
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => handleDelete(job.id)}
                        className="text-red-600 hover:text-red-700 hover:bg-red-50 dark:text-red-400 dark:hover:bg-red-950"
                      >
                        <Trash2 className="w-4 h-4" />
                      </Button>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
