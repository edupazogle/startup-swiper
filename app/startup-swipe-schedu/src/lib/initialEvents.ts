import { CalendarEvent } from './types'

export const initialEvents: Omit<CalendarEvent, 'attendees'>[] = [
  {
    id: 'wed-0900-linkedin',
    title: 'LinkedIn Promo!',
    startTime: '2025-11-19T09:00:00.000Z',
    endTime: '2025-11-19T09:30:00.000Z',
    type: 'presentation',
    isFixed: true,
    link: '/linkedin'
  },
  {
    id: 'wed-1000-opening',
    title: 'Opening show',
    startTime: '2025-11-19T10:00:00.000Z',
    endTime: '2025-11-19T10:10:00.000Z',
    type: 'presentation',
    location: 'Founder stage',
    isFixed: true
  },
  {
    id: 'wed-1010-lovable',
    title: 'All you need is Lovable - Lovable and Axcel',
    startTime: '2025-11-19T10:10:00.000Z',
    endTime: '2025-11-19T10:20:00.000Z',
    type: 'presentation',
    location: 'Founder stage',
    category: 'Software development',
    isFixed: true
  },
  {
    id: 'wed-1040-european-tech',
    title: '2025 state of European Tech',
    startTime: '2025-11-19T10:40:00.000Z',
    endTime: '2025-11-19T10:50:00.000Z',
    type: 'presentation',
    location: 'Founder stage',
    category: 'Venture',
    isFixed: true
  },
  {
    id: 'wed-1050-us-capital',
    title: 'How US Capital shapes european startups - A16Z, Redpoint, Bessemer VP',
    startTime: '2025-11-19T10:50:00.000Z',
    endTime: '2025-11-19T11:00:00.000Z',
    type: 'presentation',
    location: 'Impact stage',
    category: 'Venture',
    isFixed: true
  },
  {
    id: 'wed-1110-multiverse',
    title: 'Panel discussion: Multiverse computing, European Parliament',
    startTime: '2025-11-19T11:10:00.000Z',
    endTime: '2025-11-19T11:20:00.000Z',
    type: 'presentation',
    location: 'Impact stage',
    category: 'DeepTech computing',
    isFixed: true
  },
  {
    id: 'wed-1200-slush100-semi',
    title: 'Slush 100 Semi-finals - 20 Startup pitches',
    startTime: '2025-11-19T12:00:00.000Z',
    endTime: '2025-11-19T12:20:00.000Z',
    type: 'presentation',
    location: 'Startup stage',
    category: 'Slush 100',
    isFixed: true
  },
  {
    id: 'wed-1230-lunch',
    title: 'Lunch! 🦌🍴',
    startTime: '2025-11-19T12:30:00.000Z',
    endTime: '2025-11-19T13:30:00.000Z',
    type: 'break',
    isFixed: true
  },
  {
    id: 'wed-1230-google-idea',
    title: 'Deciding which idea to pursue - Google',
    startTime: '2025-11-19T12:30:00.000Z',
    endTime: '2025-11-19T12:40:00.000Z',
    type: 'presentation',
    location: 'Builder stage',
    category: 'Great speakers',
    isFixed: true
  },
  {
    id: 'wed-1240-harvey',
    title: 'How Harvey is changing the legal game - Harvey, Kleiner P',
    startTime: '2025-11-19T12:40:00.000Z',
    endTime: '2025-11-19T12:50:00.000Z',
    type: 'presentation',
    location: 'Builder stage',
    category: 'Agentic AI',
    isFixed: true
  },
  {
    id: 'wed-1300-benedict',
    title: 'Benedict Evans',
    startTime: '2025-11-19T13:00:00.000Z',
    endTime: '2025-11-19T13:10:00.000Z',
    type: 'presentation',
    location: 'Impact stage',
    category: 'Great speakers',
    isFixed: true
  },
  {
    id: 'wed-1330-tegmark',
    title: 'The miseducation of AI - Signal, Silo AI',
    startTime: '2025-11-19T13:30:00.000Z',
    endTime: '2025-11-19T13:40:00.000Z',
    type: 'presentation',
    location: 'Builder stage',
    category: 'Agentic AI',
    isFixed: true
  },
  {
    id: 'wed-1350-runway',
    title: 'Creating new realities with Runway - Runway, Bloomberg',
    startTime: '2025-11-19T13:50:00.000Z',
    endTime: '2025-11-19T14:00:00.000Z',
    type: 'presentation',
    location: 'Builder stage',
    category: 'Agentic AI',
    isFixed: true
  },
  {
    id: 'wed-1410-index-ventures',
    title: 'Building european champions - Index Ventures, Slush, Spec*',
    startTime: '2025-11-19T14:10:00.000Z',
    endTime: '2025-11-19T14:30:00.000Z',
    type: 'presentation',
    location: 'Founder stage',
    category: 'Venture',
    isFixed: true
  },
  {
    id: 'wed-1430-openai',
    title: 'How AI rewrites product strategy - OpenAI',
    startTime: '2025-11-19T14:30:00.000Z',
    endTime: '2025-11-19T14:50:00.000Z',
    type: 'presentation',
    location: 'Builder stage',
    category: 'Agentic AI',
    isFixed: true
  },
  {
    id: 'wed-1430-general-catalyst',
    title: 'The transformational ventures of General Catalyst - General Catalyst',
    startTime: '2025-11-19T14:30:00.000Z',
    endTime: '2025-11-19T14:50:00.000Z',
    type: 'presentation',
    location: 'Founder stage',
    category: 'Venture',
    isFixed: true
  },
  {
    id: 'wed-1510-niantic',
    title: 'From words to worlds: unlocking 2d - Lightspeed VP, Niantic Spatial',
    startTime: '2025-11-19T15:10:00.000Z',
    endTime: '2025-11-19T15:20:00.000Z',
    type: 'presentation',
    location: 'Startup stage',
    category: 'Agentic AI',
    isFixed: true
  },
  {
    id: 'wed-1510-slush100-finalists',
    title: 'Slush 100 finalists announced',
    startTime: '2025-11-19T15:10:00.000Z',
    endTime: '2025-11-19T15:20:00.000Z',
    type: 'presentation',
    location: 'Startup stage',
    category: 'Slush 100',
    isFixed: true
  },
  {
    id: 'wed-1520-anthropic',
    title: 'Deciding to go global - Anthropic, Lovable',
    startTime: '2025-11-19T15:20:00.000Z',
    endTime: '2025-11-19T15:30:00.000Z',
    type: 'presentation',
    location: 'Builder stage',
    category: 'Agentic AI',
    isFixed: true
  },
  {
    id: 'wed-1550-h-company',
    title: 'The H factor - H Company',
    startTime: '2025-11-19T15:50:00.000Z',
    endTime: '2025-11-19T16:00:00.000Z',
    type: 'presentation',
    location: 'Builder stage',
    category: 'Agentic AI',
    isFixed: true
  },
  {
    id: 'wed-1610-hippocratic',
    title: 'Do no Harm: scaling health - Hippocratic AI, General Catalyst',
    startTime: '2025-11-19T16:10:00.000Z',
    endTime: '2025-11-19T16:20:00.000Z',
    type: 'presentation',
    location: 'Impact stage',
    category: 'Health',
    isFixed: true
  },
  {
    id: 'wed-1630-ai-workflows',
    title: 'Health - The future of wearables & AI workflows - From office to industry',
    startTime: '2025-11-19T16:30:00.000Z',
    endTime: '2025-11-19T17:00:00.000Z',
    type: 'presentation',
    location: 'Startup stage',
    category: 'Health',
    isFixed: true
  },
  {
    id: 'wed-1640-hugging-face',
    title: 'AI of the hurricane - Hugging Face, Black Forrest Labs',
    startTime: '2025-11-19T16:40:00.000Z',
    endTime: '2025-11-19T16:50:00.000Z',
    type: 'presentation',
    location: 'Impact stage',
    category: 'Agentic AI',
    isFixed: true
  },
  {
    id: 'wed-1800-linkedin',
    title: 'LinkedIn Promo!',
    startTime: '2025-11-19T18:00:00.000Z',
    endTime: '2025-11-19T18:30:00.000Z',
    type: 'presentation',
    isFixed: true,
    link: '/linkedin'
  },
  {
    id: 'thu-0900-linkedin',
    title: 'LinkedIn Promo!',
    startTime: '2025-11-20T09:00:00.000Z',
    endTime: '2025-11-20T09:30:00.000Z',
    type: 'presentation',
    isFixed: true,
    link: '/linkedin'
  },
  {
    id: 'thu-1000-deeptech-quantum',
    title: 'Deeptech-Quantum - Planqc',
    startTime: '2025-11-20T10:00:00.000Z',
    endTime: '2025-11-20T10:10:00.000Z',
    type: 'presentation',
    location: 'Startup stage',
    category: 'DeepTech computing',
    isFixed: true
  },
  {
    id: 'thu-1030-nothing-google',
    title: 'Nothing matters: building hardware in the age of AI - Nothing, Google',
    startTime: '2025-11-20T10:30:00.000Z',
    endTime: '2025-11-20T10:40:00.000Z',
    type: 'presentation',
    location: 'Founder stage',
    category: 'Software development',
    isFixed: true
  },
  {
    id: 'thu-1040-portia-ai',
    title: 'Building AI-native teams - Portia AI',
    startTime: '2025-11-20T10:40:00.000Z',
    endTime: '2025-11-20T10:50:00.000Z',
    type: 'presentation',
    location: 'Builder stage',
    category: 'Software development',
    isFixed: true
  },
  {
    id: 'thu-1140-personio',
    title: 'Your personal AI assistant - Personio, Axcel',
    startTime: '2025-11-20T11:40:00.000Z',
    endTime: '2025-11-20T11:50:00.000Z',
    type: 'presentation',
    location: 'Founder stage',
    category: 'Software development',
    isFixed: true
  },
  {
    id: 'thu-1210-brussels',
    title: 'What Brussels is doing to help founders win - European commission, EU startups',
    startTime: '2025-11-20T12:10:00.000Z',
    endTime: '2025-11-20T12:20:00.000Z',
    type: 'presentation',
    location: 'Founder stage',
    category: 'Venture',
    isFixed: true
  },
  {
    id: 'thu-1220-dust-sequoia',
    title: 'Dusting off overhyped agents - Dust, Sequoia',
    startTime: '2025-11-20T12:20:00.000Z',
    endTime: '2025-11-20T12:30:00.000Z',
    type: 'presentation',
    location: 'Impact stage',
    category: 'Agentic AI',
    isFixed: true
  },
  {
    id: 'thu-1230-lunch',
    title: 'Lunch! 🦌🍴',
    startTime: '2025-11-20T12:30:00.000Z',
    endTime: '2025-11-20T13:30:00.000Z',
    type: 'break',
    isFixed: true
  },
  {
    id: 'thu-1230-bolt',
    title: 'Bolting forward - Bolt',
    startTime: '2025-11-20T12:30:00.000Z',
    endTime: '2025-11-20T12:40:00.000Z',
    type: 'presentation',
    location: 'Founder stage',
    category: 'Venture',
    isFixed: true
  },
  {
    id: 'thu-1240-ai-infrastructure',
    title: 'AI-Infrastructure and core - Trismik, priot labs, Literal labs',
    startTime: '2025-11-20T12:40:00.000Z',
    endTime: '2025-11-20T12:50:00.000Z',
    type: 'presentation',
    location: 'Venture clienting',
    category: 'Agentic AI',
    isFixed: true
  },
  {
    id: 'thu-1310-quantdown',
    title: 'Final Quantdown - IQM, Alice&Bob, Bloomberg news',
    startTime: '2025-11-20T13:10:00.000Z',
    endTime: '2025-11-20T13:20:00.000Z',
    type: 'presentation',
    location: 'Impact stage',
    category: 'DeepTech computing',
    isFixed: true
  },
  {
    id: 'thu-1320-agentic-axa',
    title: 'Agentic-powered processes at AXA, the startup edge',
    startTime: '2025-11-20T13:20:00.000Z',
    endTime: '2025-11-20T13:30:00.000Z',
    type: 'presentation',
    location: 'Venture clienting',
    category: 'Agentic AI',
    isFixed: true,
    highlight: true
  },
  {
    id: 'thu-1330-psiquantum',
    title: 'Quantum leap of faith - PsiQuantum, FT, Sifted',
    startTime: '2025-11-20T13:30:00.000Z',
    endTime: '2025-11-20T13:40:00.000Z',
    type: 'presentation',
    location: 'Founder stage',
    category: 'DeepTech computing',
    isFixed: true
  },
  {
    id: 'thu-1410-health-deeptech',
    title: 'Health-Data and deeptech - Costa labs, Robeauté, Oxom care',
    startTime: '2025-11-20T14:10:00.000Z',
    endTime: '2025-11-20T14:20:00.000Z',
    type: 'presentation',
    location: 'Venture clienting',
    category: 'Health',
    isFixed: true
  },
  {
    id: 'thu-1420-startups-talk',
    title: 'Talk with startups coming to us',
    startTime: '2025-11-20T14:20:00.000Z',
    endTime: '2025-11-20T14:30:00.000Z',
    type: 'presentation',
    location: 'Venture clienting',
    category: 'Venture',
    isFixed: true
  },
  {
    id: 'thu-1420-energy',
    title: 'Energy - software and AI - Tern, Trawe',
    startTime: '2025-11-20T14:20:00.000Z',
    endTime: '2025-11-20T14:30:00.000Z',
    type: 'presentation',
    location: 'Startup stage',
    category: 'Software development',
    isFixed: true
  },
  {
    id: 'thu-1430-health-drug',
    title: 'Health-Drug and treatment discovery - Cures1, Orakl Oncology, Relation',
    startTime: '2025-11-20T14:30:00.000Z',
    endTime: '2025-11-20T14:50:00.000Z',
    type: 'presentation',
    location: 'Venture clienting',
    category: 'Health',
    isFixed: true
  },
  {
    id: 'thu-1450-fal-ai',
    title: 'Features and labels and everything inbetween - Fal, AIez',
    startTime: '2025-11-20T14:50:00.000Z',
    endTime: '2025-11-20T15:00:00.000Z',
    type: 'presentation',
    location: 'Founder stage',
    category: 'Agentic AI',
    isFixed: true
  },
  {
    id: 'thu-1510-ai-automation',
    title: 'AI-Automation and agents - Sintra, SynthFlow AI, Anam, Asendra AI',
    startTime: '2025-11-20T15:10:00.000Z',
    endTime: '2025-11-20T15:20:00.000Z',
    type: 'presentation',
    location: 'Venture clienting',
    category: 'Agentic AI',
    isFixed: true
  },
  {
    id: 'thu-1520-storytelling',
    title: 'Storytelling and brand building - Musa Tariq, Felix Capital',
    startTime: '2025-11-20T15:20:00.000Z',
    endTime: '2025-11-20T15:30:00.000Z',
    type: 'presentation',
    location: 'Startup stage',
    category: 'Great speakers',
    isFixed: true
  },
  {
    id: 'thu-1550-moen',
    title: 'How mën is connecting the nodes - aha, Axcel',
    startTime: '2025-11-20T15:50:00.000Z',
    endTime: '2025-11-20T16:00:00.000Z',
    type: 'presentation',
    location: 'Impact stage',
    category: 'Health',
    isFixed: true
  },
  {
    id: 'thu-1600-fireside-gianni',
    title: 'Fireside chat with Gianni Cuzzo and Elena Moneta',
    startTime: '2025-11-20T16:00:00.000Z',
    endTime: '2025-11-20T16:10:00.000Z',
    type: 'presentation',
    location: 'Impact stage',
    category: 'Great speakers',
    isFixed: true
  },
  {
    id: 'thu-1610-fireside-shultz',
    title: 'Fireside chat with Alex Shultz - Meta',
    startTime: '2025-11-20T16:10:00.000Z',
    endTime: '2025-11-20T16:20:00.000Z',
    type: 'presentation',
    location: 'Founder stage',
    category: 'Great speakers',
    isFixed: true
  },
  {
    id: 'thu-1620-ai-vertical',
    title: 'AI-Vertical applications - Cortex AI, Ethon AI, AI Bob, Wizebot',
    startTime: '2025-11-20T16:20:00.000Z',
    endTime: '2025-11-20T16:30:00.000Z',
    type: 'presentation',
    location: 'Venture clienting',
    category: 'Agentic AI',
    isFixed: true
  },
  {
    id: 'thu-1630-mystery-box',
    title: 'Mystery box - Thor dynamics, Adaptive ML',
    startTime: '2025-11-20T16:30:00.000Z',
    endTime: '2025-11-20T16:40:00.000Z',
    type: 'presentation',
    location: 'Venture clienting',
    category: 'DeepTech computing',
    isFixed: true
  },
  {
    id: 'thu-1700-slush100-finals',
    title: 'Slush 100 - Finals',
    startTime: '2025-11-20T17:00:00.000Z',
    endTime: '2025-11-20T17:10:00.000Z',
    type: 'presentation',
    location: 'Founder stage',
    category: 'Slush 100',
    isFixed: true
  },
  {
    id: 'thu-1720-slush100-winner',
    title: 'Slush 100 winner announcement',
    startTime: '2025-11-20T17:20:00.000Z',
    endTime: '2025-11-20T17:30:00.000Z',
    type: 'presentation',
    location: 'Founder stage',
    category: 'Slush 100',
    isFixed: true
  },
  {
    id: 'thu-1800-linkedin',
    title: 'LinkedIn Promo!',
    startTime: '2025-11-20T18:00:00.000Z',
    endTime: '2025-11-20T18:30:00.000Z',
    type: 'presentation',
    isFixed: true,
    link: '/linkedin'
  }
]
