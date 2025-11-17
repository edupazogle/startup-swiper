import { Dialog, DialogContent } from '@/components/ui/dialog'
import { ReactNode } from 'react'

interface FastModalShellProps {
  isOpen: boolean
  onClose: () => void
  children: ReactNode
}

/**
 * Lightweight modal shell that renders instantly (<50ms)
 * Used for lazy loading heavy modal content
 */
export function FastModalShell({ isOpen, onClose, children }: FastModalShellProps) {
  return (
    <Dialog open={isOpen} onOpenChange={onClose} modal={true}>
      <DialogContent 
        className="max-w-3xl h-[80vh] md:h-[80vh] h-screen md:rounded-lg rounded-none p-0 gap-0 flex flex-col w-full max-w-full md:max-w-3xl"
      >
        {children}
      </DialogContent>
    </Dialog>
  )
}
