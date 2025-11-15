import { useState } from 'react'
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'
import { Label } from '@/components/ui/label'
import { ScrollArea } from '@/components/ui/scroll-area'
import { Startup } from '@/lib/types'

interface AddStartupDialogProps {
  open?: boolean
  onOpenChange?: (open: boolean) => void
  onAdd: (startup: Omit<Startup, 'id'>) => void
}

export function AddStartupDialog({ open: externalOpen, onOpenChange: externalOnOpenChange, onAdd }: AddStartupDialogProps) {
  const [internalOpen, setInternalOpen] = useState(false)
  const [formData, setFormData] = useState({
    companyName: '',
    companyDescription: '',
    category: '',
    axaCategory: '',
    stage: '',
    headquarterCountry: '',
    funding: '',
    usp: '',
    finalPriorityScore: 50,
    logo: '',
    website: '',
    contactPerson: '',
    contactEmail: ''
  })

  const open = externalOpen !== undefined ? externalOpen : internalOpen
  const setOpen = externalOnOpenChange || setInternalOpen

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!formData.companyName || !formData.companyDescription || !formData.category || !formData.stage) {
      return
    }

    onAdd({
      name: formData.companyName,
      shortDescription: formData.usp || formData.companyDescription.substring(0, 200),
      description: formData.companyDescription,
      topics: formData.category ? [formData.category] : [],
      tech: formData.axaCategory ? formData.axaCategory.split(',').map(c => c.trim()) : [],
      maturity: formData.stage,
      logoUrl: formData.logo || undefined,
      website: formData.website || undefined,
      billingCountry: formData.headquarterCountry,
      totalFunding: formData.funding && formData.funding !== 'NA' ? formData.funding : undefined,
      currentInvestmentStage: formData.stage,
      "Company Name": formData.companyName,
      "Company Description": formData.companyDescription,
      "Category": formData.category,
      "AXA Category": formData.axaCategory,
      "Stage": formData.stage,
      "Headquarter Country": formData.headquarterCountry,
      "Funding": formData.funding,
      "USP": formData.usp,
      "Final Priority Score": formData.finalPriorityScore,
      logo: formData.logo || undefined,
      contactPerson: formData.contactPerson || undefined,
      contactEmail: formData.contactEmail || undefined
    })

    setFormData({
      companyName: '',
      companyDescription: '',
      category: '',
      axaCategory: '',
      stage: '',
      headquarterCountry: '',
      funding: '',
      usp: '',
      finalPriorityScore: 50,
      logo: '',
      website: '',
      contactPerson: '',
      contactEmail: ''
    })
    
    setOpen(false)
  }

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogContent className="sm:max-w-[600px] max-h-[90vh] p-0">
        <DialogHeader className="px-6 pt-6">
          <DialogTitle className="text-2xl">Add Startup</DialogTitle>
        </DialogHeader>
        <ScrollArea className="max-h-[calc(90vh-100px)]">
          <form onSubmit={handleSubmit} className="space-y-5 px-6 pb-6">
            <div className="space-y-2">
              <Label htmlFor="companyName">Company Name *</Label>
              <Input
                id="companyName"
                value={formData.companyName}
                onChange={(e) => setFormData(prev => ({ ...prev, companyName: e.target.value }))}
                placeholder="Acme AI Solutions"
                required
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="companyDescription">Company Description *</Label>
              <Textarea
                id="companyDescription"
                value={formData.companyDescription}
                onChange={(e) => setFormData(prev => ({ ...prev, companyDescription: e.target.value }))}
                placeholder="What does this startup do?"
                className="min-h-[100px] resize-none"
                required
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="usp">Unique Selling Point</Label>
              <Textarea
                id="usp"
                value={formData.usp}
                onChange={(e) => setFormData(prev => ({ ...prev, usp: e.target.value }))}
                placeholder="What makes this startup unique?"
                className="min-h-[80px] resize-none"
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="category">Category *</Label>
                <Input
                  id="category"
                  value={formData.category}
                  onChange={(e) => setFormData(prev => ({ ...prev, category: e.target.value }))}
                  placeholder="e.g., Agentic"
                  required
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="stage">Stage *</Label>
                <Input
                  id="stage"
                  value={formData.stage}
                  onChange={(e) => setFormData(prev => ({ ...prev, stage: e.target.value }))}
                  placeholder="e.g., Growth"
                  required
                />
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="axaCategory">AXA Category</Label>
              <Input
                id="axaCategory"
                value={formData.axaCategory}
                onChange={(e) => setFormData(prev => ({ ...prev, axaCategory: e.target.value }))}
                placeholder="e.g., AI/Data/Software, Health/Wellness"
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="headquarterCountry">Headquarter Country</Label>
                <Input
                  id="headquarterCountry"
                  value={formData.headquarterCountry}
                  onChange={(e) => setFormData(prev => ({ ...prev, headquarterCountry: e.target.value }))}
                  placeholder="Netherlands"
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="funding">Funding</Label>
                <Input
                  id="funding"
                  value={formData.funding}
                  onChange={(e) => setFormData(prev => ({ ...prev, funding: e.target.value }))}
                  placeholder="€1.2M Pre-seed"
                />
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="finalPriorityScore">Priority Score (0-100)</Label>
              <Input
                id="finalPriorityScore"
                type="number"
                min="0"
                max="100"
                value={formData.finalPriorityScore}
                onChange={(e) => setFormData(prev => ({ ...prev, finalPriorityScore: parseInt(e.target.value) || 0 }))}
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="logo">Logo URL</Label>
              <Input
                id="logo"
                type="url"
                value={formData.logo}
                onChange={(e) => setFormData(prev => ({ ...prev, logo: e.target.value }))}
                placeholder="https://example.com/logo.png"
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="website">Website</Label>
              <Input
                id="website"
                type="url"
                value={formData.website}
                onChange={(e) => setFormData(prev => ({ ...prev, website: e.target.value }))}
                placeholder="https://example.com"
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="contactPerson">Contact Person</Label>
                <Input
                  id="contactPerson"
                  value={formData.contactPerson}
                  onChange={(e) => setFormData(prev => ({ ...prev, contactPerson: e.target.value }))}
                  placeholder="Jane Doe, CEO"
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="contactEmail">Contact Email</Label>
                <Input
                  id="contactEmail"
                  type="email"
                  value={formData.contactEmail}
                  onChange={(e) => setFormData(prev => ({ ...prev, contactEmail: e.target.value }))}
                  placeholder="jane@example.com"
                />
              </div>
            </div>

            <div className="flex gap-3 pt-4">
              <Button
                type="button"
                variant="outline"
                onClick={() => setOpen(false)}
                className="flex-1"
              >
                Cancel
              </Button>
              <Button type="submit" className="flex-1">
                Add Startup
              </Button>
            </div>
          </form>
        </ScrollArea>
      </DialogContent>
    </Dialog>
  )
}
