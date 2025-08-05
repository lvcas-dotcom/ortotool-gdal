import { api, ApiResponse, Job, RasterInfo, ClipParams, ReprojectParams, ResampleParams, MosaicParams } from './api'

// Serviços de Upload
export const uploadService = {
  async uploadRaster(file: File): Promise<{ filename: string; info?: RasterInfo }> {
    const formData = new FormData()
    formData.append('file', file)
    
    const response = await api.post('/upload/raster', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
    
    return response.data
  },

  async uploadVector(file: File): Promise<{ filename: string }> {
    const formData = new FormData()
    formData.append('file', file)
    
    const response = await api.post('/upload/vector', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
    
    return response.data
  },
}

// Serviços de Processamento
export const processingService = {
  async clipRaster(params: ClipParams): Promise<ApiResponse<{ job_id: string }>> {
    const response = await api.post('/raster/clip', params)
    return response.data
  },

  async reprojectRaster(params: ReprojectParams): Promise<ApiResponse<{ job_id: string }>> {
    const response = await api.post('/raster/reproject', params)
    return response.data
  },

  async resampleRaster(params: ResampleParams): Promise<ApiResponse<{ job_id: string }>> {
    const response = await api.post('/raster/resample', params)
    return response.data
  },

  async createMosaic(params: MosaicParams): Promise<ApiResponse<{ job_id: string }>> {
    const response = await api.post('/raster/mosaic', params)
    return response.data
  },
}

// Serviços de Jobs
export const jobService = {
  async getJob(jobId: string): Promise<ApiResponse<Job>> {
    const response = await api.get(`/jobs/${jobId}`)
    return response.data
  },

  async getJobs(): Promise<ApiResponse<Job[]>> {
    const response = await api.get('/jobs')
    return response.data
  },

  async cancelJob(jobId: string): Promise<ApiResponse<{ message: string }>> {
    const response = await api.delete(`/jobs/${jobId}`)
    return response.data
  },
}

// Serviços de Download
export const downloadService = {
  async downloadResult(jobId: string): Promise<Blob> {
    const response = await api.get(`/download/${jobId}`, {
      responseType: 'blob',
    })
    return response.data
  },

  getDownloadUrl(jobId: string): string {
    return `${api.defaults.baseURL}/download/${jobId}`
  },
}

// Serviços de Visualização
export const visualizationService = {
  async getFileMetadata(filePath: string): Promise<any> {
    const response = await api.get(`/visualization/metadata/${filePath}`)
    return response.data
  },

  async getFilePreview(filePath: string, format = 'geojson'): Promise<any> {
    const response = await api.get(`/visualization/preview/${filePath}`, {
      params: { format }
    })
    return response.data
  },

  async listUploadedFiles(): Promise<any[]> {
    const response = await api.get('/visualization/files')
    return response.data
  },
}

// Serviços de Sistema
export const systemService = {
  async getHealth(): Promise<ApiResponse<{ status: string; version: string }>> {
    const response = await api.get('/health')
    return response.data
  },

  async getStats(): Promise<ApiResponse<{ 
    active_jobs: number
    completed_jobs: number
    failed_jobs: number
    total_processed: number
  }>> {
    const response = await api.get('/stats')
    return response.data
  },
}
