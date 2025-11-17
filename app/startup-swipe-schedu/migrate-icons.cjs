#!/usr/bin/env node

/**
 * Icon Migration Script
 * Migrates from Phosphor Icons to Flowbite React Icons
 */

const fs = require('fs');
const path = require('path');

// Icon mapping from Phosphor to Flowbite
const iconMapping = {
  // Navigation & Arrows
  'ArrowUpRight': 'ArrowUpRightFromSquare',
  'ArrowCounterClockwise': 'RotateLeft',
  'ArrowClockwise': 'RotateRight',
  'ArrowsClockwise': 'Reload',
  'ArrowRight': 'ArrowRight',
  'CaretLeft': 'AngleLeft',
  'CaretRight': 'AngleRight',
  'CaretDown': 'AngleDown',
  'CaretUp': 'AngleUp',
  
  // Actions
  'Check': 'Check',
  'CheckCircle': 'CheckCircle',
  'X': 'Close',
  'Plus': 'CirclePlus',
  'Trash': 'TrashBin',
  'Copy': 'Copy',
  'PencilSimple': 'PenSwirl',
  
  // Communication
  'Bell': 'Bell',
  'BellSlash': 'BellSlash',
  'PaperPlaneRight': 'PaperPlane',
  'Share': 'ShareAll',
  'ShareNetwork': 'ShareNodes',
  'LinkedinLogo': 'Linkedin',
  
  // Users
  'User': 'User',
  'Users': 'UsersGroup',
  'UserGear': 'UserSettings',
  'SignOut': 'Logout',
  
  // Business
  'Briefcase': 'Briefcase',
  'Rocket': 'Rocket',
  'Target': 'Target',
  'CurrencyDollar': 'Dollar',
  'Star': 'Star',
  
  // Calendar & Time
  'Calendar': 'CalendarMonth',
  'CalendarBlank': 'Calendar',
  'Clock': 'Clock',
  
  // Location
  'MapPin': 'LocationPin',
  'GlobeHemisphereWest': 'Globe',
  
  // Data
  'TrendUp': 'ChartLineUp',
  
  // AI
  'Sparkle': 'WandMagicSparkles',
  'Lightbulb': 'Lightbulb',
  'Robot': 'Robot',
  
  // UI Elements
  'Heart': 'Heart',
  'Funnel': 'Filter',
  'FunnelSimple': 'Filter',
  'MagnifyingGlass': 'Search',
  'Eye': 'Eye',
  'EyeSlash': 'EyeSlash',
  'Question': 'CircleQuestion',
  
  // Theme
  'Moon': 'Moon',
  'Sun': 'Sun',
  
  // Other
  'Swatches': 'Swatchbook',
  'UsersIcon': 'UsersGroup',
};

