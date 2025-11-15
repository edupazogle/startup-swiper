import { ReactNode } from 'react'
import '../styles/auroral.css'

interface AuroralBackgroundProps {
  children?: ReactNode
}

export function AuroralBackground({ children }: AuroralBackgroundProps) {
  return (
    <div className="auroral-container">
      <div
        className="auroral-layer auroral-northern-dusk"
      />

      {children && (
        <div className="relative z-10">
          {children}
        </div>
      )}
    </div>
  )
}
