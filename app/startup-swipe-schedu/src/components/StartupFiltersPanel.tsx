import { useMemo } from 'react'
import { Close, Filter, Search } from 'flowbite-react-icons/outline'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { Separator } from '@/components/ui/separator'
import { Card } from '@/components/ui/card'
import { ThemeSwitcher } from '@/components/ThemeSwitcher'
import { ScrollArea } from '@/components/ui/scroll-area'
import { cn } from '@/lib/utils'

interface StartupFiltersPanelProps {
  // Search & Sort
  searchQuery: string
  onSearchChange: (query: string) => void
  sortBy: 'votes' | 'funding' | 'grade'
  onSortChange: (sort: 'votes' | 'funding' | 'grade') => void

  // Filters
  selectedStages: Set<string>
  onStageChange: (stage: string, isSelected: boolean) => void
  
  selectedTopics: Set<string>
  onTopicChange: (topic: string, isSelected: boolean) => void
  
  selectedTechs: Set<string>
  onTechChange: (tech: string, isSelected: boolean) => void
  
  selectedUseCases: Set<string>
  onUseCaseChange: (useCase: string, isSelected: boolean) => void
  
  selectedGrades: Set<string>
  onGradeChange: (grade: string, isSelected: boolean) => void

  // Available options
  availableStages: string[]
  availableTopics: string[]
  availableTechs: string[]
  availableUseCases: string[]
  
  // Responsive state
  isCollapsed?: boolean
  onToggleCollapse?: () => void
}

const GRADES = ['A+', 'A', 'B+', 'B', 'C+', 'C', 'F']

const getGradeColor = (grade: string) => {
  switch (grade) {
    case 'A+': return 'bg-yellow-500 text-white'
    case 'A': return 'bg-emerald-600 text-white'
    case 'B+': return 'bg-cyan-600 text-white'
    case 'B': return 'bg-blue-600 text-white'
    case 'C+': return 'bg-amber-600 text-white'
    case 'C': return 'bg-orange-600 text-white'
    case 'F': return 'bg-slate-400 text-white'
    default: return 'bg-gray-400 text-white'
  }
}

const sortOptions = [
  { value: 'votes', label: 'Most Voted' },
  { value: 'grade', label: 'Grade (A+ → F)' },
  { value: 'funding', label: 'Funding' }
]

