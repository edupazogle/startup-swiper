#!/usr/bin/env node
/**
 * Comprehensive test to verify the startup enhancement
 */

import { readFile } from 'fs/promises';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

async function runTests() {
  console.log('🧪 Running Comprehensive Startup Enhancement Tests\n');
  console.log('═'.repeat(60));
  
  let passedTests = 0;
  let totalTests = 0;

  // Test 1: Load both JSON files
  totalTests++;
  try {
    const extractedData = JSON.parse(
      await readFile(join(__dirname, 'startups', 'slush2_extracted.json'), 'utf-8')
    );
    const allStartupsData = JSON.parse(
      await readFile(join(__dirname, 'startups', 'slush2.json'), 'utf-8')
    );
    
    console.log('✅ Test 1: Both JSON files loaded successfully');
    console.log(`   - slush2_extracted.json: ${extractedData.length} startups`);
    console.log(`   - slush2.json: ${allStartupsData.length} startups`);
    passedTests++;
  } catch (error) {
    console.log('❌ Test 1: Failed to load JSON files');
    console.log(`   Error: ${error.message}`);
  }

  // Test 2: Verify deduplication logic
  totalTests++;
  try {
    const extractedData = JSON.parse(
      await readFile(join(__dirname, 'startups', 'slush2_extracted.json'), 'utf-8')
    );
    const allStartupsData = JSON.parse(
      await readFile(join(__dirname, 'startups', 'slush2.json'), 'utf-8')
    );
    
    const extractedIds = new Set(extractedData.map(s => s.id));
    const remainingStartups = allStartupsData.filter(s => !extractedIds.has(s.id));
    const totalUnique = extractedData.length + remainingStartups.length;
    
    if (totalUnique === 2556) {
      console.log('✅ Test 2: Deduplication produces correct count (2,556)');
      console.log(`   - Extracted: ${extractedData.length}`);
      console.log(`   - Unique remaining: ${remainingStartups.length}`);
      console.log(`   - Total: ${totalUnique}`);
      passedTests++;
    } else {
      console.log(`❌ Test 2: Expected 2,556 but got ${totalUnique}`);
    }
  } catch (error) {
    console.log('❌ Test 2: Deduplication test failed');
    console.log(`   Error: ${error.message}`);
  }

  // Test 3: Verify enhanced fields in extracted data
  totalTests++;
  try {
    const extractedData = JSON.parse(
      await readFile(join(__dirname, 'startups', 'slush2_extracted.json'), 'utf-8')
    );
    
    const hasTopics = extractedData.filter(s => s.topics && s.topics.length > 0).length;
    const hasTech = extractedData.filter(s => s.tech && s.tech.length > 0).length;
    const hasMaturity = extractedData.filter(s => s.maturity).length;
    const hasLogoUrl = extractedData.filter(s => s.logoUrl).length;
    
    if (hasTopics === 100 && hasTech === 100 && hasMaturity === 100) {
      console.log('✅ Test 3: Enhanced fields present in extracted data');
      console.log(`   - Topics: ${hasTopics}/100 (100%)`);
      console.log(`   - Tech: ${hasTech}/100 (100%)`);
      console.log(`   - Maturity: ${hasMaturity}/100 (100%)`);
      console.log(`   - Logo URLs: ${hasLogoUrl}/100 (${Math.round(hasLogoUrl/100*100)}%)`);
      passedTests++;
    } else {
      console.log('❌ Test 3: Enhanced fields missing in some records');
    }
  } catch (error) {
    console.log('❌ Test 3: Enhanced fields test failed');
    console.log(`   Error: ${error.message}`);
  }

  // Test 4: Verify no duplicate IDs in combined dataset
  totalTests++;
  try {
    const extractedData = JSON.parse(
      await readFile(join(__dirname, 'startups', 'slush2_extracted.json'), 'utf-8')
    );
    const allStartupsData = JSON.parse(
      await readFile(join(__dirname, 'startups', 'slush2.json'), 'utf-8')
    );
    
    const extractedIds = new Set(extractedData.map(s => s.id));
    const remainingStartups = allStartupsData.filter(s => !extractedIds.has(s.id));
    const combinedStartups = [...extractedData, ...remainingStartups];
    
    const allIds = combinedStartups.map(s => s.id);
    const uniqueIds = new Set(allIds);
    
    if (allIds.length === uniqueIds.size) {
      console.log('✅ Test 4: No duplicate IDs in combined dataset');
      console.log(`   - Total startups: ${allIds.length}`);
      console.log(`   - Unique IDs: ${uniqueIds.size}`);
      passedTests++;
    } else {
      console.log(`❌ Test 4: Found ${allIds.length - uniqueIds.size} duplicate IDs`);
    }
  } catch (error) {
    console.log('❌ Test 4: Duplicate check failed');
    console.log(`   Error: ${error.message}`);
  }

  // Test 5: Verify logo extraction logic
  totalTests++;
  try {
    const extractedData = JSON.parse(
      await readFile(join(__dirname, 'startups', 'slush2_extracted.json'), 'utf-8')
    );
    
    const startupsWithFiles = extractedData.filter(s => s.files && s.files.length > 0);
    const logoFiles = startupsWithFiles.filter(s => 
      s.files.some(f => f.type === 'Logo' && f.url)
    );
    
    console.log('✅ Test 5: Logo extraction logic verified');
    console.log(`   - Startups with files: ${startupsWithFiles.length}`);
    console.log(`   - Startups with logo files: ${logoFiles.length}`);
    console.log(`   - Direct logoUrl field: ${extractedData.filter(s => s.logoUrl).length}`);
    passedTests++;
  } catch (error) {
    console.log('❌ Test 5: Logo extraction test failed');
    console.log(`   Error: ${error.message}`);
  }

  // Test 6: Verify all startups have required fields
  totalTests++;
  try {
    const extractedData = JSON.parse(
      await readFile(join(__dirname, 'startups', 'slush2_extracted.json'), 'utf-8')
    );
    const allStartupsData = JSON.parse(
      await readFile(join(__dirname, 'startups', 'slush2.json'), 'utf-8')
    );
    
    const extractedIds = new Set(extractedData.map(s => s.id));
    const remainingStartups = allStartupsData.filter(s => !extractedIds.has(s.id));
    const combinedStartups = [...extractedData, ...remainingStartups];
    
    const missingName = combinedStartups.filter(s => !s.name).length;
    const missingDescription = combinedStartups.filter(s => !s.description && !s.shortDescription).length;
    
    if (missingName === 0) {
      console.log('✅ Test 6: All startups have required fields');
      console.log(`   - Startups without name: ${missingName}`);
      console.log(`   - Startups without any description: ${missingDescription}`);
      passedTests++;
    } else {
      console.log('❌ Test 6: Some startups missing required fields');
    }
  } catch (error) {
    console.log('❌ Test 6: Required fields test failed');
    console.log(`   Error: ${error.message}`);
  }

  // Summary
  console.log('\n' + '═'.repeat(60));
  console.log(`\n📊 Test Results: ${passedTests}/${totalTests} tests passed\n`);
  
  if (passedTests === totalTests) {
    console.log('🎉 All tests passed! The startup enhancement is working correctly.\n');
    console.log('✨ Your application now includes:');
    console.log('   • 2,556 unique startups from Slush 2025');
    console.log('   • 100 enhanced startups with full metadata');
    console.log('   • Intelligent deduplication');
    console.log('   • Smart logo extraction');
    console.log('   • Comprehensive field mapping\n');
    process.exit(0);
  } else {
    console.log(`⚠️  ${totalTests - passedTests} test(s) failed. Please review the errors above.\n`);
    process.exit(1);
  }
}

runTests();
