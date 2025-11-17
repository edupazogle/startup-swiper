import { useState } from 'react'
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { ScrollArea } from '@/components/ui/scroll-area'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { TrashBin } from 'flowbite-react-icons/outline'
import { Idea, IdeaCategory } from '@/lib/types'

interface AddIdeaDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  onAdd: (idea: Omit<Idea, 'id' | 'timestamp'>) => void
}

export function AddIdeaDialog({ open, onOpenChange, onAdd }: AddIdeaDialogProps) {
  const [name, setName] = useState('')
  const [title, setTitle] = useState('')
  const [category, setCategory] = useState<IdeaCategory | ''>('')
  const [description, setDescription] = useState('')
  const [tags, setTags] = useState('')
  const [images, setImages] = useState<string[]>([])
  const [showError, setShowError] = useState(false)

  const handleImageUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files
    if (!files) return

    Array.from(files).forEach((file) => {
      if (file.type.startsWith('image/')) {
        const reader = new FileReader()
        reader.onloadend = () => {
          const result = reader.result as string
          setImages((prev) => [...prev, result])
        }
        reader.readAsDataURL(file)
      }
    })
  }

  const handleRemoveImage = (index: number) => {
    setImages((prev) => prev.filter((_, i) => i !== index))
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()

    if (!title || !category || !description) {
      setShowError(true)
      return
    }

    setShowError(false)

    const newIdea: Omit<Idea, 'id' | 'timestamp'> = {
      name: name || 'Anonymous',
      title,
      category: category as IdeaCategory,
      description,
      tags: tags
        .split(',')
        .map(tag => tag.trim())
        .filter(tag => tag.length > 0),
      images: images.length > 0 ? images : undefined
    }

    onAdd(newIdea)
    handleClose()
  }

  const handleClose = () => {
    setName('')
    setTitle('')
    setCategory('')
    setDescription('')
    setTags('')
    setImages([])
    setShowError(false)
    onOpenChange(false)
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[600px] max-h-[90vh] p-0">
        <DialogHeader className="px-6 pt-6">
          <DialogTitle className="text-2xl">Contribute Your Idea</DialogTitle>
        </DialogHeader>
        <ScrollArea className="max-h-[calc(90vh-100px)]">
          <form onSubmit={handleSubmit} className="space-y-5 px-6 pb-6">
            {showError && (
              <Alert className="bg-destructive/20 border-destructive/50 text-destructive-foreground">
                <AlertDescription className="text-sm">
                  Please fill out all required fields (Idea Title, Whitepaper Section, and Your Idea).
                </AlertDescription>
              </Alert>
            )}

            <div className="space-y-2">
              <Label htmlFor="idea-name">Your Name (Optional)</Label>
              <Input
                id="idea-name"
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="Jane Doe"
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="idea-title">Idea Title / Headline *</Label>
              <Input
                id="idea-title"
                type="text"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                placeholder="e.g., 'Agent-based Risk Modeling'"
                required
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="idea-category">Whitepaper Section *</Label>
              <Select value={category} onValueChange={(val) => setCategory(val as IdeaCategory)}>
                <SelectTrigger>
                  <SelectValue placeholder="Select a section..." />
                </SelectTrigger>
                <SelectContent className="max-h-[400px]">
                  <SelectItem value="1">
                    1. AI: Present and Future
                  </SelectItem>
                  <SelectItem value="2">
                    2. Agentic AI: The Forefront
                  </SelectItem>
                  <SelectItem value="3">
                    3. General Trends & Venture State
                  </SelectItem>
                  <SelectItem value="4">
                    4. Other AXA Priorities (Health, DeepTech, HR, etc.)
                  </SelectItem>
                  <SelectItem value="5">
                    5. AI Business Benefits & Adoption Scenarios 2030
                  </SelectItem>
                  <SelectItem value="6">
                    6. Tech & Ethical Choices for AI Systems
                  </SelectItem>
                  <SelectItem value="7">
                    7. Make or Buy in Agentic AI Era
                  </SelectItem>
                  <SelectItem value="8">
                    8. Talent and Culture
                  </SelectItem>
                  <SelectItem value="9">
                    9. Visionaries and Leaders
                  </SelectItem>
                  <SelectItem value="10">
                    10. Startups (UVP, Impact, Next Steps)
                  </SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label htmlFor="idea-description">Your Idea / Concept *</Label>
              <Textarea
                id="idea-description"
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                placeholder="Describe your observation, recommendation, or concept. What's the problem? What's the solution? What's the impact?"
                required
                className="min-h-[120px] resize-none"
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="idea-tags">Tags (Optional)</Label>
              <Input
                id="idea-tags"
                type="text"
                value={tags}
                onChange={(e) => setTags(e.target.value)}
                placeholder="e.g., startup, competitive-intelligence, vc, risk"
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="idea-images">Images (Optional)</Label>
              <div className="space-y-3">
                <Input
                  id="idea-images"
                  type="file"
                  accept="image/*"
                  multiple
                  onChange={handleImageUpload}
                />
                
                {images.length > 0 && (
                  <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
                    {images.map((image, index) => (
                      <div key={index} className="relative group">
                        <img
                          src={image}
                          alt={`Upload ${index + 1}`}
                          className="w-full h-24 object-cover rounded-lg border"
                        />
                        <button
                          type="button"
                          onClick={() => handleRemoveImage(index)}
                          className="absolute top-1 right-1 bg-destructive/80 hover:bg-destructive text-white rounded-full p-1.5 opacity-0 group-hover:opacity-100 transition-opacity"
                        >
                          <TrashBin className="w-4 h-4"  />
                        </button>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>

            <div className="flex gap-3 pt-4">
              <Button
                type="button"
                variant="outline"
                onClick={handleClose}
                size="default"
                className="flex-1"
              >
                Cancel
              </Button>
              <Button type="submit" size="default" className="flex-1">
                Submit Idea
              </Button>
            </div>
          </form>
        </ScrollArea>
      </DialogContent>
    </Dialog>
  )
}
