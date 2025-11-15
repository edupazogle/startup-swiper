# Rise - AI-Powered Startup Discovery Platform for Slush 2025

A collaborative startup discovery and networking platform that combines Tinder-style swiping with AI-powered insights, team coordination, and intelligent recommendations for Slush 2025 conference attendees.

**Experience Qualities**:
1. **Intelligent** - AI capabilities enhance decision-making with personalized recommendations, startup insights, and smart scheduling assistance
2. **Collaborative** - Team members can vote, coordinate, and schedule meetings together with real-time insights into collective interests
3. **Engaging** - Gamified swiping interface makes startup discovery fun and intuitive while maintaining professional utility

**Complexity Level**: Complex Application (advanced functionality, AI integration, team coordination)
This is a full-featured application with multiple views, AI-powered features, persistent data storage, team collaboration tools, and intelligent assistance for conference networking.

## Essential Features

### AI Assistant Chatbot
- **Functionality**: Interactive AI assistant that answers questions about startups, events, and provides recommendations
- **Purpose**: Helps users make informed decisions and navigate their Slush experience through conversational AI
- **Trigger**: User navigates to AI Assistant tab or asks a question
- **Progression**: User asks question → AI analyzes context (startups, votes, events) → Generates personalized response → Displays in chat interface
- **Success criteria**: Accurate, helpful responses within 2-3 seconds with conversation history persistence

### AI Startup Recommendations
- **Functionality**: Machine learning-powered suggestions for startups based on user's voting patterns and interests
- **Purpose**: Surfaces relevant startups users might miss, improving discovery efficiency
- **Trigger**: After user has voted on 2+ startups with interest
- **Progression**: User votes on startups → System analyzes patterns → AI generates top 3 matches → Displays recommendation cards with match percentage and reasoning
- **Success criteria**: Recommendations feel relevant to user interests with >70% match confidence

### AI Startup Insights Generator
- **Functionality**: Generates analytical insights about individual startups including strengths, opportunities, and relevance
- **Purpose**: Provides deeper understanding beyond basic descriptions to aid decision-making
- **Trigger**: User clicks "Generate AI Insights" on startup card
- **Progression**: User requests insights → AI analyzes startup details and user interests → Generates 3-4 focused insights → Displays categorized insights (strength/opportunity/recommendation)
- **Success criteria**: Insightful, actionable information delivered in <3 seconds

### Smart Meeting Time Suggester
- **Functionality**: AI-powered meeting scheduler that suggests optimal time slots avoiding conflicts
- **Purpose**: Streamlines scheduling process by intelligently finding best meeting windows
- **Trigger**: User opens schedule meeting dialog
- **Progression**: User initiates scheduling → AI analyzes existing events → Identifies optimal slots → Presents 3 suggestions with reasoning → User selects preferred time
- **Success criteria**: Suggested times have no conflicts, fall within business hours, and respect conference schedule

### Tinder-Style Startup Swiping
- **Functionality**: Swipe right for interested, left to pass on startups
- **Purpose**: Makes startup discovery engaging and efficient with familiar interaction pattern
- **Trigger**: User navigates to Swipe view
- **Progression**: Card displays → User swipes or clicks buttons → Vote recorded → Next startup appears → Progress tracked
- **Success criteria**: Smooth animations, instant feedback, progress persistence

### Team Dashboard with Rocket Ratings
- **Functionality**: View all startups with team interest levels, add 1-5 rocket ratings, see aggregate scores
- **Purpose**: Coordinate team priorities and measure enthusiasm beyond binary interested/not interested
- **Trigger**: User navigates to Startups tab
- **Progression**: View loads → Shows startups grouped by priority → User can rate with rockets → Average displayed → Team sees collective ratings
- **Success criteria**: Real-time rating updates, clear visual hierarchy of team priorities

### Calendar & Event Management
- **Functionality**: Manage meetings, events, and schedule coordination for Slush conference
- **Purpose**: Keep team organized with centralized schedule and meeting tracking
- **Trigger**: User navigates to Calendar tab
- **Progression**: User views events → Can add new events → Schedule meetings with startups → Toggle attendance → Fixed events (lunch, etc.) pre-populated
- **Success criteria**: No scheduling conflicts, intuitive event creation, attendance tracking

### LinkedIn Content Generator
- **Functionality**: AI-powered LinkedIn post creator for sharing Slush experiences
- **Purpose**: Help users craft engaging LinkedIn content about their conference activities
- **Trigger**: User navigates to LinkedIn tab
- **Progression**: User describes experience → AI generates polished LinkedIn post → User can edit and copy → Share externally
- **Success criteria**: Professional, engaging posts generated quickly

## Edge Case Handling

- **No Startups Remaining**: Displays completion message with suggestion to check dashboard
- **No Team Interest**: Shows "No Interest Yet" section so all startups remain visible
- **Conflicting Schedules**: AI time suggester specifically avoids existing meeting conflicts
- **Empty State Handling**: Every view has thoughtful empty states guiding users to take action
- **Failed AI Requests**: Graceful error handling with retry options for all AI features
- **Stale Recommendations**: AI suggestions refresh automatically as user continues voting

## Design Direction

The design should feel modern, professional, and tech-forward while maintaining warmth and approachability. The auroral background creates visual interest and energy reminiscent of Northern lights (fitting for Nordic Slush conference), while the interface remains clean and functional. AI features are clearly marked with sparkle icons to set expectations.

## Color Selection

Custom palette - Dark theme with vibrant purple/blue aurora-inspired accents

**Primary Colors**:
- **Primary (Purple)**: oklch(0.65 0.20 280) - Vibrant purple for key actions, AI features, and brand identity. Communicates innovation and technology.
- **Accent (Pink/Magenta)**: oklch(0.50 0.25 320) - Energetic accent for hearts, engagement indicators, and positive actions. Creates excitement and approachability.

