import { Card } from '@/components/ui/card'
import { ArrowUpRightFromSquare } from 'flowbite-react-icons/outline'
import { Startup } from '@/lib/types'

interface Article {
  title: string
  description: string
  imageUrl: string
  link: string
  source: string
  date: string
}

interface StartupArticlesProps {
  startup: Startup
}

export function StartupArticles({ startup }: StartupArticlesProps) {
  const displayName = startup.name || startup["Company Name"] || 'Unknown Startup'
  
  const mockArticles: Article[] = [
    {
      title: `${displayName} Raises New Funding Round`,
      description: `The innovative startup secures significant investment to accelerate growth and expand market presence.`,
      imageUrl: 'https://images.unsplash.com/photo-1579532537598-459ecdaf39cc?w=400&h=250&fit=crop',
      link: '#',
      source: 'TechCrunch',
      date: '2 days ago'
    },
    {
      title: `Industry Leaders Partner with ${displayName}`,
      description: `Strategic partnership aims to revolutionize the sector and bring cutting-edge solutions to market.`,
      imageUrl: 'https://images.unsplash.com/photo-1557804506-669a67965ba0?w=400&h=250&fit=crop',
      link: '#',
      source: 'VentureBeat',
      date: '5 days ago'
    },
    {
      title: `${displayName} Expands to New Markets`,
      description: `Ambitious expansion plans unveiled as company scales operations internationally with new product line.`,
      imageUrl: 'https://images.unsplash.com/photo-1460925895917-afdab827c52f?w=400&h=250&fit=crop',
      link: '#',
      source: 'Forbes',
      date: '1 week ago'
    }
  ]

  return (
    <div className="h-full flex flex-col p-4">
      <div className="mb-3">
        <h3 className="text-sm font-semibold text-foreground">Related Articles</h3>
        <p className="text-xs text-muted-foreground">Latest news about {displayName}</p>
      </div>

      <div className="flex-1 overflow-y-auto space-y-3">
        {mockArticles.map((article, idx) => (
          <a
            key={idx}
            href={article.link}
            target="_blank"
            rel="noopener noreferrer"
            className="block group"
          >
            <Card className="overflow-hidden hover:shadow-lg transition-all duration-300 border-border/50 hover:border-accent/50">
              <div className="relative h-32 overflow-hidden bg-muted">
                <img 
                  src={article.imageUrl} 
                  alt={article.title}
                  className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                />
                <div className="absolute top-2 right-2 w-7 h-7 bg-white/90 backdrop-blur-sm rounded-full flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity">
                  <ArrowUpRightFromSquare className="text-foreground w-4 h-4"  />
                </div>
              </div>
              
              <div className="p-3">
                <h4 className="text-sm font-semibold text-foreground mb-1.5 line-clamp-2 group-hover:text-accent transition-colors">
                  {article.title}
                </h4>
                <p className="text-xs text-muted-foreground mb-2 line-clamp-2 leading-relaxed">
                  {article.description}
                </p>
                <div className="flex items-center justify-between text-xs">
                  <span className="text-muted-foreground font-medium">
                    {article.source}
                  </span>
                  <span className="text-muted-foreground">
                    {article.date}
                  </span>
                </div>
              </div>
            </Card>
          </a>
        ))}
      </div>
    </div>
  )
}
