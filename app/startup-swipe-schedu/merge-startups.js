#!/usr/bin/env node
/**
 * Merge missing startups from slush2.json into slush2_extracted.json
 * Preserves existing entries and uses the extracted format
 */

import { readFile, writeFile } from 'fs/promises';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

async function mergeStartups() {
  console.log('🔄 Merging startups from slush2.json into slush2_extracted.json\n');
  console.log('═'.repeat(60));

  try {
    // Load both files
    const extractedPath = join(__dirname, 'startups', 'slush2_extracted.json');
    const allStartupsPath = join(__dirname, 'startups', 'slush2.json');

    const extracted = JSON.parse(await readFile(extractedPath, 'utf-8'));
    const all = JSON.parse(await readFile(allStartupsPath, 'utf-8'));

    console.log('📊 Current state:');
    console.log(`  - Extracted: ${extracted.length} startups`);
    console.log(`  - All startups: ${all.length} startups`);

    // Get IDs that already exist in extracted
    const extractedIds = new Set(extracted.map(s => s.id));
    console.log(`\n🔍 Existing IDs in extracted: ${extractedIds.size}`);

    // Find missing startups
    const missing = all.filter(s => !extractedIds.has(s.id));
    console.log(`📋 Missing startups to add: ${missing.length}`);

    if (missing.length === 0) {
      console.log('\n✅ No new startups to add. All startups are already in slush2_extracted.json');
      return;
    }

    // Helper to extract logo URL
    const extractLogoUrl = (startup) => {
      if (startup.logoUrl) return startup.logoUrl;
      if (startup.files && Array.isArray(startup.files)) {
        const logoFile = startup.files.find(f => f.type === 'Logo');
        if (logoFile?.url) return logoFile.url;
      }
      return undefined;
    };

    // Map missing startups to extracted format
    console.log('\n🔧 Mapping startups to extracted format...');
    const mapped = missing.map(startup => {
      return {
        id: startup.id,
        dateCreated: startup.dateCreated,
        name: startup.name,
        dateFounded: startup.dateFounded,
        employees: startup.employees,
        legalEntity: startup.legalEntity,
        mainContactId: startup.mainContactId,
        website: startup.website,
        shortDescription: startup.shortDescription || (startup.description ? startup.description.substring(0, 200) : ''),
        description: startup.description || startup.shortDescription || '',
        technologyReadiness: startup.technologyReadiness,
        currentInvestmentStage: startup.currentInvestmentStage || 'Undisclosed',
        totalFunding: startup.totalFunding,
        originalTotalFunding: startup.originalTotalFunding,
        originalTotalFundingCurrency: startup.originalTotalFundingCurrency,
        lastFundingDate: startup.lastFundingDate,
        lastFunding: startup.lastFunding,
        originalLastFunding: startup.originalLastFunding,
        originalLastFundingCurrency: startup.originalLastFundingCurrency,
        pricingModel: startup.pricingModel,
        sfId: startup.sfId,
        billingCountry: startup.billingCountry,
        billingState: startup.billingState,
        billingStreet: startup.billingStreet,
        billingCity: startup.billingCity,
        billingPostalCode: startup.billingPostalCode,
        fundingIsUndisclosed: startup.fundingIsUndisclosed,
        lastModifiedById: startup.lastModifiedById,
        parentCompanyId: startup.parentCompanyId,
        lastModifiedDate: startup.lastModifiedDate,
        pitchbookId: startup.pitchbookId,
        lastPitchbookSync: startup.lastPitchbookSync,
        isMissingValidation: startup.isMissingValidation,
        lastQualityCheckDate: startup.lastQualityCheckDate,
        lastQualityCheckById: startup.lastQualityCheckById,
        isQualityChecked: startup.isQualityChecked,
        qualityChecks: startup.qualityChecks || [],
        lastQualityCheckBy: startup.lastQualityCheckBy,
        featuredLists: startup.featuredLists || [],
        opportunities: startup.opportunities || [],
        leadOpportunities: startup.leadOpportunities || [],
        files: startup.files || [],
        logoUrl: extractLogoUrl(startup),
        topics: startup.topics || [],
        tech: startup.tech || [],
        maturity: startup.maturity || 'Undisclosed',
        maturity_score: startup.maturity_score
      };
    });

    // Combine: keep existing extracted first, then add missing
    const combined = [...extracted, ...mapped];

    console.log(`\n✅ New total after merge: ${combined.length} startups`);
    console.log('\n💾 Writing to startups/slush2_extracted.json...');

    // Write back to file with proper formatting
    await writeFile(extractedPath, JSON.stringify(combined, null, 2), 'utf-8');

    console.log('✨ Done! All startups are now in slush2_extracted.json');
    console.log('\n📊 Final breakdown:');
    console.log('─'.repeat(60));
    console.log(`  Original extracted:     ${extracted.length.toString().padStart(4)} startups`);
    console.log(`  Added from slush2:      ${mapped.length.toString().padStart(4)} startups`);
    console.log(`  Total unique:           ${combined.length.toString().padStart(4)} startups`);
    console.log('─'.repeat(60));

    // Verify the merge
    const uniqueIds = new Set(combined.map(s => s.id));
    if (uniqueIds.size === combined.length) {
      console.log('\n✅ Verification: No duplicate IDs found');
    } else {
      console.log(`\n⚠️  Warning: Found ${combined.length - uniqueIds.size} duplicate IDs`);
    }

    console.log('\n🎉 Merge complete!\n');

  } catch (error) {
    console.error('❌ Error during merge:', error.message);
    process.exit(1);
  }
}

mergeStartups();