**Secondary Colors**:
- **Secondary**: oklch(0.30 0.05 280) - Muted purple for less prominent actions and hover states
- **Muted**: oklch(0.25 0.02 280) - Subtle backgrounds for cards and secondary content areas

**Background Colors**:
- **Background**: oklch(0.15 0.02 280) - Deep purple-tinted dark background, sophisticated and immersive
- **Card**: oklch(0.20 0.02 280) - Slightly lighter than background for depth and layering

**Foreground/Background Pairings**:
- Background (oklch(0.15 0.02 280)): White foreground (oklch(0.98 0 0)) - Ratio 13.5:1 ✓
- Card (oklch(0.20 0.02 280)): White foreground (oklch(0.98 0 0)) - Ratio 11.8:1 ✓
- Primary (oklch(0.65 0.20 280)): White text (oklch(0.98 0 0)) - Ratio 5.2:1 ✓
- Accent (oklch(0.50 0.25 320)): White text (oklch(0.98 0 0)) - Ratio 3.8:1 ✓
- Muted (oklch(0.25 0.02 280)): Muted foreground (oklch(0.70 0.02 280)) - Ratio 4.9:1 ✓

## Font Selection

Clean, professional system fonts that ensure fast loading and excellent readability across all devices while conveying tech-industry polish.

**Typographic Hierarchy**:
- H1 (App Title): System-ui Bold/32px (mobile) 48px (desktop)/tight letter spacing - Bold brand presence
- H2 (Section Headers): System-ui Semibold/24px (mobile) 32px (desktop)/normal - Clear section delineation
- H3 (Card Titles): System-ui Semibold/18px (mobile) 24px (desktop)/tight - Emphasizes startup names
- Body (Descriptions): System-ui Regular/14px (mobile) 16px (desktop)/relaxed line-height - Comfortable reading
- Small (Metadata): System-ui Regular/12px (mobile) 14px (desktop)/normal - Unobtrusive details
- Badges: System-ui Medium/10px (mobile) 12px (desktop)/wide tracking - Clear categorical labels

## Animations

Animations strike a balance between delightful micro-interactions and functional feedback, with the auroral background providing ambient motion while UI elements respond crisply to user actions.

**Purposeful Meaning**: Motion communicates state changes, provides feedback, and guides attention without slowing down workflows. The swipe animations feel satisfying and tactile, while AI loading states use subtle pulses to indicate processing.

**Hierarchy of Movement**:
1. **Background aurora** - Slow, ambient rotation and translation creating atmospheric presence (10-15s loops)
2. **Card swipe animations** - Dramatic exit animations with rotation and translation on swipe (300ms)
3. **AI recommendations** - Staggered fade-in reveals (100ms delays between items)
4. **Button interactions** - Quick scale transformations on press (100-150ms)
5. **Loading states** - Pulsing opacity on sparkle icons during AI processing (800ms loop)

## Component Selection

- **Components**: Heavy use of shadcn/ui v4 components for consistency and polish
  - Button - All interactive actions with variants (default, outline, ghost)
  - Card - Startup cards, recommendation cards, insight cards
  - Badge - Categories, stages, match percentages, ratings
  - Dialog - Schedule meeting, add startup, add idea forms
  - Tabs - Desktop navigation between views
  - Select - Filter dropdowns for categories
  - Input/Textarea - Form fields for scheduling and data entry
  - Progress - Swipe progress indicator
  - ScrollArea - Chat messages, long content lists
  - Avatar - Team member indicators on interested startups
  - Separator - Visual content dividers

- **Customizations**:
  - `AuroralBackground` - Custom animated gradient background component
  - `SwipeableCard` - Custom drag-to-swipe card with framer-motion
  - `AIAssistant` - Custom chat interface with message bubbles
  - `AIStartupInsights` - Custom expandable insights component
  - `AIRecommendations` - Custom recommendation cards with confidence scores
  - `AITimeSlotSuggester` - Custom smart scheduling component
  - `RocketRating` - Custom 5-rocket rating system (replacing star ratings)

- **States**: 
  - Button states: default, hover, active, disabled with color and scale changes
  - Card states: default, hover (shadow increase), dragging (opacity change)
  - Input states: default, focused (ring), error (red border), success (green accent)
  - Loading states: pulse animations on AI feature icons

- **Icon Selection**: @phosphor-icons/react with duotone and fill weights
  - `Robot` - AI Assistant
  - `Sparkle` - AI features and insights
  - `Rocket` - Rating system, high priority, startup dashboard
  - `Heart` - Interest indicator
  - `Swatches` - Swipe view
  - `CalendarBlank` - Calendar and scheduling
  - `LinkedinLogo` - LinkedIn content generator
  - `Lightbulb` - Ideas and insights
  - `UserGear` - Admin controls
  - All icons use 20-24px sizes with weight variations for active/inactive states

- **Spacing**: Tailwind spacing scale with consistent patterns
  - Container padding: `px-4 md:px-6` (16-24px)
  - Card padding: `p-4 md:p-6` (16-24px)
  - Element gaps: `gap-3 md:gap-4` (12-16px)
  - Section spacing: `space-y-4 md:space-y-6` (16-24px)
  - Border radius: 8px (`--radius: 0.5rem`)

- **Mobile**: Mobile-first responsive design with progressive enhancement
  - Bottom navigation bar on mobile (<768px) with 5 tabs
  - Desktop uses horizontal tab bar at top
  - Cards adjust from 90vw to fixed 440px max-width
  - Text scales from 12-14px mobile to 14-16px desktop
  - Touch targets minimum 44x44px on mobile
  - Safe area insets for notched devices
  - Swipe gestures work seamlessly on touch devices
