# Icon Migration to Flowbite Icons

## Overview
Migrating all icons from Phosphor Icons to Flowbite React Icons for consistency with the Flowbite design system.

## Icon Mapping Reference

### Navigation & Arrows
| Current (Phosphor) | New (Flowbite) | Category | Context |
|-------------------|----------------|----------|---------|
| `ArrowUpRight` | `ArrowUpRightFromSquare` | outline/general | External links, open new window |
| `ArrowCounterClockwise` | `RotateLeft` | outline/arrows | Undo, reset, refresh |
| `ArrowClockwise` | `RotateRight` | outline/arrows | Redo, refresh |
| `ArrowsClockwise` | `Reload` | outline/general | Refresh, reload |
| `ArrowRight` | `ArrowRight` | outline/arrows | Next, forward, continue |
| `CaretLeft` | `AngleLeft` | outline/arrows | Previous, back navigation |
| `CaretRight` | `AngleRight` | outline/arrows | Next navigation |
| `CaretDown` | `AngleDown` | outline/arrows | Dropdown expand |
| `CaretUp` | `AngleUp` | outline/arrows | Dropdown collapse |

### Actions & Status
| Current (Phosphor) | New (Flowbite) | Category | Context |
|-------------------|----------------|----------|---------|
| `Check` | `Check` | outline/general | Confirm, success, complete |
| `CheckCircle` | `CheckCircle` | outline/general | Success status, verified |
| `X` | `Close` | outline/general | Close, dismiss, cancel |
| `Plus` | `CirclePlus` | outline/general | Add new item |
| `Trash` | `TrashBin` | outline/general | Delete, remove |
| `Copy` | `Copy` | outline/general | Copy to clipboard |
| `PencilSimple` | `PenSwirl` | outline/text | Edit, modify |

### Communication & Social
| Current (Phosphor) | New (Flowbite) | Category | Context |
|-------------------|----------------|----------|---------|
| `Bell` | `Bell` | outline/general | Notifications, alerts |
| `BellSlash` | `BellSlash` | outline/general | Notifications muted |
| `PaperPlaneRight` | `PaperPlane` | outline/general | Send message, submit |
| `Share` | `ShareAll` | outline/general | Share content |
| `ShareNetwork` | `ShareNodes` | outline/general | Share to network |
| `LinkedinLogo` | `Linkedin` | outline/e-commerce | LinkedIn social |

### Users & People
| Current (Phosphor) | New (Flowbite) | Category | Context |
|-------------------|----------------|----------|---------|
| `User` | `User` | outline/user | Single user, profile |
| `Users` | `UsersGroup` | outline/user | Multiple users, team |
| `UserGear` | `UserSettings` | outline/user | User settings, admin |
| `SignOut` | `Logout` | outline/user | Logout, sign out |

### Business & Work
| Current (Phosphor) | New (Flowbite) | Category | Context |
|-------------------|----------------|----------|---------|
| `Briefcase` | `Briefcase` | outline/general | Business, work, professional |
| `Rocket` | `Rocket` | outline/general | Launch, startup, growth |
| `Target` | `Target` | outline/general | Goals, objectives, focus |
| `CurrencyDollar` | `Dollar` | outline/e-commerce | Money, funding, price |
| `Star` | `Star` | outline/general | Rating, favorite, featured |

### Calendar & Time
| Current (Phosphor) | New (Flowbite) | Category | Context |
|-------------------|----------------|----------|---------|
| `Calendar` | `CalendarMonth` | outline/general | Calendar, dates, schedule |
| `CalendarBlank` | `Calendar` | outline/general | Calendar view |
| `Clock` | `Clock` | outline/general | Time, duration, schedule |

### Location
| Current (Phosphor) | New (Flowbite) | Category | Context |
|-------------------|----------------|----------|---------|
| `MapPin` | `LocationPin` | outline/general | Location, address, place |
| `GlobeHemisphereWest` | `Globe` | outline/general | Global, worldwide, website |

