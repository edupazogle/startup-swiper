import { useState, useEffect } from 'react'
import { Close, ShareAll } from 'flowbite-react-icons/outline'
import { Button } from '@/components/ui/button'

export function IOSInstallPrompt() {
  const [showPrompt, setShowPrompt] = useState(false)

  useEffect(() => {
    // Check if it's iOS
    const isIOS = /iPad|iPhone|iPod/.test(navigator.userAgent) && !(window as any).MSStream
    
    // Check if already installed (standalone mode)
    const isInstalled = window.matchMedia('(display-mode: standalone)').matches || 
                        (window.navigator as any).standalone === true
    
    // Check if user has dismissed the prompt before
    const hasSeenPrompt = localStorage.getItem('ios-install-prompt-dismissed')
    
    // Show prompt if iOS, not installed, and hasn't been dismissed
    if (isIOS && !isInstalled && !hasSeenPrompt) {
      // Show after 3 seconds to not be intrusive
      const timer = setTimeout(() => {
        setShowPrompt(true)
      }, 3000)
      
      return () => clearTimeout(timer)
    }
  }, [])

  const handleDismiss = () => {
    setShowPrompt(false)
    // Remember dismissal for 7 days
    const expiryDate = new Date()
    expiryDate.setDate(expiryDate.getDate() + 7)
    localStorage.setItem('ios-install-prompt-dismissed', expiryDate.toISOString())
  }

  if (!showPrompt) return null

  return (
    <div className="fixed bottom-0 left-0 right-0 z-50 p-4 pb-safe animate-in slide-in-from-bottom duration-300">
      <div className="mx-auto max-w-md rounded-xl border bg-gradient-to-br from-purple-500/95 to-pink-500/95 backdrop-blur-lg p-4 shadow-2xl">
        <div className="flex items-start gap-3">
          <div className="flex-1">
            <h3 className="font-semibold text-white mb-1 flex items-center gap-2">
              <span className="text-2xl">📱</span>
              Install Startup Rise
            </h3>
            <p className="text-sm text-white/90 mb-3">
              Add to your home screen for the best Slush 2025 experience!
            </p>
            
            <div className="flex items-center gap-2 text-xs text-white/80 bg-black/20 rounded-lg p-3 mb-3">
              <div className="flex flex-col gap-1">
                <div className="flex items-center gap-2">
                  <span className="text-lg">1️⃣</span>
                  <span>Tap the <ShareAll className="inline w-4 h-4"  /> Share button below</span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-lg">2️⃣</span>
                  <span>Tap "Add to Home Screen"</span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-lg">3️⃣</span>
                  <span>Tap "Add" to install</span>
                </div>
              </div>
            </div>

            <Button
              onClick={handleDismiss}
              variant="secondary"
              size="sm"
              className="w-full bg-white/20 hover:bg-white/30 text-white border-white/30"
            >
              Got it!
            </Button>
          </div>
          
          <button
            onClick={handleDismiss}
            className="text-white/80 hover:text-white transition-colors"
            aria-label="Close"
          >
            <Close className="w-5 h-5"  />
          </button>
        </div>
      </div>
    </div>
  )
}
