import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: '🛰️ ORTOTOOL',
  description: 'Sistema de Processamento de Ortomosaicos Georreferenciados',
  icons: {
    icon: '/favicon.ico',
  },
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="pt-BR">
      <body className="min-h-screen bg-background font-sans antialiased">
        {children}
      </body>
    </html>
  )
}