### Data & Analytics
| Current (Phosphor) | New (Flowbite) | Category | Context |
|-------------------|----------------|----------|---------|
| `TrendUp` | `ChartLineUp` | outline/general | Growth, increase, analytics |

### AI & Innovation
| Current (Phosphor) | New (Flowbite) | Category | Context |
|-------------------|----------------|----------|---------|
| `Sparkle` | `WandMagicSparkles` | outline/general | AI, magic, special features |
| `Lightbulb` | `Lightbulb` | outline/general | Ideas, insights, innovation |
| `Robot` | `Robot` | outline/general | AI assistant, automation |

### UI Elements
| Current (Phosphor) | New (Flowbite) | Category | Context |
|-------------------|----------------|----------|---------|
| `Heart` | `Heart` | outline/general | Like, favorite, interested |
| `Funnel` | `Filter` | outline/general | Filter, sort |
| `FunnelSimple` | `Filter` | outline/general | Simple filter |
| `MagnifyingGlass` | `Search` | outline/general | Search, find |
| `Eye` | `Eye` | outline/general | View, show, visible |
| `EyeSlash` | `EyeSlash` | outline/general | Hide, hidden, password |
| `Question` | `CircleQuestion` | outline/general | Help, info, question |

### Theme
| Current (Phosphor) | New (Flowbite) | Category | Context |
|-------------------|----------------|----------|---------|
| `Moon` | `Moon` | outline/weather | Dark mode |
| `Sun` | `Sun` | outline/weather | Light mode |

### Other
| Current (Phosphor) | New (Flowbite) | Category | Context |
|-------------------|----------------|----------|---------|
| `Swatches` | `Swatchbook` | outline/general | Swipe view, cards |

## Import Pattern

### Old Pattern (Phosphor)
```tsx
import { Icon1, Icon2, Icon3 } from '@phosphor-icons/react'
```

### New Pattern (Flowbite)
```tsx
import { Icon1, Icon2, Icon3 } from 'flowbite-react-icons/outline'
// or for solid icons
import { Icon1, Icon2, Icon3 } from 'flowbite-react-icons/solid'
```

## Files to Update

1. **App.tsx** - Navigation icons, logo icons
2. **SwipeableCard.tsx** - Card action icons, status icons
3. **DashboardView.tsx** - Dashboard icons, action buttons
4. **CalendarView.tsx** - Calendar navigation, event icons
5. **AIAssistantView.tsx** - AI features, chat icons
6. **LoginView.tsx** - Password visibility toggles
7. **HistoryView.tsx** - Voting history icons
8. **StartupChat.tsx** - Chat and communication icons
9. **ImprovedMeetingModal.tsx** - Meeting setup icons
10. **ImprovedInsightsModalNew.tsx** - Insights and AI icons
11. **AdminView.tsx** - Admin panel icons
12. **ThemeSwitcher.tsx** - Theme toggle icons
13. **StartupFiltersPanel.tsx** - Filter and search icons
14. **QuickActionsBar.tsx** - Quick action icons
15. **AIRecommendations.tsx** - Recommendation icons

## Implementation Steps

1. ✅ Document all current icon usage
2. ✅ Create comprehensive mapping
3. ⏳ Update imports in all component files
4. ⏳ Test visual appearance and functionality
5. ⏳ Remove old icon library dependencies (optional)
6. ⏳ Update documentation

## Notes

- All Flowbite icons support both outline and solid variants
- Default size is 24px, can be customized via `size` prop
- Icons inherit text color by default via `className="w-6 h-6 text-current"`
- Consider using `FlowbiteIcons` provider for global icon configuration

## Benefits

- **Consistency**: All icons from same design system as UI components
- **Performance**: Potentially smaller bundle size
- **Flexibility**: Easy switching between outline and solid variants
- **Maintainability**: Single icon source aligned with Flowbite ecosystem
