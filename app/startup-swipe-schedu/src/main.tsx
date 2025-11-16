import { createRoot } from 'react-dom/client'
import { ErrorBoundary } from "react-error-boundary";
import { registerSW } from 'virtual:pwa-register'

import App from './App.tsx'
import { ErrorFallback } from './ErrorFallback.tsx'

import "./styles/tokens.css"
import "./main.css"
import "./styles/theme.css"
import "./index.css"

// Register PWA service worker
const updateSW = registerSW({
  onNeedRefresh() {
    if (confirm('New content available. Reload?')) {
      updateSW(true)
    }
  },
  onOfflineReady() {
    console.log('App ready to work offline')
  },
})

createRoot(document.getElementById('root')!).render(
  <ErrorBoundary FallbackComponent={ErrorFallback}>
    <App />
   </ErrorBoundary>
)