function migrateFile(filePath) {
  console.log(`\n📝 Processing: ${filePath}`);
  
  let content = fs.readFileSync(filePath, 'utf8');
  let modified = false;
  
  // Check if file uses Phosphor icons
  if (!content.includes('@phosphor-icons/react')) {
    console.log('  ⏭️  No Phosphor icons found, skipping');
    return false;
  }
  
  // Replace import statement
  const phosphorImportRegex = /import\s*\{([^}]+)\}\s*from\s*['"]@phosphor-icons\/react['"]/g;
  const matches = content.match(phosphorImportRegex);
  
  if (matches) {
    matches.forEach(match => {
      const iconNamesMatch = match.match(/\{([^}]+)\}/);
      if (iconNamesMatch) {
        const iconNames = iconNamesMatch[1]
          .split(',')
          .map(name => name.trim())
          .filter(name => name.length > 0);
        
        // Map to Flowbite icon names
        const flowbiteIcons = iconNames.map(name => {
          // Remove 'as' aliases
          const cleanName = name.split(' as ')[0].trim();
          return iconMapping[cleanName] || cleanName;
        });
        
        const newImport = `import { ${flowbiteIcons.join(', ')} } from 'flowbite-react-icons/outline'`;
        content = content.replace(match, newImport);
        modified = true;
        console.log(`  ✅ Updated import statement`);
      }
    });
  }
  
  // Replace icon component usages - remove weight and size props, add className
  Object.keys(iconMapping).forEach(phosphorIcon => {
    const flowbiteIcon = iconMapping[phosphorIcon];
    
    // Pattern 1: <Icon size={X} weight="Y" />
    const pattern1 = new RegExp(`<${phosphorIcon}\\s+size=\\{(\\d+)\\}\\s+weight="[^"]*"([^>]*?)\\/>`, 'g');
    content = content.replace(pattern1, (match, size, rest) => {
      const sizeClass = `w-${Math.ceil(size/4)} h-${Math.ceil(size/4)}`;
      const hasClassName = rest.includes('className=');
      if (hasClassName) {
        return `<${flowbiteIcon}${rest.replace(/className="([^"]*)"/, `className="$1 ${sizeClass}"`)} />`;
      }
      return `<${flowbiteIcon} className="${sizeClass}"${rest} />`;
    });
    
    // Pattern 2: <Icon className="..." weight={...} />
    const pattern2 = new RegExp(`<${phosphorIcon}([^>]*?)\\s+weight=\\{[^}]+\\}([^>]*?)\\/>`, 'g');
    content = content.replace(pattern2, `<${flowbiteIcon}$1$2 />`);
    
    // Pattern 3: <Icon ... weight="..." ... />
    const pattern3 = new RegExp(`<${phosphorIcon}([^>]*?)\\s+weight="[^"]*"([^>]*?)\\/>`, 'g');
    content = content.replace(pattern3, `<${flowbiteIcon}$1$2 />`);
    
    // Pattern 4: <Icon size={X} />
    const pattern4 = new RegExp(`<${phosphorIcon}\\s+size=\\{(\\d+)\\}([^>]*?)\\/>`, 'g');
    content = content.replace(pattern4, (match, size, rest) => {
      const sizeClass = `w-${Math.ceil(size/4)} h-${Math.ceil(size/4)}`;
      const hasClassName = rest.includes('className=');
      if (hasClassName) {
        return `<${flowbiteIcon}${rest.replace(/className="([^"]*)"/, `className="$1 ${sizeClass}"`)} />`;
      }
      return `<${flowbiteIcon} className="${sizeClass}"${rest} />`;
    });
    
    if (phosphorIcon !== flowbiteIcon) {
      modified = modified || content.includes(flowbiteIcon);
    }
  });
  
  if (modified) {
    fs.writeFileSync(filePath, content, 'utf8');
    console.log(`  ✅ File updated successfully`);
    return true;
  } else {
    console.log(`  ℹ️  No changes needed`);
    return false;
  }
}

function migrateDirectory(dirPath) {
  const files = fs.readdirSync(dirPath);
  let totalUpdated = 0;
  
  files.forEach(file => {
    const filePath = path.join(dirPath, file);
    const stat = fs.statSync(filePath);
    
    if (stat.isDirectory()) {
      totalUpdated += migrateDirectory(filePath);
    } else if (file.endsWith('.tsx') || file.endsWith('.ts')) {
      if (migrateFile(filePath)) {
        totalUpdated++;
      }
    }
  });
  
  return totalUpdated;
}

// Main execution
console.log('🚀 Starting icon migration from Phosphor to Flowbite...\n');

const componentsDir = path.join(__dirname, 'src', 'components');
const updated = migrateDirectory(componentsDir);

console.log(`\n\n✨ Migration complete! Updated ${updated} files.`);
console.log('\n📋 Next steps:');
console.log('  1. Review the changes with: git diff');
console.log('  2. Test the application: npm run dev');
console.log('  3. Build the application: npm run build');
console.log('  4. Commit the changes if everything works correctly\n');
