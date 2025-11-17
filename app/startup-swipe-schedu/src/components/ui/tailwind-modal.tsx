import { useEffect, useRef, ReactNode } from 'react'
import { cn } from '@/lib/utils'

interface TailwindModalProps {
  isOpen: boolean
  onClose: () => void
  children: ReactNode
  className?: string
  size?: 'sm' | 'md' | 'lg' | 'xl' | 'full'
}

export function TailwindModal({ 
  isOpen, 
  onClose, 
  children, 
  className,
  size = 'lg'
}: TailwindModalProps) {
  const modalRef = useRef<HTMLDivElement>(null)
  const contentRef = useRef<HTMLDivElement>(null)

  // Lock body scroll when modal is open
  useEffect(() => {
    if (isOpen) {
      document.body.style.overflow = 'hidden'
      // Focus the modal content for accessibility
      contentRef.current?.focus()
    } else {
      document.body.style.overflow = ''
    }

    return () => {
      document.body.style.overflow = ''
    }
  }, [isOpen])

  // Close on Escape key
  useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && isOpen) {
        onClose()
      }
    }

    document.addEventListener('keydown', handleEscape)
    return () => document.removeEventListener('keydown', handleEscape)
  }, [isOpen, onClose])

  // Handle backdrop click
  const handleBackdropClick = (e: React.MouseEvent) => {
    if (e.target === modalRef.current) {
      onClose()
    }
  }

  const sizeClasses = {
    sm: 'md:max-w-sm',
    md: 'md:max-w-md',
    lg: 'md:max-w-2xl',
    xl: 'md:max-w-4xl',
    full: 'md:max-w-[95vw] md:h-[95vh]'
  }

  if (!isOpen) return null

  return (
    <div
      ref={modalRef}
      className="fixed inset-0 z-[9999] flex items-center justify-center bg-black/50 backdrop-blur-sm max-md:p-0 md:p-4 transition-opacity duration-150"
      onClick={handleBackdropClick}
      role="dialog"
      aria-modal="true"
    >
      <div
        ref={contentRef}
        className={cn(
          'relative w-full bg-white dark:bg-gray-800 shadow-2xl',
          'transition-all duration-150 scale-100 opacity-100',
          'max-md:h-full max-md:rounded-none max-md:max-h-none',
          'md:rounded-xl md:max-h-[90vh] md:overflow-y-auto',
          sizeClasses[size],
          className
        )}
        tabIndex={-1}
      >
        {children}
      </div>
    </div>
  )
}

export function TailwindModalHeader({ 
  children, 
  className 
}: { 
  children: ReactNode
  className?: string 
}) {
  return (
    <div className={cn('px-4 pt-4 pb-3 md:px-6 md:pt-6 md:pb-4', className)}>
      {children}
    </div>
  )
}

export function TailwindModalBody({ 
  children, 
  className 
}: { 
  children: ReactNode
  className?: string 
}) {
  return (
    <div className={cn('px-4 py-3 md:px-6 md:py-4', className)}>
      {children}
    </div>
  )
}

export function TailwindModalFooter({ 
  children, 
  className 
}: { 
  children: ReactNode
  className?: string 
}) {
  return (
    <div className={cn('px-4 pb-4 pt-3 md:px-6 md:pb-6 md:pt-4 flex items-center justify-end gap-3', className)}>
      {children}
    </div>
  )
}

export function TailwindModalTitle({ 
  children, 
  className 
}: { 
  children: ReactNode
  className?: string 
}) {
  return (
    <h2 className={cn('text-xl font-semibold text-gray-900 dark:text-white', className)}>
      {children}
    </h2>
  )
}

export function TailwindModalDescription({ 
  children, 
  className 
}: { 
  children: ReactNode
  className?: string 
}) {
  return (
    <p className={cn('mt-2 text-sm text-gray-600 dark:text-gray-400', className)}>
      {children}
    </p>
  )
}
