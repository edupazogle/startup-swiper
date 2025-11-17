export function ModalSkeleton() {
  return (
    <div className="animate-pulse space-y-4">
      {/* Header Skeleton */}
      <div className="flex items-center gap-3">
        <div className="w-10 h-10 rounded-lg bg-gray-300 dark:bg-gray-700"></div>
        <div className="flex-1">
          <div className="h-5 bg-gray-300 dark:bg-gray-700 rounded w-3/4 mb-2"></div>
          <div className="h-3 bg-gray-300 dark:bg-gray-700 rounded w-1/2"></div>
        </div>
      </div>

      {/* Content Skeleton */}
      <div className="space-y-3 mt-6">
        <div className="h-4 bg-gray-300 dark:bg-gray-700 rounded w-full"></div>
        <div className="h-4 bg-gray-300 dark:bg-gray-700 rounded w-5/6"></div>
        <div className="h-4 bg-gray-300 dark:bg-gray-700 rounded w-4/6"></div>
      </div>

      <div className="space-y-3 mt-6">
        <div className="h-4 bg-gray-300 dark:bg-gray-700 rounded w-full"></div>
        <div className="h-4 bg-gray-300 dark:bg-gray-700 rounded w-3/4"></div>
      </div>
    </div>
  )
}

export function OutlineSkeleton() {
  return (
    <div className="space-y-4 animate-pulse">
      {/* Section Title */}
      <div className="flex items-center gap-2">
        <div className="w-4 h-4 rounded bg-gray-300 dark:bg-gray-700"></div>
        <div className="h-4 bg-gray-300 dark:bg-gray-700 rounded w-32"></div>
      </div>

      {/* Cards */}
      {[1, 2, 3].map((i) => (
        <div key={i} className="flex gap-2 bg-white dark:bg-gray-800 rounded-lg px-3 py-2 border border-gray-200 dark:border-gray-700">
          <div className="w-5 h-5 rounded-full bg-gray-300 dark:bg-gray-700 flex-shrink-0"></div>
          <div className="flex-1 space-y-2">
            <div className="h-3 bg-gray-300 dark:bg-gray-700 rounded w-full"></div>
            <div className="h-3 bg-gray-300 dark:bg-gray-700 rounded w-4/5"></div>
          </div>
        </div>
      ))}
    </div>
  )
}
