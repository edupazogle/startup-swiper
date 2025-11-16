import { useEffect, useState } from 'react'
import { useRegisterSW } from 'virtual:pwa-register/react'
import { Button } from '@/components/ui/button'
import { ArrowsClockwise, X } from '@phosphor-icons/react'

export function PWAUpdatePrompt() {
  const [showPrompt, setShowPrompt] = useState(false)
  
  const {
    offlineReady: [offlineReady, setOfflineReady],
    needRefresh: [needRefresh, setNeedRefresh],
    updateServiceWorker,
  } = useRegisterSW({
    onRegistered(r) {
      console.log('PWA: Service Worker registered', r)
    },
    onRegisterError(error) {
      console.error('PWA: Service Worker registration error', error)
    },
  })

  useEffect(() => {
    if (offlineReady || needRefresh) {
      setShowPrompt(true)
    }
  }, [offlineReady, needRefresh])

  const close = () => {
    setOfflineReady(false)
    setNeedRefresh(false)
    setShowPrompt(false)
  }

  if (!showPrompt) return null

  return (
    <div className="fixed bottom-4 right-4 z-50 max-w-sm animate-in slide-in-from-bottom-5">
      <div className="bg-gradient-to-br from-purple-500 to-indigo-600 rounded-lg shadow-2xl p-4 text-white">
        <div className="flex items-start gap-3">
          <ArrowsClockwise size={24} weight="bold" className="flex-shrink-0 mt-0.5" />
          <div className="flex-1">
            <h3 className="font-bold text-sm mb-1">
              {needRefresh ? 'New Version Available' : 'App Ready Offline'}
            </h3>
            <p className="text-xs text-white/90 mb-3">
              {needRefresh 
                ? 'A new version of the app is available. Reload to update.'
                : 'The app is ready to work offline.'}
            </p>
            <div className="flex gap-2">
              {needRefresh && (
                <Button
                  size="sm"
                  onClick={() => updateServiceWorker(true)}
                  className="bg-white text-purple-600 hover:bg-gray-100 h-8"
                >
                  Reload
                </Button>
              )}
              <Button
                size="sm"
                variant="ghost"
                onClick={close}
                className="text-white hover:bg-white/20 h-8"
              >
                {needRefresh ? 'Later' : 'OK'}
              </Button>
            </div>
          </div>
          <button
            onClick={close}
            className="text-white/80 hover:text-white transition-colors flex-shrink-0"
            aria-label="Close"
          >
            <X size={18} />
          </button>
        </div>
      </div>
    </div>
  )
}
