import { createRoot } from 'react-dom/client'
import { ErrorBoundary } from "react-error-boundary";
// import { registerSW } from 'virtual:pwa-register' // DISABLED - Service worker removed

import App from './App.tsx'
import { ErrorFallback } from './ErrorFallback.tsx'

import "./styles/tokens.css"
import "./main.css"
import "./styles/theme.css"
import "./styles/auroral.css"
import "./index.css"

// Service worker completely disabled - was causing aggressive caching issues
// const updateSW = registerSW({
//   immediate: true,
//   onNeedRefresh() {
//     console.log('🔄 New version available, reloading...')
//     updateSW(true)
//   },
//   onOfflineReady() {
//     console.log('App ready to work offline')
//   },
//   onRegisteredSW(swUrl, r) {
//     r && setInterval(() => {
//       r.update()
//     }, 60000)
//   },
// })

createRoot(document.getElementById('root')!).render(
  <ErrorBoundary FallbackComponent={ErrorFallback}>
    <App />
   </ErrorBoundary>
)
