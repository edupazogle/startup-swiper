import { motion } from 'framer-motion'
import { Sparkle, Users, Calendar, Briefcase } from '@phosphor-icons/react'

export interface QuickAction {
  id: string
  label: string
  icon: React.ReactNode
  onClick: () => void
  description?: string
}

interface QuickActionsBarProps {
  actions: QuickAction[]
  isVisible: boolean
  columns?: 2 | 3 | 4
}

const containerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.05,
      delayChildren: 0
    }
  }
}

const itemVariants = {
  hidden: { opacity: 0, scale: 0.9 },
  visible: {
    opacity: 1,
    scale: 1,
    transition: {
      duration: 0.2
    }
  },
  hover: {
    scale: 1.05,
    transition: { duration: 0.2 }
  },
  tap: {
    scale: 0.95
  }
}

export function QuickActionsBar({
  actions,
  isVisible,
  columns = 2
}: QuickActionsBarProps) {
  const colsClass = {
    2: 'grid-cols-2',
    3: 'grid-cols-3',
    4: 'grid-cols-4'
  }[columns]

  // Always render, just control visibility via CSS
  return (
    <motion.div
      variants={containerVariants}
      initial="hidden"
      animate={isVisible ? "visible" : "hidden"}
      className={`grid ${colsClass} gap-1.5 transition-all duration-300 ${isVisible ? 'opacity-100 pointer-events-auto' : 'opacity-0 pointer-events-none h-0 overflow-hidden'}`}
      role="toolbar"
      aria-label="Quick actions"
      aria-hidden={!isVisible}
    >
      {actions.map((action) => (
        <motion.button
          key={action.id}
          onClick={action.onClick}
          variants={itemVariants}
          whileHover="hover"
          whileTap="tap"
          className="group relative px-2 py-1.5 rounded-md border border-border bg-background hover:border-purple-500 hover:bg-purple-50 dark:hover:bg-purple-950 transition-colors flex flex-col items-center gap-0.5 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:ring-offset-1 dark:focus:ring-offset-background"
          aria-label={action.label}
          title={action.description || action.label}
        >
          <span className="text-purple-600 dark:text-purple-400 flex-shrink-0 text-sm" aria-hidden="true">
            {action.icon}
          </span>
          <span className="text-[10px] font-medium text-foreground text-center line-clamp-1">
            {action.label}
          </span>
        </motion.button>
      ))}
    </motion.div>
  )
}
