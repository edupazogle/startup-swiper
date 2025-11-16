import { Sparkle, X } from '@phosphor-icons/react'

interface ConciergeChatHeaderProps {
  title: string
  subtitle?: string
  icon?: React.ReactNode
  onClose?: () => void
}

export function ConciergeChatHeader({
  title,
  subtitle,
  icon = <Sparkle size={20} weight="duotone" className="text-purple-500" />,
  onClose
}: ConciergeChatHeaderProps) {
  return (
    <div className="px-3 sm:px-4 md:px-6 py-2.5 sm:py-3 border-b border-border flex items-center justify-between bg-background" role="banner">
      <div className="flex items-center gap-2 min-w-0">
        <div className="flex-shrink-0" aria-hidden="true">{icon}</div>
        <div className="min-w-0">
          <h2 className="text-sm sm:text-base font-semibold text-foreground truncate">{title}</h2>
          {subtitle && (
            <p className="text-[10px] sm:text-xs text-muted-foreground mt-0.5 truncate">{subtitle}</p>
          )}
        </div>
      </div>

      {onClose && (
        <button
          onClick={onClose}
          className="text-muted-foreground hover:text-foreground transition-colors p-1.5 -mr-1.5 flex-shrink-0"
          aria-label="Close chat"
        >
          <X size={18} />
        </button>
      )}
    </div>
  )
}
