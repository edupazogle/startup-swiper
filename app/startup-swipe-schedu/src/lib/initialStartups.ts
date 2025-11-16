import { Startup } from './types'
import allStartups from '../../startups/slush2_extracted.json'

// All startups are now in slush2_extracted.json (merged from both sources)
console.log(`🚀 Loading all startups from Slush 2025:`)
console.log(`  ✅ Total startups: ${allStartups.length}`)

// Helper function to extract logo URL from files array
const extractLogoUrl = (startup: any): string | undefined => {
  if (startup.logoUrl) return startup.logoUrl
  if (startup.files && Array.isArray(startup.files)) {
    const logoFile = startup.files.find((f: any) => f.type === 'Logo')
    if (logoFile?.url) return logoFile.url
  }
  return undefined
}

// Map the JSON data to match our Startup interface
export const initialStartups: Omit<Startup, 'id'>[] = allStartups.map((startup: any) => ({
  name: startup.name || '',
  shortDescription: startup.shortDescription || startup.description?.substring(0, 200) || '',
  description: startup.description || startup.shortDescription || '',
  logoUrl: extractLogoUrl(startup),
  website: startup.website || undefined,
  topics: startup.topics || [],
  tech: startup.tech || [],
  maturity: startup.maturity || 'Undisclosed',
  maturity_score: startup.maturity_score,
  totalFunding: startup.totalFunding?.toString() || (startup.totalFunding === 0 ? '0' : undefined),
  employees: startup.employees || undefined,
  billingCity: startup.billingCity || undefined,
  billingCountry: startup.billingCountry || undefined,
  dateFounded: startup.dateFounded || undefined,
  currentInvestmentStage: startup.currentInvestmentStage || 'Undisclosed',
  funding_stage: startup.funding_stage || undefined,
  "Company Name": startup.name || '',
  "Company Description": startup.description || '',
  "Category": startup.category || startup.topics?.[0] || undefined,
  "AXA Category": startup.axaCategory || undefined,
  "Stage": startup.currentInvestmentStage || 'Undisclosed',
  "Final Priority Score": startup.finalPriorityScore || startup.maturity_score || undefined,
  "Headquarter Country": startup.billingCountry || undefined,
  "Funding": startup.totalFunding?.toString() || (startup.totalFunding === 0 ? '0' : undefined),
  "USP": startup.usp || startup.shortDescription || undefined,
  "URL": startup.website || undefined,
  "Additional Info": startup.additionalInfo || undefined
}))
