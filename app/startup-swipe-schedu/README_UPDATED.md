# ✨ Startup Swipe & Schedule - Slush 2025

A modern, interactive startup discovery and scheduling application for Slush 2025 attendees.

## 🚀 Features

- **2,556 Unique Startups** from Slush 2025
- **Swipe Interface** - Tinder-style startup discovery
- **Smart Dashboard** - Filter and organize by topics, tech, and maturity
- **Calendar Integration** - Schedule meetings with startups
- **AI Concierge** - Get personalized recommendations
- **Team Collaboration** - Share preferences with team members

## 📊 Startup Data

This application includes comprehensive startup data:

- **100 Enhanced Startups** with full metadata (topics, tech stack, maturity scores)
- **2,456 Additional Startups** with core information
- **Total: 2,556 Unique Startups** with intelligent deduplication

For detailed information about the data loading process, see [STARTUP_DATA_LOADING.md](./STARTUP_DATA_LOADING.md).

## 🛠️ Getting Started

### Prerequisites
- Node.js (v18 or higher)
- npm or yarn

### Installation

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Verify startup data
npm run verify-startups

# Run comprehensive tests
npm run test-enhancement
```

### Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run verify-startups` - Verify startup data loading
- `npm run test-enhancement` - Run comprehensive enhancement tests
- `npm run lint` - Run ESLint

## 📱 Application Views

### 1. Swipe View
- Discover startups one at a time
- Swipe right (❤️) to show interest
- Swipe left (✖️) to pass
- Track progress through all 2,556 startups

### 2. Dashboard (Startups)
- View all startups organized by team interest
- Filter by topics, technology, and maturity
- Schedule meetings directly from the dashboard
- Rate and track your favorites

### 3. Insights
- Submit and view innovation ideas
- Collaborate with team members
- Track startup trends

### 4. Calendar
- View all Slush 2025 events
- Schedule meetings with startups
- Manage your conference schedule
- AI-powered time slot suggestions

### 5. AI Concierge
- Get personalized startup recommendations
- Chat with LinkedIn experts
- Discover relevant content and articles

### 6. Admin
- Manage startup database
- View team activity
- Add custom startups

## 🎨 Technology Stack

- **React** - UI framework
- **TypeScript** - Type safety
- **Vite** - Build tool
- **Tailwind CSS** - Styling
- **Radix UI** - Component primitives
- **Framer Motion** - Animations
- **GitHub Spark KV** - Data persistence

## 📚 Documentation

- [Startup Data Loading](./STARTUP_DATA_LOADING.md) - Technical details about data integration
- [Enhancement Summary](./ENHANCEMENT_SUMMARY.md) - Overview of recent improvements
- [PRD](./PRD.md) - Product requirements document
- [AI Prompts Guide](./AI_PROMPTS_GUIDE.md) - Guide for AI-powered features

## 🧪 Testing & Verification

The application includes comprehensive testing:

```bash
# Run all tests
npm run test-enhancement
```

Expected output:
```
🎉 All tests passed! The startup enhancement is working correctly.

✨ Your application now includes:
   • 2,556 unique startups from Slush 2025
   • 100 enhanced startups with full metadata
   • Intelligent deduplication
   • Smart logo extraction
   • Comprehensive field mapping
```

## 📄 Data Sources

- `startups/slush2_extracted.json` - 100 enhanced startups with full metadata
- `startups/slush2.json` - 2,520 startups from Slush 2025

## 🤝 Contributing

This is a template project. Feel free to customize and extend it for your needs!

## 📄 License

The Spark Template files and resources from GitHub are licensed under the terms of the MIT license, Copyright GitHub, Inc.

