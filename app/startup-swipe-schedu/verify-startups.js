#!/usr/bin/env node
/**
 * Verification script to ensure all startups are loaded correctly
 */

import { readFile } from 'fs/promises';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

async function verifyStartups() {
  console.log('🔍 Verifying startup data loading...\n');

  try {
    // Load both JSON files
    const extractedPath = join(__dirname, 'startups', 'slush2_extracted.json');
    const allStartupsPath = join(__dirname, 'startups', 'slush2.json');

    const extractedData = JSON.parse(await readFile(extractedPath, 'utf-8'));
    const allStartupsData = JSON.parse(await readFile(allStartupsPath, 'utf-8'));

    console.log('📊 Startup Files Summary:');
    console.log('─'.repeat(50));
    console.log(`  slush2_extracted.json: ${extractedData.length} startups`);
    console.log(`  slush2.json:          ${allStartupsData.length} startups`);
    console.log('─'.repeat(50));

    // Check for duplicates
    const extractedIds = new Set(extractedData.map(s => s.id));
    const remainingStartups = allStartupsData.filter(s => !extractedIds.has(s.id));
    const totalUnique = extractedData.length + remainingStartups.length;

    console.log('\n✅ Deduplication Check:');
    console.log('─'.repeat(50));
    console.log(`  Extracted startups (priority): ${extractedData.length}`);
    console.log(`  Remaining unique startups:     ${remainingStartups.length}`);
    console.log(`  Total unique startups:         ${totalUnique}`);
    console.log('─'.repeat(50));

    // Verify data quality
    const sampleExtracted = extractedData[0];
    const sampleAll = allStartupsData[0];

    console.log('\n📋 Sample Startup from slush2_extracted.json:');
    console.log('─'.repeat(50));
    console.log(`  Name: ${sampleExtracted.name}`);
    console.log(`  Short Description: ${sampleExtracted.shortDescription?.substring(0, 60)}...`);
    console.log(`  Topics: ${sampleExtracted.topics?.join(', ') || 'N/A'}`);
    console.log(`  Tech: ${sampleExtracted.tech?.join(', ') || 'N/A'}`);
    console.log(`  Maturity: ${sampleExtracted.maturity || 'N/A'}`);
    console.log(`  Logo URL: ${sampleExtracted.logoUrl ? 'Yes' : 'No'}`);
    console.log('─'.repeat(50));

    console.log('\n📋 Sample Startup from slush2.json:');
    console.log('─'.repeat(50));
    console.log(`  Name: ${sampleAll.name}`);
    console.log(`  Short Description: ${sampleAll.shortDescription?.substring(0, 60)}...`);
    console.log(`  Topics: ${sampleAll.topics?.join(', ') || 'N/A'}`);
    console.log(`  Tech: ${sampleAll.tech?.join(', ') || 'N/A'}`);
    console.log(`  Maturity: ${sampleAll.maturity || 'N/A'}`);
    console.log(`  Logo URL: ${sampleAll.logoUrl ? 'Yes' : 'No'}`);
    console.log('─'.repeat(50));

    // Check field availability
    const fieldsToCheck = ['name', 'shortDescription', 'description', 'topics', 'tech', 'maturity', 'logoUrl'];
    console.log('\n🔧 Field Availability in slush2_extracted.json:');
    console.log('─'.repeat(50));
    fieldsToCheck.forEach(field => {
      const count = extractedData.filter(s => s[field]).length;
      const percentage = ((count / extractedData.length) * 100).toFixed(1);
      console.log(`  ${field.padEnd(20)}: ${count}/${extractedData.length} (${percentage}%)`);
    });
    console.log('─'.repeat(50));

    console.log('\n✨ Verification Complete!\n');
    console.log(`🚀 Your application will load ${totalUnique} unique startups from Slush 2025`);
    console.log('   with priority given to the 100 extracted startups.\n');

  } catch (error) {
    console.error('❌ Error during verification:', error.message);
    process.exit(1);
  }
}

verifyStartups();
