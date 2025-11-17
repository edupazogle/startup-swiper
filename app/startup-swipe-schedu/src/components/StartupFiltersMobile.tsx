import { useState, useMemo } from 'react'
import { Close, Filter, Search, AngleDown, AngleUp } from 'flowbite-react-icons/outline'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { Separator } from '@/components/ui/separator'
import { Sheet, SheetContent, SheetHeader, SheetTitle, SheetTrigger } from '@/components/ui/sheet'
import { Drawer, DrawerContent, DrawerHeader, DrawerTitle, DrawerTrigger } from '@/components/ui/drawer'
import { ScrollArea } from '@/components/ui/scroll-area'
import { cn } from '@/lib/utils'
import { useIsMobile } from '@/hooks/use-mobile'

interface StartupFiltersMobileProps {
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
  { value: 'votes', label: 'Most Voted', icon: '👥' },
  { value: 'grade', label: 'Best Grade', icon: '⭐' },
  { value: 'funding', label: 'Top Funded', icon: '💰' }
]

export function StartupFiltersMobile(props: StartupFiltersMobileProps) {
  const isMobile = useIsMobile()
  const [isOpen, setIsOpen] = useState(false)

  const activeFilterCount = useMemo(() => {
    return props.selectedStages.size + 
           props.selectedTopics.size + 
           props.selectedTechs.size + 
           props.selectedUseCases.size + 
           props.selectedGrades.size
  }, [props.selectedStages, props.selectedTopics, props.selectedTechs, props.selectedUseCases, props.selectedGrades])

  const clearAllFilters = () => {
    props.selectedStages.clear()
    props.selectedTopics.clear()
    props.selectedTechs.clear()
    props.selectedUseCases.clear()
    props.selectedGrades.clear()
    props.onSearchChange('')
    // Force re-render
    props.onStageChange('', false)
  }

  // Filter Button Trigger (subtle, minimal)
  const FilterTrigger = () => (
    <Button
      variant="ghost"
      size="sm"
      className={cn(
        "relative gap-2 transition-all",
        activeFilterCount > 0 && "text-primary"
      )}
    >
      <FilterSimple 
        size={18}
        className="transition-all"
       />
      <span className="hidden sm:inline">Filters</span>
      {activeFilterCount > 0 && (
        <Badge 
          variant="default" 
          className="absolute -right-1 -top-1 h-5 w-5 rounded-full p-0 flex items-center justify-center text-xs"
        >
          {activeFilterCount}
        </Badge>
      )}
    </Button>
  )

  // Filter Content (reusable for both mobile and desktop)
  const FilterContent = () => {
    const [expandedSections, setExpandedSections] = useState<Set<string>>(new Set(['sort', 'grade']))

    const toggleSection = (section: string) => {
      const newExpanded = new Set(expandedSections)
      if (newExpanded.has(section)) {
        newExpanded.delete(section)
      } else {
        newExpanded.add(section)
      }
      setExpandedSections(newExpanded)
    }

    const CollapsibleSection = ({ 
      id,
      title, 
      count,
      children 
    }: { 
      id: string
      title: string
      count?: number
      children: React.ReactNode 
    }) => {
      const isExpanded = expandedSections.has(id)
      
      return (
        <div className="space-y-3">
          <button
            onClick={() => toggleSection(id)}
            className="flex items-center justify-between w-full text-left group"
          >
            <div className="flex items-center gap-2">
              <span className="text-sm font-semibold text-foreground uppercase tracking-wide">
                {title}
              </span>
              {count !== undefined && count > 0 && (
                <Badge variant="secondary" className="text-xs">
                  {count}
                </Badge>
              )}
            </div>
            {isExpanded ? (
              <AngleUp className="text-muted-foreground group-hover:text-foreground transition-colors w-4 h-4"  />
            ) : (
              <AngleDown className="text-muted-foreground group-hover:text-foreground transition-colors w-4 h-4"  />
            )}
          </button>
          
          {isExpanded && (
            <div className="animate-in slide-in-from-top-2 duration-200">
              {children}
            </div>
          )}
        </div>
      )
    }

    return (
      <div className="flex flex-col h-full">
        {/* Header */}
        <div className="pb-4 space-y-3">
          {/* Search */}
          <div className="relative">
            <Search 
              className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground w-4 h-4"
             />
            <Input
              type="text"
              placeholder="Search startups..."
              value={props.searchQuery}
              onChange={(e) => props.onSearchChange(e.target.value)}
              className="pl-9 h-10"
            />
          </div>

          {/* Clear All Button */}
          {activeFilterCount > 0 && (
            <Button
              variant="outline"
              size="sm"
              onClick={clearAllFilters}
              className="w-full text-xs"
            >
              <Close className="mr-1 w-4 h-4"  />
              Clear {activeFilterCount} filter{activeFilterCount !== 1 ? 's' : ''}
            </Button>
          )}
        </div>

        {/* Scrollable Filter Content */}
        <ScrollArea className="flex-1 -mx-4 px-4">
          <div className="space-y-4 pb-4">
            {/* Sort By */}
            <CollapsibleSection id="sort" title="Sort By">
              <div className="grid grid-cols-1 gap-2">
                {sortOptions.map(option => (
                  <button
                    key={option.value}
                    onClick={() => props.onSortChange(option.value as any)}
                    className={cn(
                      "flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all",
                      props.sortBy === option.value
                        ? "bg-primary text-primary-foreground shadow-sm"
                        : "bg-muted/50 text-muted-foreground hover:bg-muted hover:text-foreground"
                    )}
                  >
                    <span className="text-lg">{option.icon}</span>
                    {option.label}
                  </button>
                ))}
              </div>
            </CollapsibleSection>

            <Separator />

            {/* Grade Filter */}
            <CollapsibleSection id="grade" title="AXA Grade" count={props.selectedGrades.size}>
              <div className="flex flex-wrap gap-2">
                {GRADES.map(grade => (
                  <button
                    key={grade}
                    onClick={() => props.onGradeChange(grade, !props.selectedGrades.has(grade))}
                    className={cn(
                      "transition-all duration-200",
                      props.selectedGrades.has(grade) && "scale-105"
                    )}
                  >
                    <Badge
                      className={cn(
                        'px-3 py-1.5 text-sm font-medium cursor-pointer',
                        props.selectedGrades.has(grade) 
                          ? getGradeColor(grade) 
                          : 'bg-muted text-muted-foreground hover:bg-muted/80'
                      )}
                    >
                      {grade}
                    </Badge>
                  </button>
                ))}
              </div>
            </CollapsibleSection>

            {/* Maturity Stage */}
            {props.availableStages.length > 0 && (
              <>
                <Separator />
                <CollapsibleSection id="stage" title="Stage" count={props.selectedStages.size}>
                  <div className="space-y-2">
                    {props.availableStages.map(stage => (
                      <label key={stage} className="flex items-center gap-2.5 cursor-pointer group">
                        <input
                          type="checkbox"
                          checked={props.selectedStages.has(stage)}
                          onChange={(e) => props.onStageChange(stage, e.target.checked)}
                          className="w-4 h-4 rounded accent-primary cursor-pointer"
                        />
                        <span className="text-sm text-muted-foreground group-hover:text-foreground transition-colors">
                          {stage}
                        </span>
                      </label>
                    ))}
                  </div>
                </CollapsibleSection>
              </>
            )}

            {/* Topics */}
            {props.availableTopics.length > 0 && (
              <>
                <Separator />
                <CollapsibleSection id="topics" title="Topics" count={props.selectedTopics.size}>
                  <div className="space-y-2">
                    {props.availableTopics.slice(0, 10).map(topic => (
                      <label key={topic} className="flex items-center gap-2.5 cursor-pointer group">
                        <input
                          type="checkbox"
                          checked={props.selectedTopics.has(topic)}
                          onChange={(e) => props.onTopicChange(topic, e.target.checked)}
                          className="w-4 h-4 rounded accent-primary cursor-pointer"
                        />
                        <span className="text-sm text-muted-foreground group-hover:text-foreground transition-colors">
                          {topic}
                        </span>
                      </label>
                    ))}
                  </div>
                </CollapsibleSection>
              </>
            )}

            {/* Technology */}
            {props.availableTechs.length > 0 && (
              <>
                <Separator />
                <CollapsibleSection id="tech" title="Technology" count={props.selectedTechs.size}>
                  <div className="space-y-2">
                    {props.availableTechs.slice(0, 10).map(tech => (
                      <label key={tech} className="flex items-center gap-2.5 cursor-pointer group">
                        <input
                          type="checkbox"
                          checked={props.selectedTechs.has(tech)}
                          onChange={(e) => props.onTechChange(tech, e.target.checked)}
                          className="w-4 h-4 rounded accent-primary cursor-pointer"
                        />
                        <span className="text-sm text-muted-foreground group-hover:text-foreground transition-colors">
                          {tech}
                        </span>
                      </label>
                    ))}
                  </div>
                </CollapsibleSection>
              </>
            )}

            {/* Use Cases */}
            {props.availableUseCases.length > 0 && props.selectedTopics.size > 0 && (
              <>
                <Separator />
                <CollapsibleSection id="usecases" title="Use Cases" count={props.selectedUseCases.size}>
                  <div className="space-y-2">
                    {props.availableUseCases.map(useCase => (
                      <label key={useCase} className="flex items-center gap-2.5 cursor-pointer group">
                        <input
                          type="checkbox"
                          checked={props.selectedUseCases.has(useCase)}
                          onChange={(e) => props.onUseCaseChange(useCase, e.target.checked)}
                          className="w-4 h-4 rounded accent-primary cursor-pointer"
                        />
                        <span className="text-sm text-muted-foreground group-hover:text-foreground transition-colors">
                          {useCase}
                        </span>
                      </label>
                    ))}
                  </div>
                </CollapsibleSection>
              </>
            )}
          </div>
        </ScrollArea>
      </div>
    )
  }

  // Mobile: Bottom Drawer
  if (isMobile) {
    return (
      <Drawer open={isOpen} onOpenChange={setIsOpen}>
        <DrawerTrigger asChild>
          <FilterTrigger />
        </DrawerTrigger>
        <DrawerContent className="max-h-[85vh]">
          <DrawerHeader className="text-left border-b">
            <DrawerTitle className="flex items-center gap-2">
              <FilterSimple size={20}  />
              Filters & Sort
            </DrawerTitle>
          </DrawerHeader>
          <div className="p-4">
            <FilterContent />
          </div>
        </DrawerContent>
      </Drawer>
    )
  }

  // Desktop: Side Sheet
  return (
    <Sheet open={isOpen} onOpenChange={setIsOpen}>
      <SheetTrigger asChild>
        <FilterTrigger />
      </SheetTrigger>
      <SheetContent side="left" className="w-80 sm:w-96">
        <SheetHeader className="border-b pb-4 mb-4">
          <SheetTitle className="flex items-center gap-2">
            <FilterSimple size={20}  />
            Filters & Sort
          </SheetTitle>
        </SheetHeader>
        <FilterContent />
      </SheetContent>
    </Sheet>
  )
}
