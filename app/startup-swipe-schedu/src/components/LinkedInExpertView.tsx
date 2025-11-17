import { useState, useRef, useEffect } from 'react'
import { useKV } from '@/lib/useKV'
import { useIsMobile } from '@/hooks/use-mobile'
import { ChatMessage } from '@/lib/types'
import { Button } from '@/components/ui/button'
import { Card } from '@/components/ui/card'
import { Textarea } from '@/components/ui/textarea'
import { Badge } from '@/components/ui/badge'
import { ScrollArea } from '@/components/ui/scroll-area'
import { PaperPlane, WandMagicSparkles, FileCopy, ShareNodes, User } from 'flowbite-react-icons/outline'
import { Linkedin } from 'flowbite-react-icons/solid'
import { toast } from 'sonner'
import { motion, AnimatePresence } from 'framer-motion'

interface LinkedInExpertViewProps {
  currentUserName: string
}

export function LinkedInExpertView({ currentUserName }: LinkedInExpertViewProps) {
  const isMobile = useIsMobile()
  const [messages, setMessages] = useKV<ChatMessage[]>('linkedin-chat-messages', [])
  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const scrollRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLTextAreaElement>(null)

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight
    }
  }, [messages])

  const handleSendMessage = async () => {
    if (!input.trim() || isLoading) return

    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      role: 'user',
      content: input.trim(),
      timestamp: Date.now()
    }

    setMessages((current) => [...(current || []), userMessage])
    setInput('')
    setIsLoading(true)

    try {
      const userRequest = input.trim()
      
      const promptText = `You are the "on-the-ground" digital voice for ${currentUserName} at Slush 2024. Your mission is to capture the energy, insights, and connections being made and share them on LinkedIn.

===== YOUR PERSONA & MISSION =====

Your voice should be:
• Enthusiastic & Passionate: You're thrilled to be there. Use emojis like 🚀, ✨, 🔥, 🇫🇮
• Insightful: Don't just report what happened; share what it means. What's the "so what"?
• Global & Forward-Looking: Connect small observations to big trends (Tech, AI, VC, Global Strategy)
• Personal & Authentic: Share your personal reflections. "It was a real pleasure to...", "Fascinating to see...", "I've been thinking about..."
• Visually Driven: Every post should be anchored by a photo or video

The Goal: To sound like a human leader, not an AI. Share energy and key takeaways.

===== FRANK'S CONTENT STYLE (The "How-To") =====

1. START WITH A BANG: Always lead with a relevant emoji
   Examples:
   • 🚀 Breaking News from Slush...
   • ✨ What an incredible panel on AI...
   • 🇫🇮 Amazing energy here in Helsinki...

2. TELL A QUICK STORY: What did you just see? Who did you just meet?
   • "Just bumped into [@Name] of [@Company] and had a fascinating chat about..."
   • "Incredible to hear [@Speaker] break down the future of [Topic]..."

3. SHARE ONE KEY INSIGHT: Don't write a novel. What's the one big idea you're taking away?
   • "My key takeaway: [Your simple, powerful insight]."
   • "It's clear that [Trend] is shaping the next wave of innovation."

4. CONNECT IT BACK: Why does this matter to you, AXA Venture Clienting, or your network?
   • "This aligns perfectly with how we see the future of [Industry]..."
   • "For AXA Venture Clienting, this signals [connection to strategy]..."

5. SIGN OFF WITH EXCITEMENT: End with a forward-looking statement
   • "Excited for what's next!"
   • "Thrilled to be part of the conversation."

===== LINKEDIN PUBLICATION BEST STRATEGIES (The "Rules") =====

TIMING IS EVERYTHING (Event-Mode):
• The "best time" during an event is NOW
• Post in real-time or as close to it as possible
• A post about a morning panel has the most impact before lunch, not at 5 PM
• Capture the immediacy

THE POWER OF TAGGING (@):
• Tag People: Tag speakers, founders you meet, or partners you're with
• Format as [@FirstName LastName] so they can be tagged on LinkedIn
• Why? It notifies them (they might re-share!) and makes your post visible to their networks
• Weave it into text naturally
  ✓ Good: ✨ Great panel on AI with [@Jane Doe] and [@John Smith]...
  ✗ Bad: Tags: @JaneDoe, @JohnSmith (This looks spammy)

SMART HASHTAGGING (#):
• Don't overdo it. Stick to 3-5 relevant hashtags
• Must-Haves: #Slush2024 (or #Slush2025), #Helsinki
• Topic Tags: #AI, #Startups, #VentureCapital, #Tech, #Innovation
• Place them at the END of the post for a clean look

MEDIA IS NON-NEGOTIABLE:
• A post with no image/video is invisible
• Best Options:
  - Photos of People: A selfie with a founder, shot of your team, pic of speaker on stage
  - Short Videos: A 15-second clip of the crowd or a powerful quote from a speaker
  - A Bad Photo > No Photo: Even a slightly blurry shot that captures energy beats text-only

THE FIRST LINE IS THE "HOOK":
• LinkedIn hides the rest of your post after ~2-3 lines
• Your first sentence must make someone stop scrolling
  ✓ Good Hook: 🚀 What an incredible insight from the main stage...
  ✗ Bad Hook: Today I am attending the Slush 2024 event in Helsinki. It is an event for startups. (Too slow!)

SPARK CONVERSATION (When Possible):
• End with a simple question to your network
  - "What's the most exciting startup you've seen at #Slush2024?"
  - "Do you agree that [Trend] is the next big thing?"

===== YOUR TASK =====

User's content request: ${userRequest}

Generate a complete LinkedIn post ready to copy and paste that follows ALL the rules above. 

IMPORTANT:
- If the user mentions specific people or companies, format them as [@FirstName LastName] for tagging
- Include a reminder at the end about attaching a photo or video for maximum engagement
- Make it feel immediate and exciting, like it's happening RIGHT NOW
- Sound like ${currentUserName}, a human leader sharing authentic insights`

      const response = await window.spark.llm(promptText, 'gpt-4o')

      const assistantMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: response,
        timestamp: Date.now()
      }

      setMessages((current) => [...(current || []), assistantMessage])
    } catch (error) {
      toast.error('Failed to generate response. Please try again.')
    } finally {
      setIsLoading(false)
    }
  }

  const handleCopyMessage = (content: string) => {
    navigator.clipboard.writeText(content)
    toast.success('Copied to clipboard!')
  }

  const handleClearChat = () => {
    setMessages([])
    toast.success('Chat cleared')
  }

  const handleShareOnLinkedIn = (content: string) => {
    const linkedInShareUrl = `https://www.linkedin.com/feed/?shareActive=true&text=${encodeURIComponent(content)}`
    window.open(linkedInShareUrl, '_blank', 'noopener,noreferrer')
    toast.success('Opening LinkedIn...')
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey && !isMobile) {
      e.preventDefault()
      handleSendMessage()
    }
  }

  const quickActions = [
    "I just met the founder of [Startup Name] who is working on [Topic] - fascinating conversation about the future of [Industry]",
    "Amazing panel on stage with [Speaker Names] discussing [Topic] - the energy was electric and the insights were game-changing",
    "What meetings do I have?",
    "What startups should I prioritize if I am interested in?"
  ]

  const handleQuickAction = (prompt: string) => {
    setInput(prompt)
  }

  return (
    <div className="h-full flex flex-col">
      <div className="bg-gradient-to-r from-primary/20 to-accent/20 p-4 md:p-6 border-b border-border/50">
        <div className="max-w-4xl mx-auto">
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 rounded-full bg-primary/20 flex items-center justify-center">
              <Linkedin className="text-primary w-6 h-6"  />
            </div>
            <div>
              <h2 className="text-xl md:text-2xl font-semibold">FrankAI - LinkedIn Expert</h2>
              <p className="text-sm text-muted-foreground">Your Slush 2024 voice - capture energy & insights</p>
            </div>
          </div>
        </div>
      </div>

      <div className="flex-1 max-w-4xl w-full mx-auto flex flex-col">
        <ScrollArea className="flex-1 p-4 md:p-6" ref={scrollRef}>
          {(!messages || messages.length === 0) && (
            <div className="flex flex-col items-center justify-center h-full text-center py-12">
              <WandMagicSparkles className="text-primary/50 mb-4 w-12 h-12"  />
              <h3 className="text-lg font-semibold mb-2">Ready to Capture the Slush Energy 🚀</h3>
              <p className="text-sm text-muted-foreground mb-6 max-w-md">
                Describe your experience - who you met, what panel you saw, the insight you had - and I'll transform it into an engaging LinkedIn post with proper tagging, hooks, and hashtags
              </p>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-2 max-w-2xl w-full">
                {quickActions.map((prompt, idx) => (
                  <Button
                    key={idx}
                    variant="outline"
                    className="justify-start text-left h-auto py-3 px-4"
                    onClick={() => handleQuickAction(prompt)}
                  >
                    <WandMagicSparkles className="mr-2 flex-shrink-0 text-primary w-4 h-4"  />
                    <span className="text-sm">{prompt}</span>
                  </Button>
                ))}
              </div>
            </div>
          )}

          <AnimatePresence>
            {(messages || []).map((message) => (
              <motion.div
                key={message.id}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -10 }}
                className={`flex gap-3 mb-4 ${
                  message.role === 'user' ? 'justify-end' : 'justify-start'
                }`}
              >
              {message.role === 'assistant' && (
                <div className="w-8 h-8 rounded-full bg-primary/20 flex items-center justify-center flex-shrink-0">
                  <Linkedin className="text-primary w-5 h-5"  />
                </div>
              )}
              <Card
                className={`p-3 md:p-4 max-w-[80%] ${
                  message.role === 'user'
                    ? 'bg-primary text-primary-foreground'
                    : 'bg-card'
                }`}
              >
                {message.role === 'assistant' && (
                  <div className="flex items-start justify-between gap-4 mb-3">
                    <Badge variant="secondary" className="gap-1">
                      <WandMagicSparkles className="w-4 h-4"  />
                      AI Generated
                    </Badge>
                    <div className="flex gap-2">
                      <Button
                        size="sm"
                        variant="ghost"
                        onClick={() => handleCopyMessage(message.content)}
                        className="gap-2"
                      >
                        <FileCopy className="w-4 h-4"  />
                        Copy
                      </Button>
                      <Button
                        size="sm"
                        variant="default"
                        onClick={() => handleShareOnLinkedIn(message.content)}
                        className="gap-2"
                      >
                        <ShareAllNetwork size={16}  />
                        {!isMobile && "Share"}
                      </Button>
                    </div>
                  </div>
                )}
                <p className="text-sm whitespace-pre-wrap">{message.content}</p>
                <span className="text-xs opacity-70 mt-2 block">
                  {new Date(message.timestamp).toLocaleTimeString()}
                </span>
              </Card>
              {message.role === 'user' && (
                <div className="w-8 h-8 rounded-full bg-accent/20 flex items-center justify-center flex-shrink-0">
                  <User className="text-accent w-5 h-5"  />
                </div>
              )}
            </motion.div>
          ))}
          </AnimatePresence>

          {isLoading && (
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              className="flex gap-3 mb-4"
            >
              <div className="w-8 h-8 rounded-full bg-primary/20 flex items-center justify-center flex-shrink-0">
                <Linkedin className="text-primary w-5 h-5"  />
              </div>
              <Card className="p-3 md:p-4 bg-card">
                <div className="flex gap-1">
                  <span className="w-2 h-2 bg-primary/50 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                  <span className="w-2 h-2 bg-primary/50 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                  <span className="w-2 h-2 bg-primary/50 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
                </div>
              </Card>
            </motion.div>
          )}
        </ScrollArea>

        <div className="p-4 border-t border-border/50 bg-card/50">
          <div className="flex gap-2">
            <Textarea
              ref={inputRef}
              placeholder={isMobile 
                ? "Describe your Slush experience..." 
                : "e.g., 'Just met Jane Smith from AI Startup X, we talked about the future of healthcare AI...'"
              }
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyPress}
              disabled={isLoading}
              rows={isMobile ? 2 : 3}
              className="resize-none flex-1"
            />
            <Button
              onClick={handleSendMessage}
              disabled={!input.trim() || isLoading}
              size="icon"
            >
              <PaperPlane className="w-5 h-5"  />
            </Button>
          </div>
        </div>
      </div>
    </div>
  )
}
