/**
 * Example implementation of AdvancedFilterDropdown for DashboardView
 * 
 * This shows how to integrate the Flowbite-style advanced filter dropdown
 * with your existing startup filtering logic.
 */

import { useState, useMemo } from 'react'
import { AdvancedFilterDropdown } from '@/components/AdvancedFilterDropdown'
import { Startup, Vote } from '@/lib/types'

interface FilterExampleProps {
  startups: Startup[]
  votes: Vote[]
  onFilteredStartupsChange: (startups: Startup[]) => void
}

export function AdvancedFilterExample({ startups, votes, onFilteredStartupsChange }: FilterExampleProps) {
  // State for selected filters
  const [selectedGrades, setSelectedGrades] = useState<Set<string>>(new Set())
  const [selectedStages, setSelectedStages] = useState<Set<string>>(new Set())
  const [selectedTopics, setSelectedTopics] = useState<Set<string>>(new Set())
  const [selectedTechs, setSelectedTechs] = useState<Set<string>>(new Set())

  // Count startups for each filter option
  const filterCounts = useMemo(() => {
    const grades = new Map<string, number>()
    const stages = new Map<string, number>()
    const topics = new Map<string, number>()
    const techs = new Map<string, number>()

    startups.forEach(startup => {
      // Count grades
      const grade = startup.axa_grade || startup.axaGrade
      if (grade) grades.set(grade, (grades.get(grade) || 0) + 1)

      // Count stages
      const stage = startup.funding_stage || startup.currentInvestmentStage || startup.Stage
      if (stage) stages.set(stage, (stages.get(stage) || 0) + 1)

      // Count topics
      const topicList = Array.isArray(startup.topics) ? startup.topics : []
      topicList.forEach(topic => {
        topics.set(topic, (topics.get(topic) || 0) + 1)
      })

      // Count technologies
      const techList = Array.isArray(startup.tech) ? startup.tech : []
      techList.forEach(tech => {
        techs.set(tech, (techs.get(tech) || 0) + 1)
      })
    })

    return { grades, stages, topics, techs }
  }, [startups])

  // Build filter sections dynamically
  const filterSections = useMemo(() => [
    {
      id: 'grades',
      title: 'Grade',
      options: ['A+', 'A', 'B+', 'B', 'C+', 'C', 'F'].map(grade => ({
        id: grade,
        label: grade,
        count: filterCounts.grades.get(grade) || 0,
        checked: selectedGrades.has(grade)
      }))
    },
    {
      id: 'stages',
      title: 'Stage',
      options: Array.from(filterCounts.stages.keys())
        .sort()
        .map(stage => ({
          id: stage,
          label: stage,
          count: filterCounts.stages.get(stage) || 0,
          checked: selectedStages.has(stage)
        }))
    },
    {
      id: 'topics',
      title: 'Topics',
      options: Array.from(filterCounts.topics.keys())
        .sort()
        .map(topic => ({
          id: topic,
          label: topic,
          count: filterCounts.topics.get(topic) || 0,
          checked: selectedTopics.has(topic)
        }))
    },
    {
      id: 'technologies',
      title: 'Technologies',
      options: Array.from(filterCounts.techs.keys())
        .sort()
        .map(tech => ({
          id: tech,
          label: tech,
          count: filterCounts.techs.get(tech) || 0,
          checked: selectedTechs.has(tech)
        }))
    }
  ], [filterCounts, selectedGrades, selectedStages, selectedTopics, selectedTechs])

  // Handle filter changes
  const handleFilterChange = (sectionId: string, optionId: string, checked: boolean) => {
    switch (sectionId) {
      case 'grades':
        setSelectedGrades(prev => {
          const newSet = new Set(prev)
          checked ? newSet.add(optionId) : newSet.delete(optionId)
          return newSet
        })
        break
      case 'stages':
        setSelectedStages(prev => {
          const newSet = new Set(prev)
          checked ? newSet.add(optionId) : newSet.delete(optionId)
          return newSet
        })
        break
      case 'topics':
        setSelectedTopics(prev => {
          const newSet = new Set(prev)
          checked ? newSet.add(optionId) : newSet.delete(optionId)
          return newSet
        })
        break
      case 'technologies':
        setSelectedTechs(prev => {
          const newSet = new Set(prev)
          checked ? newSet.add(optionId) : newSet.delete(optionId)
          return newSet
        })
        break
    }
  }

  // Clear all filters
  const handleClearAll = () => {
    setSelectedGrades(new Set())
    setSelectedStages(new Set())
    setSelectedTopics(new Set())
    setSelectedTechs(new Set())
  }

  // Calculate active filter count
  const activeFilterCount = selectedGrades.size + selectedStages.size + selectedTopics.size + selectedTechs.size

  // Filter startups based on selections
  const filteredStartups = useMemo(() => {
    if (activeFilterCount === 0) return startups

    return startups.filter(startup => {
      // Check grade filter
      if (selectedGrades.size > 0) {
        const grade = startup.axa_grade || startup.axaGrade
        if (!grade || !selectedGrades.has(grade)) return false
      }

      // Check stage filter
      if (selectedStages.size > 0) {
        const stage = startup.funding_stage || startup.currentInvestmentStage || startup.Stage
        if (!stage || !selectedStages.has(stage)) return false
      }

      // Check topics filter
      if (selectedTopics.size > 0) {
        const topicList = Array.isArray(startup.topics) ? startup.topics : []
        if (!topicList.some(topic => selectedTopics.has(topic))) return false
      }

      // Check technologies filter
      if (selectedTechs.size > 0) {
        const techList = Array.isArray(startup.tech) ? startup.tech : []
        if (!techList.some(tech => selectedTechs.has(tech))) return false
      }

      return true
    })
  }, [startups, selectedGrades, selectedStages, selectedTopics, selectedTechs, activeFilterCount])

  // Update parent component when filtered startups change
  useMemo(() => {
    onFilteredStartupsChange(filteredStartups)
  }, [filteredStartups, onFilteredStartupsChange])

  return (
    <AdvancedFilterDropdown
      sections={filterSections}
      onFilterChange={handleFilterChange}
      onClearAll={handleClearAll}
      activeCount={activeFilterCount}
      buttonLabel="Filter startups"
    />
  )
}

/**
 * Integration example for DashboardView.tsx:
 * 
 * 1. Import the component:
 *    import { AdvancedFilterExample } from '@/components/examples/AdvancedFilterExample'
 * 
 * 2. Add state for filtered startups:
 *    const [filteredStartups, setFilteredStartups] = useState<Startup[]>(startups)
 * 
 * 3. Replace StartupFiltersPanel with:
 *    <AdvancedFilterExample
 *      startups={startups}
 *      votes={votes}
 *      onFilteredStartupsChange={setFilteredStartups}
 *    />
 * 
 * 4. Use filteredStartups instead of startupsWithVotes in your rendering logic
 */
