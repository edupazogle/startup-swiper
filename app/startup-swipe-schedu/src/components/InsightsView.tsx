import { Idea, IdeaCategory } from '@/lib/types'
import { Lightbulb, PencilSimple } from '@phosphor-icons/react'
import { useState } from 'react'
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'
import { api } from '@/lib/api'
import { toast } from 'sonner'

interface InsightsViewProps {
  ideas: Idea[]
  onIdeaUpdated?: () => void
}

export function InsightsView({ ideas, onIdeaUpdated }: InsightsViewProps) {
  const [editingIdea, setEditingIdea] = useState<Idea | null>(null)
  const [editTitle, setEditTitle] = useState('')
  const [editDescription, setEditDescription] = useState('')
  const [editTags, setEditTags] = useState('')
  const [isSaving, setIsSaving] = useState(false)

  const handleEditClick = (idea: Idea) => {
    setEditingIdea(idea)
    setEditTitle(idea.title)
    setEditDescription(idea.description)
    setEditTags(idea.tags.join(', '))
  }

  const handleSaveEdit = async () => {
    if (!editingIdea) return
    
    setIsSaving(true)
    try {
      await api.updateIdea(editingIdea.id, {
        title: editTitle,
        description: editDescription,
        tags: editTags.split(',').map(t => t.trim()).filter(t => t),
        name: editingIdea.name,
        timestamp: editingIdea.timestamp,
        category: editingIdea.category,
        images: editingIdea.images || []
      })
      
      toast.success('Insight updated successfully')
      setEditingIdea(null)
      if (onIdeaUpdated) {
        onIdeaUpdated()
      }
    } catch (error) {
      console.error('Error updating insight:', error)
      toast.error('Failed to update insight')
    } finally {
      setIsSaving(false)
    }
  }

  const categoryConfig: Record<IdeaCategory, { title: string; description: string; color: string; section: 'observed' | 'impacts' | 'meetings' }> = {
    '1': {
      title: '1. AI: Present and Future',
      description: 'Overview of AI evolution, foundation models, multimodal AI, self-supervised learning. Include adoption rates, investments, and key companies.',
      color: 'blue',
      section: 'observed'
    },
    '2': {
      title: '2. Agentic AI: The Forefront',
      description: 'Autonomous decision-making systems revolutionizing customer interactions, claims processing, underwriting, and software development.',
      color: 'purple',
      section: 'observed'
    },
    '3': {
      title: '3. General Trends & Venture State',
      description: 'Venture funding trends, notable startups, enterprise AI investments. Include VC insights and conference statistics.',
      color: 'green',
      section: 'observed'
    },
    '4': {
      title: '4. Other AXA Priorities',
      description: 'Health, DeepTech (Quantum, Energy), HR, Sustainability and other strategic focus areas.',
      color: 'teal',
      section: 'observed'
    },
    '5': {
      title: '5. AI Business Benefits & Adoption 2030',
      description: 'How AI benefits claims, underwriting, customer service, software development. AI adoption scenarios 2027-2030 with impact quantification.',
      color: 'orange',
      section: 'impacts'
    },
    '6': {
      title: '6. Tech & Ethical Choices',
      description: 'Recommendations for robustness, explainability, scalability, interoperability, ethical governance, and regulatory positioning.',
      color: 'pink',
      section: 'impacts'
    },
    '7': {
      title: '7. Make or Buy in Agentic AI Era',
      description: 'Learnings from innovation teams, startups, and scaleups on build vs. partner decisions.',
      color: 'yellow',
      section: 'impacts'
    },
    '8': {
      title: '8. Talent and Culture',
      description: 'Insights on team building, culture development, and organizational practices from peers and scaleups.',
      color: 'indigo',
      section: 'impacts'
    },
    '9': {
      title: '9. Visionaries and Leaders',
      description: 'Key people met: background, role, and their key messages and insights.',
      color: 'red',
      section: 'meetings'
    },
    '10': {
      title: '10. Startups',
      description: 'Company name, unique value proposition (UVP), foreseen impact for AXA, and potential next steps.',
      color: 'cyan',
      section: 'meetings'
    }
  }

  const getColorClasses = (color: string) => {
    const colorMap: Record<string, { title: string; tag: string }> = {
      blue: {
        title: 'text-blue-700',
        tag: 'bg-blue-500/30 text-blue-800 border-blue-600/40'
      },
      purple: {
        title: 'text-purple-700',
        tag: 'bg-purple-500/30 text-purple-800 border-purple-600/40'
      },
      green: {
        title: 'text-green-700',
        tag: 'bg-green-500/30 text-green-800 border-green-600/40'
      },
      teal: {
        title: 'text-teal-700',
        tag: 'bg-teal-500/30 text-teal-800 border-teal-600/40'
      },
      orange: {
        title: 'text-orange-700',
        tag: 'bg-orange-500/30 text-orange-800 border-orange-600/40'
      },
      pink: {
        title: 'text-pink-700',
        tag: 'bg-pink-500/30 text-pink-800 border-pink-600/40'
      },
      yellow: {
        title: 'text-yellow-700',
        tag: 'bg-yellow-500/30 text-yellow-800 border-yellow-600/40'
      },
      indigo: {
        title: 'text-indigo-700',
        tag: 'bg-indigo-500/30 text-indigo-800 border-indigo-600/40'
      },
      red: {
        title: 'text-red-700',
        tag: 'bg-red-500/30 text-red-800 border-red-600/40'
      },
      cyan: {
        title: 'text-cyan-700',
        tag: 'bg-cyan-500/30 text-cyan-800 border-cyan-600/40'
      }
    }
    return colorMap[color] || colorMap.blue
  }

  const getIdeasByCategory = (category: IdeaCategory) => {
    return ideas.filter(idea => idea.category === category).sort((a, b) => b.timestamp - a.timestamp)
  }

  const getSectionTitle = (section: 'observed' | 'impacts' | 'meetings') => {
    switch (section) {
      case 'observed':
        return 'I. Observed Trends'
      case 'impacts':
        return 'II. Impacts on AXA and Insurance'
      case 'meetings':
        return 'III. Key Meetings and Insights'
      default:
        return ''
    }
  }

  const categoriesBySection = {
    observed: ['1', '2', '3', '4'] as IdeaCategory[],
    impacts: ['5', '6', '7', '8'] as IdeaCategory[],
    meetings: ['9', '10'] as IdeaCategory[]
  }

  return (
    <div className="h-full overflow-y-auto">
      <div className="max-w-[1800px] mx-auto px-4 sm:px-6 lg:px-8 py-6 md:py-8">
        <div className="text-center mb-6 md:mb-8">
          <h2 className="text-2xl md:text-3xl lg:text-4xl font-bold tracking-tight text-white drop-shadow-lg mb-2 md:mb-3">
            Slush 2025 Whitepaper Insights
          </h2>
          <p className="text-sm md:text-base lg:text-lg text-white drop-shadow-md max-w-3xl mx-auto">
            Contribute observations, learnings, and insights organized by whitepaper sections. These will form the foundation of our post-event report.
          </p>
        </div>

        {(['observed', 'impacts', 'meetings'] as const).map((section) => (
          <div key={section} className="mb-10 md:mb-12">
            <h3 className="text-xl md:text-2xl font-bold text-white drop-shadow-lg mb-4 md:mb-6 pb-2 border-b border-white/30">
              {getSectionTitle(section)}
            </h3>
            
            <div className={`grid grid-cols-1 ${section === 'meetings' ? 'md:grid-cols-2' : 'md:grid-cols-2 xl:grid-cols-4'} gap-4 md:gap-5`}>
              {categoriesBySection[section].map((categoryId) => {
                const config = categoryConfig[categoryId]
                const categoryIdeas = getIdeasByCategory(categoryId)
                const colors = getColorClasses(config.color)

                return (
                  <section
                    key={categoryId}
                    className="bg-white/80 backdrop-blur-md rounded-md p-4 md:p-5 border border-white/40 shadow-lg"
                  >
                    <h4 className={`text-sm md:text-base font-semibold ${colors.title} mb-2`}>
                      {config.title}
                    </h4>
                    <p className="text-xs text-gray-700 mb-4 leading-relaxed">
                      {config.description}
                    </p>

                    <div className="space-y-3 h-[40vh] md:h-[45vh] overflow-y-auto pr-2">
                      {categoryIdeas.length === 0 ? (
                        <div className="flex flex-col items-center justify-center py-6 md:py-8 text-center">
                          <Lightbulb size={28} className="text-gray-400 mb-2" />
                          <p className="text-xs text-gray-600 italic">
                            No insights yet. Be the first!
                          </p>
                        </div>
                      ) : (
                        categoryIdeas.map((idea) => (
                          <div
                            key={idea.id}
                            className="bg-white/60 backdrop-blur-sm rounded-md p-3 shadow-md border border-white/30 transition-all duration-200 hover:bg-white/75 hover:border-white/50 relative group"
                          >
                            <button
                              onClick={() => handleEditClick(idea)}
                              className="absolute top-2 right-2 opacity-0 group-hover:opacity-100 transition-opacity p-1.5 rounded-md bg-white/80 hover:bg-white shadow-sm"
                              title="Edit insight"
                            >
                              <PencilSimple size={14} weight="bold" className="text-gray-700" />
                            </button>
                            
                            <h5 className="font-semibold text-gray-900 text-sm mb-2 pr-8">
                              {idea.title}
                            </h5>
                            <p className="text-xs text-gray-800 mb-3 whitespace-pre-wrap leading-relaxed">
                              {idea.description}
                            </p>

                            {idea.images && idea.images.length > 0 && (
                              <div className={`mb-3 ${idea.images.length === 1 ? '' : 'grid grid-cols-2 gap-2'}`}>
                                {idea.images.map((image, idx) => (
                                  <img
                                    key={idx}
                                    src={image}
                                    alt={`${idea.title} - Image ${idx + 1}`}
                                    className="w-full h-28 object-cover rounded-md border border-gray-300"
                                  />
                                ))}
                              </div>
                            )}

                            {idea.tags.length > 0 && (
                              <div className="flex flex-wrap gap-1 mb-3">
                                {idea.tags.map((tag, idx) => (
                                  <span
                                    key={idx}
                                    className={`inline-block text-[10px] font-medium px-2 py-0.5 rounded-md border ${colors.tag}`}
                                  >
                                    {tag}
                                  </span>
                                ))}
                              </div>
                            )}

                            <p className="text-[10px] text-gray-600 italic text-right border-t border-gray-300 pt-2 mt-2">
                              Submitted by: {idea.name}
                            </p>
                          </div>
                        ))
                      )}
                    </div>
                  </section>
                )
              })}
            </div>
          </div>
        ))}
      </div>

      {/* Edit Dialog */}
      <Dialog open={editingIdea !== null} onOpenChange={(open) => !open && setEditingIdea(null)}>
        <DialogContent className="sm:max-w-[600px]">
          <DialogHeader>
            <DialogTitle>Edit Insight</DialogTitle>
          </DialogHeader>
          <div className="space-y-4 py-4">
            <div>
              <label className="text-sm font-medium mb-1.5 block">Title</label>
              <Input
                value={editTitle}
                onChange={(e) => setEditTitle(e.target.value)}
                placeholder="Enter insight title"
              />
            </div>
            <div>
              <label className="text-sm font-medium mb-1.5 block">Description</label>
              <Textarea
                value={editDescription}
                onChange={(e) => setEditDescription(e.target.value)}
                placeholder="Enter insight description"
                rows={6}
                className="resize-none"
              />
            </div>
            <div>
              <label className="text-sm font-medium mb-1.5 block">Tags (comma separated)</label>
              <Input
                value={editTags}
                onChange={(e) => setEditTags(e.target.value)}
                placeholder="e.g., AI, Insurance, Innovation"
              />
            </div>
            <div className="flex justify-end gap-2 pt-2">
              <Button
                variant="outline"
                onClick={() => setEditingIdea(null)}
                disabled={isSaving}
              >
                Cancel
              </Button>
              <Button
                onClick={handleSaveEdit}
                disabled={isSaving}
              >
                {isSaving ? 'Saving...' : 'Save Changes'}
              </Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  )
}
