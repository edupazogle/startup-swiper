import { createRoot } from 'react-dom/client'
import { ErrorBoundary } from "react-error-boundary";
import { registerSW } from 'virtual:pwa-register'

import App from './App.tsx'
import { ErrorFallback } from './ErrorFallback.tsx'

import "./styles/tokens.css"
import "./main.css"
import "./styles/theme.css"
import "./styles/auroral.css"
import "./index.css"

// Register PWA service worker with aggressive update checking
const updateSW = registerSW({
  immediate: true, // Register immediately
  onNeedRefresh() {
    console.log('🔄 New version available, reloading...')
    updateSW(true) // Auto-reload without asking
  },
  onOfflineReady() {
    console.log('App ready to work offline')
  },
  onRegisteredSW(swUrl, r) {
    // Check for updates every 60 seconds
    r && setInterval(() => {
      r.update()
    }, 60000)
  },
})

createRoot(document.getElementById('root')!).render(
  <ErrorBoundary FallbackComponent={ErrorFallback}>
    <App />
   </ErrorBoundary>
)
