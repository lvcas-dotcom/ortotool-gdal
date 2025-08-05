import axios from 'axios'

// Configuração base da API
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1'

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Interceptor para logs (desenvolvimento)
if (process.env.NODE_ENV === 'development') {
  api.interceptors.request.use((config) => {
    console.log(`🔄 ${config.method?.toUpperCase()} ${config.url}`)
    return config
  })

  api.interceptors.response.use(
    (response) => {
      console.log(`✅ ${response.status} ${response.config.url}`)
      return response
    },
    (error) => {
      console.error(`❌ ${error.response?.status} ${error.config?.url}`, error.response?.data)
      return Promise.reject(error)
    }
  )
}

// Tipos para as respostas da API
export interface ApiResponse<T = any> {
  success: boolean
  data: T
  message?: string
}

export interface Job {
  job_id: string
  status: 'pending' | 'processing' | 'completed' | 'failed'
  progress: number
  result?: string
  error?: string
  created_at: string
  updated_at?: string
}

export interface RasterInfo {
  filename: string
  size: number
  format: string
  crs: string
  bounds: [number, number, number, number]
  shape: [number, number]
  nodata: number | null
}

// Parâmetros para operações
export interface ClipParams {
  raster_path: string
  vector_path: string
  output_path?: string
}

export interface ReprojectParams {
  raster_path: string
  target_crs: string
  output_path?: string
}

export interface ResampleParams {
  raster_path: string
  scale_factor?: number
  target_resolution?: [number, number]
  resampling_method?: 'nearest' | 'bilinear' | 'cubic'
  output_path?: string
}

export interface MosaicParams {
  raster_paths: string[]
  output_path?: string
  method?: 'first' | 'last' | 'min' | 'max' | 'mean'
}