export function StartupFiltersPanel({
  // Search & Sort
  searchQuery,
  onSearchChange,
  sortBy,
  onSortChange,
  
  // Filters
  selectedStages,
  onStageChange,
  selectedTopics,
  onTopicChange,
  selectedTechs,
  onTechChange,
  selectedUseCases,
  onUseCaseChange,
  selectedGrades,
  onGradeChange,
  
  // Available options
  availableStages,
  availableTopics,
  availableTechs,
  availableUseCases,
  isCollapsed = false,
  onToggleCollapse
}: StartupFiltersPanelProps) {
  
  const activeFilterCount = useMemo(() => {
    return selectedStages.size + selectedTopics.size + selectedTechs.size + selectedUseCases.size + selectedGrades.size
  }, [selectedStages, selectedTopics, selectedTechs, selectedUseCases, selectedGrades])

  const clearAllFilters = () => {
    selectedStages.clear()
    selectedTopics.clear()
    selectedTechs.clear()
    selectedUseCases.clear()
    selectedGrades.clear()
    onSearchChange('')
  }

  const FilterGroup = ({ 
    title, 
    items, 
    selectedSet, 
    onChange,
    variant = 'default'
  }: { 
    title: string
    items: string[]
    selectedSet: Set<string>
    onChange: (item: string, selected: boolean) => void
    variant?: 'default' | 'grade'
  }) => {
    if (!items.length) return null

    return (
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <h4 className="text-xs font-semibold text-foreground uppercase tracking-wide">
            {title}
            {selectedSet.size > 0 && (
              <Badge variant="secondary" className="ml-2 text-xs">
                {selectedSet.size}
              </Badge>
            )}
          </h4>
        </div>
        
        <div className={cn(
          'space-y-2',
          variant === 'grade' && 'flex flex-wrap gap-2'
        )}>
          {items.map(item => (
            <div key={item} className={cn(
              variant === 'grade' && 'flex-shrink-0'
            )}>
              {variant === 'grade' ? (
                <button
                  onClick={() => onChange(item, !selectedSet.has(item))}
                  className={cn(
                    'rounded-md transition-all duration-200',
                    selectedSet.has(item) ? 'scale-105' : ''
                  )}
                >
                  <Badge
                    variant={selectedSet.has(item) ? 'default' : 'outline'}
                    className={cn(
                      'px-3 py-1 text-sm font-medium',
                      selectedSet.has(item) ? getGradeColor(item) : 'bg-muted text-muted-foreground'
                    )}
                  >
                    {item}
                  </Badge>
                </button>
              ) : (
                <label className="flex items-center gap-2.5 cursor-pointer group">
                  <input
                    type="checkbox"
                    checked={selectedSet.has(item)}
                    onChange={(e) => onChange(item, e.target.checked)}
                    className="w-4 h-4 rounded accent-primary cursor-pointer"
                  />
                  <span className="text-sm text-muted-foreground group-hover:text-foreground transition-colors">
                    {item}
                  </span>
                </label>
              )}
            </div>
          ))}
        </div>
      </div>
    )
  }

  if (isCollapsed && onToggleCollapse) {
    return (
      <div className="flex flex-col gap-3">
        {/* Search Bar */}
        <div className="relative">
          <Search 
            className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground pointer-events-none w-4 h-4"
           />
          <Input
            type="text"
            placeholder="Search startups..."
            value={searchQuery}
            onChange={(e) => onSearchChange(e.target.value)}
            className="pl-9 h-10"
          />
        </div>

        {/* Theme Switcher (collapsed view) */}
        <ThemeSwitcher />

        {/* Compact Filter Button */}
        <Button
          variant="outline"
          size="sm"
          onClick={onToggleCollapse}
          className="w-full justify-between"
        >
          <span className="flex items-center gap-2">
            <FilterSimple size={16}  />
            Filters
          </span>
          {activeFilterCount > 0 && (
            <Badge variant="secondary" className="ml-2">
              {activeFilterCount}
            </Badge>
          )}
        </Button>

        {/* Sort Dropdown */}
        <div className="flex flex-col gap-2">
          <label className="text-xs font-semibold text-foreground uppercase tracking-wide">Sort By</label>
          <div className="grid grid-cols-3 gap-2">
            {sortOptions.map(option => (
              <Button
                key={option.value}
                variant={sortBy === option.value ? "default" : "outline"}
                size="sm"
                onClick={() => onSortChange(option.value as 'votes' | 'funding' | 'grade')}
                className="text-xs"
              >
                {option.label}
              </Button>
            ))}
          </div>
        </div>
      </div>
    )
  }

  return (
    <Card className="border">
      {/* Header */}
      <div className="p-4 md:p-6 border-b bg-card sticky top-0 z-10 space-y-3">
        <div className="flex items-center justify-between">
          <h3 className="flex items-center gap-2 text-sm md:text-base font-bold text-foreground">
            <FilterSimple size={18}  />
            Filters & Search
          </h3>
          <div className="flex items-center gap-3">
            <ThemeSwitcher />
            {activeFilterCount > 0 && (
              <Button
                variant="ghost"
                size="sm"
                onClick={clearAllFilters}
                className="text-xs text-muted-foreground hover:text-foreground"
              >
                <Close className="mr-1 w-4 h-4"  />
                Clear All
              </Button>
            )}
          </div>
        </div>

        {/* Search Bar */}
        <div className="relative">
          <Search 
            className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground pointer-events-none w-4 h-4"
           />
          <Input
            type="text"
            placeholder="Search by startup name..."
            value={searchQuery}
            onChange={(e) => onSearchChange(e.target.value)}
            className="pl-9 h-10"
          />
        </div>
      </div>

      {/* Content */}
      <ScrollArea className="h-[calc(100vh-280px)]">
        <div className="p-4 md:p-6 space-y-6">
          {/* Sort Options */}
          <div className="space-y-3">
            <h4 className="text-xs font-semibold text-foreground uppercase tracking-wide">Sort By</h4>
            <div className="space-y-2">
              {sortOptions.map(option => (
                <Button
                  key={option.value}
                  variant={sortBy === option.value ? "default" : "outline"}
                  size="sm"
                  onClick={() => onSortChange(option.value as 'votes' | 'funding' | 'grade')}
                  className="w-full justify-start text-sm"
                >
                  {option.label}
                </Button>
              ))}
            </div>
          </div>

          <Separator className="my-4" />

          {/* Grade Filter */}
          <FilterGroup
            title="AXA Grade"
            items={GRADES}
            selectedSet={selectedGrades}
            onChange={onGradeChange}
            variant="grade"
          />

          <Separator className="my-4" />

          {/* Maturity Stage Filter */}
          <FilterGroup
            title="Maturity Stage"
            items={availableStages.filter(s => s && s.trim())}
            selectedSet={selectedStages}
            onChange={onStageChange}
          />

          {availableTopics.length > 0 && (
            <>
              <Separator className="my-4" />
              {/* Topics Filter */}
              <FilterGroup
                title="Topics"
                items={availableTopics.filter(t => t && t.trim())}
                selectedSet={selectedTopics}
                onChange={onTopicChange}
              />
            </>
          )}

          {availableTechs.length > 0 && (
            <>
              <Separator className="my-4" />
              {/* Technology Filter */}
              <FilterGroup
                title="Technology"
                items={availableTechs.filter(t => t && t.trim())}
                selectedSet={selectedTechs}
                onChange={onTechChange}
              />
            </>
          )}

          {availableUseCases.length > 0 && selectedTopics.size > 0 && (
            <>
              <Separator className="my-4" />
              {/* Use Cases Filter (only show if topic is selected) */}
              <FilterGroup
                title="Use Cases"
                items={availableUseCases.filter(u => u && u.trim())}
                selectedSet={selectedUseCases}
                onChange={onUseCaseChange}
              />
              <p className="text-xs text-muted-foreground italic">
                Select a topic above to filter use cases
              </p>
            </>
          )}
        </div>
      </ScrollArea>

      {/* Footer */}
      {activeFilterCount > 0 && (
        <div className="p-4 md:p-6 border-t bg-muted/30">
          <p className="text-xs text-muted-foreground">
            Showing results with <span className="font-semibold text-foreground">{activeFilterCount} active filter(s)</span>
          </p>
        </div>
      )}
    </Card>
  )
}
