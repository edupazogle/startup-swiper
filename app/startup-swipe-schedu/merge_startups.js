const fs = require('fs');
const path = require('path');

console.log('Starting merge process...\n');

// Read the files
const slush2ExtractedPath = path.join(__dirname, 'startups/slush2_extracted.json');
const slush2Path = path.join(__dirname, 'startups/slush2.json');

console.log('Reading slush2_extracted.json...');
const slush2Extracted = JSON.parse(fs.readFileSync(slush2ExtractedPath, 'utf8'));
console.log(`✓ Found ${slush2Extracted.length} entries in slush2_extracted.json`);

console.log('Reading slush2.json...');
const slush2 = JSON.parse(fs.readFileSync(slush2Path, 'utf8'));
console.log(`✓ Found ${slush2.length} entries in slush2.json\n`);

// Create a Set of IDs from slush2_extracted to check for duplicates
const existingIds = new Set(slush2Extracted.map(item => item.id));
console.log(`Existing unique IDs in slush2_extracted.json: ${existingIds.size}`);

// Find entries from slush2 that aren't in slush2_extracted
const newEntries = slush2.filter(item => !existingIds.has(item.id));
console.log(`New entries to add from slush2.json: ${newEntries.length}`);

// Merge: keep all slush2_extracted entries + add new entries from slush2
const merged = [...slush2Extracted, ...newEntries];
console.log(`\nTotal entries after merge: ${merged.length}`);

// Create backup of original file
const backupPath = slush2ExtractedPath + '.backup';
console.log(`\nCreating backup at: ${backupPath}`);
fs.copyFileSync(slush2ExtractedPath, backupPath);
console.log('✓ Backup created');

// Write merged data back to slush2_extracted.json
console.log(`\nWriting merged data to ${slush2ExtractedPath}...`);
fs.writeFileSync(slush2ExtractedPath, JSON.stringify(merged, null, 2), 'utf8');
console.log('✓ Merge complete!');

console.log('\n=== Summary ===');
console.log(`Original slush2_extracted.json: ${slush2Extracted.length} entries`);
console.log(`Entries from slush2.json: ${slush2.length} entries`);
console.log(`New entries added: ${newEntries.length} entries`);
console.log(`Final merged file: ${merged.length} entries`);
console.log(`Backup saved to: ${backupPath}`);
