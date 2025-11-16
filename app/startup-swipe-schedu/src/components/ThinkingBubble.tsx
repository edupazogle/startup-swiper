import { motion } from 'framer-motion'

interface ThinkingBubbleProps {
  size?: 'sm' | 'md' | 'lg'
}

const sizeMap = {
  sm: 'w-6 h-6',
  md: 'w-8 h-8',
  lg: 'w-10 h-10'
}

const dotSizeMap = {
  sm: 'w-1.5 h-1.5',
  md: 'w-2 h-2',
  lg: 'w-2.5 h-2.5'
}

const dotVariants = {
  bounce: {
    y: [0, -8, 0],
    transition: {
      duration: 0.6,
      repeat: Infinity,
      ease: 'easeInOut'
    }
  }
}

export function ThinkingBubble({ size = 'md' }: ThinkingBubbleProps) {
  return (
    <div className={`flex items-center gap-1.5 ${sizeMap[size]}`} aria-label="Assistant is thinking">
      {[0, 1, 2].map((index) => (
        <motion.div
          key={index}
          className={`bg-muted-foreground rounded-full ${dotSizeMap[size]}`}
          variants={dotVariants}
          animate="bounce"
          transition={{
            delay: index * 0.1
          }}
          aria-hidden="true"
        />
      ))}
    </div>
  )
}
