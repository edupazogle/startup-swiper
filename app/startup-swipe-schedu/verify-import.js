#!/usr/bin/env node
/**
 * Verification script for the startup data import
 * Tests that the imported data is correctly structured and accessible
 */

import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

console.log('================================================================================');
console.log('STARTUP DATA VERIFICATION');
console.log('================================================================================');
console.log();

// Load the data
const dataPath = path.join(__dirname, 'startups', 'slush2_extracted.json');
const rawData = fs.readFileSync(dataPath, 'utf-8');
const startups = JSON.parse(rawData);

console.log('📊 Data Statistics:');
console.log(`   Total Startups: ${startups.length}`);
console.log();

// Check required fields
const requiredFields = [
  'id', 'name', 'description', 'website', 'billingCountry',
  'billingCity', 'maturity', 'topics', 'featuredLists'
];

console.log('🔍 Schema Validation:');
let validCount = 0;
let invalidCount = 0;

for (const startup of startups) {
  let isValid = true;
  for (const field of requiredFields) {
    if (!(field in startup)) {
      isValid = false;
      break;
    }
  }
  if (isValid) {
    validCount++;
  } else {
    invalidCount++;
  }
}

console.log(`   ✅ Valid Startups: ${validCount}`);
console.log(`   ❌ Invalid Startups: ${invalidCount}`);
console.log();

// Check for newly added startups (ID >= 44746)
const originalStartups = startups.filter(s => s.id < 44746);
const newStartups = startups.filter(s => s.id >= 44746);

console.log('📈 Import Summary:');
console.log(`   Original Startups: ${originalStartups.length}`);
console.log(`   Newly Added: ${newStartups.length}`);
console.log();

// Country distribution
const countryCount = {};
for (const startup of startups) {
  const country = startup.billingCountry || 'Unknown';
  countryCount[country] = (countryCount[country] || 0) + 1;
}

const topCountries = Object.entries(countryCount)
  .sort((a, b) => b[1] - a[1])
  .slice(0, 5);

console.log('🌍 Top 5 Countries:');
for (const [country, count] of topCountries) {
  console.log(`   ${country}: ${count} startups`);
}
console.log();

// Maturity distribution
const maturityCount = {};
for (const startup of startups) {
  const maturity = startup.maturity || 'Unknown';
  maturityCount[maturity] = (maturityCount[maturity] || 0) + 1;
}

console.log('🚀 Maturity Distribution:');
for (const [maturity, count] of Object.entries(maturityCount).sort((a, b) => b[1] - a[1])) {
  console.log(`   ${maturity}: ${count}`);
}
console.log();

// Sample startup
const sampleNew = newStartups[0];
if (sampleNew) {
  console.log('📝 Sample Newly Added Startup:');
  console.log(`   Name: ${sampleNew.name}`);
  console.log(`   ID: ${sampleNew.id}`);
  console.log(`   Country: ${sampleNew.billingCountry}`);
  console.log(`   City: ${sampleNew.billingCity}`);
  console.log(`   Maturity: ${sampleNew.maturity}`);
  console.log(`   Website: ${sampleNew.website || 'N/A'}`);
  console.log(`   Description: ${sampleNew.description?.substring(0, 100)}...`);
  console.log();
}

// Check for duplicates by name
const namesSeen = new Set();
let duplicates = 0;
for (const startup of startups) {
  const name = startup.name.toLowerCase().trim();
  if (namesSeen.has(name)) {
    duplicates++;
  } else {
    namesSeen.add(name);
  }
}

console.log('🔎 Duplicate Check:');
console.log(`   Unique Names: ${namesSeen.size}`);
console.log(`   Duplicates Found: ${duplicates}`);
console.log();

// File size
const stats = fs.statSync(dataPath);
const fileSizeMB = (stats.size / (1024 * 1024)).toFixed(2);

console.log('📦 File Information:');
console.log(`   Path: ${dataPath}`);
console.log(`   Size: ${fileSizeMB} MB`);
console.log();

console.log('================================================================================');
if (invalidCount === 0 && duplicates === 0) {
  console.log('✅ ALL CHECKS PASSED - Data is ready for frontend consumption');
} else {
  console.log('⚠️  WARNINGS DETECTED - Review issues above');
}
console.log('================================================================================');
console.log();
