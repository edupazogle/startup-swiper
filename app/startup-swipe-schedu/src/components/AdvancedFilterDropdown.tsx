import { useState, useEffect, useRef } from 'react'
import { Search, Filter, Close } from 'flowbite-react-icons/outline'
import { cn } from '@/lib/utils'

interface FilterOption {
  id: string
  label: string
  count?: number
  checked: boolean
}

interface FilterSection {
  id: string
  title: string
  options: FilterOption[]
}

interface AdvancedFilterDropdownProps {
  sections: FilterSection[]
  onFilterChange: (sectionId: string, optionId: string, checked: boolean) => void
  onClearAll?: () => void
  activeCount?: number
  buttonLabel?: string
}

export function AdvancedFilterDropdown({
  sections,
  onFilterChange,
  onClearAll,
  activeCount = 0,
  buttonLabel = 'Filter startups'
}: AdvancedFilterDropdownProps) {
  const [isOpen, setIsOpen] = useState(false)
  const [searchTerm, setSearchTerm] = useState('')
  const dropdownRef = useRef<HTMLDivElement>(null)

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false)
      }
    }

    if (isOpen) {
      document.addEventListener('mousedown', handleClickOutside)
    }

    return () => {
      document.removeEventListener('mousedown', handleClickOutside)
    }
  }, [isOpen])

  // Initialize Flowbite dropdown on mount (if needed)
  useEffect(() => {
    // Flowbite initialization is handled by the component itself
    // No need for external initialization
  }, [])

  const handleToggle = () => {
    setIsOpen(!isOpen)
  }

  const handleCheckboxChange = (sectionId: string, optionId: string, checked: boolean) => {
    onFilterChange(sectionId, optionId, checked)
  }

  const handleClearAll = () => {
    onClearAll?.()
    setSearchTerm('')
  }

  // Filter options based on search term
  const filteredSections = sections.map(section => ({
    ...section,
    options: section.options.filter(option =>
      option.label.toLowerCase().includes(searchTerm.toLowerCase())
    )
  })).filter(section => section.options.length > 0)

  return (
    <div ref={dropdownRef} className="relative inline-block">
      {/* Trigger Button */}
      <button
        onClick={handleToggle}
        type="button"
        className="inline-flex items-center gap-2 text-gray-700 dark:text-gray-200 bg-gray-100 dark:bg-gray-700 border-2 border-gray-300 dark:border-gray-600 hover:bg-gray-200 dark:hover:bg-gray-600 focus:ring-2 focus:outline-none focus:ring-blue-500 font-semibold rounded-lg text-sm px-4 py-2.5 transition-all"
      >
        <Filter className="w-4 h-4"  />
        <span className="whitespace-nowrap">{buttonLabel}</span>
        {activeCount > 0 && (
          <span className="inline-flex items-center justify-center min-w-[20px] h-5 px-1.5 text-xs font-bold text-white bg-blue-600 dark:bg-blue-500 rounded-full">
            {activeCount}
          </span>
        )}
        <svg
          className={cn(
            "w-3 h-3 transition-transform",
            isOpen && "rotate-180"
          )}
          aria-hidden="true"
          xmlns="http://www.w3.org/2000/svg"
          fill="none"
          viewBox="0 0 10 6"
        >
          <path
            stroke="currentColor"
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth="2"
            d="m1 1 4 4 4-4"
          />
        </svg>
      </button>

      {/* Dropdown Menu */}
      <div
        className={cn(
          "absolute right-0 z-50 mt-2 w-80 bg-white dark:bg-gray-800 border-2 border-gray-200 dark:border-gray-700 rounded-lg shadow-xl transition-all duration-200 origin-top-right overflow-hidden",
          isOpen ? "opacity-100 scale-100" : "opacity-0 scale-95 pointer-events-none"
        )}
      >
        {/* Search Bar */}
        <div className="p-3 border-b-2 border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-900/50">
          <div className="relative">
            <div className="absolute inset-y-0 left-0 flex items-center pl-3 pointer-events-none">
              <Search className="w-4 h-4 text-gray-500 dark:text-gray-400" />
            </div>
            <input
              type="text"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="block w-full pl-10 pr-9 py-2 bg-white dark:bg-gray-800 border-2 border-gray-300 dark:border-gray-600 text-gray-900 dark:text-gray-100 text-sm rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 placeholder:text-gray-500 dark:placeholder:text-gray-400 font-medium transition-all"
              placeholder="Search filters..."
            />
            {searchTerm && (
              <button
                onClick={() => setSearchTerm('')}
                className="absolute inset-y-0 right-0 flex items-center pr-3 text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-200 transition-colors"
              >
                <Close className="w-4 h-4"  />
              </button>
            )}
          </div>
        </div>

        {/* Filter Options - Scrollable */}
        <div className="max-h-96 overflow-y-auto p-2">
          {filteredSections.length > 0 ? (
            filteredSections.map((section) => (
              <div key={section.id} className="mb-4 last:mb-0">
                <h3 className="px-2 py-2 text-xs font-bold text-gray-600 dark:text-gray-400 uppercase tracking-wider">
                  {section.title}
                </h3>
                <ul className="space-y-1">
                  {section.options.map((option) => (
                    <li key={option.id}>
                      <label
                        className={cn(
                          "flex items-center justify-between w-full p-2.5 cursor-pointer rounded-lg group transition-colors",
                          option.checked 
                            ? "bg-blue-50 dark:bg-blue-900/30 border-2 border-blue-200 dark:border-blue-700" 
                            : "hover:bg-gray-100 dark:hover:bg-gray-700 border-2 border-transparent"
                        )}
                      >
                        <div className="flex items-center gap-2.5 flex-1 min-w-0">
                          <input
                            type="checkbox"
                            checked={option.checked}
                            onChange={(e) =>
                              handleCheckboxChange(section.id, option.id, e.target.checked)
                            }
                            className="w-4 h-4 border-2 border-gray-400 dark:border-gray-500 rounded bg-white dark:bg-gray-700 focus:ring-2 focus:ring-blue-500 text-blue-600 cursor-pointer transition-all"
                          />
                          <span className={cn(
                            "text-sm font-semibold truncate transition-colors",
                            option.checked 
                              ? "text-gray-900 dark:text-gray-100" 
                              : "text-gray-700 dark:text-gray-300 group-hover:text-gray-900 dark:group-hover:text-gray-100"
                          )}>
                            {option.label}
                          </span>
                        </div>
                        {option.count !== undefined && (
                          <span className="text-xs text-gray-500 dark:text-gray-400 font-semibold ml-2 shrink-0">
                            ({option.count})
                          </span>
                        )}
                      </label>
                    </li>
                  ))}
                </ul>
              </div>
            ))
          ) : (
            <div className="py-8 text-center">
              <Search className="w-8 h-8 mx-auto text-gray-400 dark:text-gray-500 mb-2" />
              <p className="text-sm text-gray-600 dark:text-gray-400 font-medium">No filters match "{searchTerm}"</p>
            </div>
          )}
        </div>

        {/* Footer Actions */}
        {activeCount > 0 && (
          <div className="p-2 border-t-2 border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-900/50">
            <button
              onClick={handleClearAll}
              className="w-full inline-flex items-center justify-center gap-2 px-3 py-2.5 text-sm font-semibold text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-900/20 rounded-lg transition-colors"
            >
              <Close className="w-4 h-4"  />
              Clear all filters
            </button>
          </div>
        )}
      </div>
    </div>
  )
}
