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

// Tipos para Visualização
export interface FileMetadata {
  type: 'raster' | 'vector'
  file_path: string
  file_size: number
  bounds: [number, number, number, number]
  crs: string | null
  
  // Específico para raster
  width?: number
  height?: number
  count?: number
  resolution?: [number, number]
  bands?: BandInfo[]
  
  // Específico para vetor
  feature_count?: number
  geometry_type?: string
  columns?: string[]
  column_types?: Record<string, string>
}

export interface BandInfo {
  index: number
  dtype: string
  nodata: number | null
  min?: number
  max?: number
  mean?: number
  std?: number
}

export interface GeoJSONData {
  type: 'FeatureCollection'
  features: any[]
  metadata?: {
    original_feature_count: number
    preview_feature_count: number
    crs: string
    bounds: [number, number, number, number]
  }
}

export interface UploadedFileInfo {
  name: string
  path: string
  size: number
  extension: string
  type: 'raster' | 'vector' | 'unknown'
  modified: number
}

export interface LayerConfig {
  id: string
  name: string
  type: 'raster' | 'vector'
  visible: boolean
  opacity: number
  filePath: string
  metadata?: FileMetadata
  data?: any
}
