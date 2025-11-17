import { useState } from 'react'
import { AdvancedFilterDropdown } from '@/components/AdvancedFilterDropdown'

/**
 * Demo component showing the Advanced Filter Dropdown in action
 * Use this to preview the component before full integration
 */
export function AdvancedFilterDemo() {
  const [filters, setFilters] = useState({
    grades: new Set<string>(),
    stages: new Set<string>(),
    topics: new Set<string>(),
    techs: new Set<string>()
  })

  // Mock data for demonstration
  const demoSections = [
    {
      id: 'grades',
      title: 'Grade',
      options: [
        { id: 'A+', label: 'A+', count: 45, checked: filters.grades.has('A+') },
        { id: 'A', label: 'A', count: 78, checked: filters.grades.has('A') },
        { id: 'B+', label: 'B+', count: 123, checked: filters.grades.has('B+') },
        { id: 'B', label: 'B', count: 89, checked: filters.grades.has('B') },
        { id: 'C+', label: 'C+', count: 34, checked: filters.grades.has('C+') },
        { id: 'C', label: 'C', count: 21, checked: filters.grades.has('C') },
        { id: 'F', label: 'F', count: 12, checked: filters.grades.has('F') }
      ]
    },
    {
      id: 'stages',
      title: 'Funding Stage',
      options: [
        { id: 'seed', label: 'Seed', count: 156, checked: filters.stages.has('seed') },
        { id: 'series-a', label: 'Series A', count: 89, checked: filters.stages.has('series-a') },
        { id: 'series-b', label: 'Series B', count: 45, checked: filters.stages.has('series-b') },
        { id: 'series-c', label: 'Series C+', count: 23, checked: filters.stages.has('series-c') },
        { id: 'bootstrapped', label: 'Bootstrapped', count: 67, checked: filters.stages.has('bootstrapped') }
      ]
    },
    {
      id: 'topics',
      title: 'Industry Topics',
      options: [
        { id: 'ai', label: 'Artificial Intelligence', count: 234, checked: filters.topics.has('ai') },
        { id: 'fintech', label: 'FinTech', count: 178, checked: filters.topics.has('fintech') },
        { id: 'healthtech', label: 'HealthTech', count: 145, checked: filters.topics.has('healthtech') },
        { id: 'insurtech', label: 'InsurTech', count: 98, checked: filters.topics.has('insurtech') },
        { id: 'saas', label: 'SaaS', count: 289, checked: filters.topics.has('saas') },
        { id: 'cybersecurity', label: 'Cybersecurity', count: 67, checked: filters.topics.has('cybersecurity') },
        { id: 'blockchain', label: 'Blockchain', count: 54, checked: filters.topics.has('blockchain') }
      ]
    },
    {
      id: 'techs',
      title: 'Technologies',
      options: [
        { id: 'ml', label: 'Machine Learning', count: 189, checked: filters.techs.has('ml') },
        { id: 'nlp', label: 'Natural Language Processing', count: 123, checked: filters.techs.has('nlp') },
        { id: 'computer-vision', label: 'Computer Vision', count: 78, checked: filters.techs.has('computer-vision') },
        { id: 'cloud', label: 'Cloud Computing', count: 201, checked: filters.techs.has('cloud') },
        { id: 'mobile', label: 'Mobile Apps', count: 145, checked: filters.techs.has('mobile') },
        { id: 'web', label: 'Web Development', count: 267, checked: filters.techs.has('web') },
        { id: 'api', label: 'API Platform', count: 156, checked: filters.techs.has('api') }
      ]
    }
  ]

  const handleFilterChange = (sectionId: string, optionId: string, checked: boolean) => {
    setFilters(prev => {
      const section = sectionId as keyof typeof prev
      const newSet = new Set(prev[section])
      
      if (checked) {
        newSet.add(optionId)
      } else {
        newSet.delete(optionId)
      }
      
      return { ...prev, [section]: newSet }
    })
  }

  const handleClearAll = () => {
    setFilters({
      grades: new Set(),
      stages: new Set(),
      topics: new Set(),
      techs: new Set()
    })
  }

  const activeCount = filters.grades.size + filters.stages.size + filters.topics.size + filters.techs.size

  // Display selected filters
  const selectedFilters = [
    ...Array.from(filters.grades).map(id => ({ section: 'Grade', value: id })),
    ...Array.from(filters.stages).map(id => ({ section: 'Stage', value: id })),
    ...Array.from(filters.topics).map(id => ({ section: 'Topic', value: id })),
    ...Array.from(filters.techs).map(id => ({ section: 'Tech', value: id }))
  ]

  return (
    <div className="p-8 min-h-screen bg-neutral-secondary">
      <div className="max-w-4xl mx-auto space-y-6">
        {/* Header */}
        <div>
          <h1 className="text-3xl font-bold text-heading mb-2">
            Advanced Filter Dropdown Demo
          </h1>
          <p className="text-body">
            Interactive preview of the Flowbite-style filter component
          </p>
        </div>

        {/* Demo Section */}
        <div className="bg-neutral-primary border border-default rounded-lg p-6 space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-xl font-semibold text-heading">
              Filter Startups
            </h2>
            
            {/* The Filter Component */}
            <AdvancedFilterDropdown
              sections={demoSections}
              onFilterChange={handleFilterChange}
              onClearAll={handleClearAll}
              activeCount={activeCount}
              buttonLabel="Filter startups"
            />
          </div>

          {/* Selected Filters Display */}
          {activeCount > 0 && (
            <div className="border-t border-default-medium pt-4">
              <h3 className="text-sm font-semibold text-heading mb-3">
                Active Filters ({activeCount})
              </h3>
              <div className="flex flex-wrap gap-2">
                {selectedFilters.map((filter, index) => (
                  <span
                    key={`${filter.section}-${filter.value}-${index}`}
                    className="inline-flex items-center gap-2 px-3 py-1.5 bg-brand/10 border border-brand/20 text-fg-brand text-sm rounded-base"
                  >
                    <span className="font-medium">{filter.section}:</span>
                    <span>{filter.value}</span>
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* Stats */}
          <div className="border-t border-default-medium pt-4">
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="bg-neutral-secondary rounded-base p-4">
                <div className="text-2xl font-bold text-heading">402</div>
                <div className="text-sm text-body">Total Startups</div>
              </div>
              <div className="bg-neutral-secondary rounded-base p-4">
                <div className="text-2xl font-bold text-brand">{activeCount}</div>
                <div className="text-sm text-body">Active Filters</div>
              </div>
              <div className="bg-neutral-secondary rounded-base p-4">
                <div className="text-2xl font-bold text-success">
                  {activeCount > 0 ? Math.max(10, 402 - activeCount * 15) : 402}
                </div>
                <div className="text-sm text-body">Filtered Results</div>
              </div>
              <div className="bg-neutral-secondary rounded-base p-4">
                <div className="text-2xl font-bold text-heading">28</div>
                <div className="text-sm text-body">Filter Options</div>
              </div>
            </div>
          </div>
        </div>

        {/* Features List */}
        <div className="bg-neutral-primary border border-default rounded-lg p-6">
          <h2 className="text-xl font-semibold text-heading mb-4">
            ✨ Features
          </h2>
          <ul className="space-y-2 text-body">
            <li className="flex items-start gap-2">
              <span className="text-success mt-1">✓</span>
              <span>Search functionality to filter options by keyword</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="text-success mt-1">✓</span>
              <span>Multi-select checkboxes organized by category</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="text-success mt-1">✓</span>
              <span>Real-time item counts for each filter option</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="text-success mt-1">✓</span>
              <span>Active filter count badge on the button</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="text-success mt-1">✓</span>
              <span>One-click "Clear all filters" functionality</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="text-success mt-1">✓</span>
              <span>Click outside to close dropdown</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="text-success mt-1">✓</span>
              <span>Smooth animations and transitions</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="text-success mt-1">✓</span>
              <span>Mobile-responsive design</span>
            </li>
          </ul>
        </div>

        {/* Code Example */}
        <div className="bg-neutral-primary border border-default rounded-lg p-6">
          <h2 className="text-xl font-semibold text-heading mb-4">
            💻 Usage
          </h2>
          <pre className="bg-neutral-secondary rounded-base p-4 overflow-x-auto text-sm text-body">
{`<AdvancedFilterDropdown
  sections={filterSections}
  onFilterChange={handleFilterChange}
  onClearAll={handleClearAll}
  activeCount={activeFilterCount}
  buttonLabel="Filter startups"
/>`}
          </pre>
        </div>
      </div>
    </div>
  )
}

/**
 * To use this demo:
 * 
 * 1. Add a route in your router:
 *    <Route path="/demo/filters" element={<AdvancedFilterDemo />} />
 * 
 * 2. Navigate to /demo/filters to see the component in action
 * 
 * 3. Interact with the filter dropdown to test all features
 */
