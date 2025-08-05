// Tipos globais da aplicação
export interface UploadedFile {
  id: string
  name: string
  size: number
  type: 'raster' | 'vector'
  path: string
  uploadedAt: Date
  info?: RasterInfo | VectorInfo
}

export interface RasterInfo {
  filename: string
  size: number
  format: string
  crs: string
  bounds: [number, number, number, number]
  shape: [number, number]
  nodata: number | null
  bands: number
}

export interface VectorInfo {
  filename: string
  size: number
  format: string
  crs: string
  bounds: [number, number, number, number]
  features: number
  geometry_type: string
}

export interface ProcessingJob {
  id: string
  type: 'clip' | 'reproject' | 'resample' | 'mosaic'
  status: 'pending' | 'processing' | 'completed' | 'failed'
  progress: number
  input_files: string[]
  output_file?: string
  parameters: Record<string, any>
  created_at: string
  updated_at?: string
  error?: string
}

export interface MapViewState {
  center: [number, number]
  zoom: number
  bounds?: [[number, number], [number, number]]
}

export interface ProcessingOperation {
  id: string
  name: string
  description: string
  icon: string
  category: 'geometric' | 'radiometric' | 'analysis'
  inputs: {
    raster?: boolean
    vector?: boolean
    multiple?: boolean
  }
  parameters: ProcessingParameter[]
}

export interface ProcessingParameter {
  name: string
  type: 'string' | 'number' | 'select' | 'boolean' | 'file'
  label: string
  description: string
  required: boolean
  default?: any
  options?: { value: any; label: string }[]
  min?: number
  max?: number
}

export interface AppState {
  uploadedFiles: UploadedFile[]
  activeJobs: ProcessingJob[]
  mapView: MapViewState
  selectedFiles: string[]
  selectedOperation?: ProcessingOperation
}
