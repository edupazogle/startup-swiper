export interface ExportOptions {
  format: 'json' | 'markdown' | 'txt'
  includeTimestamps: boolean
  includeMetadata: boolean
}

export interface ChatMessage {
  id: string
  role: 'user' | 'assistant'
  content: string
  timestamp: number | string
}

export function exportConversation(
  messages: ChatMessage[],
  options: ExportOptions = {
    format: 'markdown',
    includeTimestamps: true,
    includeMetadata: true
  }
): string {
  switch (options.format) {
    case 'json':
      return exportAsJSON(messages, options)
    case 'markdown':
      return exportAsMarkdown(messages, options)
    case 'txt':
      return exportAsText(messages, options)
    default:
      return exportAsMarkdown(messages, options)
  }
}

function exportAsJSON(messages: ChatMessage[], options: ExportOptions): string {
  const data = {
    ...(options.includeMetadata && {
      exportedAt: new Date().toISOString(),
      messageCount: messages.length
    }),
    messages: messages.map(msg => ({
      role: msg.role,
      content: msg.content,
      ...(options.includeTimestamps && { timestamp: msg.timestamp })
    }))
  }
  return JSON.stringify(data, null, 2)
}

function exportAsMarkdown(messages: ChatMessage[], options: ExportOptions): string {
  const lines: string[] = []

  if (options.includeMetadata) {
    lines.push('# Chat Conversation Export')
    lines.push(`*Exported: ${new Date().toLocaleString()}*`)
    lines.push(`*Messages: ${messages.length}*`)
    lines.push('')
  }

  messages.forEach(msg => {
    const prefix = msg.role === 'user' ? '👤 You' : '🤖 Assistant'
    lines.push(`## ${prefix}`)
    
    if (options.includeTimestamps && msg.timestamp) {
      const time = typeof msg.timestamp === 'number' 
        ? new Date(msg.timestamp).toLocaleString()
        : msg.timestamp
      lines.push(`*${time}*`)
    }

    lines.push('')
    lines.push(msg.content)
    lines.push('')
  })

  return lines.join('\n')
}

function exportAsText(messages: ChatMessage[], options: ExportOptions): string {
  const lines: string[] = []

  if (options.includeMetadata) {
    lines.push('CHAT CONVERSATION EXPORT')
    lines.push(`Exported: ${new Date().toLocaleString()}`)
    lines.push(`Messages: ${messages.length}`)
    lines.push('')
    lines.push('='.repeat(50))
    lines.push('')
  }

  messages.forEach(msg => {
    const prefix = msg.role === 'user' ? '[YOU]' : '[ASSISTANT]'
    lines.push(prefix)
    
    if (options.includeTimestamps && msg.timestamp) {
      const time = typeof msg.timestamp === 'number' 
        ? new Date(msg.timestamp).toLocaleString()
        : msg.timestamp
      lines.push(`Time: ${time}`)
    }

    lines.push(msg.content)
    lines.push('-'.repeat(50))
  })

  return lines.join('\n')
}

export function downloadConversation(
  messages: ChatMessage[],
  filename: string,
  options: ExportOptions
): void {
  const content = exportConversation(messages, options)
  const blob = new Blob([content], { type: 'text/plain' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = filename
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  URL.revokeObjectURL(url)
}

export function generateExportFilename(format: string): string {
  const timestamp = new Date().toISOString().split('T')[0]
  const time = new Date().toLocaleTimeString().replace(/:/g, '-')
  const ext = format === 'json' ? 'json' : 'txt'
  return `chat-${timestamp}-${time}.${ext}`
}
