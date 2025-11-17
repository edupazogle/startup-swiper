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
      <div className="bg-card border rounded-lg shadow-lg p-4">
        <div className="flex items-start gap-3">
          <div className="rounded-md bg-primary/10 p-2 flex-shrink-0">
            <ArrowsClockwise size={20} weight="bold" className="text-primary" />
          </div>
          <div className="flex-1">
            <h3 className="font-semibold text-sm mb-1 text-foreground">
              {needRefresh ? 'New Version Available' : 'App Ready Offline'}
            </h3>
            <p className="text-xs text-muted-foreground mb-3 leading-relaxed">
              {needRefresh
                ? 'A new version is available. Reload to update.'
                : 'The app is cached and ready to work offline.'}
            </p>
            <div className="flex gap-2">
              {needRefresh && (
                <Button
                  size="sm"
                  onClick={() => updateServiceWorker(true)}
                  variant="default"
                  className="h-8"
                >
                  Reload
                </Button>
              )}
              <Button
                size="sm"
                variant="outline"
                onClick={close}
                className="h-8"
              >
                {needRefresh ? 'Later' : 'OK'}
              </Button>
            </div>
          </div>
          <button
            onClick={close}
            className="text-muted-foreground hover:text-foreground transition-colors flex-shrink-0"
            aria-label="Close"
          >
            <X size={16} />
          </button>
        </div>
      </div>
    </div>
  )
}
