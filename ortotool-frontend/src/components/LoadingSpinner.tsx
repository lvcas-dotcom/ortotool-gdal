'use client'

import React from 'react'

interface LoadingSpinnerProps {
  size?: 'sm' | 'md' | 'lg'
  message?: string
  progress?: number
}

export default function LoadingSpinner({ size = 'md', message, progress }: LoadingSpinnerProps) {
  const sizeClasses = {
    sm: 'w-4 h-4',
    md: 'w-8 h-8',
    lg: 'w-12 h-12'
  }

  const containerClasses = {
    sm: 'p-2',
    md: 'p-4',
    lg: 'p-6'
  }

  return (
    <div className={`flex flex-col items-center justify-center ${containerClasses[size]}`}>
      <div className="relative">
        {/* Spinner externo */}
        <div className={`${sizeClasses[size]} border-4 border-gray-200 rounded-full animate-spin`}></div>
        
        {/* Spinner interno com gradiente */}
        <div className={`absolute top-0 left-0 ${sizeClasses[size]} border-4 border-transparent border-t-blue-500 border-r-blue-400 rounded-full animate-spin`}></div>
        
        {/* Progresso circular se fornecido */}
        {progress !== undefined && (
          <div className="absolute inset-0 flex items-center justify-center">
            <svg className={`${sizeClasses[size]} transform -rotate-90`} viewBox="0 0 36 36">
              <path
                className="text-gray-200"
                stroke="currentColor"
                strokeWidth="2"
                fill="none"
                d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
              />
              <path
                className="text-blue-500"
                stroke="currentColor"
                strokeWidth="2"
                strokeDasharray={`${progress}, 100`}
                strokeLinecap="round"
                fill="none"
                d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
              />
            </svg>
            <div className="absolute text-xs font-medium text-gray-600">
              {Math.round(progress)}%
            </div>
          </div>
        )}
      </div>
      
      {message && (
        <p className={`mt-2 text-center text-gray-600 ${
          size === 'sm' ? 'text-xs' : size === 'md' ? 'text-sm' : 'text-base'
        }`}>
          {message}
        </p>
      )}
      
      {/* Pontos de carregamento animados */}
      <div className="flex space-x-1 mt-2">
        <div className="w-1 h-1 bg-blue-500 rounded-full animate-pulse"></div>
        <div className="w-1 h-1 bg-blue-500 rounded-full animate-pulse" style={{ animationDelay: '0.2s' }}></div>
        <div className="w-1 h-1 bg-blue-500 rounded-full animate-pulse" style={{ animationDelay: '0.4s' }}></div>
      </div>
    </div>
  )
}

export function LoadingOverlay({ message, progress }: { message?: string; progress?: number }) {
  return (
    <div className="absolute inset-0 bg-white bg-opacity-90 flex items-center justify-center z-50 rounded-lg">
      <div className="bg-white p-6 rounded-lg shadow-lg border">
        <LoadingSpinner size="lg" message={message} progress={progress} />
      </div>
    </div>
  )
}

export function MapLoadingState() {
  return (
    <div className="absolute inset-0 bg-gray-50 flex items-center justify-center z-40">
      <div className="text-center">
        <div className="relative mb-4">
          <div className="w-16 h-16 border-4 border-gray-200 rounded-full animate-spin"></div>
          <div className="absolute top-0 left-0 w-16 h-16 border-4 border-transparent border-t-blue-500 border-r-blue-400 rounded-full animate-spin"></div>
        </div>
        <h3 className="text-lg font-medium text-gray-700 mb-2">Carregando Mapa</h3>
        <p className="text-gray-500 text-sm">Preparando visualização dos dados geoespaciais...</p>
        
        {/* Barra de progresso animada */}
        <div className="mt-4 w-48 bg-gray-200 rounded-full h-2">
          <div className="bg-blue-500 h-2 rounded-full animate-pulse" style={{ width: '60%' }}></div>
        </div>
      </div>
    </div>
  )
}
